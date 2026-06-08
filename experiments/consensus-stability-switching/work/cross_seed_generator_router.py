#!/usr/bin/env python3
"""Cross-seed generator-choice router from v109 raw candidate rows."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import random
from collections import defaultdict
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


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                row["seed"] = int(row["seed"])
                row["pid"] = int(row["pid"])
                row["trial"] = int(row["trial"])
                row["changed"] = bool(row["changed"])
                row["baseline_correct"] = bool(row["baseline_correct"])
                row["policy_correct"] = bool(row["policy_correct"])
                row["utility_label"] = int(row["utility_label"])
                rows.append(row)
    return rows


def feature_vector(row: dict, mode: str) -> list[float]:
    feats = list(map(float, row["features"]))
    if mode == "with_direction":
        feats.extend(
            [
                1.0 if row["target"] == "MATH/Gemma" else 0.0,
                1.0 if row["target"] == "MATH/Llama" else 0.0,
            ]
        )
    return feats


def fit_logistic(rows: list[dict], feature_mode: str, min_fit_examples: int) -> dict | None:
    train = [row for row in rows if row["changed"] and row["utility_label"] != 0]
    if len(train) < min_fit_examples or len({row["utility_label"] for row in train}) < 2:
        return None
    x = np.array([feature_vector(row, feature_mode) for row in train], dtype=float)
    y = np.array([1.0 if row["utility_label"] > 0 else 0.0 for row in train], dtype=float)
    pos = float(y.mean())
    weights = np.where(y > 0.5, 0.5 / max(pos, 1e-6), 0.5 / max(1 - pos, 1e-6))
    return MB.fit_logistic(x, y, steps=900, lr=0.06, l2=1e-2, weights=weights)


def score_rows(model: dict | None, rows: list[dict], feature_mode: str) -> list[float]:
    if model is None:
        return [0.0 for _ in rows]
    x = np.array([feature_vector(row, feature_mode) for row in rows], dtype=float)
    return list(map(float, MB.predict_logistic(model, x)))


def trial_key(row: dict) -> tuple[str, str, int, int, int]:
    return (row["target"], row["other"], int(row["seed"]), int(row["pid"]), int(row["trial"]))


def apply_threshold(rows: list[dict], scores: list[float], threshold: float | None) -> list[dict]:
    grouped: dict[tuple[str, str, int, int, int], list[tuple[dict, float]]] = defaultdict(list)
    for row, score in zip(rows, scores, strict=True):
        grouped[trial_key(row)].append((row, float(score)))
    out = []
    for key, vals in sorted(grouped.items()):
        baseline_correct = bool(vals[0][0]["baseline_correct"])
        accepted = [(row, score) for row, score in vals if threshold is not None and row["changed"] and score >= threshold]
        if accepted:
            choice, score = max(accepted, key=lambda pair: (pair[1], str(pair[0]["policy"])))
            gated_correct = bool(choice["policy_correct"])
            policy = choice["policy"]
        else:
            score = 0.0
            gated_correct = baseline_correct
            policy = "baseline"
        out.append(
            {
                "target": key[0],
                "other": key[1],
                "seed": key[2],
                "pid": key[3],
                "trial": key[4],
                "baseline_correct": baseline_correct,
                "gated_correct": gated_correct,
                "accept": bool(accepted),
                "policy": policy,
                "score": score,
            }
        )
    return out


def choose_threshold(rows: list[dict], scores: list[float]) -> float | None:
    thresholds = sorted({score for row, score in zip(rows, scores, strict=True) if row["changed"]}, reverse=True)
    best = None
    best_recoveries = -1
    for threshold in thresholds:
        eval_rows = apply_threshold(rows, scores, threshold)
        regressions = sum(row["baseline_correct"] and not row["gated_correct"] for row in eval_rows)
        if regressions:
            continue
        recoveries = sum((not row["baseline_correct"]) and row["gated_correct"] for row in eval_rows)
        if recoveries > best_recoveries:
            best = threshold
            best_recoveries = recoveries
    return best


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


def summarize_eval(eval_rows: list[dict], args: argparse.Namespace, seed: int) -> dict:
    baseline = sum(row["baseline_correct"] for row in eval_rows) / max(1, len(eval_rows))
    gated = sum(row["gated_correct"] for row in eval_rows) / max(1, len(eval_rows))
    ci_low, ci_high = bootstrap_delta(eval_rows, args.bootstrap_rounds, seed)
    return {
        "test_trials": len(eval_rows),
        "baseline_acc": baseline,
        "gated_acc": gated,
        "gated_delta": gated - baseline,
        "delta_ci_low": ci_low,
        "delta_ci_high": ci_high,
        "accepts": sum(row["accept"] for row in eval_rows),
        "recoveries": sum((not row["baseline_correct"]) and row["gated_correct"] for row in eval_rows),
        "regressions": sum(row["baseline_correct"] and not row["gated_correct"] for row in eval_rows),
    }


def evaluate_scope(rows: list[dict], target: str, other: str, scope: str, heldout_seed: int, args: argparse.Namespace) -> tuple[dict, list[dict]]:
    direction_rows = [row for row in rows if row["target"] == target and row["other"] == other]
    if scope != "pool_all":
        direction_rows = [row for row in direction_rows if row["policy"] == scope]
    train_rows = [row for row in direction_rows if row["seed"] != heldout_seed]
    test_rows = [row for row in direction_rows if row["seed"] == heldout_seed]
    model = fit_logistic(train_rows, args.feature_mode, args.min_fit_examples)
    train_scores = score_rows(model, train_rows, args.feature_mode)
    threshold = choose_threshold(train_rows, train_scores) if model is not None else None
    test_scores = score_rows(model, test_rows, args.feature_mode)
    eval_rows = apply_threshold(test_rows, test_scores, threshold)
    summary = summarize_eval(eval_rows, args, heldout_seed + 9191)
    summary.update(
        {
            "target": target,
            "other": other,
            "heldout_seed": heldout_seed,
            "scope": scope,
            "feature_mode": args.feature_mode,
            "train_seeds": ",".join(map(str, sorted({row["seed"] for row in train_rows}))),
            "fit_examples": len([row for row in train_rows if row["changed"] and row["utility_label"] != 0]),
            "threshold": "" if threshold is None else threshold,
        }
    )
    for row in eval_rows:
        row["scope"] = scope
    return summary, eval_rows


def aggregate(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["target"], row["other"], row["scope"], row["feature_mode"])].append(row)
    out = []
    for (target, other, scope, feature_mode), vals in sorted(groups.items()):
        deltas = [float(row["gated_delta"]) for row in vals]
        out.append(
            {
                "target": target,
                "other": other,
                "scope": scope,
                "feature_mode": feature_mode,
                "heldout_seeds": len(vals),
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
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, args: argparse.Namespace, rows: list[dict], agg: list[dict]) -> None:
    ranked = sorted(agg, key=lambda row: (float(row["mean_delta"]), int(row["ci_positive_seeds"])), reverse=True)
    lines = [
        "# Cross-Seed Generator Router",
        "",
        "This trains a generator-choice accept model on two seeds, chooses a zero-source-regression threshold on those source seeds, and deploys on the held-out seed.",
        "",
        f"Input: `{args.rows}`. Feature mode: `{args.feature_mode}`. Min fit examples: `{args.min_fit_examples}`.",
        "",
        "| target | other | scope | mean delta | signs | CI+ seeds | accepts | recoveries | regressions |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in ranked[:18]:
        lines.append(
            "| {target} | {other} | {scope} | {mean_delta:+.3f} | {positive_seeds}/{heldout_seeds} | {ci_positive_seeds}/{heldout_seeds} | {total_accepts} | {total_recoveries} | {total_regressions} |".format(
                target=row["target"],
                other=row["other"],
                scope=row["scope"],
                mean_delta=float(row["mean_delta"]),
                positive_seeds=row["positive_seeds"],
                heldout_seeds=row["heldout_seeds"],
                ci_positive_seeds=row["ci_positive_seeds"],
                total_accepts=row["total_accepts"],
                total_recoveries=row["total_recoveries"],
                total_regressions=row["total_regressions"],
            )
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "A robust row must stay positive across held-out seeds after the threshold is chosen only from source seeds. If v109 was mostly same-seed threshold luck, these rows should collapse toward no-op or regression.",
            "",
            f"Summary CSV: [{path.with_suffix('.csv').name}]({path.with_suffix('.csv').name}). Aggregate CSV: [{path.stem}_aggregate.csv]({path.stem}_aggregate.csv). Details: [{path.stem}_details.jsonl]({path.stem}_details.jsonl).",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, default=OUT / "cross_generator_risk_gate_v109_details.jsonl")
    parser.add_argument("--output-prefix", default="cross_seed_generator_router_v110")
    parser.add_argument("--feature-mode", choices=["base", "with_direction"], default="base")
    parser.add_argument("--min-fit-examples", type=int, default=16)
    parser.add_argument("--bootstrap-rounds", type=int, default=250)
    parser.add_argument("--scopes", default="pool_all,target_intersection_top10,target_intersection_top20,union_rank_top3")
    args = parser.parse_args()

    rows = load_rows(args.rows)
    directions = sorted({(row["target"], row["other"]) for row in rows})
    seeds = sorted({row["seed"] for row in rows})
    scopes = [scope.strip() for scope in args.scopes.split(",") if scope.strip()]
    summaries = []
    details = []
    for target, other in directions:
        for scope in scopes:
            for seed in seeds:
                summary, eval_rows = evaluate_scope(rows, target, other, scope, seed, args)
                summaries.append(summary)
                details.extend(eval_rows)

    agg = aggregate(summaries)
    out_md = OUT / f"{args.output_prefix}.md"
    write_csv(OUT / f"{args.output_prefix}.csv", summaries)
    write_csv(OUT / f"{args.output_prefix}_aggregate.csv", agg)
    with (OUT / f"{args.output_prefix}_details.jsonl").open("w") as f:
        for row in details:
            f.write(json.dumps(row) + "\n")
    write_markdown(out_md, args, summaries, agg)
    print(out_md)
    print(out_md.read_text())


if __name__ == "__main__":
    main()
