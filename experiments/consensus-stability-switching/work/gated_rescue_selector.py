#!/usr/bin/env python3
"""Tune a gate for applying a hard-packet rescue selector on ordinary trials."""

from __future__ import annotations

import argparse
import csv
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


def make_packet(row, scores_all, answers_all, n, rng):
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
    return {"question": row.get("question") or row.get("prompt"), "clusters": clusters[:5]}, bool(labels.any())


def add_predictions(packet, model):
    x = np.array([HP["cluster_features"](packet, c) for c in packet["clusters"]], dtype=float)
    probs = MB["predict_logistic"](model, x)
    learned_i = int(np.argmax(probs))
    top_sum = packet["clusters"][0]
    second_sum = packet["clusters"][1] if len(packet["clusters"]) > 1 else packet["clusters"][0]
    total_sum = sum(max(0.0, c["sum_score"]) for c in packet["clusters"]) + 1e-9
    return {
        "cluster_sum_correct": bool(top_sum["is_correct_cluster"]),
        "learned_correct": bool(packet["clusters"][learned_i]["is_correct_cluster"]),
        "learned_differs": learned_i != 0,
        "top_support_frac": float(top_sum["support_frac"]),
        "sum_margin_frac": float((top_sum["sum_score"] - second_sum["sum_score"]) / (abs(top_sum["sum_score"]) + 1e-9)),
        "top_sum_share": float(max(0.0, top_sum["sum_score"]) / total_sum),
        "learned_prob_margin": float(probs[learned_i] - probs[0]),
        "any_correct": any(c["is_correct_cluster"] for c in packet["clusters"]),
    }


def score_rows(rows, gate):
    support_t, margin_t, share_t, prob_t = gate
    correct = rescues = regresses = invokes = 0
    for r in rows:
        use_learned = (
            r["learned_differs"]
            and r["top_support_frac"] <= support_t
            and r["sum_margin_frac"] <= margin_t
            and r["top_sum_share"] <= share_t
            and r["learned_prob_margin"] >= prob_t
        )
        pred = r["learned_correct"] if use_learned else r["cluster_sum_correct"]
        correct += int(pred)
        invokes += int(use_learned)
        rescues += int(use_learned and (not r["cluster_sum_correct"]) and r["learned_correct"])
        regresses += int(use_learned and r["cluster_sum_correct"] and (not r["learned_correct"]))
    n = max(1, len(rows))
    return {
        "accuracy": correct / n,
        "invoke_rate": invokes / n,
        "rescue_rate": rescues / n,
        "regress_rate": regresses / n,
    }


def tune_gate(rows):
    supports = [0.02, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20, 0.30, 1.0]
    margins = [0.01, 0.03, 0.05, 0.08, 0.12, 0.20, 0.40, 1e9]
    shares = [0.20, 0.30, 0.40, 0.50, 0.65, 0.80, 1.0]
    probs = [-1.0, 0.0, 0.03, 0.06, 0.10, 0.20]
    best_gate = (0.0, 0.0, 0.0, 1e9)
    best_score = score_rows(rows, best_gate)
    for gate in [(s, m, sh, p) for s in supports for m in margins for sh in shares for p in probs]:
        score = score_rows(rows, gate)
        if (score["accuracy"], -score["regress_rate"], score["rescue_rate"]) > (
            best_score["accuracy"],
            -best_score["regress_rate"],
            best_score["rescue_rate"],
        ):
            best_gate, best_score = gate, score
    return best_gate, best_score


def build_rows(data, ids, scored, n, trials_per_problem, seed, model):
    rng = random.Random(seed)
    rows = []
    for pid in ids:
        scores, answers = scored[pid]
        for _ in range(trials_per_problem):
            packet, _ = make_packet(data[pid], scores, answers, n, rng)
            rows.append(add_predictions(packet, model))
    return rows


def run(args):
    model, packet_info = train_from_packets(args.train_packets)
    data = MB["load_data"](Path(args.data))
    rng = random.Random(args.seed)
    problem_ids = list(range(len(data)))
    rng.shuffle(problem_ids)
    verifier_ids = problem_ids[: args.verifier_train_problems]
    calib_ids = problem_ids[args.verifier_train_problems : args.verifier_train_problems + args.calib_problems]
    test_ids = problem_ids[args.verifier_train_problems + args.calib_problems :]

    print("training candidate verifier", flush=True)
    verifier, verifier_info = MB["train_candidate_verifier"](data, verifier_ids, args.verifier_samples_per_problem, args.seed)

    scored = {}
    for j, pid in enumerate(calib_ids + test_ids, 1):
        if j == 1 or j % 25 == 0:
            print(f"scoring problem {j}/{len(calib_ids)+len(test_ids)}", flush=True)
        samples = data[pid]["samples"]
        feats = [MB["candidate_features"](s) for s in samples]
        scored[pid] = (
            MB["predict_logistic"](verifier, np.array(feats, dtype=float)),
            [MB["extract_answer"](s) for s in samples],
        )

    calib_rows = build_rows(data, calib_ids, scored, args.n, args.trials_per_problem, args.seed + 301, model)
    test_rows = build_rows(data, test_ids, scored, args.n, args.trials_per_problem, args.seed + 401, model)
    gate, calib_score = tune_gate(calib_rows)
    test_score = score_rows(test_rows, gate)
    baseline_calib = score_rows(calib_rows, (0.0, 0.0, 0.0, 1e9))
    baseline_test = score_rows(test_rows, (0.0, 0.0, 0.0, 1e9))
    always_learned_test = {
        "accuracy": sum(float(r["learned_correct"]) for r in test_rows) / len(test_rows),
        "invoke_rate": 1.0,
        "rescue_rate": sum(float((not r["cluster_sum_correct"]) and r["learned_correct"]) for r in test_rows) / len(test_rows),
        "regress_rate": sum(float(r["cluster_sum_correct"] and (not r["learned_correct"])) for r in test_rows) / len(test_rows),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    rows = [
        {"slice": "calib_cluster_sum", "gate": "none", **baseline_calib},
        {"slice": "calib_gated", "gate": str(tuple(round(x, 4) for x in gate)), **calib_score},
        {"slice": "test_cluster_sum", "gate": "none", **baseline_test},
        {"slice": "test_always_learned", "gate": "always", **always_learned_test},
        {"slice": "test_gated", "gate": str(tuple(round(x, 4) for x in gate)), **test_score},
    ]
    csv_path = OUT / f"{args.output_prefix}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# Gated Hard-Packet Rescue Selector",
        "",
        f"Dataset: `{args.dataset_label}`.",
        f"Hard-packet model train clusters: {packet_info['clusters']}, positive rate {packet_info['positive_rate']:.3f}.",
        f"Candidate verifier positive rate: {verifier_info['positive_rate']:.3f}.",
        f"Gate tuple: `(max_top_support_frac, max_sum_margin_frac, max_top_sum_share, min_learned_prob_margin)` = `{tuple(round(x, 4) for x in gate)}`.",
        "",
        "| slice | accuracy | invoke rate | rescue rate | regress rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(f"| {row['slice']} | {row['accuracy']:.3f} | {row['invoke_rate']:.3f} | {row['rescue_rate']:.3f} | {row['regress_rate']:.3f} |")
    lines += [
        "",
        "## Read",
        "",
        "The gate is tuned on reserved calibration problems, then evaluated on held-out test problems. A useful rescue selector should beat `test_cluster_sum` without a large regression rate.",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(md_path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-packets", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--dataset-label", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--calib-problems", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--trials-per-problem", type=int, default=6)
    parser.add_argument("--n", type=int, default=128)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
