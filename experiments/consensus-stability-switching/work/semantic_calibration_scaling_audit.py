#!/usr/bin/env python3
"""Calibration-size and composition audit for split-trained semantic scorers."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
RECOVERABLE = {"recoverable_top5", "recoverable_top10_only", "recoverable_top20_only"}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


TCS = load_module("text_cluster_semantic_scorer", ROOT / "work" / "text_cluster_semantic_scorer.py")
SRC = load_module("semantic_risk_controlled_selector", ROOT / "work" / "semantic_risk_controlled_selector.py")
STD = load_module("semantic_threshold_diagnostic", ROOT / "work" / "semantic_threshold_diagnostic.py")
DMPCI = load_module("deployed_mix_policy_ci", ROOT / "work" / "deployed_mix_policy_ci.py")
SDMV = TCS.SDMV


def packet_problem_id(packet: dict) -> str:
    idx = packet.get("orig_dset_idx")
    if idx is None:
        return str(packet.get("packet_id"))
    return str(idx)


def overlap_id(packet: dict, key: str) -> str:
    if key == "problem":
        return packet_problem_id(packet)
    return str(packet.get("packet_id"))


def load_packet_paths(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        rows.extend(TCS.load_packets(path))
    return rows


def dedupe_by_problem(packets: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out = []
    for packet in sorted(packets, key=lambda row: (packet_problem_id(row), str(row.get("packet_id")))):
        key = packet_problem_id(packet)
        if key in seen:
            continue
        seen.add(key)
        out.append(packet)
    return out


def exclude_overlap(packets: list[dict], blocked: set[str], key: str) -> list[dict]:
    return [packet for packet in packets if overlap_id(packet, key) not in blocked]


def split_by_category(packets: list[dict], seed: int, calibration_frac: float) -> tuple[list[dict], list[dict]]:
    by_category: dict[str, list[dict]] = defaultdict(list)
    for packet in packets:
        by_category[str(packet.get("deployment_category") or "unknown")].append(packet)
    rng = random.Random(seed)
    fit: list[dict] = []
    calib: list[dict] = []
    for category in sorted(by_category):
        rows = list(by_category[category])
        rng.shuffle(rows)
        n_calib = max(1, round(len(rows) * calibration_frac)) if len(rows) > 1 else 0
        calib.extend(rows[:n_calib])
        fit.extend(rows[n_calib:])
    return fit, calib


def sample_calib_by_category(calib_packets: list[dict], per_category: str, seed: int) -> list[dict]:
    by_category: dict[str, list[dict]] = defaultdict(list)
    for packet in calib_packets:
        by_category[str(packet.get("deployment_category") or "unknown")].append(packet)
    rng = random.Random(seed)
    out: list[dict] = []
    for category in sorted(by_category):
        rows = list(by_category[category])
        rng.shuffle(rows)
        if per_category == "all":
            out.extend(rows)
        else:
            out.extend(rows[: min(int(per_category), len(rows))])
    return out


def answer_key_for_packets(packets: list[dict]) -> dict[str, dict]:
    return {packet["packet_id"]: TCS.answer_key_for_packet(packet) for packet in packets}


def threshold_counts(predictions: list[dict], packets: list[dict], field: str, threshold: float) -> dict:
    key = answer_key_for_packets(packets)
    transformed = STD.transformed_predictions(predictions, field)
    scored = DMPCI.score_threshold_rows(transformed, key, threshold)
    return STD.category_counts(scored)


def weighted_delta(predictions: list[dict], packets: list[dict], field: str, threshold: float, rates: dict[str, dict[str, float]]) -> dict:
    key = answer_key_for_packets(packets)
    transformed = STD.transformed_predictions(predictions, field)
    scored = DMPCI.score_threshold_rows(transformed, key, threshold)
    point = DMPCI.weighted_policy_metrics(scored, rates)[0]
    counts = STD.category_counts(scored)
    return {**point, **counts}


def bootstrap_decision(
    predictions: list[dict],
    packets: list[dict],
    field: str,
    threshold: float,
    rates: dict[str, dict[str, float]],
    rounds: int,
    seed: int,
) -> dict:
    key = answer_key_for_packets(packets)
    transformed = STD.transformed_predictions(predictions, field)
    scored = DMPCI.score_threshold_rows(transformed, key, threshold)
    ci = DMPCI.bootstrap_ci(scored, rates, threshold, rounds, seed)
    return ci[0] if ci else {"delta_ci_low": "", "delta_ci_high": "", "decision": ""}


def target_oracle_rows(predictions: list[dict], packets: list[dict], fields: list[str], rates: dict[str, dict[str, float]], rounds: int, seed: int) -> dict[str, dict]:
    key = answer_key_for_packets(packets)
    rows = []
    for field in fields:
        rows.extend(STD.threshold_rows(predictions, key, rates, field))
    best = STD.add_best_cis(STD.best_rows(rows), predictions, key, rates, rounds, seed)
    return {row["score_field"]: row for row in best}


def comma_values(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def fmt_float(value: object, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(args: argparse.Namespace) -> None:
    source_packets = load_packet_paths(args.source_packets)
    target_packets = load_packet_paths([args.test_packets])
    if args.dedupe_problems:
        source_packets = dedupe_by_problem(source_packets)
        target_packets = dedupe_by_problem(target_packets)
    raw_source_n = len(source_packets)
    raw_target_n = len(target_packets)
    target_overlap_ids = {overlap_id(packet, args.overlap_key) for packet in target_packets}
    if args.exclude_test_problems_from_source:
        source_packets = exclude_overlap(source_packets, target_overlap_ids, args.overlap_key)
    fit_packets, calib_pool = split_by_category(source_packets, args.seed, args.calibration_frac)
    if not fit_packets or not calib_pool:
        raise ValueError("fit/calibration split is empty")

    cluster_rows = TCS.cluster_rows(fit_packets, args)
    weights, train_info = TCS.train(cluster_rows, args)
    raw_target = [TCS.choose_packet(packet, weights, args) for packet in target_packets]
    raw_calib_all = [TCS.choose_packet(packet, weights, args) for packet in calib_pool]
    rates = SDMV.load_category_rates([str(path) for path in args.category_stats])
    fields = list(args.score_fields)
    target_oracle = target_oracle_rows(raw_target, target_packets, fields, rates, args.bootstrap_rounds, args.seed)

    out_rows: list[dict] = []
    for per_category in comma_values(args.calibration_per_category):
        calib_packets = sample_calib_by_category(calib_pool, per_category, args.seed + 17 * len(out_rows))
        packet_ids = {packet["packet_id"] for packet in calib_packets}
        raw_calib = [row for row in raw_calib_all if row["packet_id"] in packet_ids]
        for field in fields:
            source_args = argparse.Namespace(**vars(args))
            source_args.score_field = field
            threshold_row = SRC.choose_threshold(raw_calib, calib_packets, source_args)
            threshold = float(threshold_row["threshold"])
            target_point = weighted_delta(raw_target, target_packets, field, threshold, rates)
            target_ci = bootstrap_decision(raw_target, target_packets, field, threshold, rates, args.bootstrap_rounds, args.seed + len(out_rows) * 1009)
            source_counts = threshold_counts(raw_calib, calib_packets, field, threshold)
            oracle = target_oracle[field]
            out_rows.append(
                {
                    "setup": args.output_prefix,
                    "feature_mode": args.feature_mode,
                    "seed": args.seed,
                    "score_field": field,
                    "source_paths": ";".join(path.name for path in args.source_packets),
                    "raw_source_packets": raw_source_n,
                    "source_packets_after_filters": len(source_packets),
                    "raw_target_packets": raw_target_n,
                    "target_packets_after_filters": len(target_packets),
                    "fit_packets": len(fit_packets),
                    "calib_pool_packets": len(calib_pool),
                    "calib_per_category": per_category,
                    "calib_packets": len(calib_packets),
                    "source_threshold": threshold,
                    "source_calib_recoverable_correct": source_counts["recoverable_correct"],
                    "source_calib_recoverable_total": source_counts["recoverable_total"],
                    "source_calib_baseline_preserved": source_counts["baseline_preserved"],
                    "source_calib_baseline_total": source_counts["baseline_total"],
                    "source_target_delta": target_point["deployed_delta"],
                    "source_target_ci_low": target_ci.get("delta_ci_low", ""),
                    "source_target_ci_high": target_ci.get("delta_ci_high", ""),
                    "source_target_decision": target_ci.get("decision", ""),
                    "source_target_recoverable_correct": target_point["recoverable_correct"],
                    "source_target_recoverable_total": target_point["recoverable_total"],
                    "source_target_baseline_preserved": target_point["baseline_preserved"],
                    "source_target_baseline_total": target_point["baseline_total"],
                    "source_target_accept_rate": target_point["accept_rate"],
                    "target_oracle_threshold": oracle["threshold"],
                    "threshold_abs_gap": abs(threshold - float(oracle["threshold"])),
                    "target_oracle_delta": oracle["deployed_delta"],
                    "target_oracle_ci_low": oracle["delta_ci_low"],
                    "target_oracle_ci_high": oracle["delta_ci_high"],
                    "target_oracle_decision": oracle["decision"],
                    "target_oracle_recoverable_correct": oracle["recoverable_correct"],
                    "target_oracle_recoverable_total": oracle["recoverable_total"],
                    "target_oracle_baseline_preserved": oracle["baseline_preserved"],
                    "target_oracle_baseline_total": oracle["baseline_total"],
                }
            )

    OUT.mkdir(parents=True, exist_ok=True)
    raw_target_path = OUT / f"{args.output_prefix}_raw_target_predictions.jsonl"
    raw_calib_path = OUT / f"{args.output_prefix}_raw_calib_predictions.jsonl"
    csv_path = OUT / f"{args.output_prefix}.csv"
    write_jsonl(raw_target_path, raw_target)
    write_jsonl(raw_calib_path, raw_calib_all)
    write_csv(csv_path, out_rows)

    best_source = max(out_rows, key=lambda row: (float(row["source_target_delta"]), int(row["source_target_recoverable_correct"]), int(row["source_target_baseline_preserved"])))
    best_oracle = max(out_rows, key=lambda row: float(row["target_oracle_delta"]))
    lines = [
        "# Semantic Calibration Scaling Audit",
        "",
        f"Feature mode: `{args.feature_mode}`. Seed: `{args.seed}`.",
        f"Source packets: `{raw_source_n}` raw, `{len(source_packets)}` after filters. Target packets: `{raw_target_n}` raw, `{len(target_packets)}` after filters.",
        f"Overlap key: `{args.overlap_key}`. Problem dedupe: `{args.dedupe_problems}`.",
        f"Fit/calibration pool: `{len(fit_packets)}` / `{len(calib_pool)}` packets. Fit clusters: `{train_info['clusters']}`.",
        "",
        "## Best Source-Calibrated Row",
        "",
        f"`{best_source['score_field']}` with `{best_source['calib_per_category']}` calibration packets/category: "
        f"delta `{float(best_source['source_target_delta']):+.3f}` "
        f"CI `{fmt_float(best_source['source_target_ci_low'])}..{fmt_float(best_source['source_target_ci_high'])}`, "
        f"recoveries `{best_source['source_target_recoverable_correct']}/{best_source['source_target_recoverable_total']}`, "
        f"baseline `{best_source['source_target_baseline_preserved']}/{best_source['source_target_baseline_total']}`.",
        "",
        "## Best Target-Oracle Row",
        "",
        f"`{best_oracle['score_field']}` target oracle: delta `{float(best_oracle['target_oracle_delta']):+.3f}` "
        f"CI `{fmt_float(best_oracle['target_oracle_ci_low'])}..{fmt_float(best_oracle['target_oracle_ci_high'])}`, "
        f"recoveries `{best_oracle['target_oracle_recoverable_correct']}/{best_oracle['target_oracle_recoverable_total']}`, "
        f"baseline `{best_oracle['target_oracle_baseline_preserved']}/{best_oracle['target_oracle_baseline_total']}`.",
        "",
        "| calib/category | field | source threshold | target oracle threshold | target delta | CI | rec | baseline | oracle delta |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in out_rows:
        lines.append(
            f"| {row['calib_per_category']} | {row['score_field']} | {float(row['source_threshold']):.4f} | "
            f"{float(row['target_oracle_threshold']):.4f} | {float(row['source_target_delta']):+.3f} | "
            f"{fmt_float(row['source_target_ci_low'])}..{fmt_float(row['source_target_ci_high'])} | "
            f"{row['source_target_recoverable_correct']}/{row['source_target_recoverable_total']} | "
            f"{row['source_target_baseline_preserved']}/{row['source_target_baseline_total']} | "
            f"{float(row['target_oracle_delta']):+.3f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "Rows vary only the source calibration subset after a fixed source/target split-trained semantic scorer. A widening source-vs-oracle gap means the blocker is threshold/risk transfer rather than raw cluster ranking.",
        "",
        f"CSV: [{csv_path.name}]({csv_path.name}). Raw target predictions: [{raw_target_path.name}]({raw_target_path.name}). Raw calibration predictions: [{raw_calib_path.name}]({raw_calib_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(raw_target_path)
    print(raw_calib_path)
    print(md_path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-packets", nargs="+", type=Path, required=True)
    parser.add_argument("--test-packets", type=Path, required=True)
    parser.add_argument("--train-label", required=True)
    parser.add_argument("--test-label", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--feature-mode", choices=["numeric", "text", "both"], default="both")
    parser.add_argument("--score-fields", nargs="+", default=["confidence", "semantic_cluster_probability", "semantic_cluster_margin"])
    parser.add_argument("--category-stats", nargs="+", type=Path, required=True)
    parser.add_argument("--calibration-per-category", default="1,2,4,8,all")
    parser.add_argument("--hash-dim", type=int, default=32768)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--lr", type=float, default=0.08)
    parser.add_argument("--l2", type=float, default=1e-5)
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--calibration-frac", type=float, default=0.5)
    parser.add_argument("--max-baseline-regressions", type=int, default=0)
    parser.add_argument("--representatives-per-cluster", type=int, default=1)
    parser.add_argument("--rationale-chars", type=int, default=360)
    parser.add_argument("--include-problem", action="store_true")
    parser.add_argument("--dedupe-problems", action="store_true")
    parser.add_argument("--overlap-key", choices=["packet", "problem"], default="packet")
    parser.add_argument("--exclude-test-problems-from-source", action="store_true")
    parser.add_argument("--bootstrap-rounds", type=int, default=300)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
