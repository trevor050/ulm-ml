#!/usr/bin/env python3
"""Compare verifier smoke targets across balanced and source-unique deployed-mix assets."""

from __future__ import annotations

import argparse
import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_requirements_module():
    spec = importlib.util.spec_from_file_location("deployed_mix_verifier_requirement_table", ROOT / "work" / "deployed_mix_verifier_requirement_table.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


REQ = load_requirements_module()

CONFIGS = [
    ("balanced", "MATH/Llama", OUT / "cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv"),
    ("balanced", "MATH/Gemma", OUT / "cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv"),
    ("unique16", "MATH/Llama", OUT / "cluster_packets_math_llama_n128_deployed_mix_top20_unique16_category_stats.csv"),
    ("unique16", "MATH/Gemma", OUT / "cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_category_stats.csv"),
    ("unique24", "MATH/Llama", OUT / "cluster_packets_math_llama_n128_deployed_mix_top20_unique24_category_stats.csv"),
    ("unique32_attempt", "MATH/Llama", OUT / "cluster_packets_math_llama_n128_deployed_mix_top20_unique32_category_stats.csv"),
]


def rows_for_config(config: str, dataset: str, stats: dict[str, dict[str, float]], baseline_regressions: int) -> list[dict]:
    rows = []
    for depth in [10, 20]:
        cats = REQ.DEPTH_CATEGORIES[depth]
        uniform = REQ.min_uniform_success_count(stats, depth, baseline_regressions)
        greedy = REQ.greedy_min_successes(stats, depth, baseline_regressions)
        tail = REQ.tail_category(depth)
        tail_needed = REQ.tail_only_success_count(stats, depth, baseline_regressions)
        tail_selected = stats[tail]["selected_count"]
        tail_success_dict = {category: 0 for category in cats}
        tail_success_dict[tail] = min(tail_needed, tail_selected)
        rows.append(
            {
                "config": config,
                "dataset": dataset,
                "depth": depth,
                "baseline_regressions": baseline_regressions,
                "baseline_selected_count": stats["baseline_correct"]["selected_count"],
                "baseline_preservation": 1.0 - baseline_regressions / stats["baseline_correct"]["selected_count"],
                "recoverable_rate": REQ.recoverable_rate(stats, depth),
                "uniform_successes_per_category": uniform,
                "recoverable_categories": ",".join(cats),
                "greedy_min_success_pattern": ";".join(f"{category}:{greedy[category]}" for category in cats),
                "tail_category": tail,
                "tail_selected_count": tail_selected,
                "tail_only_successes_needed": tail_needed,
                "tail_only_successes_label": REQ.count_target_label(tail_needed, tail_selected),
                "tail_only_projected_delta": REQ.projected_delta(stats, depth, tail_success_dict, baseline_regressions),
            }
        )
    return rows


def make_rows(baseline_regressions: int) -> list[dict]:
    rows = []
    for config, dataset, path in CONFIGS:
        if not path.exists():
            continue
        rows.extend(rows_for_config(config, dataset, REQ.read_stats(path), baseline_regressions))
    return rows


def fmt(x: float) -> str:
    return f"{x:.3f}"


def write_outputs(rows: list[dict], args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    focus = [row for row in rows if int(row["depth"]) == 20]
    lines = [
        "# Deployed-Mix Requirement Representativeness Sweep",
        "",
        "This audit compares the v71 finite-sample verifier targets across the balanced deployed-mix smoke set and lower-duplication source-unique variants.",
        "",
        f"Baseline regressions assumed: `{args.baseline_regressions}`.",
        "",
        "| config | dataset | baseline preservation | recoverable top20 rate | uniform successes/category | tail-only target | tail selected count |",
        "|---|---|---:|---:|---:|---|---:|",
    ]
    for row in focus:
        lines.append(
            f"| {row['config']} | {row['dataset']} | {fmt(row['baseline_preservation'])} | "
            f"{fmt(row['recoverable_rate'])} | {row['uniform_successes_per_category']} | "
            f"`{row['tail_category']}:{row['tail_only_successes_label']}` | {row['tail_selected_count']} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "The lower-duplication assets do not erase the deployed verifier target, but they do expose the Llama sparsity caveat. Gemma's unique16 set stays well balanced and keeps a low top20-only tail target. The best-effort Llama unique32 attempt still leaves rare categories underfilled, so a failed Llama tail result on the unique set would be ambiguous unless the trace pool is expanded.",
        "",
        "Use the balanced set for a first regression-aware smoke. Use the unique-source set as a representativeness pressure check. Do not overclaim Llama top20-only tail behavior from the sparse unique set alone.",
        "",
        f"CSV: [{csv_path.name}]({csv_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(md_path.read_text())


def run(args: argparse.Namespace) -> None:
    write_outputs(make_rows(args.baseline_regressions), args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="deployed_mix_requirement_representativeness_sweep")
    parser.add_argument("--baseline-regressions", type=int, default=1)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
