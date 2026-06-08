#!/usr/bin/env python3
"""Low-dimensional process-feature cluster scorer for deployed-mix packets."""

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


BOXED_RE = re.compile(r"\\boxed\{")
FINAL_RE = re.compile(r"final answer", re.I)
HOPE_RE = re.compile(r"i hope it is correct", re.I)
THEREFORE_RE = re.compile(r"\btherefore\b|\\therefore", re.I)
HOWEVER_RE = re.compile(r"\bhowever\b", re.I)
CHECK_RE = re.compile(r"\b(check|verify|substitut|plug)\b", re.I)
ASSUME_RE = re.compile(r"\b(assume|guess|try|let)\b", re.I)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


MB = load_module("monkey_css_realbench", ROOT / "work" / "monkey_css_realbench.py")
SDMV = load_module("score_deployed_mix_verifier", ROOT / "work" / "score_deployed_mix_verifier.py")
DPCI = load_module("deployed_mix_policy_ci", ROOT / "work" / "deployed_mix_policy_ci.py")


def load_jsonl(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


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


def norm_answer(value: object) -> str:
    return SDMV.SLJ.norm(str(value))


def rep_process_features(text: str, answer: object) -> list[float]:
    chars = len(text)
    words = len(text.split())
    lines = [line for line in text.splitlines() if line.strip()]
    nums = MB.NUM_RE.findall(text)
    calc_total, calc_valid, calc_invalid = MB.equation_stats(text)
    answer_text = norm_answer(answer)
    answer_hits = 0
    if answer_text:
        answer_hits = len(re.findall(rf"(?<![\w.]){re.escape(answer_text)}(?![\w.])", text))
    boxed = len(BOXED_RE.findall(text))
    final = len(FINAL_RE.findall(text))
    hope = len(HOPE_RE.findall(text))
    therefore = len(THEREFORE_RE.findall(text))
    however = len(HOWEVER_RE.findall(text))
    checks = len(CHECK_RE.findall(text))
    assumes = len(ASSUME_RE.findall(text))
    candidate = MB.candidate_features(text)
    return [
        math.log1p(chars),
        math.log1p(words),
        min(chars / 512.0, 6.0),
        min(words / 160.0, 6.0),
        math.log1p(len(lines)),
        math.log1p(len(nums)),
        len(set(nums)) / max(1, len(nums)),
        math.log1p(calc_total),
        calc_valid / calc_total if calc_total else 0.0,
        calc_invalid / calc_total if calc_total else 0.0,
        math.log1p(answer_hits),
        math.log1p(boxed),
        math.log1p(final),
        1.0 if final and "final answer" in text[-160:].lower() else 0.0,
        math.log1p(hope),
        math.log1p(therefore),
        math.log1p(however),
        math.log1p(checks),
        math.log1p(assumes),
        *candidate,
    ]


def cluster_numeric_features(packet: dict, cluster: dict) -> list[float]:
    support = float(cluster.get("support") or 0.0)
    support_frac = float(cluster.get("support_frac") or 0.0)
    rank = float(cluster.get("rank_by_sum") or 999.0)
    sum_score = float(cluster.get("sum_score") or 0.0)
    max_score = float(cluster.get("max_score") or 0.0)
    mean_score = float(cluster.get("mean_score") or 0.0)
    baseline_match = 1.0 if norm_answer(cluster.get("answer")) == norm_answer(packet.get("baseline_answer")) else 0.0
    return [
        1.0,
        math.log1p(support),
        support_frac,
        1.0 / max(rank, 1.0),
        1.0 / math.log2(rank + 1.0),
        sum_score,
        max_score,
        mean_score,
        sum_score / max(EPS, support),
        baseline_match,
        1.0 if rank <= 3 else 0.0,
        1.0 if rank <= 5 else 0.0,
        1.0 if rank <= 10 else 0.0,
    ]


def cluster_features(packet: dict, cluster: dict, reps: int, chars: int) -> list[float]:
    reps_rows = cluster.get("representatives", [])[:reps]
    rep_vectors = []
    for rep in reps_rows:
        text = str(rep.get("text") or "")
        if chars and len(text) > chars:
            text = text[:chars]
        rep_vectors.append(rep_process_features(text, cluster.get("answer")))
    if not rep_vectors:
        rep_vectors = [[0.0] * len(rep_process_features("", cluster.get("answer")))]
    arr = np.asarray(rep_vectors, dtype=np.float64)
    return cluster_numeric_features(packet, cluster) + list(arr.mean(axis=0)) + list(arr.max(axis=0))


def packet_cluster_rows(packets: list[dict], args: argparse.Namespace) -> tuple[np.ndarray, np.ndarray, list[tuple[dict, dict]]]:
    features = []
    labels = []
    refs = []
    for packet in packets:
        for cluster in packet.get("clusters", []):
            features.append(cluster_features(packet, cluster, args.representatives_per_cluster, args.rationale_chars))
            labels.append(1.0 if cluster.get("is_correct_cluster") else 0.0)
            refs.append((packet, cluster))
    return np.asarray(features, dtype=np.float64), np.asarray(labels, dtype=np.float64), refs


def fit_logistic(x: np.ndarray, y: np.ndarray, seed: int, epochs: int, lr: float, l2: float) -> dict:
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std[std < 1e-6] = 1.0
    xs = (x - mean) / std
    xs = np.column_stack([np.ones(xs.shape[0]), xs])
    w = np.zeros(xs.shape[1], dtype=np.float64)
    pos_rate = float(y.mean()) if len(y) else 0.0
    pos_weight = 0.5 / max(pos_rate, 1e-6)
    neg_weight = 0.5 / max(1.0 - pos_rate, 1e-6)
    rng = random.Random(seed)
    order = list(range(len(y)))
    for epoch in range(epochs):
        rng.shuffle(order)
        step = lr / math.sqrt(epoch + 1)
        for idx in order:
            z = float(np.clip(np.dot(w, xs[idx]), -40, 40))
            p = 1.0 / (1.0 + math.exp(-z))
            sample_weight = pos_weight if y[idx] else neg_weight
            grad = sample_weight * (p - y[idx])
            w -= step * (grad * xs[idx] + l2 * np.r_[0.0, w[1:]])
    return {"w": w, "mean": mean, "std": std, "positive_rate": pos_rate, "features": int(x.shape[1])}


def predict_prob(model: dict, features: list[float]) -> float:
    x = (np.asarray(features, dtype=np.float64) - model["mean"]) / model["std"]
    x = np.r_[1.0, x]
    z = float(np.clip(np.dot(model["w"], x), -40, 40))
    return 1.0 / (1.0 + math.exp(-z))


def choose_packet(packet: dict, model: dict, args: argparse.Namespace) -> dict:
    scored = []
    for cluster in packet.get("clusters", []):
        prob = predict_prob(model, cluster_features(packet, cluster, args.representatives_per_cluster, args.rationale_chars))
        scored.append((prob, cluster))
    scored.sort(key=lambda item: (-item[0], int(item[1].get("rank_by_sum") or 999)))
    top, best = scored[0]
    second = scored[1][0] if len(scored) > 1 else 0.0
    return {
        "packet_id": packet["packet_id"],
        "answer": best.get("answer"),
        "confidence": top / max(EPS, top + second),
        "process_cluster_probability": top,
        "process_cluster_margin": top - second,
        "selected_rank_by_sum": best.get("rank_by_sum"),
        "selected_support": best.get("support"),
        "selected_is_correct_cluster": bool(best.get("is_correct_cluster")),
        "model": f"process_cluster_scorer_train={args.train_label}",
    }


def split_packets(packets: list[dict], seed: int, calibration_frac: float) -> tuple[list[dict], list[dict]]:
    by_category: dict[str, list[dict]] = defaultdict(list)
    for packet in packets:
        by_category[str(packet.get("deployment_category") or "unknown")].append(packet)
    rng = random.Random(seed)
    fit = []
    calib = []
    for category in sorted(by_category):
        rows = list(by_category[category])
        rng.shuffle(rows)
        n_calib = max(1, round(len(rows) * calibration_frac)) if len(rows) > 1 else 0
        calib.extend(rows[:n_calib])
        fit.extend(rows[n_calib:])
    return fit, calib


def answer_key_for_packet(packet: dict) -> dict:
    return {
        "dataset": SDMV.infer_dataset(packet.get("dataset_label", "") or packet["packet_id"]),
        "deployment_category": packet.get("deployment_category"),
        "correct_answers": packet.get("correct_answers_in_visible", []),
        "baseline_answer": packet.get("baseline_answer"),
        "baseline_is_correct": packet.get("baseline_is_correct"),
    }


def prediction_score(row: dict, score_field: str) -> float:
    return float(row.get(score_field) or 0.0)


def fallback_prediction(row: dict, packet: dict, threshold: float, score_field: str) -> dict:
    accepted = prediction_score(row, score_field) >= threshold
    out = dict(row)
    out["raw_answer"] = row.get("answer")
    out["raw_confidence"] = row.get("confidence")
    out["risk_threshold"] = threshold
    out["risk_score_field"] = score_field
    out["risk_score"] = prediction_score(row, score_field)
    out["risk_accepted"] = accepted
    if not accepted:
        out["answer"] = packet.get("baseline_answer")
        out["confidence"] = 1.0
    return out


def score_deployed(predictions: list[dict], packets: list[dict]) -> list[dict]:
    keys = {packet["packet_id"]: answer_key_for_packet(packet) for packet in packets}
    rows = []
    for pred in predictions:
        packet_id = pred["packet_id"]
        meta = keys[packet_id]
        raw = SDMV.score_prediction(pred, meta)
        accepted = bool(pred.get("risk_accepted", True))
        baseline_is_correct = bool(meta.get("baseline_is_correct"))
        deployed_correct = bool(raw["correct"]) or (not accepted and baseline_is_correct)
        rows.append(
            {
                "packet_id": packet_id,
                "dataset": raw["dataset"],
                "category": raw["category"],
                "accepted": accepted,
                "deployed_correct": deployed_correct,
                "baseline_preserved": bool(raw["preserved_baseline"]),
                "baseline_is_correct": baseline_is_correct,
                "raw_correct": bool(raw["correct"]),
                "risk_score": pred.get("risk_score", prediction_score(pred, "confidence")),
            }
        )
    return rows


def threshold_metrics(raw_predictions: list[dict], packets: list[dict], threshold: float, score_field: str) -> dict:
    deployed = [fallback_prediction(row, packet, threshold, score_field) for row, packet in zip(raw_predictions, packets, strict=True)]
    scored = score_deployed(deployed, packets)
    baseline = [row for row in scored if row["category"] == "baseline_correct"]
    recoverable = [row for row in scored if row["category"] in RECOVERABLE]
    return {
        "threshold": threshold,
        "accepted": sum(row["accepted"] for row in scored),
        "correct": sum(row["deployed_correct"] for row in scored),
        "recoverable_correct": sum(row["deployed_correct"] for row in recoverable),
        "baseline_preserved": sum(row["baseline_preserved"] for row in baseline),
        "baseline_total": len(baseline),
        "baseline_regressions": sum(1 for row in baseline if not row["deployed_correct"]),
    }


def choose_threshold(raw_predictions: list[dict], packets: list[dict], args: argparse.Namespace) -> dict:
    scores = sorted({prediction_score(row, args.score_field) for row in raw_predictions}, reverse=True)
    candidates = [max(scores) + 1.0] + scores + [0.0]
    rows = [threshold_metrics(raw_predictions, packets, threshold, args.score_field) for threshold in candidates]
    safe = [row for row in rows if row["baseline_regressions"] <= args.max_baseline_regressions]
    if not safe:
        return rows[0]
    return max(safe, key=lambda row: (row["recoverable_correct"], row["correct"], row["accepted"], -row["threshold"]))


def category_summary(scored: list[dict]) -> list[dict]:
    out = []
    for category in sorted({row["category"] for row in scored}):
        vals = [row for row in scored if row["category"] == category]
        out.append(
            {
                "category": category,
                "n": len(vals),
                "accepted": sum(row["accepted"] for row in vals),
                "deployed_correct": sum(row["deployed_correct"] for row in vals),
                "baseline_preserved": sum(row["baseline_preserved"] for row in vals),
            }
        )
    return out


def run(args: argparse.Namespace) -> None:
    source_packets = load_jsonl(args.train_packets)
    target_packets = load_jsonl(args.test_packets)
    if args.exclude_test_problems_from_train:
        test_ids = {packet.get("orig_dset_idx") for packet in target_packets}
        source_packets = [packet for packet in source_packets if packet.get("orig_dset_idx") not in test_ids]
    fit_packets, calib_packets = split_packets(source_packets, args.seed, args.calibration_frac)
    x, y, _refs = packet_cluster_rows(fit_packets, args)
    model = fit_logistic(x, y, args.seed, args.epochs, args.lr, args.l2)
    raw_calib = [choose_packet(packet, model, args) for packet in calib_packets]
    threshold_row = choose_threshold(raw_calib, calib_packets, args)
    threshold = float(threshold_row["threshold"])
    raw_target = [choose_packet(packet, model, args) for packet in target_packets]
    deployed_predictions = [fallback_prediction(row, packet, threshold, args.score_field) for row, packet in zip(raw_target, target_packets, strict=True)]
    deployed_rows = score_deployed(deployed_predictions, target_packets)
    rates = SDMV.load_category_rates([str(args.category_stats)])
    ci_rows = DPCI.bootstrap_ci(deployed_rows, rates, threshold, args.bootstrap_rounds, args.seed + 17)
    summary = category_summary(deployed_rows)

    OUT.mkdir(parents=True, exist_ok=True)
    pred_path = OUT / f"{args.output_prefix}_predictions.jsonl"
    summary_path = OUT / f"{args.output_prefix}_summary.csv"
    ci_path = OUT / f"{args.output_prefix}_ci.csv"
    md_path = OUT / f"{args.output_prefix}.md"
    write_jsonl(pred_path, deployed_predictions)
    write_csv(summary_path, summary)
    write_csv(ci_path, ci_rows)

    ci = ci_rows[0] if ci_rows else {}
    lines = [
        "# Process Cluster Scorer",
        "",
        f"Source: `{args.train_label}` -> target `{args.test_label}`.",
        f"Fit/calibration packets: `{len(fit_packets)}` / `{len(calib_packets)}` from `{len(source_packets)}` source packets.",
        f"Fit clusters: `{len(y)}`; positive rate `{model['positive_rate']:.3f}`; feature count `{model['features']}`.",
        f"Representatives/cluster: `{args.representatives_per_cluster}`; rationale chars `{args.rationale_chars}`.",
        f"Score field: `{args.score_field}`; chosen threshold `{threshold:.6f}`.",
        f"Calibration recoveries `{threshold_row['recoverable_correct']}`, baseline regressions `{threshold_row['baseline_regressions']}`.",
        "",
        "| category | n | accepted | deployed correct | baseline preserved |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(f"| {row['category']} | {row['n']} | {row['accepted']} | {row['deployed_correct']} | {row['baseline_preserved']} |")
    if ci:
        lines += [
            "",
            "## Natural-Rate Deployed Metric",
            "",
            f"Dataset `{ci['dataset']}`: deployed delta `{ci['deployed_delta']:+.3f}` "
            f"with 95% CI `{ci['delta_ci_low']:+.3f}..{ci['delta_ci_high']:+.3f}`; "
            f"decision `{ci['decision']}`.",
        ]
    lines += [
        "",
        f"Predictions: [{pred_path.name}]({pred_path.name}).",
        f"Summary CSV: [{summary_path.name}]({summary_path.name}). CI CSV: [{ci_path.name}]({ci_path.name}).",
    ]
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(md_path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-packets", type=Path, required=True)
    parser.add_argument("--test-packets", type=Path, required=True)
    parser.add_argument("--category-stats", type=Path, required=True)
    parser.add_argument("--train-label", required=True)
    parser.add_argument("--test-label", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--score-field", choices=["confidence", "process_cluster_probability", "process_cluster_margin"], default="confidence")
    parser.add_argument("--representatives-per-cluster", type=int, default=2)
    parser.add_argument("--rationale-chars", type=int, default=700)
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--lr", type=float, default=0.04)
    parser.add_argument("--l2", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--calibration-frac", type=float, default=0.5)
    parser.add_argument("--max-baseline-regressions", type=int, default=0)
    parser.add_argument("--bootstrap-rounds", type=int, default=250)
    parser.add_argument("--exclude-test-problems-from-train", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
