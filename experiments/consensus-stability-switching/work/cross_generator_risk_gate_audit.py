#!/usr/bin/env python3
"""Risk-gate cross-generator agreement policies on held-out problems."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_mb():
    spec = importlib.util.spec_from_file_location("monkey_css_realbench", ROOT / "work" / "monkey_css_realbench.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


MB = load_mb()


def load_data(path: Path) -> list[dict]:
    with path.open() as f:
        return json.load(f)


def split_ids(n: int, train: int, gap: int, seed: int) -> tuple[list[int], list[int]]:
    rng = random.Random(seed)
    ids = list(range(n))
    rng.shuffle(ids)
    return ids[:train], ids[train + gap :]


def score_problem_samples(data: list[dict], pids: list[int], train_ids: list[int], args: argparse.Namespace, seed: int) -> dict[int, dict]:
    verifier, _info = MB.train_candidate_verifier(data, train_ids, args.verifier_samples_per_problem, seed)
    scored = {}
    for j, pid in enumerate(pids, start=1):
        if j == 1 or j % 25 == 0 or j == len(pids):
            print(f"scoring problem {j}/{len(pids)} for seed {seed}", flush=True)
        row = data[pid]
        feats = np.array([MB.candidate_features(sample) for sample in row["samples"]], dtype=float)
        scored[pid] = {
            "scores": MB.predict_logistic(verifier, feats),
            "answers": [MB.extract_answer(sample) for sample in row["samples"]],
            "labels": np.array([bool(x) for x in row["is_corrects"]], dtype=bool),
        }
    return scored


def clusters_from_indices(scored: dict, idxs: list[int]) -> list[dict]:
    totals: dict[str, float] = defaultdict(float)
    support: Counter[str] = Counter()
    max_score: dict[str, float] = defaultdict(float)
    correct: dict[str, bool] = defaultdict(bool)
    for idx in idxs:
        answer = scored["answers"][idx]
        if answer is None:
            continue
        score = float(scored["scores"][idx])
        totals[answer] += score
        support[answer] += 1
        max_score[answer] = max(max_score[answer], score)
        correct[answer] = correct[answer] or bool(scored["labels"][idx])
    rows = []
    for answer in totals:
        rows.append(
            {
                "answer": answer,
                "sum_score": totals[answer],
                "support": support[answer],
                "support_frac": support[answer] / max(1, len(idxs)),
                "max_score": max_score[answer],
                "correct": correct[answer],
            }
        )
    rows.sort(key=lambda row: (row["sum_score"], row["support"], row["max_score"], str(row["answer"])), reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    return rows


def second_metric(clusters: list[dict], key: str) -> float:
    return float(clusters[1][key]) if len(clusters) > 1 else 0.0


def reciprocal_rank(rank: int) -> float:
    return 1.0 / math.log2(rank + 1.0)


def choose_target_intersection(target: list[dict], other: list[dict], k: int) -> tuple[dict, dict]:
    other_by_answer = {str(row["answer"]): row for row in other[:k]}
    for row in target[:k]:
        match = other_by_answer.get(str(row["answer"]))
        if match is not None:
            return row, match
    return target[0], {}


def choose_union(target: list[dict], other: list[dict], k: int) -> tuple[dict, dict]:
    candidates: dict[str, dict] = {}
    origins: dict[str, dict] = {}
    for source, clusters in [("target", target[:k]), ("other", other[:k])]:
        for row in clusters:
            answer = str(row["answer"])
            if answer not in candidates:
                candidates[answer] = {"answer": row["answer"], "correct": False, "score": 0.0}
                origins[answer] = {}
            candidates[answer]["correct"] = candidates[answer]["correct"] or bool(row["correct"])
            candidates[answer]["score"] += reciprocal_rank(int(row["rank"])) + float(row["support_frac"])
            origins[answer][source] = row
            if source == "target":
                candidates[answer]["score"] += 0.05
    best = max(candidates.values(), key=lambda row: (row["score"], str(row["answer"])))
    return best, origins.get(str(best["answer"]), {})


def policy_choice(policy: str, target: list[dict], other: list[dict]) -> tuple[dict, dict]:
    if policy.startswith("target_intersection_top"):
        return choose_target_intersection(target, other, int(policy.removeprefix("target_intersection_top")))
    if policy.startswith("union_rank_top"):
        return choose_union(target, other, int(policy.removeprefix("union_rank_top")))
    if policy == "other_cluster_sum":
        return other[0], {"other": other[0]}
    raise ValueError(policy)


def features(policy: str, choice: dict, meta: dict, target: list[dict], other: list[dict]) -> list[float]:
    target_top = target[0]
    other_top = other[0]
    selected_answer = str(choice["answer"])
    target_match = meta.get("target") or next((row for row in target if str(row["answer"]) == selected_answer), {})
    other_match = meta.get("other") or next((row for row in other if str(row["answer"]) == selected_answer), {})
    target_rank = float(target_match.get("rank") or 99)
    other_rank = float(other_match.get("rank") or 99)
    changed = 1.0 if selected_answer != str(target_top["answer"]) else 0.0
    target_margin = float(target_top["sum_score"]) - second_metric(target, "sum_score")
    other_margin = float(other_top["sum_score"]) - second_metric(other, "sum_score")
    return [
        1.0,
        changed,
        1.0 / max(target_rank, 1.0),
        1.0 / max(other_rank, 1.0),
        float(target_match.get("support_frac") or 0.0),
        float(other_match.get("support_frac") or 0.0),
        float(target_match.get("sum_score") or 0.0) / max(float(target_top["sum_score"]), 1e-9),
        float(other_match.get("sum_score") or 0.0) / max(float(other_top["sum_score"]), 1e-9),
        float(target_top["support_frac"]),
        float(other_top["support_frac"]),
        target_margin / max(float(target_top["sum_score"]), 1e-9),
        other_margin / max(float(other_top["sum_score"]), 1e-9),
        1.0 if policy.startswith("target_intersection") else 0.0,
        1.0 if policy.startswith("union_rank") else 0.0,
        1.0 if policy == "other_cluster_sum" else 0.0,
    ]


def fit_logistic(rows: list[dict]) -> dict | None:
    train = [row for row in rows if row["changed"] and row["utility_label"] != 0]
    if len(train) < 8 or len({row["utility_label"] for row in train}) < 2:
        return None
    x = np.array([row["features"] for row in train], dtype=float)
    y = np.array([1.0 if row["utility_label"] > 0 else 0.0 for row in train], dtype=float)
    pos = float(y.mean())
    weights = np.where(y > 0.5, 0.5 / max(pos, 1e-6), 0.5 / max(1 - pos, 1e-6))
    return MB.fit_logistic(x, y, steps=900, lr=0.06, l2=1e-2, weights=weights)


def predict(model: dict | None, rows: list[dict]) -> list[float]:
    if model is None:
        return [0.0 for _ in rows]
    x = np.array([row["features"] for row in rows], dtype=float)
    return list(map(float, MB.predict_logistic(model, x)))


def split_problem_rows(rows: list[dict], calib_problems: int, seed: int) -> tuple[list[dict], list[dict]]:
    pids = sorted({int(row["pid"]) for row in rows})
    rng = random.Random(seed)
    rng.shuffle(pids)
    calib = set(pids[:calib_problems])
    return [row for row in rows if int(row["pid"]) in calib], [row for row in rows if int(row["pid"]) not in calib]


def percentile(vals: list[float], p: float) -> float:
    vals = sorted(vals)
    if not vals:
        return 0.0
    idx = round((len(vals) - 1) * p)
    return float(vals[max(0, min(len(vals) - 1, idx))])


def bootstrap_delta(rows: list[dict], rounds: int, seed: int) -> tuple[float, float]:
    by_problem: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_problem[str(row["pid"])].append(row)
    pids = list(by_problem)
    rng = random.Random(seed)
    vals = []
    for _ in range(rounds):
        sample = []
        for _ in pids:
            sample.extend(by_problem[rng.choice(pids)])
        baseline = sum(row["baseline_correct"] for row in sample) / max(1, len(sample))
        gated = sum(row["gated_correct"] for row in sample) / max(1, len(sample))
        vals.append(gated - baseline)
    return percentile(vals, 0.025), percentile(vals, 0.975)


def build_rows(target_label: str, other_label: str, target_data: list[dict], other_data: list[dict], seed: int, args: argparse.Namespace) -> list[dict]:
    train_ids, test_ids = split_ids(len(target_data), args.verifier_train_problems, args.audit_holdout_gap, seed)
    target_scored = score_problem_samples(target_data, test_ids, train_ids, args, seed)
    other_scored = score_problem_samples(other_data, test_ids, train_ids, args, seed + 17)
    policies = [p.strip() for p in args.policies.split(",") if p.strip()]
    rng = random.Random(seed + 1009)
    out = []
    for pid in test_ids:
        for trial in range(args.trials_per_problem):
            target_idxs = rng.sample(range(len(target_data[pid]["samples"])), args.n)
            other_idxs = rng.sample(range(len(other_data[pid]["samples"])), args.n)
            target_clusters = clusters_from_indices(target_scored[pid], target_idxs)
            other_clusters = clusters_from_indices(other_scored[pid], other_idxs)
            if not target_clusters or not other_clusters:
                continue
            baseline = target_clusters[0]
            for policy in policies:
                choice, meta = policy_choice(policy, target_clusters, other_clusters)
                changed = str(choice["answer"]) != str(baseline["answer"])
                correct = bool(choice["correct"])
                baseline_correct = bool(baseline["correct"])
                utility_label = int((not baseline_correct) and correct) - int(baseline_correct and not correct)
                out.append(
                    {
                        "target": target_label,
                        "other": other_label,
                        "seed": seed,
                        "pid": pid,
                        "trial": trial,
                        "policy": policy,
                        "baseline_correct": baseline_correct,
                        "policy_correct": correct,
                        "changed": changed,
                        "utility_label": utility_label,
                        "features": features(policy, choice, meta, target_clusters, other_clusters),
                    }
                )
    return out


def choose_threshold(calib_rows: list[dict], scores: list[float]) -> float | None:
    changed_scores = sorted({score for row, score in zip(calib_rows, scores, strict=True) if row["changed"]}, reverse=True)
    best = None
    best_recoveries = -1
    for threshold in changed_scores:
        accepted = [(row, score) for row, score in zip(calib_rows, scores, strict=True) if row["changed"] and score >= threshold]
        regressions = sum(row["baseline_correct"] and not row["policy_correct"] for row, _ in accepted)
        if regressions:
            continue
        recoveries = sum((not row["baseline_correct"]) and row["policy_correct"] for row, _ in accepted)
        if recoveries > best_recoveries:
            best = threshold
            best_recoveries = recoveries
    return best


def evaluate_group(rows: list[dict], args: argparse.Namespace) -> list[dict]:
    results = []
    for calib_problems in [int(x) for x in args.calibration_problems.split(",") if x.strip()]:
        calib_rows, test_rows = split_problem_rows(rows, calib_problems, int(rows[0]["seed"]) + calib_problems)
        model = fit_logistic(calib_rows)
        calib_scores = predict(model, calib_rows)
        threshold = choose_threshold(calib_rows, calib_scores) if model is not None else None
        test_scores = predict(model, test_rows)
        eval_rows = []
        for row, score in zip(test_rows, test_scores, strict=True):
            accept = bool(row["changed"] and threshold is not None and score >= threshold)
            gated_correct = bool(row["policy_correct"] if accept else row["baseline_correct"])
            out = dict(row)
            out["accept"] = accept
            out["score"] = score
            out["gated_correct"] = gated_correct
            eval_rows.append(out)
        baseline = sum(row["baseline_correct"] for row in eval_rows) / max(1, len(eval_rows))
        raw = sum(row["policy_correct"] for row in eval_rows) / max(1, len(eval_rows))
        gated = sum(row["gated_correct"] for row in eval_rows) / max(1, len(eval_rows))
        recoveries = sum((not row["baseline_correct"]) and row["gated_correct"] for row in eval_rows)
        regressions = sum(row["baseline_correct"] and not row["gated_correct"] for row in eval_rows)
        accepts = sum(row["accept"] for row in eval_rows)
        ci_low, ci_high = bootstrap_delta(eval_rows, args.bootstrap_rounds, int(rows[0]["seed"]) + 5000 + calib_problems)
        results.append(
            {
                "target": rows[0]["target"],
                "other": rows[0]["other"],
                "seed": rows[0]["seed"],
                "policy": rows[0]["policy"],
                "calib_problems": calib_problems,
                "test_trials": len(eval_rows),
                "baseline_acc": baseline,
                "raw_policy_acc": raw,
                "gated_acc": gated,
                "gated_delta": gated - baseline,
                "delta_ci_low": ci_low,
                "delta_ci_high": ci_high,
                "accepts": accepts,
                "recoveries": recoveries,
                "regressions": regressions,
                "threshold": "" if threshold is None else threshold,
                "fit_examples": len([row for row in calib_rows if row["changed"] and row["utility_label"] != 0]),
            }
        )
    return results


def aggregate(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["target"], row["other"], row["policy"], str(row["calib_problems"]))].append(row)
    out = []
    for (target, other, policy, calib), vals in sorted(groups.items()):
        deltas = [float(row["gated_delta"]) for row in vals]
        out.append(
            {
                "target": target,
                "other": other,
                "policy": policy,
                "calib_problems": calib,
                "seeds": len(vals),
                "mean_delta": sum(deltas) / len(deltas),
                "min_delta": min(deltas),
                "max_delta": max(deltas),
                "positive_seeds": sum(d > 0 for d in deltas),
                "ci_positive_seeds": sum(float(row["delta_ci_low"]) > 0 for row in vals),
                "total_accepts": sum(int(row["accepts"]) for row in vals),
                "total_recoveries": sum(int(row["recoveries"]) for row in vals),
                "total_regressions": sum(int(row["regressions"]) for row in vals),
            }
        )
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt(x: float) -> str:
    return f"{x:+.3f}"


def write_outputs(detail: list[dict], summary: list[dict], aggregate_rows: list[dict], args: argparse.Namespace) -> None:
    OUT.mkdir(exist_ok=True)
    detail_path = OUT / f"{args.output_prefix}_details.jsonl"
    summary_path = OUT / f"{args.output_prefix}.csv"
    aggregate_path = OUT / f"{args.output_prefix}_aggregate.csv"
    md_path = OUT / f"{args.output_prefix}.md"
    with detail_path.open("w") as f:
        for row in detail:
            safe = dict(row)
            safe["features"] = [round(float(x), 6) for x in safe["features"]]
            f.write(json.dumps(safe) + "\n")
    write_csv(summary_path, summary)
    write_csv(aggregate_path, aggregate_rows)

    best = sorted(aggregate_rows, key=lambda row: (float(row["mean_delta"]), -int(row["total_regressions"])), reverse=True)[:14]
    lines = [
        "# Cross-Generator Risk-Gate Audit",
        "",
        "This tests whether the asymmetric v108 auxiliary-generator signal can be calibrated into a conservative accept/fallback policy.",
        "",
        f"Config: `N={args.n}`, trials/problem `{args.trials_per_problem}`, seeds `{args.seeds}`, policies `{args.policies}`, calibration problems `{args.calibration_problems}`.",
        "",
        "| target | other | policy | calib problems | mean delta | signs | CI+ seeds | accepts | recoveries | regressions |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in best:
        lines.append(
            f"| {row['target']} | {row['other']} | {row['policy']} | {row['calib_problems']} | {fmt(float(row['mean_delta']))} | "
            f"{row['positive_seeds']}/{row['seeds']} | {row['ci_positive_seeds']}/{row['seeds']} | {row['total_accepts']} | "
            f"{row['total_recoveries']} | {row['total_regressions']} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "A useful result would keep positive Gemma-with-Llama movement while learning no-op for Llama-with-Gemma. A weak result means the auxiliary trace has raw signal but still needs richer calibration or generator-choice features.",
        "",
        f"Details: [{detail_path.name}]({detail_path.name}). Summary CSV: [{summary_path.name}]({summary_path.name}). Aggregate CSV: [{aggregate_path.name}]({aggregate_path.name}).",
    ]
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(md_path.read_text())


def run(args: argparse.Namespace) -> None:
    print("loading Llama trace", flush=True)
    llama = load_data(Path(args.llama))
    print("loading Gemma trace", flush=True)
    gemma = load_data(Path(args.gemma))
    print("traces loaded", flush=True)
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    detail = []
    for seed in seeds:
        detail.extend(build_rows("MATH/Gemma", "MATH/Llama", gemma, llama, seed, args))
        detail.extend(build_rows("MATH/Llama", "MATH/Gemma", llama, gemma, seed, args))
    grouped: dict[tuple[str, str, int, str], list[dict]] = defaultdict(list)
    for row in detail:
        grouped[(row["target"], row["other"], int(row["seed"]), row["policy"])].append(row)
    summary = []
    for vals in grouped.values():
        summary.extend(evaluate_group(vals, args))
    aggregate_rows = aggregate(summary)
    write_outputs(detail, summary, aggregate_rows, args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--llama", default=str(ROOT / "work" / "MATH_Llama-3-8B-Instruct.json"))
    parser.add_argument("--gemma", default=str(ROOT / "work" / "MATH_Gemma-2B.json"))
    parser.add_argument("--n", type=int, default=128)
    parser.add_argument("--trials-per-problem", type=int, default=8)
    parser.add_argument("--seeds", default="60601,60602,60603")
    parser.add_argument("--policies", default="target_intersection_top10,target_intersection_top20,union_rank_top3")
    parser.add_argument("--calibration-problems", default="12,24,36")
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--audit-holdout-gap", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--bootstrap-rounds", type=int, default=250)
    parser.add_argument("--output-prefix", default="cross_generator_risk_gate_v109")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
