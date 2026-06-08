#!/usr/bin/env python3
"""Train shallow cluster selectors on hard packet features and test transfer."""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import runpy
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
MB = runpy.run_path(str(ROOT / "work" / "monkey_css_realbench.py"))
NUM_RE = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?")


def norm_float(x):
    try:
        return float(str(x).replace(",", "").strip())
    except Exception:
        return None


def problem_numbers(packet):
    nums = []
    for raw in NUM_RE.findall(packet.get("question") or ""):
        val = norm_float(raw)
        if val is not None and math.isfinite(val):
            nums.append(val)
    return nums


def repetition_score(text):
    if not text:
        return 0.0
    longest = current = 1
    prev = text[0]
    for ch in text[1:]:
        if ch == prev:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
            prev = ch
    return min(1.0, longest / 80.0)


def cluster_features(packet, cluster):
    reps = cluster.get("representatives", [])
    texts = [r.get("text", "") for r in reps]
    joined = "\n".join(texts)
    answer = str(cluster.get("answer"))
    ans_val = norm_float(answer)
    nums = problem_numbers(packet)
    max_abs = max([abs(x) for x in nums] + [1.0])
    if ans_val is None or not math.isfinite(ans_val):
        magnitude = 1.0
        in_problem = 0.0
        near_problem = 0.0
    else:
        magnitude = math.log1p(abs(ans_val)) / math.log1p(max_abs + 1.0)
        in_problem = 1.0 if any(abs(ans_val - x) <= 1e-9 for x in nums) else 0.0
        near_problem = min((abs(ans_val - x) for x in nums), default=max_abs) / (max_abs + 1.0)
    answer_mentions = sum(1 for text in texts if answer in text) / max(1, len(texts))
    digit_density = sum(ch.isdigit() for ch in joined) / max(1, len(joined))
    avg_len = sum(len(t) for t in texts) / max(1, len(texts))
    avg_rep = sum(repetition_score(t) for t in texts) / max(1, len(texts))
    rep_scores = [float(r.get("score", 0.0)) for r in reps]
    rank = float(cluster.get("rank_by_sum", 99))
    return [
        float(cluster["support_frac"]),
        math.log1p(float(cluster["support"])),
        float(cluster["sum_score"]),
        float(cluster["max_score"]),
        float(cluster["mean_score"]),
        1.0 / rank,
        answer_mentions,
        in_problem,
        near_problem,
        magnitude,
        digit_density,
        math.log1p(avg_len),
        avg_rep,
        float(np.mean(rep_scores)) if rep_scores else 0.0,
        float(np.std(rep_scores)) if rep_scores else 0.0,
    ]


def load_packets(path):
    return [json.loads(line) for line in Path(path).open()]


def rows_from_packets(packets):
    rows = []
    for packet in packets:
        for cluster in packet["clusters"]:
            rows.append((cluster_features(packet, cluster), float(cluster["is_correct_cluster"]), packet["packet_id"]))
    return rows


def train_model(packets):
    rows = rows_from_packets(packets)
    x = np.array([r[0] for r in rows], dtype=float)
    y = np.array([r[1] for r in rows], dtype=float)
    pos = float(y.mean())
    weights = np.where(y > 0.5, 0.5 / max(pos, 1e-6), 0.5 / max(1 - pos, 1e-6))
    model = MB["fit_logistic"](x, y, steps=1600, lr=0.04, l2=1e-2, weights=weights)
    return model, {"clusters": len(rows), "positive_rate": pos}


def choose_by_model(packet, model):
    x = np.array([cluster_features(packet, c) for c in packet["clusters"]], dtype=float)
    probs = MB["predict_logistic"](model, x)
    return packet["clusters"][int(np.argmax(probs))]


def choose_baseline(packet, name):
    clusters = packet["clusters"]
    if name == "cluster_sum":
        return max(clusters, key=lambda c: c["sum_score"])
    if name == "support":
        return max(clusters, key=lambda c: (c["support"], c["sum_score"]))
    if name == "mean_score":
        return max(clusters, key=lambda c: (c["mean_score"], c["support"]))
    if name == "max_score":
        return max(clusters, key=lambda c: (c["max_score"], c["support"]))
    raise ValueError(name)


def eval_selector(packets, selector, model=None):
    correct = 0
    ranks = Counter()
    for packet in packets:
        cluster = choose_by_model(packet, model) if selector == "learned" else choose_baseline(packet, selector)
        correct += int(cluster["is_correct_cluster"])
        ranks[int(cluster["rank_by_sum"])] += 1
    return correct / max(1, len(packets)), ranks


def split_packets(packets, seed):
    rng = random.Random(seed)
    packets = list(packets)
    rng.shuffle(packets)
    mid = len(packets) // 2
    return packets[:mid], packets[mid:]


def experiment(label, train_packets, test_packets):
    model, info = train_model(train_packets)
    learned, ranks = eval_selector(test_packets, "learned", model)
    rows = {
        "experiment": label,
        "train_packets": len(train_packets),
        "test_packets": len(test_packets),
        "train_clusters": info["clusters"],
        "train_positive_rate": info["positive_rate"],
        "learned": learned,
        "learned_rank_mode": ranks.most_common(1)[0][0] if ranks else "",
    }
    for baseline in ["cluster_sum", "support", "max_score", "mean_score"]:
        acc, _ = eval_selector(test_packets, baseline)
        rows[baseline] = acc
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llama", required=True)
    parser.add_argument("--gemma", required=True)
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--output-prefix", default="hard_packet_feature_transfer")
    args = parser.parse_args()

    llama = load_packets(args.llama)
    gemma = load_packets(args.gemma)
    llama_a, llama_b = split_packets(llama, args.seed)
    gemma_a, gemma_b = split_packets(gemma, args.seed)

    results = [
        experiment("llama_half_to_llama_half", llama_a, llama_b),
        experiment("gemma_half_to_gemma_half", gemma_a, gemma_b),
        experiment("llama_to_gemma", llama, gemma),
        experiment("gemma_to_llama", gemma, llama),
        experiment("pooled_half_to_pooled_half", llama_a + gemma_a, llama_b + gemma_b),
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    fields = list(results[0].keys())
    with csv_path.open("w") as f:
        f.write(",".join(fields) + "\n")
        for row in results:
            f.write(",".join(str(row[k]) for k in fields) + "\n")

    lines = [
        "# Hard-Packet Shallow Feature Transfer",
        "",
        "This tests a cheap objection to the cluster-verifier proposal: maybe shallow supervised features over the visible clusters are already enough.",
        "",
        "| experiment | train packets | test packets | cluster_sum | support | max_score | mean_score | learned shallow selector |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in results:
        lines.append(
            f"| {row['experiment']} | {row['train_packets']} | {row['test_packets']} | {row['cluster_sum']:.3f} | {row['support']:.3f} | {row['max_score']:.3f} | {row['mean_score']:.3f} | {row['learned']:.3f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "`cluster_sum` is zero by construction on these hard packets. The learned selector is trained on only visible packet features: support, verifier mass, score moments, answer magnitude/proximity features, text length, digit density, and simple repetition/mention counts.",
        "",
        "The learned selector doing well here does not yet prove a deployed method, because these packets are conditioned on `cluster_sum` failing and ensure a correct cluster is visible. It does prove the packet task is not pure noise. The next test is whether this rescue selector improves accuracy on ordinary candidate sets where failure cases are not labeled in advance.",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(md_path.read_text())


if __name__ == "__main__":
    main()
