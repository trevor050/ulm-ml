#!/usr/bin/env python3
"""Compare two pairwise router-judge budget rows trial-by-trial."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def parse_bool(value: object) -> bool:
    return str(value).lower() == "true"


def load_pairs(path: Path, low_budget: int, high_budget: int) -> list[dict]:
    by_key: dict[tuple[int, int, int, str], dict[int, dict]] = defaultdict(dict)
    with path.open() as f:
        for row in csv.DictReader(f):
            budget = int(row["regression_budget"])
            if budget not in {low_budget, high_budget}:
                continue
            row["seed"] = int(row["seed"])
            row["pid"] = int(row["pid"])
            row["trial"] = int(row["trial"])
            row["baseline_correct"] = parse_bool(row["baseline_correct"])
            row["raw_router_correct"] = parse_bool(row["raw_router_correct"])
            row["pairwise_gated_correct"] = parse_bool(row["pairwise_gated_correct"])
            row["raw_accept"] = parse_bool(row["raw_accept"])
            row["pairwise_accept"] = parse_bool(row["pairwise_accept"])
            key = (row["seed"], row["pid"], row["trial"], row["policy"])
            by_key[key][budget] = row
    out = []
    for (seed, pid, trial, policy), rows in sorted(by_key.items()):
        if low_budget not in rows or high_budget not in rows:
            continue
        low = rows[low_budget]
        high = rows[high_budget]
        increment = int(high["pairwise_gated_correct"]) - int(low["pairwise_gated_correct"])
        out.append(
            {
                "seed": seed,
                "pid": pid,
                "trial": trial,
                "policy": policy,
                "baseline_correct": low["baseline_correct"],
                "raw_router_correct": low["raw_router_correct"],
                "low_correct": low["pairwise_gated_correct"],
                "high_correct": high["pairwise_gated_correct"],
                "increment": increment,
                "low_accept": low["pairwise_accept"],
                "high_accept": high["pairwise_accept"],
                "low_judge": low["judge_model"],
                "low_rule": low["judge_rule"],
                "low_choice": low["judge_choice"],
                "high_judge": high["judge_model"],
                "high_rule": high["judge_rule"],
                "high_choice": high["judge_choice"],
                "low_packet": low["packet_id"],
                "high_packet": high["packet_id"],
            }
        )
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def group_rows(rows: list[dict]) -> dict[tuple[int, int], list[dict]]:
    groups: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(int(row["seed"]), int(row["pid"]))].append(row)
    return groups


def leave_one_out(rows: list[dict]) -> list[dict]:
    groups = group_rows(rows)
    total_increment = sum(int(row["increment"]) for row in rows)
    total_rows = len(rows)
    out = []
    for (seed, pid), vals in sorted(groups.items()):
        group_increment = sum(int(row["increment"]) for row in vals)
        kept_rows = total_rows - len(vals)
        kept_increment = total_increment - group_increment
        out.append(
            {
                "dropped_seed": seed,
                "dropped_pid": pid,
                "dropped_trials": len(vals),
                "dropped_increment": group_increment,
                "loo_increment_delta": kept_increment / max(1, kept_rows),
            }
        )
    return out


def fmt_counter(counter: Counter) -> str:
    return "; ".join(f"{key}:{val}" for key, val in counter.most_common()) or "-"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--details", type=Path, default=OUT / "pairwise_router_judge_natural_rate_v125_budget2_details.csv")
    parser.add_argument("--low-budget", type=int, default=1)
    parser.add_argument("--high-budget", type=int, default=2)
    parser.add_argument("--output-prefix", default="pairwise_router_budget_increment_v129")
    args = parser.parse_args()

    rows = load_pairs(args.details, args.low_budget, args.high_budget)
    if not rows:
        raise ValueError(f"no paired rows found in {args.details}")
    loo = leave_one_out(rows)
    groups = group_rows(rows)
    group_rows_out = [
        {
            "seed": seed,
            "pid": pid,
            "trials": len(vals),
            "increment": sum(int(row["increment"]) for row in vals),
            "positive_trials": sum(int(row["increment"]) > 0 for row in vals),
            "negative_trials": sum(int(row["increment"]) < 0 for row in vals),
        }
        for (seed, pid), vals in sorted(groups.items())
    ]
    total_increment = sum(int(row["increment"]) for row in rows)
    positive_trials = sum(int(row["increment"]) > 0 for row in rows)
    negative_trials = sum(int(row["increment"]) < 0 for row in rows)
    by_policy = Counter()
    by_policy_signed = Counter()
    by_seed = Counter()
    for row in rows:
        inc = int(row["increment"])
        if inc:
            by_policy[(row["policy"], inc)] += 1
            by_policy_signed[row["policy"]] += inc
            by_seed[row["seed"]] += inc

    write_csv(OUT / f"{args.output_prefix}_trial_deltas.csv", rows)
    write_csv(OUT / f"{args.output_prefix}_loo.csv", loo)
    write_csv(OUT / f"{args.output_prefix}_group_deltas.csv", group_rows_out)

    min_loo = min(loo, key=lambda row: float(row["loo_increment_delta"]))
    max_loo = max(loo, key=lambda row: float(row["loo_increment_delta"]))
    top_positive = sorted(group_rows_out, key=lambda row: int(row["increment"]), reverse=True)[:12]
    top_negative = [row for row in sorted(group_rows_out, key=lambda row: int(row["increment"]))[:12] if int(row["increment"]) < 0]
    md = OUT / f"{args.output_prefix}.md"
    lines = [
        "# Pairwise Router-Judge Budget Increment Audit",
        "",
        f"Input details: `{args.details.name}`. This compares pairwise source budget `{args.high_budget}` against budget `{args.low_budget}` trial-by-trial.",
        "",
        "## Aggregate",
        "",
        "| trials | net increment | delta | positive trials | negative trials | positive groups | negative groups | zero groups | LOO positive | min LOO | max LOO |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        f"| {len(rows)} | {total_increment:+d} | {total_increment / len(rows):+.3f} | {positive_trials} | {negative_trials} | "
        f"{sum(int(row['increment']) > 0 for row in group_rows_out)} | {sum(int(row['increment']) < 0 for row in group_rows_out)} | "
        f"{sum(int(row['increment']) == 0 for row in group_rows_out)} | {sum(float(row['loo_increment_delta']) > 0 for row in loo)}/{len(loo)} | "
        f"{float(min_loo['loo_increment_delta']):+.3f} dropping s{min_loo['dropped_seed']}/p{min_loo['dropped_pid']} | "
        f"{float(max_loo['loo_increment_delta']):+.3f} dropping s{max_loo['dropped_seed']}/p{max_loo['dropped_pid']} |",
        "",
        "## Breakdowns",
        "",
        f"- Signed policy increment: `{fmt_counter(by_policy_signed)}`",
        f"- Trial changes by policy/sign: `{fmt_counter(by_policy)}`",
        f"- Signed seed increment: `{fmt_counter(by_seed)}`",
        "",
        "## Top Positive Groups",
        "",
        "| seed | pid | trials | increment | positive trials | negative trials |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in top_positive:
        lines.append(f"| {row['seed']} | {row['pid']} | {row['trials']} | {int(row['increment']):+d} | {row['positive_trials']} | {row['negative_trials']} |")
    lines.extend(["", "## Negative Groups", "", "| seed | pid | trials | increment | positive trials | negative trials |", "|---:|---:|---:|---:|---:|---:|"])
    for row in top_negative:
        lines.append(f"| {row['seed']} | {row['pid']} | {row['trials']} | {int(row['increment']):+d} | {row['positive_trials']} | {row['negative_trials']} |")
    if not top_negative:
        lines.append("| - | - | - | - | - | - |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "The increment audit separates the high-budget gain from the already-positive lower-budget result. If the increment is positive under every leave-one-problem-out drop, the extra budget is not a single-problem artifact. If most groups are zero, the increment is still sparse and should be reported as a risk/reward tail choice rather than a broad selector improvement.",
            "",
            f"Trial deltas: [{args.output_prefix}_trial_deltas.csv]({args.output_prefix}_trial_deltas.csv). Group deltas: [{args.output_prefix}_group_deltas.csv]({args.output_prefix}_group_deltas.csv). LOO: [{args.output_prefix}_loo.csv]({args.output_prefix}_loo.csv).",
        ]
    )
    md.write_text("\n".join(lines))
    print(md)
    print(md.read_text())


if __name__ == "__main__":
    main()
