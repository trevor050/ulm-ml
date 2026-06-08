#!/usr/bin/env python3
"""Project adaptive-depth accuracy against verifier-token budget."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


PROMPT_FILES = {
    ("MATH/Llama", 5, "compact"): OUT / "cluster_verifier_prompts_math_llama_n128_top5_compact.jsonl",
    ("MATH/Llama", 10, "compact"): OUT / "cluster_verifier_prompts_math_llama_n128_top10_strict_compact.jsonl",
    ("MATH/Llama", 20, "compact"): OUT / "cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.jsonl",
    ("MATH/Llama", 5, "full"): OUT / "cluster_verifier_prompts_math_llama_n128_full.jsonl",
    ("MATH/Llama", 10, "full"): OUT / "cluster_verifier_prompts_math_llama_n128_top10_strict.jsonl",
    ("MATH/Llama", 20, "full"): OUT / "cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse.jsonl",
    ("MATH/Gemma", 5, "compact"): OUT / "cluster_verifier_prompts_math_gemma2b_n128_top5_compact.jsonl",
    ("MATH/Gemma", 10, "compact"): OUT / "cluster_verifier_prompts_math_gemma2b_n128_top10_strict_compact.jsonl",
    ("MATH/Gemma", 20, "compact"): OUT / "cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse_compact.jsonl",
    ("MATH/Gemma", 5, "full"): OUT / "cluster_verifier_prompts_math_gemma2b_n128_full.jsonl",
    ("MATH/Gemma", 10, "full"): OUT / "cluster_verifier_prompts_math_gemma2b_n128_top10_strict.jsonl",
    ("MATH/Gemma", 20, "full"): OUT / "cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse.jsonl",
}


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def prompt_stats(path: Path) -> dict:
    lengths = []
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            content = next(message["content"] for message in row["messages"] if message["role"] == "user")
            lengths.append(len(content))
    lengths.sort()
    p90 = lengths[max(0, math.ceil(0.9 * len(lengths)) - 1)]
    avg = sum(lengths) / len(lengths)
    return {
        "count": len(lengths),
        "avg_chars": avg,
        "p90_chars": p90,
        "max_chars": lengths[-1],
        "est_avg_tokens": avg / 4,
    }


def attach_cost(row: dict, stats: dict) -> dict:
    invoke_rate = float(row["invoke_rate"])
    delta = float(row["projected_delta"])
    tokens_per_problem = invoke_rate * float(stats["est_avg_tokens"])
    return {
        "est_tokens_per_problem": tokens_per_problem,
        "tokens_per_accuracy_point": tokens_per_problem / delta if delta > 0 else float("inf"),
        "projected_acc": float(row["projected_acc"]),
        "projected_delta": delta,
    }


def pareto_frontier(rows: list[dict]) -> list[dict]:
    best_acc = -float("inf")
    frontier = []
    for row in sorted(rows, key=lambda r: (float(r["est_tokens_per_problem"]), -float(r["projected_acc"]))):
        acc = float(row["projected_acc"])
        if acc > best_acc + 1e-12:
            frontier.append(row)
            best_acc = acc
    return frontier


def build_rows(frontier_csv: Path, scenario: str, policy: str) -> list[dict]:
    stats_by_key = {key: prompt_stats(path) for key, path in PROMPT_FILES.items() if key[2] == policy}
    out_rows = []
    for row in read_csv(frontier_csv):
        depth = int(float(row["depth"]))
        dataset = row["dataset"]
        if row["scenario"] != scenario:
            continue
        if depth not in {5, 10, 20}:
            continue
        stats = stats_by_key[(dataset, depth, policy)]
        cost = attach_cost(row, stats)
        out_rows.append(
            {
                "dataset": dataset,
                "policy": policy,
                "depth": depth,
                "invoke_rate": float(row["invoke_rate"]),
                "cluster_sum": float(row["cluster_sum"]),
                "avg_prompt_tokens": stats["est_avg_tokens"],
                "p90_prompt_chars": stats["p90_chars"],
                **cost,
            }
        )
    return out_rows


def run(args: argparse.Namespace) -> None:
    rows = []
    for policy in args.policies.split(","):
        rows.extend(build_rows(Path(args.frontier_csv), args.scenario, policy.strip()))

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    fieldnames = [
        "dataset",
        "policy",
        "depth",
        "invoke_rate",
        "cluster_sum",
        "projected_acc",
        "projected_delta",
        "avg_prompt_tokens",
        "est_tokens_per_problem",
        "tokens_per_accuracy_point",
        "p90_prompt_chars",
    ]
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    by_dataset_policy = defaultdict(list)
    for row in rows:
        by_dataset_policy[(row["dataset"], row["policy"])].append(row)

    lines = [
        "# Iso-Budget Adaptive-Depth Frontier",
        "",
        f"Scenario: `{args.scenario}`. Token estimate: prompt characters / 4. Policies: `{args.policies}`.",
        "",
        "This report asks whether adaptive depth still looks useful when the x-axis is estimated verifier tokens per original problem rather than invocation rate alone. It uses compact prompt assets for depths 5/10/20 and the matching full prompt assets as a cost comparison.",
        "",
        "## Pareto Frontier",
        "",
        "| dataset | policy | depth | invoke | projected acc | delta | tokens/problem | tokens per +1.0 acc |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key in sorted(by_dataset_policy):
        for row in pareto_frontier(by_dataset_policy[key]):
            lines.append(
                f"| {row['dataset']} | {row['policy']} | {row['depth']} | {row['invoke_rate']:.2f} | "
                f"{row['projected_acc']:.3f} | {row['projected_delta']:+.3f} | "
                f"{row['est_tokens_per_problem']:.0f} | {row['tokens_per_accuracy_point']:.0f} |"
            )

    lines += [
        "",
        "## Best Compact Rows By Dataset",
        "",
        "| dataset | best low-budget row | best accuracy row |",
        "|---|---|---|",
    ]
    for dataset in sorted({row["dataset"] for row in rows}):
        compact = [row for row in rows if row["dataset"] == dataset and row["policy"] == "compact"]
        efficient = min(compact, key=lambda r: r["tokens_per_accuracy_point"])
        accurate = max(compact, key=lambda r: r["projected_acc"])
        lines.append(
            f"| {dataset} | depth {efficient['depth']}, invoke {efficient['invoke_rate']:.2f}: "
            f"`{efficient['projected_acc']:.3f}` at `{efficient['est_tokens_per_problem']:.0f}` tok/problem | "
            f"depth {accurate['depth']}, invoke {accurate['invoke_rate']:.2f}: "
            f"`{accurate['projected_acc']:.3f}` at `{accurate['est_tokens_per_problem']:.0f}` tok/problem |"
        )

    lines += [
        "",
        "## Read",
        "",
        "The cost-aware version of the method should be judged as a frontier, not a single operating point. If a verifier can use compact prompts, top-20 inspection is no longer automatically disqualified by prompt length; however, higher invoke rates still have to buy enough deployed accuracy to justify their average token budget.",
        "",
        "Caveat: these are projected verifier-success rows from `adaptive_depth_frontier.csv`, not measured external verifier accuracies. The prompt costs are measured from actual prompt assets.",
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
    parser.add_argument("--frontier-csv", default=str(OUT / "adaptive_depth_frontier.csv"))
    parser.add_argument("--scenario", default="external_80_2pct_false_regress")
    parser.add_argument("--policies", default="compact,full")
    parser.add_argument("--output-prefix", default="iso_budget_depth_frontier")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
