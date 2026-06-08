#!/usr/bin/env python3
"""Hashed text/numeric cluster scorer for deployed-mix packets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
TOKEN_RE = re.compile(r"[A-Za-z]+|\d+(?:\.\d+)?|[-+*/=^(){}\\]+|[^\sA-Za-z\d]")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SDMV = load_module("score_deployed_mix_verifier", ROOT / "work" / "score_deployed_mix_verifier.py")


def stable_hash(text: str, dim: int) -> int:
    digest = hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little") % dim


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def tokenize(text: str) -> list[str]:
    return [tok.lower() for tok in TOKEN_RE.findall(text)]


def packet_text(packet: dict, cluster: dict, reps: int, chars: int, include_problem: bool) -> str:
    parts = []
    if include_problem:
        parts += ["problem", str(packet.get("question") or "")]
    parts += ["answer", str(cluster.get("answer") or "")]
    for rep in cluster.get("representatives", [])[:reps]:
        text = str(rep.get("text") or "")
        if chars and len(text) > chars:
            text = text[:chars]
        parts += ["rationale", text]
    return "\n".join(parts)


def numeric_features(packet: dict, cluster: dict) -> dict[str, float]:
    support = float(cluster.get("support") or 0.0)
    support_frac = float(cluster.get("support_frac") or 0.0)
    rank = float(cluster.get("rank_by_sum") or 999.0)
    sum_score = float(cluster.get("sum_score") or 0.0)
    max_score = float(cluster.get("max_score") or 0.0)
    mean_score = float(cluster.get("mean_score") or 0.0)
    return {
        "bias": 1.0,
        "support_log": math.log1p(support),
        "support_frac": support_frac,
        "rank_inv": 1.0 / max(rank, 1.0),
        "rank_log_inv": 1.0 / math.log2(rank + 1.0),
        "sum_score": sum_score,
        "max_score": max_score,
        "mean_score": mean_score,
        "baseline_match": 1.0 if str(cluster.get("answer")) == str(packet.get("baseline_answer")) else 0.0,
    }


def sparse_features(packet: dict, cluster: dict, args: argparse.Namespace) -> dict[int, float]:
    feats: dict[int, float] = {}
    if args.feature_mode in {"text", "both"}:
        tokens = tokenize(packet_text(packet, cluster, args.representatives_per_cluster, args.rationale_chars, args.include_problem))
        counts = Counter(tokens)
        # Unigrams plus adjacent token pairs. Log-scaled counts keep long rationales from dominating.
        for tok, count in counts.items():
            idx = stable_hash("tok:" + tok, args.hash_dim)
            feats[idx] = feats.get(idx, 0.0) + math.log1p(count)
        for a, b in zip(tokens, tokens[1:]):
            idx = stable_hash("bigram:" + a + " " + b, args.hash_dim)
            feats[idx] = feats.get(idx, 0.0) + 0.5
    if args.feature_mode in {"numeric", "both"}:
        offset = args.hash_dim
        for i, (name, value) in enumerate(numeric_features(packet, cluster).items()):
            feats[offset + i] = float(value)
    return feats


def load_packets(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def cluster_rows(packets: list[dict], args: argparse.Namespace) -> list[tuple[str, dict[int, float], int, dict, dict]]:
    rows = []
    for packet in packets:
        for cluster in packet["clusters"]:
            y = 1 if cluster.get("is_correct_cluster") else 0
            rows.append((packet["packet_id"], sparse_features(packet, cluster, args), y, packet, cluster))
    return rows


def train(rows: list[tuple[str, dict[int, float], int, dict, dict]], args: argparse.Namespace) -> tuple[np.ndarray, dict]:
    dim = args.hash_dim + (len(numeric_features({}, {})) if args.feature_mode in {"numeric", "both"} else 0)
    weights = np.zeros(dim, dtype=np.float64)
    labels = [row[2] for row in rows]
    pos_rate = sum(labels) / max(1, len(labels))
    pos_weight = 0.5 / max(pos_rate, 1e-6)
    neg_weight = 0.5 / max(1.0 - pos_rate, 1e-6)
    rng = random.Random(args.seed)
    order = list(range(len(rows)))
    for epoch in range(args.epochs):
        rng.shuffle(order)
        lr = args.lr / math.sqrt(epoch + 1)
        for idx in order:
            _, feats, y, _, _ = rows[idx]
            score = sum(weights[j] * v for j, v in feats.items())
            pred = sigmoid(score)
            sample_weight = pos_weight if y else neg_weight
            grad_scale = sample_weight * (pred - y)
            for j, v in feats.items():
                weights[j] -= lr * (grad_scale * v + args.l2 * weights[j])
    return weights, {"clusters": len(rows), "positive_rate": pos_rate, "dim": dim}


def predict_prob(weights: np.ndarray, feats: dict[int, float]) -> float:
    return sigmoid(sum(weights[j] * v for j, v in feats.items()))


def choose_packet(packet: dict, weights: np.ndarray, args: argparse.Namespace) -> dict:
    scored = []
    for cluster in packet["clusters"]:
        prob = predict_prob(weights, sparse_features(packet, cluster, args))
        scored.append((prob, cluster))
    scored.sort(key=lambda item: (-item[0], int(item[1].get("rank_by_sum") or 999)))
    top, best = scored[0]
    second = scored[1][0] if len(scored) > 1 else 0.0
    return {
        "packet_id": packet["packet_id"],
        "answer": best["answer"],
        "confidence": top / max(1e-12, top + second),
        "semantic_cluster_probability": top,
        "semantic_cluster_margin": top - second,
        "selected_rank_by_sum": best.get("rank_by_sum"),
        "selected_support": best.get("support"),
        "selected_is_correct_cluster": bool(best.get("is_correct_cluster")),
        "model": f"hashed_semantic_{args.feature_mode}_train={args.train_label}",
    }


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


def answer_key_for_packet(packet: dict) -> dict:
    return {
        "dataset": SDMV.infer_dataset(packet.get("dataset_label", "") or packet["packet_id"]),
        "deployment_category": packet.get("deployment_category"),
        "correct_answers": packet.get("correct_answers_in_visible", []),
        "baseline_answer": packet.get("baseline_answer"),
        "baseline_is_correct": packet.get("baseline_is_correct"),
    }


def summary_rows(predictions: list[dict], test_packets: list[dict]) -> list[dict]:
    keys = {packet["packet_id"]: answer_key_for_packet(packet) for packet in test_packets}
    scored = [SDMV.score_prediction(pred, keys[pred["packet_id"]]) for pred in predictions]
    by_cat = defaultdict(list)
    for row in scored:
        by_cat[(row["dataset"], row["category"])].append(row)
    out = []
    for (dataset, category), vals in sorted(by_cat.items()):
        out.append(
            {
                "dataset": dataset,
                "category": category,
                "n": len(vals),
                "correct": sum(row["correct"] for row in vals),
                "correct_rate": sum(row["correct"] for row in vals) / max(1, len(vals)),
                "baseline_preserved": sum(row["preserved_baseline"] for row in vals),
                "baseline_preservation": sum(row["preserved_baseline"] for row in vals) / max(1, len(vals)),
                "avg_confidence": SDMV.mean_confidence(vals),
            }
        )
    return out


def exclude_overlapping_problems(train_packets: list[dict], test_packets: list[dict]) -> list[dict]:
    test_ids = {packet.get("orig_dset_idx") for packet in test_packets}
    return [packet for packet in train_packets if packet.get("orig_dset_idx") not in test_ids]


def run(args: argparse.Namespace) -> None:
    train_packets = load_packets(args.train_packets)
    test_packets = load_packets(args.test_packets)
    raw_train_n = len(train_packets)
    if args.exclude_test_problems_from_train:
        train_packets = exclude_overlapping_problems(train_packets, test_packets)
    rows = cluster_rows(train_packets, args)
    weights, info = train(rows, args)
    predictions = [choose_packet(packet, weights, args) for packet in test_packets]
    summary = summary_rows(predictions, test_packets)

    OUT.mkdir(parents=True, exist_ok=True)
    pred_path = OUT / f"{args.output_prefix}_predictions.jsonl"
    summary_csv = OUT / f"{args.output_prefix}_summary.csv"
    write_jsonl(pred_path, predictions)
    write_csv(summary_csv, summary)

    lines = [
        "# Hashed Text Cluster Scorer",
        "",
        f"Feature mode: `{args.feature_mode}`",
        f"Train: `{args.train_label}` on `{len(train_packets)}` packets / `{info['clusters']}` clusters.",
        f"Test: `{args.test_label}` on `{len(test_packets)}` packets.",
        f"Training positive cluster rate: `{info['positive_rate']:.3f}`.",
    ]
    if args.exclude_test_problems_from_train:
        lines.append(f"Problem-overlap filter kept `{len(train_packets)}` of `{raw_train_n}` train packets.")
    lines += [
        "",
        "| dataset | category | n | correct | correct rate | baseline preserved | preservation | avg confidence |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['dataset']} | {row['category']} | {row['n']} | {row['correct']} | {row['correct_rate']:.3f} | "
            f"{row['baseline_preserved']} | {row['baseline_preservation']:.3f} | {row['avg_confidence']:.3f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "This is a dependency-light supervised semantic cluster scorer. It hashes problem/candidate/rationale text and optional numeric cluster features, trains a weighted logistic model on visible cluster labels, and emits answer/confidence predictions for the deployed-mix report harness.",
        "",
        f"Predictions: [{pred_path.name}]({pred_path.name}). Summary CSV: [{summary_csv.name}]({summary_csv.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(pred_path)
    print(summary_csv)
    print(md_path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-packets", type=Path, required=True)
    parser.add_argument("--test-packets", type=Path, required=True)
    parser.add_argument("--train-label", required=True)
    parser.add_argument("--test-label", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--feature-mode", choices=["numeric", "text", "both"], default="both")
    parser.add_argument("--hash-dim", type=int, default=32768)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--lr", type=float, default=0.08)
    parser.add_argument("--l2", type=float, default=1e-5)
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--representatives-per-cluster", type=int, default=1)
    parser.add_argument("--rationale-chars", type=int, default=360)
    parser.add_argument("--include-problem", action="store_true")
    parser.add_argument("--exclude-test-problems-from-train", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
