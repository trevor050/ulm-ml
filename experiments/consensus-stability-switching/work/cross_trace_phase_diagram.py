#!/usr/bin/env python3
"""Cross-trace selectability regime sweep over sample count N."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import random
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_bootstrap_module():
    spec = importlib.util.spec_from_file_location("canonical_gap_bootstrap_ci", ROOT / "work" / "canonical_gap_bootstrap_ci.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


BOOT = load_bootstrap_module()
MB = BOOT.MB

METRICS = ["any_correct", "cluster_sum", "headroom", "top5", "top10", "top20", "top20_gain", "top20_headroom_closed"]


def fmt(x: float) -> str:
    return f"{x:.3f}"


def classify_regime(row: dict[str, float]) -> str:
    if row["any_correct"] >= 0.95 and row["headroom"] <= 0.20:
        return "shallow/surfaced"
    if row["any_correct"] < 0.40:
        return "coverage-limited"
    if row["headroom"] >= 0.30:
        return "depth-limited"
    return "mixed"


def score_problem_for_n(
    row: dict,
    verifier: np.ndarray,
    n: int,
    trials_per_problem: int,
    seed: int,
    pid: int,
) -> dict:
    rng = random.Random(seed + 100_003 * n + pid)
    trial_indices = [rng.sample(range(len(row["samples"])), n) for _ in range(trials_per_problem)]
    feature_indices = sorted({idx for trial in trial_indices for idx in trial})
    features = np.array([MB.candidate_features(row["samples"][idx]) for idx in feature_indices], dtype=float)
    scores = MB.predict_logistic(verifier, features)
    scores_by_idx = dict(zip(feature_indices, map(float, scores), strict=True))
    answers_by_idx = {idx: MB.extract_answer(row["samples"][idx]) for idx in feature_indices}
    labels_by_idx = {idx: bool(row["is_corrects"][idx]) for idx in feature_indices}
    trial_rows = [BOOT.trial_metrics(idxs, scores_by_idx, answers_by_idx, labels_by_idx) for idxs in trial_indices]
    out = {"problem_id": pid, "trials": len(trial_rows)}
    for key in ["any_correct", "cluster_sum", "top2", "top3", "top5", "top10", "top20", "top50"]:
        out[key] = sum(t[key] for t in trial_rows) / len(trial_rows)
    out["_miss_ranks"] = [t["miss_rank"] for t in trial_rows if t["miss_rank"] is not None]
    return out


def run_dataset(label: str, data: list[dict], args: argparse.Namespace) -> list[dict]:
    train_ids, test_ids = BOOT.split_problem_ids(len(data), args.verifier_train_problems, args.audit_holdout_gap, args.seed)
    print(f"=== {label} ===", flush=True)
    print(f"training verifier on {len(train_ids)} problems", flush=True)
    verifier, info = MB.train_candidate_verifier(data, train_ids, args.verifier_samples_per_problem, args.seed)
    print(
        f"verifier train samples={info['samples']} positive_rate={info['positive_rate']:.3f}; "
        f"heldout problems={len(test_ids)}",
        flush=True,
    )

    by_n: dict[int, list[dict]] = defaultdict(list)
    for j, pid in enumerate(test_ids, start=1):
        if j == 1 or j % 25 == 0 or j == len(test_ids):
            print(f"scoring heldout problem {j}/{len(test_ids)}", flush=True)
        row = data[pid]
        for n in args.ns:
            by_n[n].append(score_problem_for_n(row, verifier, n, args.trials_per_problem, args.seed, pid))

    rows = []
    for n in args.ns:
        agg = BOOT.aggregate(by_n[n])
        out = {"dataset": label, "n": n, "problems": agg["problems"], "regime": classify_regime(agg)}
        for metric in METRICS:
            out[metric] = agg[metric]
        out["miss_rank_p50"] = agg["miss_rank_p50"]
        out["miss_rank_p75"] = agg["miss_rank_p75"]
        out["miss_rank_p90"] = agg["miss_rank_p90"]
        rows.append(out)
    return rows


def transition_summary(rows: list[dict]) -> list[dict]:
    out = []
    for dataset in sorted({row["dataset"] for row in rows}):
        ds_rows = sorted([row for row in rows if row["dataset"] == dataset], key=lambda r: int(r["n"]))
        regimes = " -> ".join(f"N={row['n']}:{row['regime']}" for row in ds_rows)
        max_headroom = max(ds_rows, key=lambda r: float(r["headroom"]))
        final = ds_rows[-1]
        out.append(
            {
                "dataset": dataset,
                "path": regimes,
                "max_headroom_n": max_headroom["n"],
                "max_headroom": max_headroom["headroom"],
                "final_n": final["n"],
                "final_regime": final["regime"],
                "final_any_correct": final["any_correct"],
                "final_cluster_sum": final["cluster_sum"],
                "final_headroom": final["headroom"],
            }
        )
    return out


def write_outputs(rows: list[dict], args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    fields = [
        "dataset",
        "n",
        "regime",
        "problems",
        *METRICS,
        "miss_rank_p50",
        "miss_rank_p75",
        "miss_rank_p90",
    ]
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    trans_path = OUT / f"{args.output_prefix}_transitions.csv"
    trans_rows = transition_summary(rows)
    with trans_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "dataset",
                "path",
                "max_headroom_n",
                "max_headroom",
                "final_n",
                "final_regime",
                "final_any_correct",
                "final_cluster_sum",
                "final_headroom",
            ],
        )
        writer.writeheader()
        writer.writerows(trans_rows)

    lines = [
        "# Cross-Trace Selectability Phase Diagram",
        "",
        "N-sweep over all local Monkey Business traces using the same cheap verifier and answer-cluster depth metrics.",
        "",
        f"Config: seed `{args.seed}`, N values `{', '.join(map(str, args.ns))}`, trials/problem `{args.trials_per_problem}`, verifier train problems `{args.verifier_train_problems}`, verifier samples/problem `{args.verifier_samples_per_problem}`.",
        "",
        "| dataset | N | regime | cluster_sum | oracle | headroom | top10 | top20 | top20 gain | top20 closed | miss p50/p90 |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(rows, key=lambda r: (r["dataset"], int(r["n"]))):
        lines.append(
            f"| {row['dataset']} | {row['n']} | {row['regime']} | "
            f"{fmt(row['cluster_sum'])} | {fmt(row['any_correct'])} | {fmt(row['headroom'])} | "
            f"{fmt(row['top10'])} | {fmt(row['top20'])} | {fmt(row['top20_gain'])} | "
            f"{fmt(row['top20_headroom_closed'])} | {row['miss_rank_p50']} / {row['miss_rank_p90']} |"
        )
    lines += [
        "",
        "## Regime Paths",
        "",
        "| dataset | path | max headroom | final read |",
        "|---|---|---:|---|",
    ]
    for row in trans_rows:
        lines.append(
            f"| {row['dataset']} | {row['path']} | "
            f"N={row['max_headroom_n']} {fmt(row['max_headroom'])} | "
            f"N={row['final_n']} {row['final_regime']}, oracle {fmt(row['final_any_correct'])}, cluster_sum {fmt(row['final_cluster_sum'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "The regime view is sample-count dependent. GSM8K/Llama quickly enters a shallow/surfaced regime. MATH/Pythia remains coverage-limited across the sweep. MATH/Llama and MATH/Gemma transition from coverage-limited or mixed at low N into depth-limited high-coverage regimes, which is the setting where adaptive cluster-depth verification is most motivated.",
        "",
        f"CSV: [{csv_path.name}]({csv_path.name}).",
        f"Transitions CSV: [{trans_path.name}]({trans_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(trans_path)
    print(md_path.read_text())


def run(args: argparse.Namespace) -> None:
    rows = []
    for spec in args.dataset:
        label, path = spec.split("=", 1)
        data = MB.load_data(Path(path))
        rows.extend(run_dataset(label, data, args))
    write_outputs(rows, args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", nargs="+", required=True, help="label=path")
    parser.add_argument("--ns", nargs="+", type=int, default=[4, 8, 16, 32, 64, 128])
    parser.add_argument("--trials-per-problem", type=int, default=12)
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--audit-holdout-gap", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--output-prefix", default="cross_trace_phase_diagram")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
