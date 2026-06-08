#!/usr/bin/env python3
"""Audit deployed-mix packet representativeness and duplication."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_packets(path: str) -> list[dict]:
    with Path(path).open() as f:
        return [json.loads(line) for line in f if line.strip()]


def dataset_name(rows: list[dict], path: str) -> str:
    if rows:
        label = rows[0].get("dataset_label", "")
        if "Llama" in label:
            return "MATH/Llama"
        if "Gemma" in label:
            return "MATH/Gemma"
    name = Path(path).name.lower()
    if "llama" in name:
        return "MATH/Llama"
    if "gemma" in name:
        return "MATH/Gemma"
    return Path(path).stem


def quantile(vals: list[int], q: float) -> int | str:
    if not vals:
        return ""
    vals = sorted(vals)
    idx = min(len(vals) - 1, max(0, round(q * (len(vals) - 1))))
    return vals[idx]


def summary_rows(dataset: str, rows: list[dict]) -> list[dict]:
    out = []
    for category in ["ALL"] + sorted({row["deployment_category"] for row in rows}):
        vals = rows if category == "ALL" else [row for row in rows if row["deployment_category"] == category]
        problem_counts = Counter(row["orig_dset_idx"] for row in vals)
        ranks = [int(row["correct_rank_sum"]) for row in vals if row.get("correct_rank_sum") is not None]
        out.append(
            {
                "dataset": dataset,
                "category": category,
                "packets": len(vals),
                "unique_problems": len(problem_counts),
                "max_packets_per_problem": max(problem_counts.values()) if problem_counts else 0,
                "duplicate_packet_share": (len(vals) - len(problem_counts)) / max(1, len(vals)),
                "unique_baseline_answers": len({row.get("baseline_answer") for row in vals}),
                "rank_p50": quantile(ranks, 0.50),
                "rank_p90": quantile(ranks, 0.90),
            }
        )
    return out


def cross_model_rows(by_dataset: dict[str, list[dict]]) -> list[str]:
    lines = []
    if len(by_dataset) < 2:
        return lines
    names = sorted(by_dataset)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            left_ids = {row["orig_dset_idx"] for row in by_dataset[left]}
            right_ids = {row["orig_dset_idx"] for row in by_dataset[right]}
            overlap = left_ids & right_ids
            lines.append(f"- `{left}` and `{right}` share `{len(overlap)}` source problems out of `{len(left_ids)}` / `{len(right_ids)}` unique problems.")
    return lines


def run(args: argparse.Namespace) -> None:
    by_dataset = {}
    rows = []
    for path in args.packets:
        packets = load_packets(path)
        dataset = dataset_name(packets, path)
        by_dataset[dataset] = packets
        rows.extend(summary_rows(dataset, packets))

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    fields = [
        "dataset",
        "category",
        "packets",
        "unique_problems",
        "max_packets_per_problem",
        "duplicate_packet_share",
        "unique_baseline_answers",
        "rank_p50",
        "rank_p90",
    ]
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Deployed-Mix Representativeness Audit",
        "",
        "Audit of source-problem duplication, category balance, baseline-answer diversity, and correct-rank spread in the deployed-mix packet assets.",
        "",
        "| dataset | category | packets | unique problems | max/problem | duplicate share | unique baseline answers | rank p50 | rank p90 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {row['category']} | {row['packets']} | {row['unique_problems']} | "
            f"{row['max_packets_per_problem']} | {row['duplicate_packet_share']:.3f} | "
            f"{row['unique_baseline_answers']} | {row['rank_p50']} | {row['rank_p90']} |"
        )
    overlap_lines = cross_model_rows(by_dataset)
    if overlap_lines:
        lines += ["", "## Cross-Model Overlap", "", *overlap_lines]
    all_rows = [row for row in rows if row["category"] == "ALL"]
    if all(row["duplicate_packet_share"] == 0 for row in all_rows):
        read = "This packet set is one-packet-per-source within each model. Remaining caveats are category imbalance and cross-model source overlap."
    else:
        read = "The deployed-mix packet set is category-balanced, not source-problem-unique. It should be treated as a regression-aware smoke benchmark unless expanded with stricter one-packet-per-source sampling."
    lines += [
        "",
        "## Read",
        "",
        read,
        "",
        f"CSV: [{csv_path.name}]({csv_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(md_path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packets", nargs="+", required=True)
    parser.add_argument("--output-prefix", default="deployed_mix_representativeness")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
