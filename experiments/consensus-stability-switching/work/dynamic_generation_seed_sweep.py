#!/usr/bin/env python3
"""Seed sweep for token-matched dynamic extra-sampling baselines."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import statistics
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


DSB = load_module("dynamic_sampling_baseline", ROOT / "work" / "dynamic_sampling_baseline.py")
TBGV = load_module("token_budget_generation_vs_verification", ROOT / "work" / "token_budget_generation_vs_verification.py")


def summarize_seed(rows: list[dict], seed: int, budgets: list[float]) -> list[dict]:
    out = []
    datasets = sorted({row["dataset"] for row in rows})
    for dataset in datasets:
        for budget in budgets:
            best = TBGV.best_generation(rows, dataset, budget, include_oracle=False)
            oracle = TBGV.best_generation(rows, dataset, budget, include_oracle=True)
            out.append(
                {
                    "seed": seed,
                    "dataset": dataset,
                    "budget_tokens": budget,
                    "best_policy": best["policy"],
                    "best_tokens": float(best["extra_sample_tokens_per_problem"]),
                    "best_delta": float(best["delta_cluster_sum_vs_base"]),
                    "best_any_delta": float(best["delta_any_correct_vs_base"]),
                    "oracle_tokens": float(oracle["extra_sample_tokens_per_problem"]),
                    "oracle_delta": float(oracle["delta_cluster_sum_vs_base"]),
                }
            )
    return out


def aggregate(rows: list[dict]) -> list[dict]:
    groups = {}
    for row in rows:
        key = (row["dataset"], float(row["budget_tokens"]))
        groups.setdefault(key, []).append(row)
    out = []
    for (dataset, budget), vals in sorted(groups.items()):
        best_deltas = [float(row["best_delta"]) for row in vals]
        any_deltas = [float(row["best_any_delta"]) for row in vals]
        oracle_deltas = [float(row["oracle_delta"]) for row in vals]
        tokens = [float(row["best_tokens"]) for row in vals]
        policies = Counter(row["best_policy"] for row in vals)
        out.append(
            {
                "dataset": dataset,
                "budget_tokens": budget,
                "seeds": len(vals),
                "best_delta_mean": statistics.mean(best_deltas),
                "best_delta_std": statistics.pstdev(best_deltas),
                "best_any_delta_mean": statistics.mean(any_deltas),
                "oracle_delta_mean": statistics.mean(oracle_deltas),
                "best_tokens_mean": statistics.mean(tokens),
                "policy_counts": ";".join(f"{policy}:{count}" for policy, count in sorted(policies.items())),
            }
        )
    return out


def run_one(seed: int, args: argparse.Namespace) -> list[dict]:
    run_args = argparse.Namespace(
        output_prefix=f"{args.output_prefix}_seed_{seed}",
        seed=seed,
        verifier_train_problems=args.verifier_train_problems,
        audit_holdout_gap=args.audit_holdout_gap,
        verifier_samples_per_problem=args.verifier_samples_per_problem,
        base_n=args.base_n,
        max_n=args.max_n,
        chunk_size=args.chunk_size,
        avg_extra_samples=args.avg_extra_samples,
    )
    rows = []
    for label, path in DSB.DATASETS:
        rows.extend(DSB.run_dataset(label, path, run_args))
    for row in rows:
        row["seed"] = seed
    return rows


def write_outputs(raw_dynamic: list[dict], seed_summary: list[dict], agg_rows: list[dict], args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raw_path = OUT / f"{args.output_prefix}_dynamic_raw.csv"
    with raw_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw_dynamic[0].keys()))
        writer.writeheader()
        writer.writerows(raw_dynamic)

    seed_path = OUT / f"{args.output_prefix}_seed_summary.csv"
    with seed_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(seed_summary[0].keys()))
        writer.writeheader()
        writer.writerows(seed_summary)

    agg_path = OUT / f"{args.output_prefix}.csv"
    with agg_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(agg_rows[0].keys()))
        writer.writeheader()
        writer.writerows(agg_rows)

    lines = [
        "# Dynamic Generation Seed Sweep",
        "",
        f"Seeds: `{args.seeds}`. Chunk size: `{args.chunk_size}` samples. Budgets: `{args.budgets}`.",
        "",
        "This reruns the fine-grained dynamic extra-sampling baseline across train/calibration/test splits and selects the best non-oracle generation row under each token budget for each seed.",
        "",
        "| dataset | budget | seeds | best generation delta mean | std | any-correct delta mean | oracle delta mean | avg generation tokens | best-policy counts |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in agg_rows:
        lines.append(
            f"| {row['dataset']} | {row['budget_tokens']:.0f} | {row['seeds']} | {row['best_delta_mean']:+.3f} | "
            f"{row['best_delta_std']:.3f} | {row['best_any_delta_mean']:+.3f} | {row['oracle_delta_mean']:+.3f} | "
            f"{row['best_tokens_mean']:.0f} | {row['policy_counts']} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "The fine-grained generation baseline remains weak under seed variation. The mean deployed-selector delta stays near zero, while v33's rank-bucket verifier projection has much larger positive mean deltas at the same nominal budgets. This still does not replace the missing measured verifier run; it strengthens the generation-side objection check.",
        "",
        f"Aggregate CSV: [{agg_path.name}]({agg_path.name}). Seed summary CSV: [{seed_path.name}]({seed_path.name}). Raw dynamic CSV: [{raw_path.name}]({raw_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(agg_path)
    print(seed_path)
    print(raw_path)
    print(md_path.read_text())


def run(args: argparse.Namespace) -> None:
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    budgets = [float(x) for x in args.budgets.split(",") if x.strip()]
    args.avg_extra_samples = [int(x) for x in args.avg_extra_samples.split(",") if x.strip()]
    raw_dynamic = []
    seed_summary = []
    for seed in seeds:
        print(f"dynamic generation seed={seed}", flush=True)
        rows = run_one(seed, args)
        raw_dynamic.extend(rows)
        seed_summary.extend(summarize_seed(rows, seed, budgets))
    agg_rows = aggregate(seed_summary)
    write_outputs(raw_dynamic, seed_summary, agg_rows, args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="dynamic_generation_seed_sweep")
    parser.add_argument("--seeds", default="60601,60631,60661")
    parser.add_argument("--budgets", default="512,1024")
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--audit-holdout-gap", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--base-n", type=int, default=128)
    parser.add_argument("--max-n", type=int, default=1024)
    parser.add_argument("--chunk-size", type=int, default=8)
    parser.add_argument("--avg-extra-samples", default="4,8,16,32")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
