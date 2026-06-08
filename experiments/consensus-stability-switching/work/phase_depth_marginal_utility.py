#!/usr/bin/env python3
"""Analyze marginal top-k cluster-depth utility by phase and sample count."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def f(row: dict, key: str) -> float:
    return float(row[key])


def depth_label(row: dict) -> str:
    regime = row["majority_regime"]
    any_correct = f(row, "any_correct_mean")
    cluster_sum = f(row, "cluster_sum_mean")
    top5_gain = f(row, "top5_mean") - cluster_sum
    top10_gain = f(row, "top10_mean") - cluster_sum
    top20_gain = f(row, "top20_mean") - cluster_sum
    top20_increment = top20_gain - top10_gain
    top10_increment = top10_gain - top5_gain

    if regime == "coverage-limited" and any_correct < 0.40:
        return "coverage-first"
    if regime == "shallow/surfaced" and cluster_sum >= 0.80:
        return "shallow-control"
    if top20_gain >= 0.30 and top20_increment >= 0.04:
        return "deep-top20"
    if top10_gain >= 0.25 and top10_increment >= 0.04:
        return "medium-top10"
    if top5_gain >= 0.15:
        return "shallow-top5"
    return "low-priority"


def marginal_rows(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        cluster_sum = f(row, "cluster_sum_mean")
        top5 = f(row, "top5_mean")
        top10 = f(row, "top10_mean")
        top20 = f(row, "top20_mean")
        headroom = f(row, "headroom_mean")
        top5_gain = top5 - cluster_sum
        top10_gain = top10 - cluster_sum
        top20_gain = top20 - cluster_sum
        out.append(
            {
                "dataset": row["dataset"],
                "n": int(float(row["n"])),
                "majority_regime": row["majority_regime"],
                "cluster_sum": cluster_sum,
                "any_correct": f(row, "any_correct_mean"),
                "headroom": headroom,
                "top5_gain": top5_gain,
                "top10_gain": top10_gain,
                "top20_gain": top20_gain,
                "top5_closes": top5_gain / headroom if headroom > 1e-12 else 0.0,
                "top10_closes": top10_gain / headroom if headroom > 1e-12 else 0.0,
                "top20_closes": top20_gain / headroom if headroom > 1e-12 else 0.0,
                "increment_top5_to_top10": top10 - top5,
                "increment_top10_to_top20": top20 - top10,
                "depth_label": depth_label(row),
            }
        )
    return out


def transition_rows(rows: list[dict]) -> list[dict]:
    out = []
    for dataset in sorted({row["dataset"] for row in rows}):
        ds = sorted([row for row in rows if row["dataset"] == dataset], key=lambda r: int(r["n"]))
        final = ds[-1]
        first_deep = next((row for row in ds if row["depth_label"] == "deep-top20"), None)
        best_increment = max(ds, key=lambda r: float(r["increment_top10_to_top20"]))
        out.append(
            {
                "dataset": dataset,
                "label_path": " -> ".join(f"N={row['n']}:{row['depth_label']}" for row in ds),
                "first_deep_n": first_deep["n"] if first_deep else "",
                "final_label": final["depth_label"],
                "final_top5_gain": final["top5_gain"],
                "final_top10_gain": final["top10_gain"],
                "final_top20_gain": final["top20_gain"],
                "final_top20_increment": final["increment_top10_to_top20"],
                "max_top20_increment_n": best_increment["n"],
                "max_top20_increment": best_increment["increment_top10_to_top20"],
            }
        )
    return out


def fmt(x: float) -> str:
    return f"{x:.3f}"


def write_outputs(rows: list[dict], args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    trans = transition_rows(rows)
    trans_path = OUT / f"{args.output_prefix}_transitions.csv"
    with trans_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(trans[0].keys()))
        writer.writeheader()
        writer.writerows(trans)

    focus = [row for row in rows if int(row["n"]) in {32, 128}]
    lines = [
        "# Phase Depth Marginal Utility",
        "",
        "This audit asks whether depth-limited traces really need deep cluster inspection or whether top-5/top-10 would capture the same selectability headroom.",
        "",
        "| dataset | N | phase | depth label | top5 gain | top10 gain | top20 gain | top5/top10/top20 closes | top10->top20 increment |",
        "|---|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in focus:
        lines.append(
            f"| {row['dataset']} | {row['n']} | {row['majority_regime']} | {row['depth_label']} | "
            f"{fmt(row['top5_gain'])} | {fmt(row['top10_gain'])} | {fmt(row['top20_gain'])} | "
            f"{fmt(row['top5_closes'])}/{fmt(row['top10_closes'])}/{fmt(row['top20_closes'])} | "
            f"{fmt(row['increment_top10_to_top20'])} |"
        )
    lines += [
        "",
        "## Depth Paths",
        "",
        "| dataset | depth-label path | first deep N | final N=128 marginal read |",
        "|---|---|---:|---|",
    ]
    for row in trans:
        first = row["first_deep_n"] if row["first_deep_n"] != "" else "none"
        lines.append(
            f"| {row['dataset']} | {row['label_path']} | {first} | "
            f"{row['final_label']}: top5 `{fmt(row['final_top5_gain'])}`, top10 `{fmt(row['final_top10_gain'])}`, "
            f"top20 `{fmt(row['final_top20_gain'])}`, top10->top20 `{fmt(row['final_top20_increment'])}` |"
        )
    lines += [
        "",
        "## Read",
        "",
        "Top-20 is not a universal prescription. GSM8K/Llama is a shallow-control case: verification has residual positive gain but the selector is already strong. MATH/Pythia remains coverage-first: deeper inspection recovers some visible misses, but most sampled sets still lack a correct answer. MATH/Llama and MATH/Gemma are the clean deep-inspection targets: top-5 buys a large first chunk of headroom, top-10 helps, and the top10->top20 increment remains nontrivial at high N.",
        "",
        "This makes the adaptive-depth claim sharper. The method should not always run top-20; it should use phase and marginal-depth diagnostics to decide when deeper semantic inspection is worth paying for.",
        "",
        f"CSV: [{csv_path.name}]({csv_path.name}). Transitions CSV: [{trans_path.name}]({trans_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(trans_path)
    print(md_path.read_text())


def run(args: argparse.Namespace) -> None:
    write_outputs(marginal_rows(read_csv(Path(args.phase_csv))), args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase-csv", default=str(OUT / "cross_trace_phase_seed_sweep.csv"))
    parser.add_argument("--output-prefix", default="phase_depth_marginal_utility")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
