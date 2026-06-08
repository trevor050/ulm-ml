#!/usr/bin/env python3
"""Permutation control for the cross-seed generator router."""

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


def load_router():
    spec = importlib.util.spec_from_file_location("cross_seed_generator_router", ROOT / "work" / "cross_seed_generator_router.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ROUTER = load_router()


def feature_vector(row: dict, mode: str) -> list[float]:
    return ROUTER.feature_vector(row, mode)


def load_rows(path: Path) -> list[dict]:
    return ROUTER.load_rows(path)


def trial_key(row: dict) -> tuple[str, str, int, int, int]:
    return ROUTER.trial_key(row)


def fit_placebo_logistic(rows: list[dict], feature_mode: str, min_fit_examples: int, fit_steps: int, label_key: str) -> dict | None:
    train = [row for row in rows if row["changed"] and int(row[label_key]) != 0]
    if len(train) < min_fit_examples or len({int(row[label_key]) for row in train}) < 2:
        return None
    x = np.array([feature_vector(row, feature_mode) for row in train], dtype=float)
    y = np.array([1.0 if int(row[label_key]) > 0 else 0.0 for row in train], dtype=float)
    pos = float(y.mean())
    weights = np.where(y > 0.5, 0.5 / max(pos, 1e-6), 0.5 / max(1 - pos, 1e-6))
    return ROUTER.MB.fit_logistic(x, y, steps=fit_steps, lr=0.08, l2=1e-2, weights=weights)


def fit_placebo_centroid(rows: list[dict], feature_mode: str, min_fit_examples: int, label_key: str) -> dict | None:
    train = [row for row in rows if row["changed"] and int(row[label_key]) != 0]
    if len(train) < min_fit_examples or len({int(row[label_key]) for row in train}) < 2:
        return None
    x = np.array([feature_vector(row, feature_mode) for row in train], dtype=float)
    y = np.array([1.0 if int(row[label_key]) > 0 else 0.0 for row in train], dtype=float)
    pos = x[y > 0.5].mean(axis=0)
    neg = x[y < 0.5].mean(axis=0)
    weights = pos - neg
    scale = np.linalg.norm(weights) or 1.0
    return {"weights": weights / scale, "bias": 0.0, "kind": "centroid"}


def score_rows(model: dict | None, rows: list[dict], feature_mode: str) -> list[float]:
    if model is not None and model.get("kind") == "centroid":
        x = np.array([feature_vector(row, feature_mode) for row in rows], dtype=float)
        logits = x @ np.array(model["weights"], dtype=float) + float(model["bias"])
        return list(map(float, 1.0 / (1.0 + np.exp(-logits))))
    return ROUTER.score_rows(model, rows, feature_mode)


def apply_threshold_true(rows: list[dict], scores: list[float], threshold: float | None) -> list[dict]:
    return ROUTER.apply_threshold(rows, scores, threshold)


def apply_threshold_labels(rows: list[dict], scores: list[float], threshold: float | None, label_key: str) -> list[dict]:
    grouped: dict[tuple[str, str, int, int, int], list[tuple[dict, float]]] = defaultdict(list)
    for row, score in zip(rows, scores, strict=True):
        grouped[trial_key(row)].append((row, float(score)))
    out = []
    for key, vals in sorted(grouped.items()):
        accepted = [(row, score) for row, score in vals if threshold is not None and row["changed"] and score >= threshold]
        if accepted:
            choice, score = max(accepted, key=lambda pair: (pair[1], str(pair[0]["policy"])))
            utility_label = int(choice[label_key])
            policy = choice["policy"]
        else:
            score = 0.0
            utility_label = 0
            policy = "baseline"
        out.append({"key": key, "utility_label": utility_label, "accept": bool(accepted), "policy": policy, "score": score})
    return out


def choose_threshold_by_label(rows: list[dict], scores: list[float], label_key: str) -> float | None:
    best_by_trial: dict[tuple[str, str, int, int, int], tuple[float, int]] = {}
    for row, score in zip(rows, scores, strict=True):
        if not row["changed"]:
            continue
        key = trial_key(row)
        score = float(score)
        if key not in best_by_trial or score > best_by_trial[key][0]:
            best_by_trial[key] = (score, int(row[label_key]))
    candidates = sorted(best_by_trial.values(), key=lambda item: item[0], reverse=True)
    best = None
    best_recoveries = -1
    recoveries = 0
    regressions = 0
    for threshold, label in candidates:
        recoveries += int(label > 0)
        regressions += int(label < 0)
        if regressions:
            continue
        if recoveries > best_recoveries:
            best = threshold
            best_recoveries = recoveries
    return best


def permute_train_labels(train_rows: list[dict], rng: random.Random) -> list[dict]:
    out = [dict(row) for row in train_rows]
    nonzero_idx = [i for i, row in enumerate(out) if row["changed"] and int(row["utility_label"]) != 0]
    labels = [int(out[i]["utility_label"]) for i in nonzero_idx]
    rng.shuffle(labels)
    for row in out:
        row["placebo_utility_label"] = 0
    for idx, label in zip(nonzero_idx, labels, strict=True):
        out[idx]["placebo_utility_label"] = label
    return out


def summarize_true(eval_rows: list[dict]) -> dict:
    baseline = sum(row["baseline_correct"] for row in eval_rows) / max(1, len(eval_rows))
    gated = sum(row["gated_correct"] for row in eval_rows) / max(1, len(eval_rows))
    return {
        "test_trials": len(eval_rows),
        "baseline_acc": baseline,
        "gated_acc": gated,
        "gated_delta": gated - baseline,
        "accepts": sum(row["accept"] for row in eval_rows),
        "recoveries": sum((not row["baseline_correct"]) and row["gated_correct"] for row in eval_rows),
        "regressions": sum(row["baseline_correct"] and not row["gated_correct"] for row in eval_rows),
    }


def evaluate_placebo(rows: list[dict], target: str, other: str, scope: str, heldout_seed: int, args: argparse.Namespace, rng: random.Random) -> dict:
    direction_rows = [row for row in rows if row["target"] == target and row["other"] == other]
    if scope != "pool_all":
        direction_rows = [row for row in direction_rows if row["policy"] == scope]
    train_rows = [row for row in direction_rows if row["seed"] != heldout_seed]
    test_rows = [row for row in direction_rows if row["seed"] == heldout_seed]
    permuted = permute_train_labels(train_rows, rng)
    if args.fit_mode == "centroid":
        model = fit_placebo_centroid(permuted, args.feature_mode, args.min_fit_examples, "placebo_utility_label")
    else:
        model = fit_placebo_logistic(permuted, args.feature_mode, args.min_fit_examples, args.fit_steps, "placebo_utility_label")
    train_scores = score_rows(model, permuted, args.feature_mode)
    threshold = choose_threshold_by_label(permuted, train_scores, "placebo_utility_label") if model is not None else None
    test_scores = score_rows(model, test_rows, args.feature_mode)
    eval_rows = apply_threshold_true(test_rows, test_scores, threshold)
    summary = summarize_true(eval_rows)
    summary.update(
        {
            "target": target,
            "other": other,
            "heldout_seed": heldout_seed,
            "scope": scope,
            "feature_mode": args.feature_mode,
            "fit_examples": len([row for row in permuted if row["changed"] and int(row["placebo_utility_label"]) != 0]),
            "threshold": "" if threshold is None else threshold,
        }
    )
    return summary


def aggregate_iteration(rows: list[dict], iteration: int) -> list[dict]:
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["target"], row["other"], row["scope"])].append(row)
    out = []
    for (target, other, scope), vals in sorted(groups.items()):
        out.append(
            {
                "iteration": iteration,
                "target": target,
                "other": other,
                "scope": scope,
                "heldout_seeds": len(vals),
                "mean_delta": sum(float(row["gated_delta"]) for row in vals) / len(vals),
                "total_accepts": sum(int(row["accepts"]) for row in vals),
                "total_recoveries": sum(int(row["recoveries"]) for row in vals),
                "total_regressions": sum(int(row["regressions"]) for row in vals),
            }
        )
    return out


def percentile(vals: list[float], p: float) -> float:
    vals = sorted(vals)
    if not vals:
        return 0.0
    idx = round((len(vals) - 1) * p)
    return float(vals[max(0, min(len(vals) - 1, idx))])


def load_observed(path: Path) -> dict[tuple[str, str, str], dict]:
    out = {}
    with path.open() as f:
        for row in csv.DictReader(f):
            out[(row["target"], row["other"], row["scope"])] = row
    return out


def summarize_placebos(placebo_agg: list[dict], observed: dict[tuple[str, str, str], dict]) -> list[dict]:
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in placebo_agg:
        groups[(row["target"], row["other"], row["scope"])].append(row)
    out = []
    for key, vals in sorted(groups.items()):
        deltas = [float(row["mean_delta"]) for row in vals]
        obs = observed.get(key, {})
        obs_delta = float(obs.get("mean_delta", 0.0))
        out.append(
            {
                "target": key[0],
                "other": key[1],
                "scope": key[2],
                "observed_delta": obs_delta,
                "placebo_mean": sum(deltas) / len(deltas),
                "placebo_p95": percentile(deltas, 0.95),
                "placebo_max": max(deltas),
                "placebo_ge_observed": sum(delta >= obs_delta for delta in deltas),
                "iterations": len(deltas),
                "empirical_p": (sum(delta >= obs_delta for delta in deltas) + 1) / (len(deltas) + 1),
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


def write_markdown(path: Path, args: argparse.Namespace, rows: list[dict]) -> None:
    ranked = sorted(rows, key=lambda row: (float(row["observed_delta"]), -float(row["empirical_p"])), reverse=True)
    lines = [
        "# Cross-Seed Router Placebo",
        "",
        "This permutes source-seed utility labels before fitting and thresholding the v110 router, then evaluates on true held-out outcomes.",
        "",
        f"Iterations: `{args.iterations}`. Input rows: `{args.rows}`. Observed aggregate: `{args.observed_aggregate}`.",
        "",
        "| target | other | scope | observed | placebo mean | placebo p95 | placebo max | >= obs | empirical p |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in ranked:
        lines.append(
            "| {target} | {other} | {scope} | {observed_delta:+.3f} | {placebo_mean:+.3f} | {placebo_p95:+.3f} | {placebo_max:+.3f} | {placebo_ge_observed}/{iterations} | {empirical_p:.3f} |".format(
                **{
                    **row,
                    "observed_delta": float(row["observed_delta"]),
                    "placebo_mean": float(row["placebo_mean"]),
                    "placebo_p95": float(row["placebo_p95"]),
                    "placebo_max": float(row["placebo_max"]),
                    "empirical_p": float(row["empirical_p"]),
                }
            )
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "If the v110 router is mostly threshold luck, label-permuted source fits should often match the observed held-out delta. If observed rows sit far above the placebo distribution, the source utility signal is doing real work.",
            "",
            f"Summary CSV: [{path.with_suffix('.csv').name}]({path.with_suffix('.csv').name}). Placebo aggregate CSV: [{path.stem}_placebo_iterations.csv]({path.stem}_placebo_iterations.csv).",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, default=OUT / "cross_generator_risk_gate_v109_details.jsonl")
    parser.add_argument("--observed-aggregate", type=Path, default=OUT / "cross_seed_generator_router_v110_aggregate.csv")
    parser.add_argument("--output-prefix", default="cross_seed_router_placebo_v111")
    parser.add_argument("--feature-mode", choices=["base", "with_direction"], default="base")
    parser.add_argument("--min-fit-examples", type=int, default=16)
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--fit-steps", type=int, default=250)
    parser.add_argument("--fit-mode", choices=["centroid", "logistic"], default="centroid")
    parser.add_argument("--seed", type=int, default=61110)
    parser.add_argument("--scopes", default="pool_all,union_rank_top3")
    args = parser.parse_args()

    rows = load_rows(args.rows)
    directions = sorted({(row["target"], row["other"]) for row in rows})
    seeds = sorted({row["seed"] for row in rows})
    scopes = [scope.strip() for scope in args.scopes.split(",") if scope.strip()]
    all_iteration_rows = []
    rng = random.Random(args.seed)
    for iteration in range(args.iterations):
        if iteration == 0 or (iteration + 1) % 25 == 0 or iteration + 1 == args.iterations:
            print(f"placebo iteration {iteration + 1}/{args.iterations}", flush=True)
        summaries = []
        for target, other in directions:
            for scope in scopes:
                for heldout_seed in seeds:
                    summaries.append(evaluate_placebo(rows, target, other, scope, heldout_seed, args, rng))
        all_iteration_rows.extend(aggregate_iteration(summaries, iteration))

    observed = load_observed(args.observed_aggregate)
    summary = summarize_placebos(all_iteration_rows, observed)
    out_md = OUT / f"{args.output_prefix}.md"
    write_csv(OUT / f"{args.output_prefix}.csv", summary)
    write_csv(OUT / f"{args.output_prefix}_placebo_iterations.csv", all_iteration_rows)
    write_markdown(out_md, args, summary)
    print(out_md)
    print(out_md.read_text())


if __name__ == "__main__":
    main()
