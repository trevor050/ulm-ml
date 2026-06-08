#!/usr/bin/env python3
"""Summarize targeted rich pairwise-router probe scores across models."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


DEFAULT_SCORES = {
    "qwen14b": OUT / "qwen14b_pairwise_router_rich_probe_v130_score.csv",
    "mathstral": OUT / "mathstral_pairwise_router_rich_probe_v130_score.csv",
    "gemma4": OUT / "gemma4_pairwise_router_rich_probe_v130_score.csv",
}


def load_manifest(path: Path) -> dict[str, dict]:
    with path.open() as f:
        return {row["packet_id"]: row for row in csv.DictReader(f)}


def load_score(path: Path) -> list[dict]:
    with path.open() as f:
        return list(csv.DictReader(f))


def accepted(choice: str) -> bool:
    return choice in {"B", "BOTH"}


def metric(rows: list[dict]) -> dict:
    n = len(rows)
    exact = sum(row["exact_correct"] == "True" for row in rows)
    accepts = sum(accepted(row["pred_choice"]) for row in rows)
    recoveries = sum(accepted(row["pred_choice"]) and row["baseline_correct"] == "False" and row["policy_correct"] == "True" for row in rows)
    regressions = sum(accepted(row["pred_choice"]) and row["baseline_correct"] == "True" and row["policy_correct"] == "False" for row in rows)
    choices = Counter(row["pred_choice"] for row in rows)
    return {
        "rows": n,
        "choice_accuracy": exact / max(1, n),
        "accepts": accepts,
        "recoveries": recoveries,
        "regressions": regressions,
        "pred_A": choices["A"],
        "pred_B": choices["B"],
        "pred_BOTH": choices["BOTH"],
        "pred_NEITHER": choices["NEITHER"],
        "pred_INVALID": choices["INVALID"],
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=OUT / "pairwise_router_rich_probe_v130_manifest.csv")
    parser.add_argument("--output-prefix", default="pairwise_router_rich_probe_v130_summary")
    parser.add_argument("--score", action="append", default=[], help="model=path to score CSV; may be repeated")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    score_paths = dict(DEFAULT_SCORES)
    for spec in args.score:
        if "=" not in spec:
            raise ValueError(f"score spec must be model=path, got {spec!r}")
        model, path = spec.split("=", 1)
        score_paths[model] = Path(path)

    variant_rows = []
    category_rows = []
    packet_rows = []
    for model, path in sorted(score_paths.items()):
        scores = load_score(path)
        by_variant: dict[str, list[dict]] = defaultdict(list)
        by_category: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for row in scores:
            meta = manifest[row["packet_id"]]
            row = {**row, **{f"manifest_{k}": v for k, v in meta.items()}}
            variant = meta["prompt_variant"]
            category = row["category"]
            by_variant[variant].append(row)
            by_category[(variant, category)].append(row)
            packet_rows.append(
                {
                    "model": model,
                    "prompt_variant": variant,
                    "source_packet_id": meta["source_packet_id"],
                    "category": category,
                    "expected_choice": row["expected_choice"],
                    "pred_choice": row["pred_choice"],
                    "confidence": row["confidence"],
                    "exact_correct": row["exact_correct"],
                    "accepted_candidate": accepted(row["pred_choice"]),
                }
            )
        for variant, rows in sorted(by_variant.items()):
            variant_rows.append({"model": model, "prompt_variant": variant, **metric(rows)})
        for (variant, category), rows in sorted(by_category.items()):
            category_rows.append({"model": model, "prompt_variant": variant, "category": category, **metric(rows)})

    out = OUT / args.output_prefix
    write_csv(out.with_suffix(".csv"), variant_rows)
    write_csv(OUT / f"{args.output_prefix}_categories.csv", category_rows)
    write_csv(OUT / f"{args.output_prefix}_details.csv", packet_rows)

    md = out.with_suffix(".md")
    lines = [
        "# Pairwise Rich Probe Summary",
        "",
        f"Manifest: `{args.manifest.name}`.",
        "",
        "## By Prompt Variant",
        "",
        "| model | variant | rows | choice acc | accepts | rec/reg | A | B | BOTH | NEITHER | invalid |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in variant_rows:
        lines.append(
            f"| {row['model']} | {row['prompt_variant']} | {row['rows']} | {row['choice_accuracy']:.3f} | "
            f"{row['accepts']} | {row['recoveries']}/{row['regressions']} | {row['pred_A']} | {row['pred_B']} | "
            f"{row['pred_BOTH']} | {row['pred_NEITHER']} | {row['pred_INVALID']} |"
        )
    lines.extend(
        [
            "",
            "## By Variant And Category",
            "",
            "| model | variant | category | rows | choice acc | accepts | rec/reg | A | B | BOTH | NEITHER | invalid |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in category_rows:
        lines.append(
            f"| {row['model']} | {row['prompt_variant']} | {row['category']} | {row['rows']} | {row['choice_accuracy']:.3f} | "
            f"{row['accepts']} | {row['recoveries']}/{row['regressions']} | {row['pred_A']} | {row['pred_B']} | "
            f"{row['pred_BOTH']} | {row['pred_NEITHER']} | {row['pred_INVALID']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "This is a targeted stress panel, not a natural-rate benchmark. It is designed to test whether richer answer-only pairwise prompts repair known qwen/union regressions while preserving matched recoveries and safe fallback behavior.",
            "",
            f"Variant CSV: [{args.output_prefix}.csv]({args.output_prefix}.csv). Category CSV: [{args.output_prefix}_categories.csv]({args.output_prefix}_categories.csv). Details: [{args.output_prefix}_details.csv]({args.output_prefix}_details.csv).",
        ]
    )
    md.write_text("\n".join(lines))
    print(md)
    print(md.read_text())


if __name__ == "__main__":
    main()
