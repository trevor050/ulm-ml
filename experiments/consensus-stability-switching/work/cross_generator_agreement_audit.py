#!/usr/bin/env python3
"""Audit whether a second generator trace can rerank or rescue answer clusters."""

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
    verifier, info = MB.train_candidate_verifier(data, train_ids, args.verifier_samples_per_problem, seed)
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
    return {"info": info, "by_pid": scored}


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


def by_answer(clusters: list[dict]) -> dict[str, dict]:
    return {str(row["answer"]): row for row in clusters}


def reciprocal_rank_score(rank: int) -> float:
    return 1.0 / math.log2(rank + 1.0)


def choose_intersection(target: list[dict], other: list[dict], k: int) -> dict:
    other_answers = {str(row["answer"]) for row in other[:k]}
    for row in target[:k]:
        if str(row["answer"]) in other_answers:
            return row
    return target[0]


def choose_other_if_intersection(target: list[dict], other: list[dict], k: int) -> dict:
    target_answers = {str(row["answer"]) for row in target[:k]}
    for row in other[:k]:
        if str(row["answer"]) in target_answers:
            return row
    return target[0]


def choose_union_rank(target: list[dict], other: list[dict], k: int) -> dict:
    candidates: dict[str, dict] = {}
    for source, clusters in [("target", target[:k]), ("other", other[:k])]:
        for row in clusters:
            answer = str(row["answer"])
            if answer not in candidates:
                candidates[answer] = {"answer": row["answer"], "correct": False, "score": 0.0, "source": source}
            candidates[answer]["correct"] = candidates[answer]["correct"] or bool(row["correct"])
            candidates[answer]["score"] += reciprocal_rank_score(int(row["rank"])) + float(row["support_frac"])
            if source == "target":
                candidates[answer]["score"] += 0.05
    return max(candidates.values(), key=lambda row: (row["score"], str(row["answer"])))


def eval_trial(target: list[dict], other: list[dict], k_values: list[int]) -> dict[str, dict]:
    if not target or not other:
        return {}
    out = {
        "target_cluster_sum": target[0],
        "other_cluster_sum": other[0],
    }
    for k in k_values:
        out[f"target_intersection_top{k}"] = choose_intersection(target, other, k)
        out[f"other_intersection_top{k}"] = choose_other_if_intersection(target, other, k)
        out[f"union_rank_top{k}"] = choose_union_rank(target, other, k)
    return out


def percentile(vals: list[float], p: float) -> float:
    vals = sorted(vals)
    if not vals:
        return 0.0
    idx = round((len(vals) - 1) * p)
    return float(vals[max(0, min(len(vals) - 1, idx))])


def bootstrap_delta(rows: list[dict], policy: str, rounds: int, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    by_problem: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_problem[str(row["pid"])].append(row)
    pids = list(by_problem)
    draws = []
    for _ in range(rounds):
        sample = []
        for _ in pids:
            sample.extend(by_problem[rng.choice(pids)])
        baseline = sum(float(row["target_cluster_sum"]) for row in sample) / max(1, len(sample))
        acc = sum(float(row[policy]) for row in sample) / max(1, len(sample))
        draws.append(acc - baseline)
    return percentile(draws, 0.025), percentile(draws, 0.975)


def build_trial_rows(target_label: str, other_label: str, target_data: list[dict], other_data: list[dict], seed: int, args: argparse.Namespace) -> list[dict]:
    train_ids, test_ids = split_ids(len(target_data), args.verifier_train_problems, args.audit_holdout_gap, seed)
    print(f"{target_label}: training/scoring target verifier", flush=True)
    target_scored = score_problem_samples(target_data, test_ids, train_ids, args, seed)["by_pid"]
    print(f"{other_label}: training/scoring other verifier", flush=True)
    other_scored = score_problem_samples(other_data, test_ids, train_ids, args, seed + 17)["by_pid"]

    rng = random.Random(seed + 1009)
    rows = []
    for pid in test_ids:
        for trial in range(args.trials_per_problem):
            target_idxs = rng.sample(range(len(target_data[pid]["samples"])), args.n)
            other_idxs = rng.sample(range(len(other_data[pid]["samples"])), args.n)
            target_clusters = clusters_from_indices(target_scored[pid], target_idxs)
            other_clusters = clusters_from_indices(other_scored[pid], other_idxs)
            choices = eval_trial(target_clusters, other_clusters, [int(x) for x in args.k_values.split(",") if x.strip()])
            if not choices:
                continue
            row = {"target": target_label, "other": other_label, "seed": seed, "pid": pid, "trial": trial}
            baseline_correct = bool(choices["target_cluster_sum"]["correct"])
            row["target_cluster_sum"] = baseline_correct
            for name, choice in choices.items():
                row[name] = bool(choice["correct"])
                row[f"{name}_answer"] = choice.get("answer")
            row["target_any_correct"] = any(bool(c["correct"]) for c in target_clusters)
            row["other_any_correct"] = any(bool(c["correct"]) for c in other_clusters)
            target_answers = set(by_answer(target_clusters))
            other_answers = set(by_answer(other_clusters))
            row["top20_answer_overlap"] = len(set(list(target_answers)[:20]) & set(list(other_answers)[:20]))
            rows.append(row)
    return rows


def summarize(rows: list[dict], args: argparse.Namespace) -> list[dict]:
    policies = [
        key
        for key, value in rows[0].items()
        if isinstance(value, bool)
        and (key in {"target_cluster_sum", "other_cluster_sum"} or key.startswith(("target_intersection_", "other_intersection_", "union_rank_")))
    ]
    out = []
    grouped: dict[tuple[str, str, int], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["target"], row["other"], int(row["seed"]))].append(row)
    for (target, other, seed), vals in sorted(grouped.items()):
        baseline = sum(float(row["target_cluster_sum"]) for row in vals) / max(1, len(vals))
        target_any = sum(float(row["target_any_correct"]) for row in vals) / max(1, len(vals))
        other_any = sum(float(row["other_any_correct"]) for row in vals) / max(1, len(vals))
        for policy in policies:
            acc = sum(float(row[policy]) for row in vals) / max(1, len(vals))
            recoveries = sum((not row["target_cluster_sum"]) and row[policy] for row in vals)
            regressions = sum(row["target_cluster_sum"] and not row[policy] for row in vals)
            ci_low, ci_high = bootstrap_delta(vals, policy, args.bootstrap_rounds, seed + 9001)
            out.append(
                {
                    "target": target,
                    "other": other,
                    "seed": seed,
                    "policy": policy,
                    "trials": len(vals),
                    "problems": len({row["pid"] for row in vals}),
                    "target_cluster_sum": baseline,
                    "target_any_correct": target_any,
                    "other_any_correct": other_any,
                    "policy_acc": acc,
                    "delta": acc - baseline,
                    "delta_ci_low": ci_low,
                    "delta_ci_high": ci_high,
                    "recoveries": recoveries,
                    "regressions": regressions,
                    "baseline_correct_trials": sum(row["target_cluster_sum"] for row in vals),
                }
            )
    return out


def aggregate_over_seeds(summary: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in summary:
        grouped[(row["target"], row["other"], row["policy"])].append(row)
    out = []
    for (target, other, policy), vals in sorted(grouped.items()):
        deltas = [float(row["delta"]) for row in vals]
        out.append(
            {
                "target": target,
                "other": other,
                "policy": policy,
                "seeds": len(vals),
                "mean_delta": sum(deltas) / len(deltas),
                "min_delta": min(deltas),
                "max_delta": max(deltas),
                "positive_seeds": sum(d > 0 for d in deltas),
                "clean_seeds": sum(int(row["regressions"]) == 0 for row in vals),
                "mean_policy_acc": sum(float(row["policy_acc"]) for row in vals) / len(vals),
                "mean_target_cluster_sum": sum(float(row["target_cluster_sum"]) for row in vals) / len(vals),
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


def write_outputs(summary: list[dict], aggregate: list[dict], args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary_path = OUT / f"{args.output_prefix}.csv"
    aggregate_path = OUT / f"{args.output_prefix}_aggregate.csv"
    md_path = OUT / f"{args.output_prefix}.md"
    write_csv(summary_path, summary)
    write_csv(aggregate_path, aggregate)

    best = sorted(aggregate, key=lambda row: (float(row["mean_delta"]), -int(row["total_regressions"])), reverse=True)[:12]
    clean = [row for row in aggregate if int(row["total_regressions"]) == 0]
    best_clean = sorted(clean, key=lambda row: float(row["mean_delta"]), reverse=True)[:8]
    lines = [
        "# Cross-Generator Agreement Audit",
        "",
        "This tests whether a second generator trace is useful as a verifier-like signal. Policies either rerank target clusters that also appear in the other generator, choose the other generator's top answer, or form a simple rank/support union over both top-k answer frontiers.",
        "",
        f"Config: `N={args.n}`, trials/problem `{args.trials_per_problem}`, seeds `{args.seeds}`, bootstrap rounds `{args.bootstrap_rounds}`.",
        "",
        "## Best Mean Deltas",
        "",
        "| target | other | policy | seeds | mean delta | min/max | positive seeds | recoveries | regressions |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in best:
        lines.append(
            f"| {row['target']} | {row['other']} | {row['policy']} | {row['seeds']} | {fmt(float(row['mean_delta']))} | "
            f"{fmt(float(row['min_delta']))}/{fmt(float(row['max_delta']))} | {row['positive_seeds']}/{row['seeds']} | "
            f"{row['total_recoveries']} | {row['total_regressions']} |"
        )
    lines += [
        "",
        "## Best No-Regression Rows",
        "",
        "| target | other | policy | seeds | mean delta | positive seeds | recoveries |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in best_clean:
        lines.append(
            f"| {row['target']} | {row['other']} | {row['policy']} | {row['seeds']} | {fmt(float(row['mean_delta']))} | "
            f"{row['positive_seeds']}/{row['seeds']} | {row['total_recoveries']} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "A positive, low-regression row would mean cross-generator agreement is a plausible cheap evidence source before invoking a stronger verifier. A regression-heavy row means agreement is not calibrated enough to replace the baseline selector, but still may expose oracle headroom.",
        "",
        f"Per-seed CSV: [{summary_path.name}]({summary_path.name}). Aggregate CSV: [{aggregate_path.name}]({aggregate_path.name}).",
    ]
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(summary_path)
    print(aggregate_path)
    print(md_path.read_text())


def run(args: argparse.Namespace) -> None:
    llama = load_data(Path(args.llama))
    gemma = load_data(Path(args.gemma))
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    rows = []
    for seed in seeds:
        print(f"seed {seed}: Llama target / Gemma other", flush=True)
        rows.extend(build_trial_rows("MATH/Llama", "MATH/Gemma", llama, gemma, seed, args))
        print(f"seed {seed}: Gemma target / Llama other", flush=True)
        rows.extend(build_trial_rows("MATH/Gemma", "MATH/Llama", gemma, llama, seed, args))
    summary = summarize(rows, args)
    aggregate = aggregate_over_seeds(summary)
    write_outputs(summary, aggregate, args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--llama", default=str(ROOT / "work" / "MATH_Llama-3-8B-Instruct.json"))
    parser.add_argument("--gemma", default=str(ROOT / "work" / "MATH_Gemma-2B.json"))
    parser.add_argument("--n", type=int, default=128)
    parser.add_argument("--trials-per-problem", type=int, default=8)
    parser.add_argument("--k-values", default="3,5,10,20")
    parser.add_argument("--seeds", default="60601,60602,60603")
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--audit-holdout-gap", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--bootstrap-rounds", type=int, default=250)
    parser.add_argument("--output-prefix", default="cross_generator_agreement_v108")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
