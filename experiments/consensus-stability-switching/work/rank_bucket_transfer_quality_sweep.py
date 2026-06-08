#!/usr/bin/env python3
"""Verifier-quality sweep for rank-bucket cross-model transfer."""

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


TRANSFER = load_module("rank_bucket_cross_model_transfer", ROOT / "work" / "rank_bucket_cross_model_transfer.py")
RBDP = TRANSFER.RBDP
BDP = TRANSFER.BDP


def parse_float_list(raw: str) -> list[float]:
    return [float(part) for part in raw.split(",") if part.strip()]


def parse_int_list(raw: str) -> list[int]:
    return [int(part) for part in raw.split(",") if part.strip()]


def quality_label(success: float, regress: float) -> str:
    return f"s{success:g}_r{regress:g}"


def make_candidates_for_quality(
    dataset: str,
    rows: list[dict],
    probs: list[dict[str, float]],
    costs: dict[tuple[str, int], float],
    depths: list[int],
    verifier_success: float,
    false_regress: float,
) -> list[dict]:
    candidates = []
    for row_id, bucket_probs in enumerate(probs):
        for depth in depths:
            prob = RBDP.prob_recoverable_by_depth(bucket_probs, depth)
            utility = BDP.expected_utility(prob, verifier_success, false_regress)
            if utility <= 0:
                continue
            cost = costs[(dataset, depth)]
            candidates.append(
                {
                    "row_id": row_id,
                    "depth": depth,
                    "prob_recoverable": prob,
                    "expected_utility": utility,
                    "cost": cost,
                    "density": utility / cost,
                }
            )
    return candidates


def evaluate_transfer_pair_quality(
    train_dataset: str,
    train_calib_rows: list[dict],
    target_dataset: str,
    target_test_rows: list[dict],
    costs: dict[tuple[str, int], float],
    args: argparse.Namespace,
) -> list[dict]:
    models = RBDP.fit_bucket_models(train_calib_rows)
    probs = RBDP.predict_bucket_probs(models, target_test_rows)
    train_dist = RBDP.bucket_distribution(train_calib_rows)
    target_dist = RBDP.bucket_distribution(target_test_rows)

    rows = []
    for success in args.success_grid:
        for regress in args.regress_grid:
            candidates = make_candidates_for_quality(
                target_dataset,
                target_test_rows,
                probs,
                costs,
                args.depths,
                success,
                regress,
            )
            for budget in args.budgets:
                selected = BDP.greedy_select(candidates, total_budget=budget * len(target_test_rows))
                result = BDP.evaluate_policy(target_test_rows, selected, success, regress)
                rows.append(
                    {
                        "seed": args.seed,
                        "quality": quality_label(success, regress),
                        "verifier_success": success,
                        "false_regress": regress,
                        "train_dataset": train_dataset,
                        "target_dataset": target_dataset,
                        "transfer": "within" if train_dataset == target_dataset else "cross",
                        "budget_tokens_per_problem": budget,
                        "projected_acc": result["projected_acc"],
                        "projected_delta": result["projected_delta"],
                        "cluster_sum": result["cluster_sum"],
                        "tokens_per_problem": result["tokens_per_problem"],
                        "invoke_rate": result["invoke_rate"],
                        "depth5_rate": result["depth5_rate"],
                        "depth10_rate": result["depth10_rate"],
                        "depth20_rate": result["depth20_rate"],
                        "avg_depth_if_invoked": result["avg_depth_if_invoked"],
                        "recoverable_invoked_rate": result["recoverable_invoked_rate"],
                        "false_or_unhelpful_invoked_rate": result["false_or_unhelpful_invoked_rate"],
                        "train_top5_rate": train_dist["top5"],
                        "train_top10_only_rate": train_dist["top10_only"],
                        "train_top20_only_rate": train_dist["top20_only"],
                        "target_top5_rate": target_dist["top5"],
                        "target_top10_only_rate": target_dist["top10_only"],
                        "target_top20_only_rate": target_dist["top20_only"],
                        "acc_gap_vs_within": "",
                        "delta_gap_vs_within": "",
                    }
                )
    return rows


def annotate_gaps(rows: list[dict]) -> list[dict]:
    within = {
        (
            row["seed"],
            row["quality"],
            row["target_dataset"],
            float(row["budget_tokens_per_problem"]),
        ): row
        for row in rows
        if row["transfer"] == "within"
    }
    for row in rows:
        base = within.get(
            (
                row["seed"],
                row["quality"],
                row["target_dataset"],
                float(row["budget_tokens_per_problem"]),
            )
        )
        if base is None:
            continue
        row["acc_gap_vs_within"] = float(row["projected_acc"]) - float(base["projected_acc"])
        row["delta_gap_vs_within"] = float(row["projected_delta"]) - float(base["projected_delta"])
    return rows


def run_seed(seed: int, args: argparse.Namespace, costs: dict[tuple[str, int], float]) -> list[dict]:
    seed_args = argparse.Namespace(**vars(args))
    seed_args.seed = seed
    prepared = TRANSFER.prepare_seed(seed, seed_args)
    rows = []
    for train_dataset, (train_calib_rows, _train_test_rows) in prepared.items():
        for target_dataset, (_target_calib_rows, target_test_rows) in prepared.items():
            rows.extend(
                evaluate_transfer_pair_quality(
                    train_dataset,
                    train_calib_rows,
                    target_dataset,
                    target_test_rows,
                    costs,
                    seed_args,
                )
            )
    return annotate_gaps(rows)


def mean_std(vals: list[float]) -> tuple[float, float]:
    return statistics.mean(vals), statistics.pstdev(vals) if len(vals) > 1 else 0.0


def aggregate(rows: list[dict]) -> list[dict]:
    groups = {}
    for row in rows:
        key = (
            row["quality"],
            float(row["verifier_success"]),
            float(row["false_regress"]),
            row["train_dataset"],
            row["target_dataset"],
            row["transfer"],
            float(row["budget_tokens_per_problem"]),
        )
        groups.setdefault(key, []).append(row)

    out = []
    for (quality, success, regress, train_dataset, target_dataset, transfer, budget), vals in sorted(groups.items()):
        acc_mean, acc_std = mean_std([float(row["projected_acc"]) for row in vals])
        delta_mean, delta_std = mean_std([float(row["projected_delta"]) for row in vals])
        gap_mean, gap_std = mean_std([float(row["acc_gap_vs_within"]) for row in vals])
        invoke_mean, _ = mean_std([float(row["invoke_rate"]) for row in vals])
        d5_mean, _ = mean_std([float(row["depth5_rate"]) for row in vals])
        d10_mean, _ = mean_std([float(row["depth10_rate"]) for row in vals])
        d20_mean, _ = mean_std([float(row["depth20_rate"]) for row in vals])
        spent_mean, _ = mean_std([float(row["tokens_per_problem"]) for row in vals])
        out.append(
            {
                "quality": quality,
                "verifier_success": success,
                "false_regress": regress,
                "train_dataset": train_dataset,
                "target_dataset": target_dataset,
                "transfer": transfer,
                "budget_tokens_per_problem": budget,
                "seeds": len(vals),
                "acc_mean": acc_mean,
                "acc_std": acc_std,
                "delta_mean": delta_mean,
                "delta_std": delta_std,
                "acc_gap_vs_within_mean": gap_mean,
                "acc_gap_vs_within_std": gap_std,
                "invoke_rate_mean": invoke_mean,
                "depth5_rate_mean": d5_mean,
                "depth10_rate_mean": d10_mean,
                "depth20_rate_mean": d20_mean,
                "spent_tokens_mean": spent_mean,
            }
        )
    return out


def focus_rows(rows: list[dict], args: argparse.Namespace) -> list[dict]:
    focus_budget = float(args.focus_budget)
    focus_qualities = set(args.focus_qualities)
    return [
        row
        for row in rows
        if row["transfer"] == "cross"
        and float(row["budget_tokens_per_problem"]) == focus_budget
        and row["quality"] in focus_qualities
    ]


def summarize_quality(rows: list[dict], args: argparse.Namespace) -> list[dict]:
    focus_budget = float(args.focus_budget)
    out = []
    for row in rows:
        if row["transfer"] != "cross" or float(row["budget_tokens_per_problem"]) != focus_budget:
            continue
        out.append(
            {
                "quality": row["quality"],
                "train_dataset": row["train_dataset"],
                "target_dataset": row["target_dataset"],
                "acc_mean": row["acc_mean"],
                "delta_mean": row["delta_mean"],
                "gap_vs_within": row["acc_gap_vs_within_mean"],
                "invoke_rate": row["invoke_rate_mean"],
                "depth20_rate": row["depth20_rate_mean"],
            }
        )
    return out


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

    summary = summarize_quality(agg_rows, args)
    summary_path = OUT / f"{args.output_prefix}_summary.csv"
    with summary_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)

    lines = [
        "# Rank-Bucket Transfer Quality Sweep",
        "",
        "This audit repeats the v85 cross-model rank-bucket transfer test across verifier success / false-regression assumptions. Candidate scoring and bucket probabilities are computed once per seed, then the verifier-quality assumptions change only the action utilities and selected depth budget.",
        "",
        f"Seeds: `{args.seeds}`. Budget focus: `{args.focus_budget}` tokens/problem. Success grid: `{args.success_grid}`. False-regression grid: `{args.regress_grid}`.",
        "",
        "| quality | train | target | acc mean | delta mean | gap vs within | invoke | depth20 |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in focus_rows(agg_rows, args):
        lines.append(
            f"| {row['quality']} | {row['train_dataset']} | {row['target_dataset']} | "
            f"{row['acc_mean']:.3f} | {row['delta_mean']:+.3f} | {row['acc_gap_vs_within_mean']:+.3f} | "
            f"{row['invoke_rate_mean']:.2f} | {row['depth20_rate_mean']:.2f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "The target question is not whether lower-quality verifiers produce high absolute accuracy; lower success and higher false-regression naturally reduce projected gains. The question is whether cross-model allocation collapses relative to within-model allocation. Small cross-vs-within gaps across the quality grid mean the bucket-depth mapping transfers; large or sign-flipping gaps mean it is calibration fragile.",
        "",
        "Caveat: this remains projected verifier-quality evidence. It does not replace a measured verifier run.",
        "",
        f"Aggregate CSV: [{agg_path.name}]({agg_path.name}). Raw CSV: [{raw_path.name}]({raw_path.name}). Summary CSV: [{summary_path.name}]({summary_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(agg_path)
    print(raw_path)
    print(summary_path)
    print(md_path.read_text())


def run(args: argparse.Namespace) -> None:
    args.depths = parse_int_list(args.depths)
    args.budgets = parse_float_list(args.budgets)
    args.success_grid = parse_float_list(args.success_grid)
    args.regress_grid = parse_float_list(args.regress_grid)
    args.focus_qualities = [part.strip() for part in args.focus_qualities.split(",") if part.strip()]
    seeds = parse_int_list(args.seeds)
    costs = BDP.compact_costs()
    raw_rows = []
    for seed in seeds:
        print(f"rank-bucket transfer quality seed={seed}", flush=True)
        raw_rows.extend(run_seed(seed, args, costs))
    write_outputs(raw_rows, aggregate(raw_rows), args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="rank_bucket_transfer_quality_sweep")
    parser.add_argument("--seeds", default="60601,60631,60661")
    parser.add_argument("--focus-budget", type=float, default=1024)
    parser.add_argument("--focus-qualities", default="s0.5_r0.05,s0.8_r0.02,s1_r0")
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--calib-problems", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--calib-trials", type=int, default=48)
    parser.add_argument("--test-trials", type=int, default=12)
    parser.add_argument("--n", type=int, default=128)
    parser.add_argument("--depths", default="5,10,20")
    parser.add_argument("--budgets", default="512,1024")
    parser.add_argument("--success-grid", default="0.50,0.80,1.00")
    parser.add_argument("--regress-grid", default="0.00,0.02,0.05")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
