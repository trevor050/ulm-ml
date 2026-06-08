#!/usr/bin/env python3
"""Aggregate v103 expanded-target semantic calibration runs."""

from __future__ import annotations

import csv
import glob
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
PATTERN = re.compile(r"semantic_target_calibration_v103_(packet|problem)_(.*)_(numeric|text|both)_seed(\d+)$")
EPS = 1e-9


def f(row: dict, key: str) -> float:
    try:
        return float(row[key])
    except (TypeError, ValueError, KeyError):
        return 0.0


def i(row: dict, key: str) -> int:
    try:
        return int(float(row[key]))
    except (TypeError, ValueError, KeyError):
        return 0


def clean(row: dict, prefix: str) -> bool:
    return i(row, f"{prefix}_baseline_preserved") == i(row, f"{prefix}_baseline_total")


def positive(row: dict, key: str) -> bool:
    return f(row, key) > EPS


def load_rows() -> list[dict]:
    rows = []
    for path in sorted(glob.glob(str(OUT / "semantic_target_calibration_v103_*.csv"))):
        if path.endswith(("_all_rows.csv", "_summary.csv", "_direction_summary.csv")):
            continue
        with open(path, newline="") as fobj:
            for row in csv.DictReader(fobj):
                match = PATTERN.match(row["setup"])
                if not match:
                    continue
                row["overlap_regime"] = match.group(1)
                row["direction"] = match.group(2)
                row["feature_from_name"] = match.group(3)
                row["seed_from_name"] = match.group(4)
                rows.append(row)
    return rows


def best(rows: list[dict], key: str) -> dict:
    return max(rows, key=lambda row: (f(row, key), i(row, "test_recoverable_correct"), i(row, "test_baseline_preserved")))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as fobj:
        writer = csv.DictWriter(fobj, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict]) -> list[dict]:
    out = []
    for regime in ["packet", "problem"]:
        vals = [row for row in rows if row["overlap_regime"] == regime]
        clean_vals = [row for row in vals if clean(row, "test")]
        substantial = [row for row in vals if i(row, "target_test_packets") >= 60]
        substantial_clean = [row for row in substantial if clean(row, "test")]
        best_row = best(vals, "test_delta")
        best_clean = best(clean_vals, "test_delta")
        best_substantial = best(substantial, "test_delta") if substantial else best_row
        best_substantial_clean = best(substantial_clean, "test_delta") if substantial_clean else best_clean
        best_oracle = max(vals, key=lambda row: (f(row, "test_oracle_delta"), i(row, "test_oracle_recoverable_correct"), i(row, "test_oracle_baseline_preserved")))
        out.append(
            {
                "overlap_regime": regime,
                "rows": len(vals),
                "target_calibrated_lower_ci_positive": sum(positive(row, "test_ci_low") for row in vals),
                "target_calibrated_point_positive": sum(positive(row, "test_delta") for row in vals),
                "target_calibrated_clean_point_positive": sum(positive(row, "test_delta") and clean(row, "test") for row in vals),
                "substantial_rows_test_ge60": len(substantial),
                "substantial_clean_point_positive": sum(positive(row, "test_delta") and clean(row, "test") for row in substantial),
                "heldout_oracle_lower_ci_positive": sum(positive(row, "test_oracle_ci_low") for row in vals),
                "best_target_calibrated_setup": best_row["setup"],
                "best_target_calibrated_field": best_row["score_field"],
                "best_target_calibrated_calib_per_category": best_row["target_calib_per_category"],
                "best_target_calibrated_delta": best_row["test_delta"],
                "best_target_calibrated_ci_low": best_row["test_ci_low"],
                "best_target_calibrated_recoveries": best_row["test_recoverable_correct"],
                "best_target_calibrated_baseline": f"{best_row['test_baseline_preserved']}/{best_row['test_baseline_total']}",
                "best_target_calibrated_test_packets": best_row["target_test_packets"],
                "best_clean_delta": best_clean["test_delta"],
                "best_clean_ci_low": best_clean["test_ci_low"],
                "best_clean_recoveries": best_clean["test_recoverable_correct"],
                "best_clean_baseline": f"{best_clean['test_baseline_preserved']}/{best_clean['test_baseline_total']}",
                "best_clean_test_packets": best_clean["target_test_packets"],
                "best_substantial_delta": best_substantial["test_delta"],
                "best_substantial_ci_low": best_substantial["test_ci_low"],
                "best_substantial_baseline": f"{best_substantial['test_baseline_preserved']}/{best_substantial['test_baseline_total']}",
                "best_substantial_test_packets": best_substantial["target_test_packets"],
                "best_substantial_clean_delta": best_substantial_clean["test_delta"],
                "best_substantial_clean_ci_low": best_substantial_clean["test_ci_low"],
                "best_substantial_clean_baseline": f"{best_substantial_clean['test_baseline_preserved']}/{best_substantial_clean['test_baseline_total']}",
                "best_substantial_clean_test_packets": best_substantial_clean["target_test_packets"],
                "best_oracle_setup": best_oracle["setup"],
                "best_oracle_field": best_oracle["score_field"],
                "best_oracle_delta": best_oracle["test_oracle_delta"],
                "best_oracle_ci_low": best_oracle["test_oracle_ci_low"],
                "best_oracle_recoveries": best_oracle["test_oracle_recoverable_correct"],
                "best_oracle_baseline": f"{best_oracle['test_oracle_baseline_preserved']}/{best_oracle['test_oracle_baseline_total']}",
                "best_oracle_test_packets": best_oracle["target_test_packets"],
            }
        )
    return out


def direction_summary(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["overlap_regime"], row["direction"])].append(row)
    out = []
    for (regime, direction), vals in sorted(grouped.items()):
        clean_vals = [row for row in vals if clean(row, "test")]
        best_row = best(vals, "test_delta")
        best_clean = best(clean_vals, "test_delta")
        best_oracle = max(vals, key=lambda row: f(row, "test_oracle_delta"))
        out.append(
            {
                "overlap_regime": regime,
                "direction": direction,
                "rows": len(vals),
                "target_calibrated_lower_ci_positive": sum(positive(row, "test_ci_low") for row in vals),
                "target_calibrated_clean_point_positive": sum(positive(row, "test_delta") and clean(row, "test") for row in vals),
                "heldout_oracle_lower_ci_positive": sum(positive(row, "test_oracle_ci_low") for row in vals),
                "best_target_calibrated_delta": best_row["test_delta"],
                "best_target_calibrated_ci_low": best_row["test_ci_low"],
                "best_target_calibrated_baseline": f"{best_row['test_baseline_preserved']}/{best_row['test_baseline_total']}",
                "best_clean_delta": best_clean["test_delta"],
                "best_clean_ci_low": best_clean["test_ci_low"],
                "best_clean_baseline": f"{best_clean['test_baseline_preserved']}/{best_clean['test_baseline_total']}",
                "best_oracle_delta": best_oracle["test_oracle_delta"],
                "best_oracle_ci_low": best_oracle["test_oracle_ci_low"],
                "best_oracle_baseline": f"{best_oracle['test_oracle_baseline_preserved']}/{best_oracle['test_oracle_baseline_total']}",
            }
        )
    return out


def main() -> None:
    rows = load_rows()
    if not rows:
        raise SystemExit("no v103 rows found")
    all_path = OUT / "semantic_target_calibration_v103_all_rows.csv"
    summary_path = OUT / "semantic_target_calibration_v103_summary.csv"
    direction_path = OUT / "semantic_target_calibration_v103_direction_summary.csv"
    write_csv(all_path, rows)
    summary_rows = summarize(rows)
    direction_rows = direction_summary(rows)
    write_csv(summary_path, summary_rows)
    write_csv(direction_path, direction_rows)

    lines = [
        "# v103 Expanded-Target Semantic Calibration Aggregate",
        "",
        f"Input rows: `{len(rows)}` from `36` runs. Rows train on Llama source packets and evaluate expanded duplicated Gemma target packets (`48/category`).",
        "",
        "| overlap | rows | target-cal CI+ | target-cal point+ | clean point+ | test>=60 rows | test>=60 clean point+ | oracle CI+ | best delta | best clean | best substantial clean | best oracle |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['overlap_regime']} | {row['rows']} | {row['target_calibrated_lower_ci_positive']} | "
            f"{row['target_calibrated_point_positive']} | {row['target_calibrated_clean_point_positive']} | "
            f"{row['substantial_rows_test_ge60']} | {row['substantial_clean_point_positive']} | "
            f"{row['heldout_oracle_lower_ci_positive']} | "
            f"{float(row['best_target_calibrated_delta']):+.3f} ({row['best_target_calibrated_baseline']}, n={row['best_target_calibrated_test_packets']}) | "
            f"{float(row['best_clean_delta']):+.3f} ({row['best_clean_baseline']}, n={row['best_clean_test_packets']}) | "
            f"{float(row['best_substantial_clean_delta']):+.3f} ({row['best_substantial_clean_baseline']}, n={row['best_substantial_clean_test_packets']}) | "
            f"{float(row['best_oracle_delta']):+.3f} ({row['best_oracle_baseline']}, n={row['best_oracle_test_packets']}) |"
        )
    lines += [
        "",
        "## Read",
        "",
        "The expanded duplicated Gemma target panel tests whether v102 failed only because target-style calibration had too few labeled packets. It still finds no lower-CI-positive target-calibrated policies. Many clean rows recover exactly one held-out packet without regressing baseline-correct packets, but the best lower bound is numerically zero. The held-out oracle threshold can clear the rule, so the blocker is target-threshold calibration strength, not total absence of signal.",
        "",
        f"All rows: [{all_path.name}]({all_path.name}). Summary: [{summary_path.name}]({summary_path.name}). Direction summary: [{direction_path.name}]({direction_path.name}).",
    ]
    md_path = OUT / "semantic_target_calibration_v103_aggregate.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(summary_path)
    print(direction_path)
    print(md_path.read_text())


if __name__ == "__main__":
    main()
