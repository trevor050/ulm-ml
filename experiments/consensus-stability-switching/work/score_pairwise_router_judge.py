#!/usr/bin/env python3
"""Score pairwise router-judge predictions."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


VALID = {"A", "B", "BOTH", "NEITHER"}


def norm_choice(value: object) -> str:
    text = str(value or "").strip().upper()
    if text in VALID:
        return text
    match = re.search(r"\b(A|B|BOTH|NEITHER)\b", text)
    if match:
        return match.group(1)
    return "INVALID"


def load_manifest(path: Path) -> dict[str, dict]:
    with path.open() as f:
        return {row["packet_id"]: row for row in csv.DictReader(f)}


def load_predictions(path: Path) -> dict[str, dict]:
    out = {}
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            out[row["packet_id"]] = row
    return out


def category_correct(expected: str, pred: str) -> bool:
    return pred == expected


def accept_candidate(pred: str, threshold: float, confidence: object) -> bool:
    try:
        conf = float(confidence)
    except (TypeError, ValueError):
        conf = 0.0
    return conf >= threshold and pred in {"B", "BOTH"}


def summarize(rows: list[dict], threshold: float) -> dict:
    total = len(rows)
    exact = sum(row["exact_correct"] for row in rows)
    baseline_correct = sum(row["baseline_correct"] for row in rows)
    gated_correct = 0
    accepts = recoveries = regressions = 0
    for row in rows:
        accept = accept_candidate(row["pred_choice"], threshold, row["confidence"])
        if accept:
            accepts += 1
            correct = row["policy_correct"]
        else:
            correct = row["baseline_correct"]
        gated_correct += int(correct)
        if accept and (not row["baseline_correct"]) and row["policy_correct"]:
            recoveries += 1
        if accept and row["baseline_correct"] and (not row["policy_correct"]):
            regressions += 1
    return {
        "threshold": threshold,
        "rows": total,
        "choice_accuracy": exact / max(1, total),
        "baseline_acc": baseline_correct / max(1, total),
        "gated_acc": gated_correct / max(1, total),
        "gated_delta": (gated_correct - baseline_correct) / max(1, total),
        "accepts": accepts,
        "recoveries": recoveries,
        "regressions": regressions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    parser.add_argument("--thresholds", default="0,0.5,0.7,0.9")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    predictions = load_predictions(args.predictions)
    rows = []
    for packet_id, meta in manifest.items():
        pred = predictions.get(packet_id, {})
        pred_choice = norm_choice(pred.get("answer"))
        row = {
            "packet_id": packet_id,
            "category": meta["category"],
            "expected_choice": meta["expected_choice"],
            "pred_choice": pred_choice,
            "confidence": pred.get("confidence"),
            "exact_correct": category_correct(meta["expected_choice"], pred_choice),
            "baseline_correct": str(meta["baseline_correct"]).lower() == "true",
            "policy_correct": str(meta["policy_correct"]).lower() == "true",
            "raw_answer": pred.get("answer"),
            "model": pred.get("model"),
        }
        rows.append(row)

    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    detail_path = args.output_prefix.with_suffix(".csv")
    with detail_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    by_cat = []
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["category"]].append(row)
    for cat, vals in sorted(groups.items()):
        by_cat.append(
            {
                "category": cat,
                "rows": len(vals),
                "choice_accuracy": sum(row["exact_correct"] for row in vals) / max(1, len(vals)),
                "pred_A": sum(row["pred_choice"] == "A" for row in vals),
                "pred_B": sum(row["pred_choice"] == "B" for row in vals),
                "pred_BOTH": sum(row["pred_choice"] == "BOTH" for row in vals),
                "pred_NEITHER": sum(row["pred_choice"] == "NEITHER" for row in vals),
                "pred_INVALID": sum(row["pred_choice"] == "INVALID" for row in vals),
            }
        )
    cat_path = args.output_prefix.parent / f"{args.output_prefix.name}_categories.csv"
    with cat_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(by_cat[0]))
        writer.writeheader()
        writer.writerows(by_cat)

    thresholds = [float(val) for val in args.thresholds.split(",") if val.strip()]
    thresh_rows = [summarize(rows, threshold) for threshold in thresholds]
    thresh_path = args.output_prefix.parent / f"{args.output_prefix.name}_thresholds.csv"
    with thresh_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(thresh_rows[0]))
        writer.writeheader()
        writer.writerows(thresh_rows)

    md_path = args.output_prefix.with_suffix(".md")
    lines = [
        "# Pairwise Router Judge Score",
        "",
        f"Predictions: `{args.predictions}`.",
        "",
        "## Category Accuracy",
        "",
        "| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in by_cat:
        lines.append(
            f"| {row['category']} | {row['rows']} | {row['choice_accuracy']:.3f} | {row['pred_A']} | {row['pred_B']} | {row['pred_BOTH']} | {row['pred_NEITHER']} | {row['pred_INVALID']} |"
        )
    lines.extend(
        [
            "",
            "## Confidence-Gated Candidate Acceptance",
            "",
            "| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in thresh_rows:
        lines.append(
            f"| {row['threshold']:.2f} | {row['rows']} | {row['choice_accuracy']:.3f} | {row['baseline_acc']:.3f} | {row['gated_acc']:.3f} | {row['gated_delta']:+.3f} | {row['accepts']} | {row['recoveries']} | {row['regressions']} |"
        )
    lines.extend(["", f"Details: `{detail_path}`. Categories: `{cat_path}`. Thresholds: `{thresh_path}`."])
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(md_path.read_text())


if __name__ == "__main__":
    main()
