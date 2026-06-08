#!/usr/bin/env python3
"""Multi-seed robustness sweep for rank-bucket depth allocation."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


RBDP = load_module("rank_bucket_depth_policy", ROOT / "work" / "rank_bucket_depth_policy.py")


def f(row: dict, key: str) -> float:
    return float(row[key])


def aggregate(rows: list[dict]) -> list[dict]:
    groups = {}
    for row in rows:
        key = (row["dataset"], float(row["budget_tokens_per_problem"]), row["policy"])
        groups.setdefault(key, []).append(row)
    out = []
    for (dataset, budget, policy), vals in sorted(groups.items()):
        accs = [f(v, "projected_acc") for v in vals]
        deltas = [f(v, "projected_delta") for v in vals]
        invokes = [f(v, "invoke_rate") for v in vals]
        d5s = [f(v, "depth5_rate") for v in vals]
        d10s = [f(v, "depth10_rate") for v in vals]
        d20s = [f(v, "depth20_rate") for v in vals]
        spent = [f(v, "tokens_per_problem") for v in vals]
        out.append(
            {
                "dataset": dataset,
                "budget_tokens_per_problem": budget,
                "policy": policy,
                "seeds": len(vals),
                "acc_mean": statistics.mean(accs),
                "acc_std": statistics.pstdev(accs),
                "delta_mean": statistics.mean(deltas),
                "delta_std": statistics.pstdev(deltas),
                "invoke_rate_mean": statistics.mean(invokes),
                "depth5_rate_mean": statistics.mean(d5s),
                "depth10_rate_mean": statistics.mean(d10s),
                "depth20_rate_mean": statistics.mean(d20s),
                "spent_tokens_mean": statistics.mean(spent),
            }
        )
    return out


def focus_rows(rows: list[dict], budgets: list[float]) -> list[dict]:
    wanted = set(float(x) for x in budgets)
    return [row for row in rows if float(row["budget_tokens_per_problem"]) in wanted]


def run_one(seed: int, args: argparse.Namespace) -> list[dict]:
    run_args = argparse.Namespace(
        output_prefix=f"{args.output_prefix}_seed_{seed}",
        seed=seed,
        verifier_train_problems=args.verifier_train_problems,
        calib_problems=args.calib_problems,
        verifier_samples_per_problem=args.verifier_samples_per_problem,
        calib_trials=args.calib_trials,
        test_trials=args.test_trials,
        n=args.n,
        depths=args.depths,
        budgets=args.budgets,
        verifier_success=args.verifier_success,
        false_regress=args.false_regress,
    )
    RBDP.run(run_args)
    path = OUT / f"{args.output_prefix}_seed_{seed}.csv"
    rows = []
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            row["seed"] = seed
            rows.append(row)
    return rows


def write_outputs(raw_rows: list[dict], agg_rows: list[dict], args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raw_path = OUT / f"{args.output_prefix}_raw.csv"
    with raw_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw_rows[0].keys()))
        writer.writeheader()
        writer.writerows(raw_rows)

    agg_path = OUT / f"{args.output_prefix}.csv"
    with agg_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(agg_rows[0].keys()))
        writer.writeheader()
        writer.writerows(agg_rows)

    focus_budgets = [float(x) for x in args.focus_budgets.split(",") if x.strip()]
    focus = focus_rows(agg_rows, focus_budgets)
    lines = [
        "# Rank-Bucket Policy Seed Sweep",
        "",
        f"Seeds: `{args.seeds}`. Budgets: `{args.budgets}`.",
        "",
        "This robustness sweep reruns the rank-bucket depth allocation policy on multiple train/calibration/test splits and reports mean projected accuracy and mean delta over `cluster_sum`.",
        "",
        "| dataset | budget | acc mean | acc std | delta mean | delta std | invoke | depth mix | spent tokens |",
        "|---|---:|---:|---:|---:|---:|---:|---|---:|",
    ]
    for row in focus:
        mix = f"5:{row['depth5_rate_mean']:.2f}, 10:{row['depth10_rate_mean']:.2f}, 20:{row['depth20_rate_mean']:.2f}"
        lines.append(
            f"| {row['dataset']} | {row['budget_tokens_per_problem']:.0f} | {row['acc_mean']:.3f} | {row['acc_std']:.3f} | "
            f"{row['delta_mean']:+.3f} | {row['delta_std']:.3f} | {row['invoke_rate_mean']:.2f} | {mix} | {row['spent_tokens_mean']:.0f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "This is still a projected verifier-success result. The quantity to trust is the mean delta over `cluster_sum`; the standard deviation shows how much the policy moves with split/seed. A stable positive delta supports the rank-bucket depth-allocation direction, while the external verifier run remains the missing benchmark.",
        "",
        f"Aggregate CSV: [{agg_path.name}]({agg_path.name}). Raw CSV: [{raw_path.name}]({raw_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(agg_path)
    print(raw_path)
    print(md_path.read_text())


def run(args: argparse.Namespace) -> None:
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    raw_rows = []
    for seed in seeds:
        print(f"rank-bucket sweep seed={seed}", flush=True)
        raw_rows.extend(run_one(seed, args))
    agg_rows = aggregate(raw_rows)
    write_outputs(raw_rows, agg_rows, args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="rank_bucket_seed_sweep")
    parser.add_argument("--seeds", default="60601,60631,60661")
    parser.add_argument("--focus-budgets", default="512,1024")
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--calib-problems", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--calib-trials", type=int, default=48)
    parser.add_argument("--test-trials", type=int, default=12)
    parser.add_argument("--n", type=int, default=128)
    parser.add_argument("--depths", default="5,10,20")
    parser.add_argument("--budgets", default="128,256,512,1024")
    parser.add_argument("--verifier-success", type=float, default=0.8)
    parser.add_argument("--false-regress", type=float, default=0.02)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
