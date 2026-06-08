#!/usr/bin/env python3
"""Risk-return frontier for cross-seed generator routers."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ROUTER = load_module("cross_seed_generator_router", ROOT / "work" / "cross_seed_generator_router.py")
HEURISTIC = load_module("cross_seed_router_heuristic_ablation", ROOT / "work" / "cross_seed_router_heuristic_ablation.py")


def zscore_from_train(train_scores: list[float], test_scores: list[float]) -> tuple[list[float], list[float]]:
    usable = [float(score) for score in train_scores if float(score) > -1e8]
    if not usable:
        return train_scores, test_scores
    mean = sum(usable) / len(usable)
    std = (sum((score - mean) ** 2 for score in usable) / len(usable)) ** 0.5 or 1.0
    return (
        [((float(score) - mean) / std) if float(score) > -1e8 else float(score) for score in train_scores],
        [((float(score) - mean) / std) if float(score) > -1e8 else float(score) for score in test_scores],
    )


def score_family(
    train_rows: list[dict],
    test_rows: list[dict],
    family: str,
    feature_mode: str,
    min_fit_examples: int,
) -> tuple[list[float], list[float]]:
    if family == "learned":
        model = ROUTER.fit_logistic(train_rows, feature_mode, min_fit_examples)
        return ROUTER.score_rows(model, train_rows, feature_mode), ROUTER.score_rows(model, test_rows, feature_mode)
    if family.startswith("heur_"):
        mode = family.removeprefix("heur_")
        return [HEURISTIC.score(row, mode) for row in train_rows], [HEURISTIC.score(row, mode) for row in test_rows]
    if family.startswith("combo_"):
        mode = family.removeprefix("combo_")
        model = ROUTER.fit_logistic(train_rows, feature_mode, min_fit_examples)
        learned_train, learned_test = zscore_from_train(
            ROUTER.score_rows(model, train_rows, feature_mode),
            ROUTER.score_rows(model, test_rows, feature_mode),
        )
        heuristic_train, heuristic_test = zscore_from_train(
            [HEURISTIC.score(row, mode) for row in train_rows],
            [HEURISTIC.score(row, mode) for row in test_rows],
        )
        return (
            [learned + heuristic for learned, heuristic in zip(learned_train, heuristic_train, strict=True)],
            [learned + heuristic for learned, heuristic in zip(learned_test, heuristic_test, strict=True)],
        )
    raise ValueError(f"unknown score family: {family}")


def choose_threshold(rows: list[dict], scores: list[float], source_regression_budget: int) -> tuple[float | None, dict]:
    best_by_trial: dict[tuple[str, str, int, int, int], tuple[float, int, str]] = {}
    for row, score in zip(rows, scores, strict=True):
        if not row["changed"]:
            continue
        key = ROUTER.trial_key(row)
        candidate = (float(score), int(row["utility_label"]), str(row["policy"]))
        if key not in best_by_trial or (candidate[0], candidate[2]) > (best_by_trial[key][0], best_by_trial[key][2]):
            best_by_trial[key] = candidate

    by_score: dict[float, list[tuple[int, str]]] = defaultdict(list)
    for score, label, policy in best_by_trial.values():
        by_score[float(score)].append((int(label), str(policy)))

    best_threshold = None
    best_key = (-1, -1, 0)
    recoveries = 0
    regressions = 0
    accepts = 0
    best_stats = {"source_accepts": 0, "source_recoveries": 0, "source_regressions": 0}
    for threshold in sorted(by_score, reverse=True):
        labels = by_score[threshold]
        accepts += len(labels)
        recoveries += sum(1 for label, _policy in labels if label > 0)
        regressions += sum(1 for label, _policy in labels if label < 0)
        if regressions > source_regression_budget:
            continue
        candidate_key = (recoveries, recoveries - regressions, -accepts)
        if candidate_key > best_key:
            best_key = candidate_key
            best_threshold = threshold
            best_stats = {
                "source_accepts": accepts,
                "source_recoveries": recoveries,
                "source_regressions": regressions,
            }
    return best_threshold, best_stats


def summarize_eval(eval_rows: list[dict], args: argparse.Namespace, seed: int) -> dict:
    summary = ROUTER.summarize_eval(eval_rows, args, seed)
    summary["accepted_policies"] = ",".join(sorted({row["policy"] for row in eval_rows if row["accept"]}))
    return summary


def evaluate(
    rows: list[dict],
    target: str,
    other: str,
    scope: str,
    family: str,
    source_regression_budget: int,
    heldout_seed: int,
    args: argparse.Namespace,
) -> tuple[dict, list[dict]]:
    direction_rows = [row for row in rows if row["target"] == target and row["other"] == other]
    if scope != "pool_all":
        direction_rows = [row for row in direction_rows if row["policy"] == scope]
    train_rows = [row for row in direction_rows if row["seed"] != heldout_seed]
    test_rows = [row for row in direction_rows if row["seed"] == heldout_seed]
    train_scores, test_scores = score_family(train_rows, test_rows, family, args.feature_mode, args.min_fit_examples)
    threshold, source_stats = choose_threshold(train_rows, train_scores, source_regression_budget)
    eval_rows = ROUTER.apply_threshold(test_rows, test_scores, threshold)
    summary = summarize_eval(eval_rows, args, heldout_seed + 17117 + source_regression_budget)
    summary.update(
        {
            "target": target,
            "other": other,
            "heldout_seed": heldout_seed,
            "scope": scope,
            "score_family": family,
            "source_regression_budget": source_regression_budget,
            "threshold": "" if threshold is None else threshold,
            "train_seeds": ",".join(map(str, sorted({row["seed"] for row in train_rows}))),
            **source_stats,
        }
    )
    for row in eval_rows:
        row["scope"] = scope
        row["score_family"] = family
        row["source_regression_budget"] = source_regression_budget
    return summary, eval_rows


def aggregate(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str, str, str, int], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["target"], row["other"], row["scope"], row["score_family"], int(row["source_regression_budget"]))].append(row)
    out = []
    for (target, other, scope, family, source_budget), vals in sorted(groups.items()):
        deltas = [float(row["gated_delta"]) for row in vals]
        out.append(
            {
                "target": target,
                "other": other,
                "scope": scope,
                "score_family": family,
                "source_regression_budget": source_budget,
                "heldout_seeds": len(vals),
                "mean_delta": sum(deltas) / len(deltas),
                "min_delta": min(deltas),
                "max_delta": max(deltas),
                "positive_seeds": sum(delta > 0 for delta in deltas),
                "ci_positive_seeds": sum(float(row["delta_ci_low"]) > 0 for row in vals),
                "total_accepts": sum(int(row["accepts"]) for row in vals),
                "total_recoveries": sum(int(row["recoveries"]) for row in vals),
                "total_regressions": sum(int(row["regressions"]) for row in vals),
                "total_source_accepts": sum(int(row["source_accepts"]) for row in vals),
                "total_source_recoveries": sum(int(row["source_recoveries"]) for row in vals),
                "total_source_regressions": sum(int(row["source_regressions"]) for row in vals),
            }
        )
    return out


def frontier(rows: list[dict]) -> list[dict]:
    out = []
    for target, other, scope in sorted({(row["target"], row["other"], row["scope"]) for row in rows}):
        vals = [row for row in rows if row["target"] == target and row["other"] == other and row["scope"] == scope]
        for max_regressions in [0, 1, 2, 4, 8, 16, 32, 64]:
            eligible = [row for row in vals if int(row["total_regressions"]) <= max_regressions]
            if not eligible:
                continue
            best = max(eligible, key=lambda row: (float(row["mean_delta"]), int(row["ci_positive_seeds"]), -int(row["total_regressions"])))
            out.append(
                {
                    "target": target,
                    "other": other,
                    "scope": scope,
                    "max_heldout_regressions": max_regressions,
                    "score_family": best["score_family"],
                    "source_regression_budget": best["source_regression_budget"],
                    "mean_delta": best["mean_delta"],
                    "min_delta": best["min_delta"],
                    "max_delta": best["max_delta"],
                    "positive_seeds": best["positive_seeds"],
                    "ci_positive_seeds": best["ci_positive_seeds"],
                    "total_accepts": best["total_accepts"],
                    "total_recoveries": best["total_recoveries"],
                    "total_regressions": best["total_regressions"],
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


def fmt(value: object) -> str:
    return f"{float(value):+.3f}"


def write_markdown(path: Path, args: argparse.Namespace, agg: list[dict], frontier_rows: list[dict]) -> None:
    gemma_frontier = [
        row for row in frontier_rows if row["target"] == "MATH/Gemma" and row["other"] == "MATH/Llama" and row["scope"] == "pool_all"
    ]
    ranked = sorted(
        [row for row in agg if row["target"] == "MATH/Gemma" and row["other"] == "MATH/Llama" and row["scope"] == "pool_all"],
        key=lambda row: (float(row["mean_delta"]), -int(row["total_regressions"])),
        reverse=True,
    )
    lines = [
        "# Cross-Seed Router Risk Frontier",
        "",
        "This extends v110/v112 by sweeping explicit source-regression budgets and combined learned-plus-heuristic scores under the same held-out-seed transfer protocol.",
        "",
        f"Input: `{args.rows}`. Feature mode: `{args.feature_mode}`. Source budgets: `{args.source_regression_budgets}`.",
        "",
        "## Gemma-with-Llama pool_all frontier",
        "",
        "| held-out regression cap | best score family | source budget | mean delta | signs | CI+ seeds | accepts | recoveries | regressions |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in gemma_frontier:
        lines.append(
            "| {cap} | {score_family} | {source_regression_budget} | {mean_delta} | {positive_seeds}/3 | {ci_positive_seeds}/3 | {total_accepts} | {total_recoveries} | {total_regressions} |".format(
                cap=row["max_heldout_regressions"],
                score_family=row["score_family"],
                source_regression_budget=row["source_regression_budget"],
                mean_delta=fmt(row["mean_delta"]),
                positive_seeds=row["positive_seeds"],
                ci_positive_seeds=row["ci_positive_seeds"],
                total_accepts=row["total_accepts"],
                total_recoveries=row["total_recoveries"],
                total_regressions=row["total_regressions"],
            )
        )
    lines.extend(
        [
            "",
            "## Top Gemma-with-Llama pool_all rows",
            "",
            "| score family | source budget | mean delta | signs | CI+ seeds | accepts | recoveries | regressions | source recoveries | source regressions |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in ranked[:18]:
        lines.append(
            "| {score_family} | {source_regression_budget} | {mean_delta} | {positive_seeds}/3 | {ci_positive_seeds}/3 | {total_accepts} | {total_recoveries} | {total_regressions} | {total_source_recoveries} | {total_source_regressions} |".format(
                score_family=row["score_family"],
                source_regression_budget=row["source_regression_budget"],
                mean_delta=fmt(row["mean_delta"]),
                positive_seeds=row["positive_seeds"],
                ci_positive_seeds=row["ci_positive_seeds"],
                total_accepts=row["total_accepts"],
                total_recoveries=row["total_recoveries"],
                total_regressions=row["total_regressions"],
                total_source_recoveries=row["total_source_recoveries"],
                total_source_regressions=row["total_source_regressions"],
            )
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "The strongest low-risk result is no longer the plain v110 learned score. A simple train-standardized sum of learned-router probability and auxiliary confidence/rank evidence improves the Gemma-with-Llama branch at the same held-out regression scale. The frontier is still asymmetric: Llama-with-Gemma remains flat.",
            "",
            "The held-out regression-cap rows are diagnostic summaries over the full sweep, not a deployable threshold-selection rule. The deployable part is the source-budget protocol: train on two seeds, choose the threshold by source-seed budget, then report held-out recoveries and regressions.",
            "",
            f"Summary CSV: [{path.with_suffix('.csv').name}]({path.with_suffix('.csv').name}). Aggregate CSV: [{path.stem}_aggregate.csv]({path.stem}_aggregate.csv). Frontier CSV: [{path.stem}_frontier.csv]({path.stem}_frontier.csv). Details: [{path.stem}_details.jsonl]({path.stem}_details.jsonl).",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, default=OUT / "cross_generator_risk_gate_v109_details.jsonl")
    parser.add_argument("--output-prefix", default="cross_seed_router_frontier_v113")
    parser.add_argument("--feature-mode", choices=["base", "with_direction"], default="base")
    parser.add_argument("--min-fit-examples", type=int, default=16)
    parser.add_argument("--bootstrap-rounds", type=int, default=250)
    parser.add_argument("--scopes", default="pool_all,union_rank_top3")
    parser.add_argument(
        "--score-families",
        default=(
            "learned,"
            "heur_other_conf,heur_other_rank,heur_other_support,heur_target_weak_other_conf,heur_margin_gap,heur_candidate_ratio_gap,heur_policy_prior,"
            "combo_other_conf,combo_other_rank,combo_other_support,combo_target_weak_other_conf,combo_margin_gap,combo_candidate_ratio_gap,combo_policy_prior"
        ),
    )
    parser.add_argument("--source-regression-budgets", default="0,1,2,4,8,16,32")
    args = parser.parse_args()

    rows = ROUTER.load_rows(args.rows)
    directions = sorted({(row["target"], row["other"]) for row in rows})
    seeds = sorted({row["seed"] for row in rows})
    scopes = [scope.strip() for scope in args.scopes.split(",") if scope.strip()]
    families = [family.strip() for family in args.score_families.split(",") if family.strip()]
    budgets = [int(budget) for budget in args.source_regression_budgets.split(",") if budget.strip()]

    summaries = []
    details = []
    for target, other in directions:
        for scope in scopes:
            for family in families:
                for budget in budgets:
                    for seed in seeds:
                        summary, eval_rows = evaluate(rows, target, other, scope, family, budget, seed, args)
                        summaries.append(summary)
                        details.extend(eval_rows)

    aggregate_rows = aggregate(summaries)
    frontier_rows = frontier(aggregate_rows)
    out_md = OUT / f"{args.output_prefix}.md"
    write_csv(OUT / f"{args.output_prefix}.csv", summaries)
    write_csv(OUT / f"{args.output_prefix}_aggregate.csv", aggregate_rows)
    write_csv(OUT / f"{args.output_prefix}_frontier.csv", frontier_rows)
    with (OUT / f"{args.output_prefix}_details.jsonl").open("w") as f:
        for row in details:
            f.write(json.dumps(row) + "\n")
    write_markdown(out_md, args, aggregate_rows, frontier_rows)
    print(out_md)
    print(out_md.read_text())


if __name__ == "__main__":
    main()
