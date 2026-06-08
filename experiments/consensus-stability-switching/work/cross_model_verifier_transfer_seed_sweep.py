#!/usr/bin/env python3
"""Seed sweep for cross-model cheap verifier transfer."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_transfer_module():
    spec = importlib.util.spec_from_file_location("cross_model_verifier_transfer", ROOT / "work" / "cross_model_verifier_transfer.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


XFER = load_transfer_module()


def mean_std(vals: list[float]) -> tuple[float, float]:
    if not vals:
        return 0.0, 0.0
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    return mean, math.sqrt(var)


def rows_for_seed(args: argparse.Namespace, seed: int) -> list[dict]:
    run_args = argparse.Namespace(**vars(args))
    run_args.seed = seed
    datasets = {}
    for spec in run_args.dataset:
        label, path = spec.split("=", 1)
        datasets[label] = XFER.MB.load_data(Path(path))

    trained = XFER.train_verifiers(datasets, run_args)
    target_caches = XFER.prepare_target_caches(datasets, run_args)
    rows = []
    for train_label, (verifier, verifier_info) in trained.items():
        for target_label, target_cache in target_caches.items():
            rows.append(XFER.evaluate_transfer(train_label, verifier, verifier_info, target_label, target_cache, run_args))
    return XFER.annotate_gaps(rows)


def summarize(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["train_model"], row["target_model"], row["transfer"])].append(row)

    summary = []
    for (train, target, transfer), group in sorted(groups.items()):
        cluster_mean, cluster_std = mean_std([float(r["cluster_sum"]) for r in group])
        gap_mean, gap_std = mean_std([float(r["cluster_sum_gap_vs_within"]) for r in group])
        auc_gap_mean, auc_gap_std = mean_std([float(r["candidate_auc_gap_vs_within"]) for r in group])
        top20_gap_mean, top20_gap_std = mean_std([float(r["oracle_top20_gap_vs_within"]) for r in group])
        summary.append(
            {
                "train_model": train,
                "target_model": target,
                "transfer": transfer,
                "seeds": len(group),
                "cluster_sum_mean": cluster_mean,
                "cluster_sum_std": cluster_std,
                "cluster_gap_mean": gap_mean,
                "cluster_gap_std": gap_std,
                "auc_gap_mean": auc_gap_mean,
                "auc_gap_std": auc_gap_std,
                "top20_gap_mean": top20_gap_mean,
                "top20_gap_std": top20_gap_std,
            }
        )
    return summary


def write_outputs(rows: list[dict], summary: list[dict], args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    row_csv = OUT / f"{args.output_prefix}.csv"
    fields = list(rows[0].keys())
    with row_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary_csv = OUT / f"{args.output_prefix}_summary.csv"
    summary_fields = list(summary[0].keys())
    with summary_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summary)

    lines = [
        "# Cross-Model Verifier Transfer Seed Sweep",
        "",
        "Repeat the v52 cheap-scorer transfer test across deterministic split/sampling seeds.",
        "",
        f"Config: seeds `{','.join(map(str, args.seeds))}`, N `{args.n}`, trials/problem `{args.trials_per_problem}`, train problems `{args.verifier_train_problems}`, samples/train-problem `{args.verifier_samples_per_problem}`, holdout gap `{args.audit_holdout_gap}`.",
        "",
        "| train | target | transfer | seeds | cluster mean | cluster sd | gap mean | gap sd | AUC gap mean | top20 gap mean |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['train_model']} | {row['target_model']} | {row['transfer']} | {row['seeds']} | "
            f"{row['cluster_sum_mean']:.3f} | {row['cluster_sum_std']:.3f} | "
            f"{row['cluster_gap_mean']:+.3f} | {row['cluster_gap_std']:.3f} | "
            f"{row['auc_gap_mean']:+.3f} | {row['top20_gap_mean']:+.3f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "If the cross rows keep near-zero or positive `cluster_gap_mean`, the v52 transfer result is not just one lucky split. This remains a cheap text-feature scorer test, not an external LLM verifier benchmark.",
        "",
        f"Rows: [{row_csv.name}]({row_csv.name}). Summary: [{summary_csv.name}]({summary_csv.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(summary_csv)
    print(md_path.read_text())


def run(args: argparse.Namespace) -> None:
    rows = []
    for seed in args.seeds:
        print(f"=== seed {seed} ===", flush=True)
        rows.extend(rows_for_seed(args, seed))
    summary = summarize(rows)
    write_outputs(rows, summary, args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", nargs="+", required=True, help="label=path")
    parser.add_argument("--seeds", type=int, nargs="+", default=[60601, 60602, 60603])
    parser.add_argument("--n", type=int, default=128)
    parser.add_argument("--trials-per-problem", type=int, default=12)
    parser.add_argument("--verifier-train-problems", type=int, default=20)
    parser.add_argument("--audit-holdout-gap", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=120)
    parser.add_argument("--max-target-problems", type=int, default=0)
    parser.add_argument("--output-prefix", default="cross_model_verifier_transfer_seed_sweep")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
