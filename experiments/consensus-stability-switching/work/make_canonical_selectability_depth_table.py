#!/usr/bin/env python3
"""Generate the canonical high-N selectability/depth table."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


DATASETS = {
    "MATH/Llama": {
        "selectability": "cluster_selectability_math_llama_parser_v2.csv",
        "depth": "deep_topk_math_llama_n128.csv",
    },
    "MATH/Gemma": {
        "selectability": "cluster_selectability_math_gemma2b_parser_v2.csv",
        "depth": "deep_topk_math_gemma2b_n128.csv",
    },
}


def load_row(path: Path, slice_name: str) -> dict[str, str]:
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["slice"] == slice_name:
                return row
    raise ValueError(f"missing slice {slice_name} in {path}")


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def fmt(x: float) -> str:
    return f"{x:.3f}"


def fmt_int(x: str | float) -> str:
    return str(int(float(x)))


def canonical_rows() -> list[dict]:
    rows = []
    for dataset, paths in DATASETS.items():
        selectability = load_row(OUT / paths["selectability"], "N=128")
        depth = load_row(OUT / paths["depth"], "N=128")
        rows.append(
            {
                "dataset": dataset,
                "trials": fmt_int(depth["trials"]),
                "selector": f(depth, "cluster_sum"),
                "oracle": f(depth, "any_correct"),
                "headroom": f(depth, "cluster_sum_headroom"),
                "top2": f(depth, "top2_oracle"),
                "top3": f(depth, "top3_oracle"),
                "top5": f(depth, "top5_oracle"),
                "top10": f(depth, "top10_oracle"),
                "top20": f(depth, "top20_oracle"),
                "top50": f(depth, "top50_oracle"),
                "avg_clusters": f(depth, "avg_clusters"),
                "miss_p50": fmt_int(depth["miss_rank_p50"]),
                "miss_p75": fmt_int(depth["miss_rank_p75"]),
                "miss_p90": fmt_int(depth["miss_rank_p90"]),
                "top2_closed": f(depth, "top2_headroom_closed"),
                "top3_closed": f(depth, "top3_headroom_closed"),
                "top5_closed": f(depth, "top5_headroom_closed"),
                "top10_closed": f(depth, "top10_headroom_closed"),
                "top20_closed": f(depth, "top20_headroom_closed"),
                "top50_closed": f(depth, "top50_headroom_closed"),
                "selectability_selector": f(selectability, "cluster_sum"),
                "selectability_oracle": f(selectability, "any_correct"),
                "selector_delta_vs_selectability": f(depth, "cluster_sum") - f(selectability, "cluster_sum"),
                "oracle_delta_vs_selectability": f(depth, "any_correct") - f(selectability, "any_correct"),
                "selectability_path": paths["selectability"],
                "depth_path": paths["depth"],
            }
        )
    return rows


def write_csv(rows: list[dict], output_prefix: str) -> Path:
    csv_path = OUT / f"{output_prefix}.csv"
    fields = [
        "dataset",
        "trials",
        "selector",
        "oracle",
        "headroom",
        "top2",
        "top3",
        "top5",
        "top10",
        "top20",
        "top50",
        "avg_clusters",
        "miss_p50",
        "miss_p75",
        "miss_p90",
        "top2_closed",
        "top3_closed",
        "top5_closed",
        "top10_closed",
        "top20_closed",
        "top50_closed",
        "selectability_selector",
        "selectability_oracle",
        "selector_delta_vs_selectability",
        "oracle_delta_vs_selectability",
        "selectability_path",
        "depth_path",
    ]
    with csv_path.open("w", newline="") as fobj:
        writer = csv.DictWriter(fobj, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return csv_path


def markdown(rows: list[dict], csv_path: Path) -> str:
    lines = [
        "# Canonical Selectability And Depth Table",
        "",
        "**Date:** June 1, 2026",
        "**Purpose:** one script-generated reviewer-facing citation target for the high-N MATH selectability gap and depth-oracle numbers.",
        "",
        "The older artifacts report several nearby numbers because they answer slightly different questions: multi-N parser-v2 selectability, deep N=128 top-k visibility, and earlier top-k bounds. For the paper draft, use this table unless intentionally discussing parser/trial sensitivity.",
        "",
        "## Source Artifacts",
        "",
    ]
    for dataset, meta in DATASETS.items():
        lines.append(f"- `{dataset}` selectability: `{meta['selectability']}`")
        lines.append(f"- `{dataset}` depth: `{meta['depth']}`")
    lines += [
        "",
        "All canonical rows below use parser-v2 held-out MATH, `N=128`, and top-k windows ranked by `cluster_sum`. The depth rows are the canonical source for top-k/depth claims.",
        "",
        "## Canonical High-N Table",
        "",
        "| dataset | trials | `cluster_sum` | full cluster oracle | headroom | top-5 oracle | top-10 oracle | top-20 oracle | avg clusters | miss rank p50/p75/p90 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {row['trials']} | {fmt(row['selector'])} | {fmt(row['oracle'])} | "
            f"{fmt(row['headroom'])} | {fmt(row['top5'])} | {fmt(row['top10'])} | {fmt(row['top20'])} | "
            f"{row['avg_clusters']:.1f} | {row['miss_p50']} / {row['miss_p75']} / {row['miss_p90']} |"
        )
    lines += [
        "",
        "## Shallow-Reranking Failure",
        "",
        "| dataset | top-2 oracle | top-3 oracle | top-5 oracle | read |",
        "|---|---:|---:|---:|---|",
    ]
    for row in rows:
        read = "top-3 leaves most headroom untouched" if row["dataset"] == "MATH/Llama" else "top-3 is nowhere near enough"
        lines.append(f"| {row['dataset']} | {fmt(row['top2'])} | {fmt(row['top3'])} | {fmt(row['top5'])} | {read} |")
    lines += [
        "",
        "## Headroom Closed By Inspection Depth",
        "",
        "| dataset | top-2 | top-3 | top-5 | top-10 | top-20 | top-50 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {fmt(row['top2_closed'])} | {fmt(row['top3_closed'])} | "
            f"{fmt(row['top5_closed'])} | {fmt(row['top10_closed'])} | {fmt(row['top20_closed'])} | {fmt(row['top50_closed'])} |"
        )
    lines += [
        "",
        "## Provenance Drift Check",
        "",
        "This table intentionally exposes the small difference between the multi-N selectability audit and the deep N=128 depth audit.",
        "",
        "| dataset | selectability `cluster_sum` | depth `cluster_sum` | delta | selectability oracle | depth oracle | delta |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {fmt(row['selectability_selector'])} | {fmt(row['selector'])} | "
            f"{row['selector_delta_vs_selectability']:+.3f} | {fmt(row['selectability_oracle'])} | {fmt(row['oracle'])} | "
            f"{row['oracle_delta_vs_selectability']:+.3f} |"
        )
    lines += [
        "",
        "## How To Quote",
        "",
        "Safe wording:",
        "",
        "> In parser-v2 high-N MATH audits, `cluster_sum` reaches `0.448` on Llama and `0.233` on Gemma, while a full answer-cluster oracle reaches `0.852` and `0.725`. Correct clusters on selector misses are often buried: miss-rank p50/p90 is `6/21` for Llama and `8/33` for Gemma. Top-10/top-20 inspection closes much more headroom than top-2/top-3 reranking.",
        "",
        "Avoid wording:",
        "",
        "> The exact oracle is `0.846`.",
        "",
        "That number comes from the multi-N parser-v2 selectability table for any-correct/oracle cluster. The deep N=128 visibility audit reports `0.852` because it is the direct top-k depth source. The difference is small, but reviewers will notice if the draft pretends all artifacts are one identical run.",
        "",
        f"CSV: [{csv_path.name}]({csv_path.name}).",
    ]
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = canonical_rows()
    csv_path = write_csv(rows, args.output_prefix)
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text(markdown(rows, csv_path))
    print(md_path)
    print(csv_path)
    print(md_path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="canonical_selectability_depth_table")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
