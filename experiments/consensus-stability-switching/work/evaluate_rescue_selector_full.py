#!/usr/bin/env python3
"""Evaluate hard-packet-trained rescue selectors on ordinary N=128 trials."""

from __future__ import annotations

import argparse
import csv
import json
import random
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
MB = runpy.run_path(str(ROOT / "work" / "monkey_css_realbench.py"))
HP = runpy.run_path(str(ROOT / "work" / "hard_packet_feature_transfer.py"))


def train_from_packets(path):
    packets = HP["load_packets"](path)
    return HP["train_model"](packets)


def cluster_rows(row, scores_all, answers_all, n, rng):
    idxs = rng.sample(range(len(row["samples"])), n)
    labels = np.array([row["is_corrects"][i] for i in idxs], dtype=bool)
    preds = [answers_all[i] for i in idxs]
    scores = np.array([scores_all[i] for i in idxs], dtype=float)
    groups = {}
    for local_i, pred in enumerate(preds):
        if pred is None:
            continue
        groups.setdefault(pred, []).append(local_i)
    if not groups:
        groups[None] = list(range(len(idxs)))

    clusters = []
    for pred, local_idxs in groups.items():
        vals = [float(scores[i]) for i in local_idxs]
        rep_order = sorted(local_idxs, key=lambda i: float(scores[i]), reverse=True)
        clusters.append(
            {
                "answer": pred,
                "support": len(local_idxs),
                "support_frac": len(local_idxs) / n,
                "sum_score": float(sum(vals)),
                "max_score": float(max(vals)),
                "mean_score": float(sum(vals) / len(vals)),
                "is_correct_cluster": bool(labels[local_idxs].any()),
                "representatives": [
                    {
                        "score": float(scores[i]),
                        "is_correct_candidate": bool(labels[i]),
                        "text": row["samples"][idxs[i]],
                    }
                    for i in rep_order[:3]
                ],
            }
        )
    clusters.sort(key=lambda c: (c["sum_score"], c["support"], c["max_score"]), reverse=True)
    for rank, cluster in enumerate(clusters, 1):
        cluster["rank_by_sum"] = rank
    packet = {
        "packet_id": str(row.get("orig_dset_idx", "")),
        "question": row.get("question") or row.get("prompt"),
        "clusters": clusters[:5],
    }
    return packet, bool(labels.any())


def choose(packet, selector, model=None):
    clusters = packet["clusters"]
    if selector == "cluster_sum":
        return max(clusters, key=lambda c: c["sum_score"])
    if selector == "support":
        return max(clusters, key=lambda c: (c["support"], c["sum_score"]))
    if selector == "mean_score":
        return max(clusters, key=lambda c: (c["mean_score"], c["support"]))
    if selector == "learned":
        x = np.array([HP["cluster_features"](packet, c) for c in clusters], dtype=float)
        probs = MB["predict_logistic"](model, x)
        return clusters[int(np.argmax(probs))]
    raise ValueError(selector)


def run_eval(args, model):
    data = MB["load_data"](Path(args.data))
    rng = random.Random(args.seed)
    problem_ids = list(range(len(data)))
    rng.shuffle(problem_ids)
    verifier_ids = problem_ids[: args.verifier_train_problems]
    test_ids = problem_ids[args.verifier_train_problems + args.audit_holdout_gap :]

    print("training candidate verifier", flush=True)
    verifier, verifier_info = MB["train_candidate_verifier"](data, verifier_ids, args.verifier_samples_per_problem, args.seed)

    scored = {}
    for j, pid in enumerate(test_ids, 1):
        if j == 1 or j % 25 == 0:
            print(f"scoring problem {j}/{len(test_ids)}", flush=True)
        samples = data[pid]["samples"]
        feats = [MB["candidate_features"](s) for s in samples]
        scores = MB["predict_logistic"](verifier, np.array(feats, dtype=float))
        answers = [MB["extract_answer"](s) for s in samples]
        scored[pid] = (scores, answers)

    trial_rng = random.Random(args.seed + 211)
    totals = {k: 0.0 for k in ["any_correct", "cluster_sum", "support", "mean_score", "learned"]}
    count = 0
    rescue = 0
    regress = 0
    learned_on_miss = 0
    learned_on_visible_miss = 0
    for pid in test_ids:
        scores, answers = scored[pid]
        for _ in range(args.trials_per_problem):
            packet, any_correct = cluster_rows(data[pid], scores, answers, args.n, trial_rng)
            values = {selector: choose(packet, selector, model)["is_correct_cluster"] for selector in ["cluster_sum", "support", "mean_score", "learned"]}
            totals["any_correct"] += float(any_correct)
            for key, val in values.items():
                totals[key] += float(val)
            rescue += int((not values["cluster_sum"]) and values["learned"])
            regress += int(values["cluster_sum"] and (not values["learned"]))
            learned_on_miss += int(any_correct and (not values["cluster_sum"]) and values["learned"])
            visible_correct = any(c["is_correct_cluster"] for c in packet["clusters"])
            learned_on_visible_miss += int(visible_correct and (not values["cluster_sum"]) and values["learned"])
            count += 1
    overall = {k: v / count for k, v in totals.items()}
    overall.update(
        {
            "trials": count,
            "rescues_cluster_sum_misses": rescue / count,
            "regresses_cluster_sum_hits": regress / count,
            "learned_correct_on_recoverable_misses": learned_on_miss / count,
            "learned_correct_on_visible_misses": learned_on_visible_miss / count,
            "verifier_train_positive_rate": verifier_info["positive_rate"],
        }
    )
    return overall


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-packets", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--dataset-label", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--audit-holdout-gap", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--trials-per-problem", type=int, default=8)
    parser.add_argument("--n", type=int, default=128)
    args = parser.parse_args()

    model, info = train_from_packets(args.train_packets)
    result = run_eval(args, model)
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(result.keys()))
        writer.writeheader()
        writer.writerow(result)

    lines = [
        "# Hard-Packet Rescue Selector On Ordinary Trials",
        "",
        f"Dataset: `{args.dataset_label}`.",
        f"Training packets: `{Path(args.train_packets).name}` ({info['clusters']} visible clusters, positive rate {info['positive_rate']:.3f}).",
        f"Evaluation: N={args.n}, {args.trials_per_problem} trials per held-out problem.",
        "",
        "| selector/metric | value |",
        "|---|---:|",
    ]
    for key in ["any_correct", "cluster_sum", "support", "mean_score", "learned", "rescues_cluster_sum_misses", "regresses_cluster_sum_hits", "learned_correct_on_recoverable_misses", "learned_correct_on_visible_misses"]:
        lines.append(f"| {key} | {result[key]:.3f} |")
    lines += [
        "",
        "## Read",
        "",
        "The learned selector is trained only on constructed hard packets, then deployed on ordinary candidate sets where `cluster_sum` may already be correct and where correct clusters may be absent or outside the visible top five. This tests whether a rescue heuristic becomes a real selector or merely solves the conditioned packet task.",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(md_path.read_text())


if __name__ == "__main__":
    main()
