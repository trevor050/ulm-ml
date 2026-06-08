#!/usr/bin/env python3
"""Multi-seed robustness check for selected failure-detector variants."""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path

import numpy as np

import failure_detector_zoo as zoo


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


SELECTED_VARIANTS = [
    ("hand_risk", None, None, None),
    ("all_raw", "all", "raw", 5e-3),
    ("support_diversity_raw", "support_diversity", "raw", 5e-3),
    ("support_diversity_quadratic", "support_diversity", "quadratic", 5e-2),
    ("all_quadratic", "all", "quadratic", 1e-1),
    ("diversity_only_raw", "diversity_only", "raw", 5e-3),
]


def score_variant(name: str, subset: str | None, mode: str | None, l2: float | None, train_rows: list[dict], test_rows: list[dict]) -> np.ndarray:
    train_x_all = np.array([r["features"] for r in train_rows], dtype=float)
    test_x_all = np.array([r["features"] for r in test_rows], dtype=float)
    if name == "hand_risk":
        return zoo.hand_risk_scores(train_x_all, test_x_all)
    assert subset is not None and mode is not None and l2 is not None
    return zoo.fit_predict(train_rows, test_rows, subset, mode, l2, "visible_miss")


def run_one(dataset: str, data_path: Path, seed: int, args: argparse.Namespace) -> list[dict]:
    train_rows, test_rows, _ = zoo.build_dataset(
        data_path,
        seed,
        args.verifier_train_problems,
        args.calib_problems,
        args.verifier_samples_per_problem,
        args.calib_trials,
        args.test_trials,
        args.n,
    )
    out = []
    for name, subset, mode, l2 in SELECTED_VARIANTS:
        scores = score_variant(name, subset, mode, l2, train_rows, test_rows)
        for row in zoo.evaluate_variant(dataset, name, scores, test_rows):
            row["seed"] = seed
            out.append(row)
    return out


def aggregate(rows: list[dict]) -> list[dict]:
    groups = {}
    for row in rows:
        key = (row["dataset"], row["variant"], round(float(row["invoke_rate"]), 2))
        groups.setdefault(key, []).append(row)
    out = []
    for (dataset, variant, invoke_rate), vals in sorted(groups.items()):
        accs = [float(v["projected_perfect_acc"]) for v in vals]
        aucs = [float(v["auc"]) for v in vals]
        precs = [float(v["precision"]) for v in vals]
        captures = [float(v["visible_miss_capture"]) for v in vals]
        out.append(
            {
                "dataset": dataset,
                "variant": variant,
                "invoke_rate": invoke_rate,
                "seeds": len(vals),
                "acc_mean": statistics.mean(accs),
                "acc_std": statistics.pstdev(accs),
                "auc_mean": statistics.mean(aucs),
                "precision_mean": statistics.mean(precs),
                "capture_mean": statistics.mean(captures),
            }
        )
    return out


def best_rows(agg_rows: list[dict], rates: list[float]) -> list[dict]:
    out = []
    for dataset in sorted({r["dataset"] for r in agg_rows}):
        for rate in rates:
            candidates = [r for r in agg_rows if r["dataset"] == dataset and abs(float(r["invoke_rate"]) - rate) < 0.015]
            if candidates:
                out.append(max(candidates, key=lambda r: float(r["acc_mean"])))
    return out


def run(args: argparse.Namespace) -> None:
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    specs = [
        ("MATH/Llama", ROOT / "work" / "MATH_Llama-3-8B-Instruct.json"),
        ("MATH/Gemma", ROOT / "work" / "MATH_Gemma-2B.json"),
    ]
    rows = []
    for seed in seeds:
        for dataset, path in specs:
            print(f"seed={seed} dataset={dataset}", flush=True)
            rows.extend(run_one(dataset, path, seed, args))

    OUT.mkdir(parents=True, exist_ok=True)
    raw_path = OUT / f"{args.output_prefix}_raw.csv"
    with raw_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    agg_rows = aggregate(rows)
    agg_path = OUT / f"{args.output_prefix}.csv"
    with agg_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(agg_rows[0].keys()))
        writer.writeheader()
        writer.writerows(agg_rows)

    winners = best_rows(agg_rows, [0.10, 0.20, 0.30])
    lines = [
        "# Failure Detector Seed Sweep",
        "",
        f"Seeds: `{', '.join(map(str, seeds))}`. Selected detector variants only; this is a robustness check for v18, not a full hyperparameter search.",
        "",
        "| dataset | invoke | best variant | acc mean | acc std | AUC mean | precision mean | capture mean |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in winners:
        lines.append(
            f"| {row['dataset']} | {float(row['invoke_rate']):.2f} | {row['variant']} | {float(row['acc_mean']):.3f} | {float(row['acc_std']):.3f} | {float(row['auc_mean']):.3f} | {float(row['precision_mean']):.3f} | {float(row['capture_mean']):.3f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "The mean frontier is the quantity to trust here; individual-seed best variants can overstate the deployed method. If the Llama support/diversity family remains near the top across seeds while Gemma stays lower, the detector-improvability claim is robust but model-regime dependent.",
        "",
        f"Aggregate CSV: [{agg_path.name}]({agg_path.name}). Raw CSV: [{raw_path.name}]({raw_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(agg_path)
    print(raw_path)
    print(md_path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="failure_detector_seed_sweep")
    parser.add_argument("--seeds", default="11,17,23")
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--calib-problems", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--calib-trials", type=int, default=48)
    parser.add_argument("--test-trials", type=int, default=12)
    parser.add_argument("--n", type=int, default=128)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
