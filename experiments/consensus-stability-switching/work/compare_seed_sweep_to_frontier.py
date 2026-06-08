#!/usr/bin/env python3
"""Compare multi-seed detector sweep means to the original v17 frontier."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def read(path: Path) -> list[dict]:
    with path.open() as f:
        return list(csv.DictReader(f))


def f(row: dict, key: str) -> float:
    return float(row[key])


def run(args: argparse.Namespace) -> None:
    original = [
        row
        for row in read(OUT / "detector_verifier_frontier.csv")
        if row["scenario"] == "perfect_visible_no_regress"
    ]
    sweep = read(OUT / "failure_detector_seed_sweep.csv")
    rows = []
    for dataset in ["MATH/Llama", "MATH/Gemma"]:
        for rate in [0.10, 0.20, 0.30]:
            orig = max(
                [r for r in original if r["dataset"] == dataset and abs(f(r, "invoke_rate") - rate) < 0.015],
                key=lambda r: f(r, "perfect_visible_oracle_acc"),
            )
            candidates = [r for r in sweep if r["dataset"] == dataset and abs(f(r, "invoke_rate") - rate) < 0.015]
            best = max(candidates, key=lambda r: f(r, "acc_mean"))
            rows.append(
                {
                    "dataset": dataset,
                    "invoke_rate": rate,
                    "original_acc": f(orig, "perfect_visible_oracle_acc"),
                    "seed_sweep_acc_mean": f(best, "acc_mean"),
                    "seed_sweep_acc_std": f(best, "acc_std"),
                    "delta": f(best, "acc_mean") - f(orig, "perfect_visible_oracle_acc"),
                    "best_variant": best["variant"],
                    "auc_mean": f(best, "auc_mean"),
                }
            )

    csv_path = OUT / f"{args.output_prefix}.csv"
    with csv_path.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Seed Sweep vs Original Frontier",
        "",
        "| dataset | invoke | original acc | seed-sweep mean | std | delta | best variant | AUC mean |",
        "|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {row['invoke_rate']:.2f} | {row['original_acc']:.3f} | {row['seed_sweep_acc_mean']:.3f} | {row['seed_sweep_acc_std']:.3f} | {row['delta']:+.3f} | {row['best_variant']} | {row['auc_mean']:.3f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "The single-seed v18 detector-zoo result overstates the improvement. Averaged over three seeds, Llama keeps a modest positive gain while Gemma is approximately flat or slightly worse against the original frontier.",
        "",
        f"Raw CSV: [{csv_path.name}]({csv_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(md_path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="detector_seed_sweep_vs_frontier")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
