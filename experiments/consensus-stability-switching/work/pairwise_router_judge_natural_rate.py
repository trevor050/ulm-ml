#!/usr/bin/env python3
"""Natural-rate scoring for pairwise-gated auxiliary-generator routing."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_module(name: str, relpath: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


PROMPTS = load_module("make_pairwise_router_judge_prompts", "work/make_pairwise_router_judge_prompts.py")
CAL = load_module("pairwise_router_judge_calibration", "work/pairwise_router_judge_calibration.py")
V113 = PROMPTS.V113


def load_manifest(path: Path) -> dict[str, dict]:
    with path.open() as f:
        rows = {}
        for row in csv.DictReader(f):
            row["seed"] = int(row["seed"])
            row["pid"] = int(row["pid"])
            row["trial"] = int(row["trial"])
            row["baseline_correct"] = str(row["baseline_correct"]).lower() == "true"
            row["policy_correct"] = str(row["policy_correct"]).lower() == "true"
            rows[row["packet_id"]] = row
        return rows


def load_answer_rows(path: Path, policies: set[str], target: str, other: str) -> list[dict]:
    return PROMPTS.load_answer_rows(path, policies, target, other)


def prediction_paths(args: argparse.Namespace) -> dict[str, Path]:
    return {"mathstral": args.mathstral, "qwen14b": args.qwen14b, "gemma4": args.gemma4}


def accepted_key(row: dict) -> tuple[int, int, int, str]:
    return (int(row["seed"]), int(row["pid"]), int(row["trial"]), str(row["policy"]))


def build_packet_lookup(manifest: dict[str, dict]) -> dict[tuple[int, int, int, str], str]:
    out = {}
    for packet_id, row in manifest.items():
        key = accepted_key(row)
        if key in out:
            raise ValueError(f"duplicate manifest action key: {key}")
        out[key] = packet_id
    return out


def choose_pairwise_rules(
    rows: list[dict],
    budgets: list[int],
    models: list[str],
    rules: list[str],
    test_pids_by_seed: dict[int, set[int]],
) -> list[dict]:
    seeds = sorted(test_pids_by_seed)
    out = []
    for heldout_seed in seeds:
        test_pids = test_pids_by_seed[heldout_seed]
        source_rows = [row for row in rows if int(row["seed"]) != heldout_seed and int(row["pid"]) not in test_pids]
        for budget in budgets:
            model, rule, source_counts = CAL.choose_rule(source_rows, models, rules, budget)
            out.append(
                {
                    "heldout_seed": heldout_seed,
                    "regression_budget": budget,
                    "selected_model": model,
                    "selected_rule": rule,
                    "source_rows": len(source_rows),
                    "source_recoveries": source_counts["recoveries"],
                    "source_regressions": source_counts["regressions"],
                }
            )
    return out


def natural_fold_rows(
    answer_rows: list[dict],
    heldout_seed: int,
    score_mode: str,
    router_budget: int,
    args: argparse.Namespace,
) -> list[dict]:
    prepared = PROMPTS.V118.prepare_problem_disjoint(answer_rows, heldout_seed, score_mode, args)
    threshold, _selector_counts = V113.choose_threshold(prepared["train_rows"], prepared["train_scores"], router_budget)
    return V113.apply_threshold(prepared["test_rows"], prepared["test_scores"], threshold)


def summarize(eval_rows: list[dict], model: str, rule: str, packet_lookup: dict, merged_by_packet: dict) -> dict:
    baseline_correct = 0
    raw_correct = 0
    pairwise_correct = 0
    raw_accepts = raw_recoveries = raw_regressions = 0
    pairwise_accepts = pairwise_recoveries = pairwise_regressions = 0
    detail_rows = []
    for row in eval_rows:
        baseline = bool(row["baseline_correct"])
        raw = bool(row["gated_correct"])
        baseline_correct += int(baseline)
        raw_correct += int(raw)
        pairwise = baseline
        judge_accept = False
        packet_id = ""
        judge_choice = "NOT_ROUTED"
        if row["accept"]:
            raw_accepts += 1
            raw_recoveries += int((not baseline) and raw)
            raw_regressions += int(baseline and not raw)
            packet_id = packet_lookup.get((int(row["seed"]), int(row["pid"]), int(row["trial"]), str(row["policy"])), "")
            if not packet_id:
                raise KeyError(f"missing pairwise packet for accepted action: {row}")
            pairwise_row = merged_by_packet[packet_id]
            judge_choice = pairwise_row[f"{model}_choice"]
            judge_accept = CAL.accepted(pairwise_row, model, rule)
            if judge_accept:
                pairwise = raw
                pairwise_accepts += 1
                pairwise_recoveries += int((not baseline) and pairwise)
                pairwise_regressions += int(baseline and not pairwise)
        pairwise_correct += int(pairwise)
        detail_rows.append(
            {
                "target": row["target"],
                "other": row["other"],
                "seed": int(row["seed"]),
                "pid": int(row["pid"]),
                "trial": int(row["trial"]),
                "baseline_correct": baseline,
                "raw_router_correct": raw,
                "pairwise_gated_correct": pairwise,
                "raw_accept": bool(row["accept"]),
                "pairwise_accept": judge_accept,
                "policy": row["policy"],
                "packet_id": packet_id,
                "judge_model": model,
                "judge_rule": rule,
                "judge_choice": judge_choice,
            }
        )
    total = len(eval_rows)
    return {
        "counts": {
            "trials": total,
            "baseline_acc": baseline_correct / max(1, total),
            "raw_router_acc": raw_correct / max(1, total),
            "raw_router_delta": (raw_correct - baseline_correct) / max(1, total),
            "pairwise_gated_acc": pairwise_correct / max(1, total),
            "pairwise_gated_delta": (pairwise_correct - baseline_correct) / max(1, total),
            "delta_vs_raw_router": (pairwise_correct - raw_correct) / max(1, total),
            "raw_accepts": raw_accepts,
            "raw_recoveries": raw_recoveries,
            "raw_regressions": raw_regressions,
            "pairwise_accepts": pairwise_accepts,
            "pairwise_recoveries": pairwise_recoveries,
            "pairwise_regressions": pairwise_regressions,
            "recovery_retention": pairwise_recoveries / max(1, raw_recoveries),
            "regression_retention": pairwise_regressions / max(1, raw_regressions),
        },
        "details": detail_rows,
    }


def percentile(vals: list[float], p: float) -> float:
    vals = sorted(vals)
    if not vals:
        return 0.0
    idx = round((len(vals) - 1) * p)
    return vals[max(0, min(len(vals) - 1, idx))]


def bootstrap_ci(rows: list[dict], column: str, rounds: int, seed: int) -> tuple[float, float]:
    by_problem: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in rows:
        by_problem[(int(row["seed"]), int(row["pid"]))].append(row)
    keys = list(by_problem)
    rng = random.Random(seed)
    vals = []
    for _ in range(rounds):
        sample = []
        for _ in keys:
            sample.extend(by_problem[rng.choice(keys)])
        baseline = sum(row["baseline_correct"] for row in sample) / max(1, len(sample))
        gated = sum(row[column] for row in sample) / max(1, len(sample))
        vals.append(gated - baseline)
    return percentile(vals, 0.025), percentile(vals, 0.975)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--answer-rows", type=Path, default=OUT / "cross_seed_router_symbolic_guard_v118_answer_rows.jsonl")
    parser.add_argument("--manifest", type=Path, default=OUT / "pairwise_router_judge_v120_budget0_all_manifest.csv")
    parser.add_argument("--mathstral", type=Path, default=OUT / "mathstral_pairwise_router_judge_v120_budget0_all_predictions.jsonl")
    parser.add_argument("--qwen14b", type=Path, default=OUT / "qwen14b_pairwise_router_judge_v120_budget0_all_predictions.jsonl")
    parser.add_argument("--gemma4", type=Path, default=OUT / "gemma4_pairwise_router_judge_v120_budget0_all_predictions.jsonl")
    parser.add_argument("--output-prefix", default="pairwise_router_judge_natural_rate_v122")
    parser.add_argument("--router-score-mode", default="base_utility")
    parser.add_argument("--router-regression-budget", type=int, default=0)
    parser.add_argument("--pairwise-regression-budgets", default="0,1,2,5")
    parser.add_argument("--rules", default="never,B,B_or_BOTH")
    parser.add_argument("--policies", default="target_intersection_top10,target_intersection_top20,union_rank_top3")
    parser.add_argument("--target", default="MATH/Gemma")
    parser.add_argument("--other", default="MATH/Llama")
    parser.add_argument("--seeds", default="60601,60602,60603")
    parser.add_argument("--min-fit-examples", type=int, default=16)
    parser.add_argument("--bootstrap-rounds", type=int, default=5000)
    args = parser.parse_args()

    policies = {policy.strip() for policy in args.policies.split(",") if policy.strip()}
    answer_rows = load_answer_rows(args.answer_rows, policies, args.target, args.other)
    manifest = load_manifest(args.manifest)
    packet_lookup = build_packet_lookup(manifest)
    merged = CAL.merged_rows(manifest, prediction_paths(args))
    merged_by_packet = {row["packet_id"]: row for row in merged}
    models = ["mathstral", "qwen14b", "gemma4"]
    rules = [rule.strip() for rule in args.rules.split(",") if rule.strip()]
    budgets = [int(val) for val in args.pairwise_regression_budgets.split(",") if val.strip()]
    natural_by_seed = {
        seed: natural_fold_rows(answer_rows, seed, args.router_score_mode, args.router_regression_budget, args)
        for seed in sorted({int(row["seed"]) for row in answer_rows})
    }
    test_pids_by_seed = {seed: {int(row["pid"]) for row in fold_rows} for seed, fold_rows in natural_by_seed.items()}
    rule_rows = choose_pairwise_rules(merged, budgets, models, rules, test_pids_by_seed)
    summaries = []
    detail_rows = []
    for rule_row in rule_rows:
        seed = int(rule_row["heldout_seed"])
        scored = summarize(
            natural_by_seed[seed],
            rule_row["selected_model"],
            rule_row["selected_rule"],
            packet_lookup,
            merged_by_packet,
        )
        counts = scored["counts"]
        summaries.append({**rule_row, **counts})
        for row in scored["details"]:
            detail_rows.append({**rule_row, "regression_budget": rule_row["regression_budget"], **row})

    aggregate = []
    for budget in budgets:
        rows = [row for row in summaries if int(row["regression_budget"]) == budget]
        details = [row for row in detail_rows if int(row["regression_budget"]) == budget]
        raw_ci = bootstrap_ci(details, "raw_router_correct", args.bootstrap_rounds, 60622 + budget)
        pairwise_ci = bootstrap_ci(details, "pairwise_gated_correct", args.bootstrap_rounds, 60722 + budget)
        trials = sum(int(row["trials"]) for row in rows)
        baseline_correct = sum(float(row["baseline_acc"]) * int(row["trials"]) for row in rows)
        raw_correct = sum(float(row["raw_router_acc"]) * int(row["trials"]) for row in rows)
        pairwise_correct = sum(float(row["pairwise_gated_acc"]) * int(row["trials"]) for row in rows)
        aggregate.append(
            {
                "regression_budget": budget,
                "folds": len(rows),
                "trials": trials,
                "baseline_acc": baseline_correct / max(1, trials),
                "raw_router_acc": raw_correct / max(1, trials),
                "raw_router_delta": (raw_correct - baseline_correct) / max(1, trials),
                "raw_router_delta_ci95": f"[{raw_ci[0]:+.3f}, {raw_ci[1]:+.3f}]",
                "pairwise_gated_acc": pairwise_correct / max(1, trials),
                "pairwise_gated_delta": (pairwise_correct - baseline_correct) / max(1, trials),
                "pairwise_gated_delta_ci95": f"[{pairwise_ci[0]:+.3f}, {pairwise_ci[1]:+.3f}]",
                "delta_vs_raw_router": (pairwise_correct - raw_correct) / max(1, trials),
                "raw_accepts": sum(int(row["raw_accepts"]) for row in rows),
                "raw_recoveries": sum(int(row["raw_recoveries"]) for row in rows),
                "raw_regressions": sum(int(row["raw_regressions"]) for row in rows),
                "pairwise_accepts": sum(int(row["pairwise_accepts"]) for row in rows),
                "pairwise_recoveries": sum(int(row["pairwise_recoveries"]) for row in rows),
                "pairwise_regressions": sum(int(row["pairwise_regressions"]) for row in rows),
                "recovery_retention": sum(int(row["pairwise_recoveries"]) for row in rows) / max(1, sum(int(row["raw_recoveries"]) for row in rows)),
                "regression_retention": sum(int(row["pairwise_regressions"]) for row in rows) / max(1, sum(int(row["raw_regressions"]) for row in rows)),
                "selected": "; ".join(f"{row['heldout_seed']}:{row['selected_model']}/{row['selected_rule']}" for row in rows),
            }
        )

    out_prefix = OUT / args.output_prefix
    write_csv(out_prefix.with_suffix(".csv"), summaries)
    write_csv(OUT / f"{args.output_prefix}_aggregate.csv", aggregate)
    write_csv(OUT / f"{args.output_prefix}_details.csv", detail_rows)
    md = OUT / f"{args.output_prefix}.md"
    lines = [
        "# Pairwise Router-Judge Natural-Rate Scoring",
        "",
        "This natural-rate audit takes the full held-out trial denominator. The raw router first chooses an auxiliary-generator action exactly as in v120/v123. The pairwise judge then either accepts that action or falls back to the baseline selector. Source rule selection excludes every problem id in the held-out seed, including problems where the raw router proposes no switch.",
        "",
        f"Router score: `{args.router_score_mode}`. Router source regression budget: `{args.router_regression_budget}`. Pairwise rules: `{args.rules}`.",
        "",
        "| pairwise source budget | trials | baseline | raw router delta | pairwise delta | raw rec/reg | pairwise rec/reg | rec kept | reg kept | selected |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in aggregate:
        lines.append(
            f"| {row['regression_budget']} | {row['trials']} | {row['baseline_acc']:.3f} | "
            f"{row['raw_router_delta']:+.3f} {row['raw_router_delta_ci95']} | "
            f"{row['pairwise_gated_delta']:+.3f} {row['pairwise_gated_delta_ci95']} | "
            f"{row['raw_recoveries']}/{row['raw_regressions']} | {row['pairwise_recoveries']}/{row['pairwise_regressions']} | "
            f"{row['recovery_retention']:.3f} | {row['regression_retention']:.3f} | {row['selected']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "The accepted-action v121 table is a stress test of whether local LLM judges can identify good router actions once the router proposes one. This natural-rate table is the deployable interpretation: it charges the judge against every held-out trial, including trials where the router never proposes a switch.",
            "",
            f"Per-fold CSV: [{args.output_prefix}.csv]({args.output_prefix}.csv). Aggregate CSV: [{args.output_prefix}_aggregate.csv]({args.output_prefix}_aggregate.csv). Trial details: [{args.output_prefix}_details.csv]({args.output_prefix}_details.csv).",
        ]
    )
    md.write_text("\n".join(lines))
    print(md)
    print(md.read_text())


if __name__ == "__main__":
    main()
