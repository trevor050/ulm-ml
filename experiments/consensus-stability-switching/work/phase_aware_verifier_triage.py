#!/usr/bin/env python3
"""Turn the phase diagram into verifier-spend triage rules."""

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


def break_even_success(top20_gain: float, false_regress: float) -> float:
    """Verifier success needed when all rows are inspected and failures may regress."""
    if top20_gain <= 1e-12:
        return float("inf")
    return false_regress * (1.0 - top20_gain) / top20_gain


def projected_delta(top20_gain: float, verifier_success: float, false_regress: float) -> float:
    return verifier_success * top20_gain - false_regress * (1.0 - top20_gain)


def action_label(row: dict, verifier_success: float, false_regress: float) -> str:
    regime = row["majority_regime"]
    any_correct = f(row, "any_correct_mean")
    cluster_sum = f(row, "cluster_sum_mean")
    top20_gain = f(row, "top20_gain_mean")
    closed = f(row, "top20_headroom_closed_mean")
    delta = projected_delta(top20_gain, verifier_success, false_regress)

    if regime == "coverage-limited" and any_correct < 0.40:
        return "defer/generate-coverage"
    if regime == "shallow/surfaced" and cluster_sum >= 0.80 and top20_gain < 0.16:
        return "defer/mostly-surfaced"
    if regime == "depth-limited" and top20_gain >= 0.30 and closed >= 0.80 and delta >= 0.15:
        return "spend/depth-20"
    if regime == "depth-limited" and delta > 0.05:
        return "spend/selective"
    if regime == "mixed" and delta > 0.05:
        return "transition/audit"
    return "do-not-prioritize"


def triage_rows(rows: list[dict], verifier_success: float, false_regress: float) -> list[dict]:
    out = []
    for row in rows:
        top20_gain = f(row, "top20_gain_mean")
        delta = projected_delta(top20_gain, verifier_success, false_regress)
        cluster_sum = f(row, "cluster_sum_mean")
        any_correct = f(row, "any_correct_mean")
        out.append(
            {
                "dataset": row["dataset"],
                "n": int(float(row["n"])),
                "majority_regime": row["majority_regime"],
                "regime_votes": row["regime_votes"],
                "cluster_sum": cluster_sum,
                "any_correct": any_correct,
                "headroom": f(row, "headroom_mean"),
                "top20": f(row, "top20_mean"),
                "top20_gain": top20_gain,
                "top20_headroom_closed": f(row, "top20_headroom_closed_mean"),
                "projected_delta": delta,
                "projected_acc": cluster_sum + delta,
                "break_even_success_2pct_regress": break_even_success(top20_gain, 0.02),
                "break_even_success_5pct_regress": break_even_success(top20_gain, 0.05),
                "action": action_label(row, verifier_success, false_regress),
            }
        )
    return out


def best_depth_targets(rows: list[dict]) -> list[dict]:
    out = []
    for dataset in sorted({row["dataset"] for row in rows}):
        ds = sorted([row for row in rows if row["dataset"] == dataset], key=lambda r: int(r["n"]))
        best_gain = max(ds, key=lambda r: float(r["top20_gain"]))
        first_spend = next((row for row in ds if row["action"].startswith("spend/")), None)
        final = ds[-1]
        out.append(
            {
                "dataset": dataset,
                "first_spend_n": first_spend["n"] if first_spend else "",
                "first_spend_action": first_spend["action"] if first_spend else "",
                "max_gain_n": best_gain["n"],
                "max_gain": best_gain["top20_gain"],
                "max_gain_regime": best_gain["majority_regime"],
                "final_action": final["action"],
                "final_projected_delta": final["projected_delta"],
                "final_projected_acc": final["projected_acc"],
            }
        )
    return out


def fmt(x: float) -> str:
    if x == float("inf"):
        return "inf"
    return f"{x:.3f}"


def write_outputs(rows: list[dict], args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    targets = best_depth_targets(rows)
    targets_path = OUT / f"{args.output_prefix}_targets.csv"
    with targets_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(targets[0].keys()))
        writer.writeheader()
        writer.writerows(targets)

    focus = [row for row in rows if int(row["n"]) in {8, 32, 128}]
    lines = [
        "# Phase-Aware Verifier Triage",
        "",
        "This table turns the v62 sample-count phase diagram into spend/no-spend guidance for a hypothetical top-20 answer-cluster verifier.",
        "",
        f"Assumption for projected deltas: verifier success `{args.verifier_success:.2f}` on top-20 recoverable misses, false-regression `{args.false_regress:.2f}` on false/unhelpful invocations. Break-even columns report required success under 2% and 5% false-regression.",
        "",
        "| dataset | N | phase | action | cluster_sum | oracle | top20 gain | top20 closes | proj delta | break-even success 2%/5% |",
        "|---|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in focus:
        lines.append(
            f"| {row['dataset']} | {row['n']} | {row['majority_regime']} | {row['action']} | "
            f"{fmt(row['cluster_sum'])} | {fmt(row['any_correct'])} | {fmt(row['top20_gain'])} | "
            f"{fmt(row['top20_headroom_closed'])} | {fmt(row['projected_delta'])} | "
            f"{fmt(row['break_even_success_2pct_regress'])}/{fmt(row['break_even_success_5pct_regress'])} |"
        )

    lines += [
        "",
        "## Dataset Targets",
        "",
        "| dataset | first spend N | max-gain point | final N=128 read |",
        "|---|---|---|---|",
    ]
    for row in targets:
        first = "none" if row["first_spend_n"] == "" else f"N={row['first_spend_n']} {row['first_spend_action']}"
        lines.append(
            f"| {row['dataset']} | {first} | N={row['max_gain_n']} {row['max_gain_regime']} gain `{fmt(row['max_gain'])}` | "
            f"{row['final_action']}, projected delta `{fmt(row['final_projected_delta'])}`, projected acc `{fmt(row['final_projected_acc'])}` |"
        )

    lines += [
        "",
        "## Read",
        "",
        "The phase map now has an operational consequence. MATH/Llama and MATH/Gemma become the clean verifier-spend targets once they enter the depth-limited phase: top-20 closes most of the headroom and the required recovery success under realistic false-regression is tiny. GSM8K/Llama is already mostly surfaced, so verification is not the first place to spend effort despite positive residual gain. MATH/Pythia has buried correct clusters, but remains coverage-limited: top-20 verification can recover some misses, yet the final accuracy stays low because most problems never generated a correct answer in the sampled set.",
        "",
        "This is not a measured semantic-verifier result. It is the pre-verifier decision layer: when an endpoint is available, the measured run should be concentrated on depth-limited MATH first and used on surfaced/coverage-limited regimes as controls.",
        "",
        f"CSV: [{csv_path.name}]({csv_path.name}). Targets CSV: [{targets_path.name}]({targets_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(targets_path)
    print(md_path.read_text())


def run(args: argparse.Namespace) -> None:
    rows = triage_rows(read_csv(Path(args.phase_csv)), args.verifier_success, args.false_regress)
    write_outputs(rows, args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase-csv", default=str(OUT / "cross_trace_phase_seed_sweep.csv"))
    parser.add_argument("--output-prefix", default="phase_aware_verifier_triage")
    parser.add_argument("--verifier-success", type=float, default=0.8)
    parser.add_argument("--false-regress", type=float, default=0.02)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
