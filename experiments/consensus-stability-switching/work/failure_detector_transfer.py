#!/usr/bin/env python3
"""Cross-model transfer for cluster_sum failure detectors."""

from __future__ import annotations

import argparse
import csv
import random
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FD = runpy.run_path(str(ROOT / "work" / "failure_detector_diagnostics.py"))
MB = runpy.run_path(str(ROOT / "work" / "monkey_css_realbench.py"))


def build_split(data_path, seed, verifier_train_problems, calib_problems, verifier_samples_per_problem, n, trials_per_problem):
    data = MB["load_data"](Path(data_path))
    rng = random.Random(seed)
    problem_ids = list(range(len(data)))
    rng.shuffle(problem_ids)
    verifier_ids = problem_ids[:verifier_train_problems]
    calib_ids = problem_ids[verifier_train_problems : verifier_train_problems + calib_problems]
    test_ids = problem_ids[verifier_train_problems + calib_problems :]

    print(f"training candidate verifier for {Path(data_path).name}", flush=True)
    verifier, verifier_info = MB["train_candidate_verifier"](data, verifier_ids, verifier_samples_per_problem, seed)
    scored = {}
    for j, pid in enumerate(calib_ids + test_ids, 1):
        if j == 1 or j % 25 == 0:
            print(f"scoring {Path(data_path).name} problem {j}/{len(calib_ids)+len(test_ids)}", flush=True)
        samples = data[pid]["samples"]
        feats = [MB["candidate_features"](s) for s in samples]
        scored[pid] = (
            MB["predict_logistic"](verifier, np.array(feats, dtype=float)),
            [MB["extract_answer"](s) for s in samples],
        )
    calib_rows = FD["build_rows"](data, calib_ids, scored, n, trials_per_problem, seed + 501)
    test_rows = FD["build_rows"](data, test_ids, scored, n, trials_per_problem, seed + 601)
    return {
        "calib": calib_rows,
        "test": test_rows,
        "verifier_info": verifier_info,
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


def evaluate(scores, rows, label_key):
    labels = [bool(r[label_key]) for r in rows]
    out = {
        "test_positive_rate": sum(float(x) for x in labels) / len(labels),
        "auc": FD["auc"](scores, labels),
    }
    for rate in [0.10, 0.20, 0.30]:
        metrics = FD["precision_recall_at"](scores, rows, rate, label_key)
        for key, val in metrics.items():
            out[f"{key}_at_{int(rate*100)}"] = val
    return out


def run(args):
    datasets = {
        "llama": build_split(
            args.llama_data,
            args.seed,
            args.verifier_train_problems,
            args.calib_problems,
            args.verifier_samples_per_problem,
            args.n,
            args.trials_per_problem,
        ),
        "gemma": build_split(
            args.gemma_data,
            args.seed,
            args.verifier_train_problems,
            args.calib_problems,
            args.verifier_samples_per_problem,
            args.n,
            args.trials_per_problem,
        ),
    }
    rows = []
    for target in ["miss", "visible_miss"]:
        models = {}
        for train_name, split in datasets.items():
            model, pos = fit_detector(split["calib"], target)
            models[train_name] = (model, pos)
        pooled_model, pooled_pos = fit_detector(datasets["llama"]["calib"] + datasets["gemma"]["calib"], target)
        models["pooled"] = (pooled_model, pooled_pos)

        for train_name, (model, train_pos) in models.items():
            for test_name, split in datasets.items():
                scores = predict(model, split["test"])
                metrics = evaluate(scores, split["test"], target)
                rows.append(
                    {
                        "target": target,
                        "train": train_name,
                        "test": test_name,
                        "train_positive_rate": train_pos,
                        **metrics,
                    }
                )

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Failure Detector Transfer Matrix",
        "",
        f"Evaluation: N={args.n}, {args.trials_per_problem} trials per problem.",
        "",
        "## AUC",
        "",
        "| target | train | test | AUC | precision@20 | recall@20 | oracle acc@20 |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for target in ["miss", "visible_miss"]:
        for row in [r for r in rows if r["target"] == target]:
            lines.append(
                f"| {target} | {row['train']} | {row['test']} | {row['auc']:.3f} | {row['precision_at_20']:.3f} | {row['recall_at_20']:.3f} | {row['perfect_visible_oracle_acc_at_20']:.3f} |"
            )
    lines += [
        "",
        "## Read",
        "",
        "Each detector is trained on calibration problems from one source trace, then evaluated on held-out test problems from Llama or Gemma. `pooled` trains on both calibration splits. If cross-transfer is weak, failure detection should be treated as model/task-calibrated rather than universal.",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(md_path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llama-data", default="work/MATH_Llama-3-8B-Instruct.json")
    parser.add_argument("--gemma-data", default="work/MATH_Gemma-2B.json")
    parser.add_argument("--output-prefix", default="failure_detector_transfer_math_llama_gemma_n128")
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
