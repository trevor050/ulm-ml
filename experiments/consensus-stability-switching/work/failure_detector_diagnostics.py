#!/usr/bin/env python3
"""Diagnose whether cluster_sum failures are detectable from cheap set features."""

from __future__ import annotations

import argparse
import csv
import math
import random
import runpy
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
MB = runpy.run_path(str(ROOT / "work" / "monkey_css_realbench.py"))


def answer_entropy(clusters):
    counts = np.array([c["support"] for c in clusters], dtype=float)
    total = counts.sum()
    if total <= 0 or len(counts) <= 1:
        return 0.0
    p = counts / total
    return float(-(p * np.log(p + 1e-12)).sum() / math.log(len(counts) + 1))


def make_trial(row, scores_all, answers_all, n, rng):
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
        groups[None] = list(range(n))
    clusters = []
    for pred, local_idxs in groups.items():
        vals = np.array([scores[i] for i in local_idxs], dtype=float)
        clusters.append(
            {
                "answer": pred,
                "support": len(local_idxs),
                "support_frac": len(local_idxs) / n,
                "sum_score": float(vals.sum()),
                "max_score": float(vals.max()),
                "mean_score": float(vals.mean()),
                "std_score": float(vals.std()),
                "correct": bool(labels[local_idxs].any()),
            }
        )
    clusters.sort(key=lambda c: (c["sum_score"], c["support"], c["max_score"]), reverse=True)
    top = clusters[0]
    second = clusters[1] if len(clusters) > 1 else clusters[0]
    score_vals = np.array([c["sum_score"] for c in clusters], dtype=float)
    support_vals = np.array([c["support_frac"] for c in clusters], dtype=float)
    total_mass = float(score_vals.clip(min=0).sum() + 1e-9)
    any_correct = bool(labels.any())
    visible_correct = any(c["correct"] for c in clusters[:5])
    cluster_sum_correct = bool(top["correct"])
    miss = any_correct and (not cluster_sum_correct)
    visible_miss = visible_correct and (not cluster_sum_correct)
    features = [
        top["support_frac"],
        second["support_frac"],
        top["support_frac"] - second["support_frac"],
        top["sum_score"],
        second["sum_score"],
        top["sum_score"] - second["sum_score"],
        (top["sum_score"] - second["sum_score"]) / (abs(top["sum_score"]) + 1e-9),
        max(0.0, top["sum_score"]) / total_mass,
        top["max_score"],
        top["mean_score"],
        top["std_score"],
        float(len(clusters)),
        answer_entropy(clusters),
        float(score_vals.mean()),
        float(score_vals.std()),
        float(support_vals.std()),
        math.log2(n),
    ]
    return {
        "features": features,
        "any_correct": any_correct,
        "visible_correct": visible_correct,
        "cluster_sum_correct": cluster_sum_correct,
        "miss": miss,
        "visible_miss": visible_miss,
        "top_support": top["support_frac"],
        "cluster_count": len(clusters),
    }


def auc(scores, labels):
    pairs = sorted(zip(scores, labels), key=lambda x: x[0])
    pos = sum(labels)
    neg = len(labels) - pos
    if pos == 0 or neg == 0:
        return 0.5
    rank_sum = 0.0
    for rank, (_, label) in enumerate(pairs, 1):
        if label:
            rank_sum += rank
    return (rank_sum - pos * (pos + 1) / 2) / (pos * neg)


def precision_recall_at(scores, rows, rate, label_key):
    k = max(1, int(round(len(rows) * rate)))
    order = sorted(range(len(rows)), key=lambda i: scores[i], reverse=True)
    chosen = [rows[i] for i in order[:k]]
    positives = sum(float(r[label_key]) for r in rows)
    hits = sum(float(r[label_key]) for r in chosen)
    cluster_sum = sum(float(r["cluster_sum_correct"]) for r in rows) / len(rows)
    perfect_visible_gain = sum(float(r["visible_miss"]) for r in chosen) / len(rows)
    return {
        "invoke_rate": k / len(rows),
        "precision": hits / k,
        "recall": hits / max(1.0, positives),
        "perfect_visible_oracle_acc": cluster_sum + perfect_visible_gain,
        "visible_miss_capture": sum(float(r["visible_miss"]) for r in chosen) / max(1.0, sum(float(r["visible_miss"]) for r in rows)),
    }


def fit_detector(rows, label_key):
    x = np.array([r["features"] for r in rows], dtype=float)
    y = np.array([float(r[label_key]) for r in rows], dtype=float)
    pos = float(y.mean())
    weights = np.where(y > 0.5, 0.5 / max(pos, 1e-6), 0.5 / max(1 - pos, 1e-6))
    model = MB["fit_logistic"](x, y, steps=1400, lr=0.04, l2=5e-3, weights=weights)
    return model, pos


def predict(model, rows):
    x = np.array([r["features"] for r in rows], dtype=float)
    return MB["predict_logistic"](model, x)


def build_rows(data, ids, scored, n, trials_per_problem, seed):
    rng = random.Random(seed)
    rows = []
    for pid in ids:
        scores, answers = scored[pid]
        for _ in range(trials_per_problem):
            rows.append(make_trial(data[pid], scores, answers, n, rng))
    return rows


def summarize_rows(rows):
    return {
        "trials": len(rows),
        "any_correct": sum(float(r["any_correct"]) for r in rows) / len(rows),
        "visible_correct": sum(float(r["visible_correct"]) for r in rows) / len(rows),
        "cluster_sum": sum(float(r["cluster_sum_correct"]) for r in rows) / len(rows),
        "miss": sum(float(r["miss"]) for r in rows) / len(rows),
        "visible_miss": sum(float(r["visible_miss"]) for r in rows) / len(rows),
    }


def run(args):
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

    calib_rows = build_rows(data, calib_ids, scored, args.n, args.trials_per_problem, args.seed + 501)
    test_rows = build_rows(data, test_ids, scored, args.n, args.trials_per_problem, args.seed + 601)

    reports = []
    for label_key in ["miss", "visible_miss"]:
        model, train_pos = fit_detector(calib_rows, label_key)
        scores = predict(model, test_rows)
        labels = [bool(r[label_key]) for r in test_rows]
        base = {
            "target": label_key,
            "train_positive_rate": train_pos,
            "test_positive_rate": sum(float(x) for x in labels) / len(labels),
            "auc": auc(scores, labels),
        }
        for rate in [0.05, 0.10, 0.20, 0.30, 0.50]:
            m = precision_recall_at(scores, test_rows, rate, label_key)
            reports.append({**base, **{f"at_{int(rate*100)}_{k}": v for k, v in m.items()}})

    # Flatten for CSV readability: one row per target/rate.
    flat_rows = []
    for target in ["miss", "visible_miss"]:
        model, train_pos = fit_detector(calib_rows, target)
        scores = predict(model, test_rows)
        labels = [bool(r[target]) for r in test_rows]
        for rate in [0.05, 0.10, 0.20, 0.30, 0.50]:
            flat_rows.append(
                {
                    "target": target,
                    "invoke_rate": rate,
                    "train_positive_rate": train_pos,
                    "test_positive_rate": sum(float(x) for x in labels) / len(labels),
                    "auc": auc(scores, labels),
                    **precision_recall_at(scores, test_rows, rate, target),
                }
            )

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(flat_rows[0].keys()))
        writer.writeheader()
        writer.writerows(flat_rows)

    calib_summary = summarize_rows(calib_rows)
    test_summary = summarize_rows(test_rows)
    lines = [
        "# Cluster-Sum Failure Detector Diagnostics",
        "",
        f"Dataset: `{args.dataset_label}`.",
        f"Candidate verifier train samples: {verifier_info['samples']}, positive rate {verifier_info['positive_rate']:.3f}.",
        f"Evaluation: N={args.n}, {args.trials_per_problem} trials per problem.",
        "",
        "## Trial Base Rates",
        "",
        "| split | any-correct | visible-correct top5 | cluster_sum | miss | visible miss |",
        "|---|---:|---:|---:|---:|---:|",
        f"| calibration | {calib_summary['any_correct']:.3f} | {calib_summary['visible_correct']:.3f} | {calib_summary['cluster_sum']:.3f} | {calib_summary['miss']:.3f} | {calib_summary['visible_miss']:.3f} |",
        f"| test | {test_summary['any_correct']:.3f} | {test_summary['visible_correct']:.3f} | {test_summary['cluster_sum']:.3f} | {test_summary['miss']:.3f} | {test_summary['visible_miss']:.3f} |",
        "",
        "## Detector Quality",
        "",
        "| target | AUC | invoke rate | precision | recall | perfect visible-oracle acc if invoked | visible-miss capture |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in flat_rows:
        lines.append(
            f"| {row['target']} | {row['auc']:.3f} | {row['invoke_rate']:.2f} | {row['precision']:.3f} | {row['recall']:.3f} | {row['perfect_visible_oracle_acc']:.3f} | {row['visible_miss_capture']:.3f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "`miss` means any correct candidate exists but `cluster_sum` selected a wrong cluster. `visible_miss` means a correct cluster is visible in the top five clusters but `cluster_sum` selected a wrong cluster.",
        "",
        "`perfect visible-oracle acc if invoked` is an optimistic upper bound: start from `cluster_sum`, invoke a perfect top-five verifier only on the flagged sets, and assume no regressions. If that bound is still low, the detector is not surfacing enough useful failures.",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(md_path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--dataset-label", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--calib-problems", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--trials-per-problem", type=int, default=12)
    parser.add_argument("--n", type=int, default=128)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
