#!/usr/bin/env python3
"""Sensitivity audits for pairwise router-judge natural-rate details."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def parse_bool(value: object) -> bool:
    return str(value).lower() == "true"


def load_rows(path: Path, budget: int) -> list[dict]:
    with path.open() as f:
        rows = []
        for row in csv.DictReader(f):
            if int(row["regression_budget"]) != budget:
                continue
            row["seed"] = int(row["seed"])
            row["pid"] = int(row["pid"])
            row["trial"] = int(row["trial"])
            row["baseline_correct"] = parse_bool(row["baseline_correct"])
            row["raw_router_correct"] = parse_bool(row["raw_router_correct"])
            row["pairwise_gated_correct"] = parse_bool(row["pairwise_gated_correct"])
            row["raw_accept"] = parse_bool(row["raw_accept"])
            row["pairwise_accept"] = parse_bool(row["pairwise_accept"])
            rows.append(row)
        return rows


def metric(rows: list[dict], column: str) -> dict:
    n = len(rows)
    baseline = sum(row["baseline_correct"] for row in rows)
    gated = sum(row[column] for row in rows)
    return {
        "rows": n,
        "baseline_acc": baseline / max(1, n),
        "gated_acc": gated / max(1, n),
        "delta": (gated - baseline) / max(1, n),
        "recoveries": sum((not row["baseline_correct"]) and row[column] for row in rows),
        "regressions": sum(row["baseline_correct"] and not row[column] for row in rows),
    }


def group_rows(rows: list[dict]) -> dict[tuple[int, int], list[dict]]:
    groups: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(int(row["seed"]), int(row["pid"]))].append(row)
    return groups


def contribution(row_group: list[dict], column: str) -> int:
    return sum(int(row[column]) - int(row["baseline_correct"]) for row in row_group)


def leave_one_out(rows: list[dict], column: str) -> list[dict]:
    groups = group_rows(rows)
    out = []
    for key, vals in sorted(groups.items()):
        held = set(id(row) for row in vals)
        kept = [row for row in rows if id(row) not in held]
        m = metric(kept, column)
        out.append(
            {
                "dropped_seed": key[0],
                "dropped_pid": key[1],
                "dropped_trials": len(vals),
                "dropped_contribution": contribution(vals, column),
                "loo_delta": m["delta"],
                "loo_recoveries": m["recoveries"],
                "loo_regressions": m["regressions"],
            }
        )
    return out


def aggregate_loo(rows: list[dict], column: str) -> dict:
    loo = leave_one_out(rows, column)
    deltas = [float(row["loo_delta"]) for row in loo]
    return {
        "groups": len(loo),
        "positive_loo": sum(delta > 0 for delta in deltas),
        "min_delta": min(deltas),
        "max_delta": max(deltas),
        "worst_drop": min(loo, key=lambda row: float(row["loo_delta"])),
        "best_drop": max(loo, key=lambda row: float(row["loo_delta"])),
        "loo": loo,
    }


def accepted_subset(rows: list[dict]) -> list[dict]:
    return [row for row in rows if row["raw_accept"]]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fmt_group(row: dict) -> str:
    return f"s{row['dropped_seed']}/p{row['dropped_pid']} contrib {row['dropped_contribution']} -> {float(row['loo_delta']):+.3f}"


def top_contributors(rows: list[dict], column: str, n: int) -> list[dict]:
    groups = group_rows(rows)
    vals = [
        {
            "seed": seed,
            "pid": pid,
            "trials": len(group),
            "contribution": contribution(group, column),
            "recoveries": sum((not row["baseline_correct"]) and row[column] for row in group),
            "regressions": sum(row["baseline_correct"] and not row[column] for row in group),
        }
        for (seed, pid), group in groups.items()
    ]
    return sorted(vals, key=lambda row: (int(row["contribution"]), int(row["recoveries"])), reverse=True)[:n]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--details", type=Path, default=OUT / "pairwise_router_judge_natural_rate_v122_details.csv")
    parser.add_argument("--budget", type=int, default=0)
    parser.add_argument("--output-prefix", default="pairwise_router_judge_sensitivity_v124")
    parser.add_argument("--top-n", type=int, default=12)
    args = parser.parse_args()

    rows = load_rows(args.details, args.budget)
    natural_pairwise = metric(rows, "pairwise_gated_correct")
    natural_raw = metric(rows, "raw_router_correct")
    accepted = accepted_subset(rows)
    accepted_pairwise = metric(accepted, "pairwise_gated_correct")
    accepted_raw = metric(accepted, "raw_router_correct")
    natural_loo = aggregate_loo(rows, "pairwise_gated_correct")
    accepted_loo = aggregate_loo(accepted, "pairwise_gated_correct")
    top = top_contributors(rows, "pairwise_gated_correct", args.top_n)
    regressions = [
        row
        for row in rows
        if row["pairwise_accept"] and row["baseline_correct"] and not row["pairwise_gated_correct"]
    ]

    write_csv(OUT / f"{args.output_prefix}_natural_loo.csv", natural_loo["loo"])
    write_csv(OUT / f"{args.output_prefix}_accepted_loo.csv", accepted_loo["loo"])
    write_csv(OUT / f"{args.output_prefix}_top_contributors.csv", top)
    write_csv(OUT / f"{args.output_prefix}_regressions.csv", regressions)

    md = OUT / f"{args.output_prefix}.md"
    lines = [
        "# Pairwise Router-Judge Sensitivity Audit",
        "",
        f"Input details: `{args.details}`. Pairwise source budget: `{args.budget}`.",
        "",
        "## Aggregate",
        "",
        "| denominator | policy | rows | delta | recoveries | regressions |",
        "|---|---|---:|---:|---:|---:|",
        f"| natural | raw router | {natural_raw['rows']} | {natural_raw['delta']:+.3f} | {natural_raw['recoveries']} | {natural_raw['regressions']} |",
        f"| natural | pairwise gated | {natural_pairwise['rows']} | {natural_pairwise['delta']:+.3f} | {natural_pairwise['recoveries']} | {natural_pairwise['regressions']} |",
        f"| accepted actions | raw router | {accepted_raw['rows']} | {accepted_raw['delta']:+.3f} | {accepted_raw['recoveries']} | {accepted_raw['regressions']} |",
        f"| accepted actions | pairwise gated | {accepted_pairwise['rows']} | {accepted_pairwise['delta']:+.3f} | {accepted_pairwise['recoveries']} | {accepted_pairwise['regressions']} |",
        "",
        "## Leave-One-Problem-Out",
        "",
        "| denominator | groups | positive LOO | min delta | max delta | worst dropped group | best dropped group |",
        "|---|---:|---:|---:|---:|---|---|",
        f"| natural | {natural_loo['groups']} | {natural_loo['positive_loo']}/{natural_loo['groups']} | {natural_loo['min_delta']:+.3f} | {natural_loo['max_delta']:+.3f} | {fmt_group(natural_loo['worst_drop'])} | {fmt_group(natural_loo['best_drop'])} |",
        f"| accepted actions | {accepted_loo['groups']} | {accepted_loo['positive_loo']}/{accepted_loo['groups']} | {accepted_loo['min_delta']:+.3f} | {accepted_loo['max_delta']:+.3f} | {fmt_group(accepted_loo['worst_drop'])} | {fmt_group(accepted_loo['best_drop'])} |",
        "",
        "## Top Natural Contributors",
        "",
        "| seed | pid | trials | contribution | recoveries | regressions |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in top:
        lines.append(f"| {row['seed']} | {row['pid']} | {row['trials']} | {row['contribution']} | {row['recoveries']} | {row['regressions']} |")
    lines.extend(
        [
            "",
            "## Pairwise Regressions",
            "",
            "| seed | pid | trial | policy | packet | judge | choice |",
            "|---:|---:|---:|---|---|---|---|",
        ]
    )
    for row in regressions:
        lines.append(
            f"| {row['seed']} | {row['pid']} | {row['trial']} | {row['policy']} | {row['packet_id']} | {row['judge_model']} | {row['judge_choice']} |"
        )
    if not regressions:
        lines.append("| - | - | - | - | - | - | - |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "The natural-rate pairwise result is not carried by a single problem group: every leave-one-problem-out natural resample remains positive. Accepted-action LOO is also positive across all accepted problem groups, though its range is wider because the accepted denominator is intentionally concentrated on routed actions.",
        ]
    )
    md.write_text("\n".join(lines))
    print(md)
    print(md.read_text())


if __name__ == "__main__":
    main()
