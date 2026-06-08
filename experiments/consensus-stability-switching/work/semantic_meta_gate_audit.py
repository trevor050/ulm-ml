#!/usr/bin/env python3
"""Target-style multifeature semantic accept/fallback gate audit."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
RECOVERABLE = {"recoverable_top5", "recoverable_top10_only", "recoverable_top20_only"}
EPS = 1e-12
DECISION_EPS = 1e-9


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


TCS = load_module("text_cluster_semantic_scorer", ROOT / "work" / "text_cluster_semantic_scorer.py")
SDMV = TCS.SDMV
SLJ = SDMV.SLJ


def load_jsonl(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def split_target_packets(packets: list[dict], per_category: str, seed: int) -> tuple[list[dict], list[dict]]:
    by_category: dict[str, list[dict]] = defaultdict(list)
    for packet in packets:
        by_category[str(packet.get("deployment_category") or "unknown")].append(packet)
    rng = random.Random(seed)
    calib: list[dict] = []
    test: list[dict] = []
    for category in sorted(by_category):
        rows = list(by_category[category])
        rng.shuffle(rows)
        if per_category == "all":
            n_calib = max(1, len(rows) // 2)
        else:
            n_calib = min(int(per_category), max(0, len(rows) - 1))
        calib.extend(rows[:n_calib])
        test.extend(rows[n_calib:])
    return calib, test


def norm_answer(value: object) -> str:
    return SLJ.norm(str(value))


def pred_correct(pred: dict, packet: dict) -> bool:
    answer = norm_answer(pred.get("answer"))
    correct = {norm_answer(x) for x in packet.get("correct_answers_in_visible", [])}
    return bool(correct) and answer in correct


def pred_matches_baseline(pred: dict, packet: dict) -> bool:
    return norm_answer(pred.get("answer")) == norm_answer(packet.get("baseline_answer"))


def feature_vector(pred: dict, packet: dict) -> list[float]:
    confidence = float(pred.get("confidence") or 0.0)
    prob = float(pred.get("semantic_cluster_probability") or 0.0)
    margin = float(pred.get("semantic_cluster_margin") or 0.0)
    rank = float(pred.get("selected_rank_by_sum") or 999.0)
    support = float(pred.get("selected_support") or 0.0)
    return [
        1.0,
        confidence,
        math.log(max(confidence, EPS)),
        prob,
        math.log(max(prob, EPS)),
        margin,
        math.log(max(abs(margin), EPS)),
        1.0 / max(rank, 1.0),
        1.0 / math.log2(rank + 1.0),
        math.log1p(support),
        support,
        1.0 if pred_matches_baseline(pred, packet) else 0.0,
        1.0 if rank <= 3 else 0.0,
        1.0 if rank <= 5 else 0.0,
        1.0 if rank <= 10 else 0.0,
        confidence * (1.0 / max(rank, 1.0)),
        prob * math.log1p(support),
        margin * math.log1p(support),
    ]


def build_examples(predictions: list[dict], packets: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    pred_by_id = {row["packet_id"]: row for row in predictions}
    rows = []
    features = []
    labels = []
    weights = []
    for packet in packets:
        pred = pred_by_id.get(packet["packet_id"])
        if pred is None:
            continue
        accept_correct = pred_correct(pred, packet)
        fallback_correct = bool(packet.get("baseline_is_correct"))
        advantage = int(accept_correct) - int(fallback_correct)
        category = str(packet.get("deployment_category") or "unknown")
        # Neutral rows provide no utility label for the gate. Keep the learned gate focused on
        # recovery-vs-regression boundaries rather than modeling no-op regions.
        if advantage == 0:
            continue
        rows.append({"packet": packet, "prediction": pred, "advantage": advantage, "category": category})
        features.append(feature_vector(pred, packet))
        labels.append(1.0 if advantage > 0 else 0.0)
        weights.append(2.0 if advantage < 0 else 1.0)
    if not rows:
        return np.zeros((0, 18)), np.zeros(0), np.zeros(0), []
    return np.asarray(features, dtype=np.float64), np.asarray(labels, dtype=np.float64), np.asarray(weights, dtype=np.float64), rows


def train_gate(features: np.ndarray, labels: np.ndarray, weights: np.ndarray, args: argparse.Namespace) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    if len(labels) < 2 or len(set(float(x) for x in labels)) < 2:
        dim = features.shape[1] if features.ndim == 2 else 18
        return np.zeros(dim), np.zeros(dim), np.ones(dim), {"status": "degenerate", "examples": len(labels), "positives": int(labels.sum())}
    mean = features.mean(axis=0)
    std = features.std(axis=0)
    std[std < 1e-6] = 1.0
    x = (features - mean) / std
    w = np.zeros(x.shape[1], dtype=np.float64)
    rng = random.Random(args.seed)
    order = list(range(len(labels)))
    for epoch in range(args.epochs):
        rng.shuffle(order)
        lr = args.lr / math.sqrt(epoch + 1)
        for idx in order:
            z = float(np.dot(w, x[idx]))
            p = 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, z))))
            grad = weights[idx] * (p - labels[idx])
            w -= lr * (grad * x[idx] + args.l2 * w)
    return w, mean, std, {"status": "fit", "examples": len(labels), "positives": int(labels.sum())}


def gate_scores(predictions: list[dict], packets: list[dict], weights: np.ndarray, mean: np.ndarray, std: np.ndarray) -> dict[str, float]:
    out = {}
    pred_by_id = {row["packet_id"]: row for row in predictions}
    for packet in packets:
        pred = pred_by_id.get(packet["packet_id"])
        if pred is None:
            continue
        feats = np.asarray(feature_vector(pred, packet), dtype=np.float64)
        score = float(np.dot(weights, (feats - mean) / std))
        out[packet["packet_id"]] = score
    return out


def deployed_rows(predictions: list[dict], packets: list[dict], scores: dict[str, float], threshold: float) -> list[dict]:
    pred_by_id = {row["packet_id"]: row for row in predictions}
    rows = []
    for packet in packets:
        pred = pred_by_id.get(packet["packet_id"])
        if pred is None:
            continue
        accepted = scores.get(packet["packet_id"], -1e99) >= threshold
        deployed_answer = pred.get("answer") if accepted else packet.get("baseline_answer")
        correct_answers = {norm_answer(answer) for answer in packet.get("correct_answers_in_visible", [])}
        deployed_correct = (bool(correct_answers) and norm_answer(deployed_answer) in correct_answers) or (not accepted and bool(packet.get("baseline_is_correct")))
        rows.append(
            {
                "packet_id": packet["packet_id"],
                "dataset": SDMV.infer_dataset(packet.get("dataset_label", "") or packet["packet_id"]),
                "category": str(packet.get("deployment_category") or "unknown"),
                "accepted": accepted,
                "deployed_correct": deployed_correct,
                "baseline_preserved": norm_answer(deployed_answer) == norm_answer(packet.get("baseline_answer")),
                "semantic_correct": pred_correct(pred, packet),
                "baseline_is_correct": bool(packet.get("baseline_is_correct")),
                "score": scores.get(packet["packet_id"], -1e99),
            }
        )
    return rows


def weighted_metrics(rows: list[dict], rates: dict[str, dict[str, float]]) -> dict:
    point = load_module("deployed_mix_policy_ci", ROOT / "work" / "deployed_mix_policy_ci.py").weighted_policy_metrics(rows, rates)[0]
    if abs(float(point.get("deployed_delta", 0.0))) <= DECISION_EPS:
        point["deployed_delta"] = 0.0
    recoverable = [row for row in rows if row["category"] in RECOVERABLE]
    baseline = [row for row in rows if row["category"] == "baseline_correct"]
    point.update(
        {
            "recoverable_correct": sum(row["deployed_correct"] for row in recoverable),
            "recoverable_total": len(recoverable),
            "baseline_preserved": sum(row["baseline_preserved"] for row in baseline),
            "baseline_total": len(baseline),
            "accepted": sum(row["accepted"] for row in rows),
            "packets": len(rows),
        }
    )
    return point


def percentile(vals: list[float], q: float) -> float:
    vals = sorted(vals)
    if not vals:
        return 0.0
    idx = min(len(vals) - 1, max(0, int(round(q * (len(vals) - 1)))))
    return vals[idx]


def bootstrap_ci(rows: list[dict], rates: dict[str, dict[str, float]], rounds: int, seed: int) -> dict:
    rng = random.Random(seed)
    by_category: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_category[row["category"]].append(row)
    samples = []
    for _ in range(rounds):
        sample = []
        for vals in by_category.values():
            sample.extend(vals[rng.randrange(len(vals))] for _ in vals)
        samples.append(weighted_metrics(sample, rates)["deployed_delta"])
    return {"delta_ci_low": percentile(samples, 0.025), "delta_ci_high": percentile(samples, 0.975)}


def choose_threshold(rows: list[dict], scores: dict[str, float], rates: dict[str, dict[str, float]], args: argparse.Namespace) -> tuple[float, dict]:
    if not rows:
        no_op = 1e99
        metrics = weighted_metrics(deployed_rows([], [], {}, no_op), rates) if False else {}
        return no_op, metrics
    candidates = sorted({scores[row["packet_id"]] for row in rows}, reverse=True)
    thresholds = [1e99] + candidates + [min(candidates) - 1.0]
    best_threshold = 1e99
    best_metrics: dict | None = None
    for threshold in thresholds:
        accepted_rows = [dict(row, accepted=row["score"] >= threshold) for row in rows]
        # Reconstruct utility on calibration examples directly because rows here already encode
        # advantage examples, not full deployed rows.
        regressions = sum(1 for row in accepted_rows if row["accepted"] and row["advantage"] < 0)
        recoveries = sum(1 for row in accepted_rows if row["accepted"] and row["advantage"] > 0)
        metric = {"recoveries": recoveries, "regressions": regressions, "accepted": sum(row["accepted"] for row in accepted_rows)}
        if regressions > args.max_calib_regressions:
            continue
        if best_metrics is None or (metric["recoveries"], -metric["accepted"]) > (best_metrics["recoveries"], -best_metrics["accepted"]):
            best_threshold = threshold
            best_metrics = metric
    if best_metrics is None:
        best_threshold = 1e99
        best_metrics = {"recoveries": 0, "regressions": 0, "accepted": 0}
    return best_threshold, best_metrics


def oracle_threshold(predictions: list[dict], packets: list[dict], scores: dict[str, float], rates: dict[str, dict[str, float]], args: argparse.Namespace) -> tuple[float, dict]:
    values = sorted({scores.get(packet["packet_id"], -1e99) for packet in packets}, reverse=True)
    thresholds = [1e99] + values + ([min(values) - 1.0] if values else [])
    best_threshold = 1e99
    best_metrics: dict | None = None
    best_rows = []
    for threshold in thresholds:
        rows = deployed_rows(predictions, packets, scores, threshold)
        metrics = weighted_metrics(rows, rates)
        if best_metrics is None or (metrics["deployed_delta"], metrics["recoverable_correct"], metrics["baseline_preserved"]) > (
            best_metrics["deployed_delta"],
            best_metrics["recoverable_correct"],
            best_metrics["baseline_preserved"],
        ):
            best_threshold = threshold
            best_metrics = metrics
            best_rows = rows
    assert best_metrics is not None
    best_metrics = dict(best_metrics)
    best_metrics.update(bootstrap_ci(best_rows, rates, args.bootstrap_rounds, args.seed + 9001))
    return best_threshold, best_metrics


def parse_run_label(path: Path) -> dict:
    name = path.name.replace("_raw_target_predictions.jsonl", "")
    match = re.search(r"semantic_target_calibration_v(103|104)_problem_(unique|pooled)_llama_to_expanded_gemma_(?:rich_)?both_seed(\d+)", name)
    if not match:
        return {"family": "unknown", "source_kind": "unknown", "seed": "0", "setup": name}
    return {"family": f"v{match.group(1)}", "source_kind": match.group(2), "seed": match.group(3), "setup": name}


def run(args: argparse.Namespace) -> None:
    packets = load_jsonl(args.test_packets)
    packet_by_id = {packet["packet_id"]: packet for packet in packets}
    rates = SDMV.load_category_rates([str(path) for path in args.category_stats])
    out_rows = []
    for raw_path in args.raw_predictions:
        predictions = load_jsonl(raw_path)
        predictions = [row for row in predictions if row["packet_id"] in packet_by_id]
        label = parse_run_label(raw_path)
        for per_category in [part.strip() for part in args.calibration_per_category.split(",") if part.strip()]:
            calib_packets, test_packets = split_target_packets(packets, per_category, int(label["seed"]) + len(out_rows) * 17)
            calib_ids = {packet["packet_id"] for packet in calib_packets}
            test_ids = {packet["packet_id"] for packet in test_packets}
            calib_predictions = [row for row in predictions if row["packet_id"] in calib_ids]
            test_predictions = [row for row in predictions if row["packet_id"] in test_ids]
            x, y, example_weights, examples = build_examples(calib_predictions, calib_packets)
            weights, mean, std, train_info = train_gate(x, y, example_weights, argparse.Namespace(**{**vars(args), "seed": int(label["seed"])}))
            calib_scores_all = gate_scores(calib_predictions, calib_packets, weights, mean, std)
            gate_examples = []
            for example in examples:
                packet = example["packet"]
                gate_examples.append(
                    {
                        "packet_id": packet["packet_id"],
                        "score": calib_scores_all.get(packet["packet_id"], -1e99),
                        "advantage": example["advantage"],
                    }
                )
            threshold, calib_metric = choose_threshold(gate_examples, calib_scores_all, rates, args)
            test_scores = gate_scores(test_predictions, test_packets, weights, mean, std)
            test_rows = deployed_rows(test_predictions, test_packets, test_scores, threshold)
            test_metrics = weighted_metrics(test_rows, rates)
            test_ci = bootstrap_ci(test_rows, rates, args.bootstrap_rounds, int(label["seed"]) + len(out_rows) * 1009)
            oracle_t, oracle_metrics = oracle_threshold(test_predictions, test_packets, test_scores, rates, argparse.Namespace(**{**vars(args), "seed": int(label["seed"])}))
            out_rows.append(
                {
                    **label,
                    "calib_per_category": per_category,
                    "target_calib_packets": len(calib_packets),
                    "target_test_packets": len(test_packets),
                    "train_status": train_info["status"],
                    "gate_train_examples": train_info["examples"],
                    "gate_train_positives": train_info["positives"],
                    "gate_threshold": threshold,
                    "calib_gate_recoveries": calib_metric.get("recoveries", 0),
                    "calib_gate_regressions": calib_metric.get("regressions", 0),
                    "test_delta": test_metrics["deployed_delta"],
                    "test_ci_low": test_ci["delta_ci_low"],
                    "test_ci_high": test_ci["delta_ci_high"],
                    "test_decision": "pass_lower_ci_positive" if test_ci["delta_ci_low"] > DECISION_EPS else "uncertain_or_negative",
                    "test_recoverable_correct": test_metrics["recoverable_correct"],
                    "test_recoverable_total": test_metrics["recoverable_total"],
                    "test_baseline_preserved": test_metrics["baseline_preserved"],
                    "test_baseline_total": test_metrics["baseline_total"],
                    "test_accepted": test_metrics["accepted"],
                    "test_packets": test_metrics["packets"],
                    "oracle_threshold": oracle_t,
                    "oracle_delta": oracle_metrics["deployed_delta"],
                    "oracle_ci_low": oracle_metrics["delta_ci_low"],
                    "oracle_ci_high": oracle_metrics["delta_ci_high"],
                    "oracle_decision": "pass_lower_ci_positive" if oracle_metrics["delta_ci_low"] > DECISION_EPS else "uncertain_or_negative",
                    "oracle_recoverable_correct": oracle_metrics["recoverable_correct"],
                    "oracle_baseline_preserved": oracle_metrics["baseline_preserved"],
                    "oracle_baseline_total": oracle_metrics["baseline_total"],
                }
            )

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    write_csv(csv_path, out_rows)
    lines = [
        "# Semantic Meta-Gate Audit",
        "",
        f"Raw prediction files: `{len(args.raw_predictions)}`. Rows: `{len(out_rows)}`.",
        "",
        "| family | source | rows | CI+ | point+ | clean point+ | oracle CI+ | best clean | best oracle |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in out_rows:
        groups[(row["family"], row["source_kind"])].append(row)
    for (family, source), rows in sorted(groups.items()):
        clean = [row for row in rows if int(row["test_baseline_preserved"]) == int(row["test_baseline_total"])]
        best_clean = max(clean or rows, key=lambda row: (float(row["test_delta"]), int(row["test_recoverable_correct"])))
        best_oracle = max(rows, key=lambda row: (float(row["oracle_delta"]), int(row["oracle_recoverable_correct"])))
        lines.append(
            f"| {family} | {source} | {len(rows)} | "
            f"{sum(float(row['test_ci_low']) > DECISION_EPS for row in rows)} | "
            f"{sum(float(row['test_delta']) > DECISION_EPS for row in rows)} | "
            f"{sum(float(row['test_delta']) > DECISION_EPS and int(row['test_baseline_preserved']) == int(row['test_baseline_total']) for row in rows)} | "
            f"{sum(float(row['oracle_ci_low']) > DECISION_EPS for row in rows)} | "
            f"{float(best_clean['test_delta']):+.3f} ({best_clean['test_baseline_preserved']}/{best_clean['test_baseline_total']}) | "
            f"{float(best_oracle['oracle_delta']):+.3f} ({best_oracle['oracle_baseline_preserved']}/{best_oracle['oracle_baseline_total']}) |"
        )
    lines += [
        "",
        "## Read",
        "",
        "The meta-gate trains a multifeature target-style accept/fallback policy on recovery-vs-regression examples, then chooses a calibration threshold that allows no baseline-correct regressions on the calibration split. It tests whether v103/v104 failed because one-dimensional semantic-score thresholding was too weak.",
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
    parser.add_argument("--raw-predictions", nargs="+", type=Path, required=True)
    parser.add_argument("--test-packets", type=Path, required=True)
    parser.add_argument("--category-stats", nargs="+", type=Path, required=True)
    parser.add_argument("--calibration-per-category", default="1,2,4,8,16,24,all")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--l2", type=float, default=1e-4)
    parser.add_argument("--max-calib-regressions", type=int, default=0)
    parser.add_argument("--bootstrap-rounds", type=int, default=250)
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--output-prefix", default="semantic_meta_gate_v105")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
