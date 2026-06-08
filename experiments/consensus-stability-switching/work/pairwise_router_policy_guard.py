#!/usr/bin/env python3
"""Policy-family guards for pairwise router-judge routing."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import itertools
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


NAT = load_module("pairwise_router_judge_natural_rate", "work/pairwise_router_judge_natural_rate.py")
PROMPTS = NAT.PROMPTS
CAL = NAT.CAL
V113 = NAT.V113


def policy_label(policies: set[str]) -> str:
    return "+".join(sorted(policies)) if policies else "none"


def parse_policies(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def policy_sets(policies: list[str]) -> list[set[str]]:
    out = []
    for size in range(1, len(policies) + 1):
        for combo in itertools.combinations(sorted(policies), size):
            out.append(set(combo))
    return out


def accepted(row: dict, model: str, rule: str, allowed_policies: set[str]) -> bool:
    if str(row.get("policy", "")) not in allowed_policies:
        return False
    return CAL.accepted(row, model, rule)


def counts(rows: list[dict], model: str, rule: str, allowed_policies: set[str]) -> dict:
    baseline_correct = sum(row["baseline_correct"] for row in rows)
    correct = accepts = recoveries = regressions = 0
    by_policy: dict[str, dict[str, int]] = defaultdict(lambda: {"accepts": 0, "recoveries": 0, "regressions": 0})
    for row in rows:
        accept = accepted(row, model, rule, allowed_policies)
        if accept:
            accepts += 1
            row_correct = row["policy_correct"]
            bucket = by_policy[str(row["policy"])]
            bucket["accepts"] += 1
            if (not row["baseline_correct"]) and row["policy_correct"]:
                recoveries += 1
                bucket["recoveries"] += 1
            if row["baseline_correct"] and (not row["policy_correct"]):
                regressions += 1
                bucket["regressions"] += 1
        else:
            row_correct = row["baseline_correct"]
        correct += int(row_correct)
    return {
        "rows": len(rows),
        "baseline_acc": baseline_correct / max(1, len(rows)),
        "gated_acc": correct / max(1, len(rows)),
        "gated_delta": (correct - baseline_correct) / max(1, len(rows)),
        "accepts": accepts,
        "recoveries": recoveries,
        "regressions": regressions,
        "by_policy": dict(by_policy),
    }


def choose_guard(
    source_rows: list[dict],
    models: list[str],
    rules: list[str],
    policies: list[str],
    budget: int,
) -> tuple[str, str, set[str], dict]:
    best_model = models[0]
    best_rule = "never"
    best_policies: set[str] = set()
    best_counts = counts(source_rows, best_model, "never", set())
    best_key = (best_counts["recoveries"], -best_counts["regressions"], -best_counts["accepts"], -len(best_policies), policy_label(best_policies))
    for model in models:
        for rule in rules:
            candidate_sets = [set()] if rule == "never" else policy_sets(policies)
            for allowed in candidate_sets:
                row_counts = counts(source_rows, model, rule, allowed)
                if row_counts["regressions"] > budget:
                    continue
                key = (row_counts["recoveries"], -row_counts["regressions"], -row_counts["accepts"], -len(allowed), policy_label(allowed))
                if key > best_key:
                    best_model = model
                    best_rule = rule
                    best_policies = set(allowed)
                    best_counts = row_counts
                    best_key = key
    return best_model, best_rule, best_policies, best_counts


def natural_fold_rows(answer_rows: list[dict], heldout_seed: int, score_mode: str, router_budget: int, args: argparse.Namespace) -> list[dict]:
    prepared = PROMPTS.V118.prepare_problem_disjoint(answer_rows, heldout_seed, score_mode, args)
    threshold, _selector_counts = V113.choose_threshold(prepared["train_rows"], prepared["train_scores"], router_budget)
    return V113.apply_threshold(prepared["test_rows"], prepared["test_scores"], threshold)


def summarize(eval_rows: list[dict], model: str, rule: str, allowed_policies: set[str], packet_lookup: dict, merged_by_packet: dict) -> dict:
    baseline_correct = raw_correct = guarded_correct = 0
    raw_accepts = raw_recoveries = raw_regressions = 0
    guarded_accepts = guarded_recoveries = guarded_regressions = 0
    details = []
    for row in eval_rows:
        baseline = bool(row["baseline_correct"])
        raw = bool(row["gated_correct"])
        guarded = baseline
        guard_accept = False
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
            guard_accept = accepted(pairwise_row, model, rule, allowed_policies)
            if guard_accept:
                guarded = raw
                guarded_accepts += 1
                guarded_recoveries += int((not baseline) and guarded)
                guarded_regressions += int(baseline and not guarded)
        baseline_correct += int(baseline)
        raw_correct += int(raw)
        guarded_correct += int(guarded)
        details.append(
            {
                "target": row["target"],
                "other": row["other"],
                "seed": int(row["seed"]),
                "pid": int(row["pid"]),
                "trial": int(row["trial"]),
                "baseline_correct": baseline,
                "raw_router_correct": raw,
                "guarded_correct": guarded,
                "raw_accept": bool(row["accept"]),
                "guarded_accept": guard_accept,
                "policy": row["policy"],
                "packet_id": packet_id,
                "judge_model": model,
                "judge_rule": rule,
                "judge_choice": judge_choice,
                "allowed_policies": policy_label(allowed_policies),
            }
        )
    total = len(eval_rows)
    return {
        "counts": {
            "trials": total,
            "baseline_acc": baseline_correct / max(1, total),
            "raw_router_acc": raw_correct / max(1, total),
            "raw_router_delta": (raw_correct - baseline_correct) / max(1, total),
            "guarded_acc": guarded_correct / max(1, total),
            "guarded_delta": (guarded_correct - baseline_correct) / max(1, total),
            "delta_vs_raw_router": (guarded_correct - raw_correct) / max(1, total),
            "raw_accepts": raw_accepts,
            "raw_recoveries": raw_recoveries,
            "raw_regressions": raw_regressions,
            "guarded_accepts": guarded_accepts,
            "guarded_recoveries": guarded_recoveries,
            "guarded_regressions": guarded_regressions,
            "recovery_retention": guarded_recoveries / max(1, raw_recoveries),
            "regression_retention": guarded_regressions / max(1, raw_regressions),
        },
        "details": details,
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
        guarded = sum(row[column] for row in sample) / max(1, len(sample))
        vals.append(guarded - baseline)
    return percentile(vals, 0.025), percentile(vals, 0.975)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def policy_breakdown(rows: list[dict]) -> str:
    buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"rec": 0, "reg": 0})
    for row in rows:
        policy = str(row["policy"])
        if row["guarded_accept"] and (not row["baseline_correct"]) and row["guarded_correct"]:
            buckets[policy]["rec"] += 1
        if row["guarded_accept"] and row["baseline_correct"] and (not row["guarded_correct"]):
            buckets[policy]["reg"] += 1
    return "; ".join(f"{policy}:{vals['rec']}/{vals['reg']}" for policy, vals in sorted(buckets.items())) or "-"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--answer-rows", type=Path, default=OUT / "cross_seed_answer_rows_gemma_with_llama_v125.jsonl")
    parser.add_argument("--manifest", type=Path, default=OUT / "pairwise_router_judge_v125_budget2_all_manifest.csv")
    parser.add_argument("--mathstral", type=Path, default=OUT / "mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl")
    parser.add_argument("--qwen14b", type=Path, default=OUT / "qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl")
    parser.add_argument("--gemma4", type=Path, default=OUT / "gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl")
    parser.add_argument("--output-prefix", default="pairwise_router_policy_guard_v129")
    parser.add_argument("--router-score-mode", default="base_utility")
    parser.add_argument("--router-regression-budget", type=int, default=2)
    parser.add_argument("--guard-regression-budgets", default="0,1,2,5")
    parser.add_argument("--rules", default="never,B,B_or_BOTH")
    parser.add_argument("--policies", default="target_intersection_top10,target_intersection_top20,union_rank_top3")
    parser.add_argument("--target", default="MATH/Gemma")
    parser.add_argument("--other", default="MATH/Llama")
    parser.add_argument("--seeds", default="60601,60602,60603")
    parser.add_argument("--min-fit-examples", type=int, default=16)
    parser.add_argument("--bootstrap-rounds", type=int, default=5000)
    args = parser.parse_args()

    policies = parse_policies(args.policies)
    answer_rows = NAT.load_answer_rows(args.answer_rows, set(policies), args.target, args.other)
    manifest = NAT.load_manifest(args.manifest)
    packet_lookup = NAT.build_packet_lookup(manifest)
    merged = CAL.merged_rows(manifest, {"mathstral": args.mathstral, "qwen14b": args.qwen14b, "gemma4": args.gemma4})
    merged_by_packet = {row["packet_id"]: row for row in merged}
    models = ["mathstral", "qwen14b", "gemma4"]
    rules = parse_policies(args.rules)
    budgets = [int(val) for val in args.guard_regression_budgets.split(",") if val.strip()]
    natural_by_seed = {
        seed: natural_fold_rows(answer_rows, seed, args.router_score_mode, args.router_regression_budget, args)
        for seed in sorted({int(row["seed"]) for row in answer_rows})
    }
    test_pids_by_seed = {seed: {int(row["pid"]) for row in rows} for seed, rows in natural_by_seed.items()}

    summaries = []
    detail_rows = []
    for heldout_seed, eval_rows in natural_by_seed.items():
        test_pids = test_pids_by_seed[heldout_seed]
        source_rows = [row for row in merged if int(row["seed"]) != heldout_seed and int(row["pid"]) not in test_pids]
        for budget in budgets:
            model, rule, allowed, source_counts = choose_guard(source_rows, models, rules, policies, budget)
            scored = summarize(eval_rows, model, rule, allowed, packet_lookup, merged_by_packet)
            counts_row = scored["counts"]
            summaries.append(
                {
                    "heldout_seed": heldout_seed,
                    "guard_regression_budget": budget,
                    "selected_model": model,
                    "selected_rule": rule,
                    "allowed_policies": policy_label(allowed),
                    "source_rows": len(source_rows),
                    "source_accepts": source_counts["accepts"],
                    "source_recoveries": source_counts["recoveries"],
                    "source_regressions": source_counts["regressions"],
                    **counts_row,
                }
            )
            for row in scored["details"]:
                detail_rows.append(
                    {
                        "heldout_seed": heldout_seed,
                        "guard_regression_budget": budget,
                        "selected_model": model,
                        "selected_rule": rule,
                        **row,
                    }
                )

    aggregate = []
    for budget in budgets:
        rows = [row for row in summaries if int(row["guard_regression_budget"]) == budget]
        details = [row for row in detail_rows if int(row["guard_regression_budget"]) == budget]
        ci = bootstrap_ci(details, "guarded_correct", args.bootstrap_rounds, 61027 + budget)
        raw_ci = bootstrap_ci(details, "raw_router_correct", args.bootstrap_rounds, 61127 + budget)
        trials = sum(int(row["trials"]) for row in rows)
        baseline_correct = sum(float(row["baseline_acc"]) * int(row["trials"]) for row in rows)
        raw_correct = sum(float(row["raw_router_acc"]) * int(row["trials"]) for row in rows)
        guarded_correct = sum(float(row["guarded_acc"]) * int(row["trials"]) for row in rows)
        aggregate.append(
            {
                "guard_regression_budget": budget,
                "folds": len(rows),
                "trials": trials,
                "baseline_acc": baseline_correct / max(1, trials),
                "raw_router_delta": (raw_correct - baseline_correct) / max(1, trials),
                "raw_router_delta_ci95": f"[{raw_ci[0]:+.3f}, {raw_ci[1]:+.3f}]",
                "guarded_delta": (guarded_correct - baseline_correct) / max(1, trials),
                "guarded_delta_ci95": f"[{ci[0]:+.3f}, {ci[1]:+.3f}]",
                "raw_recoveries": sum(int(row["raw_recoveries"]) for row in rows),
                "raw_regressions": sum(int(row["raw_regressions"]) for row in rows),
                "guarded_accepts": sum(int(row["guarded_accepts"]) for row in rows),
                "guarded_recoveries": sum(int(row["guarded_recoveries"]) for row in rows),
                "guarded_regressions": sum(int(row["guarded_regressions"]) for row in rows),
                "recovery_retention": sum(int(row["guarded_recoveries"]) for row in rows) / max(1, sum(int(row["raw_recoveries"]) for row in rows)),
                "regression_retention": sum(int(row["guarded_regressions"]) for row in rows) / max(1, sum(int(row["raw_regressions"]) for row in rows)),
                "selected": "; ".join(
                    f"{row['heldout_seed']}:{row['selected_model']}/{row['selected_rule']}/{row['allowed_policies']}"
                    for row in rows
                ),
                "policy_rec_reg": policy_breakdown(details),
            }
        )

    write_csv(OUT / f"{args.output_prefix}.csv", summaries)
    write_csv(OUT / f"{args.output_prefix}_aggregate.csv", aggregate)
    write_csv(OUT / f"{args.output_prefix}_details.csv", detail_rows)

    md = OUT / f"{args.output_prefix}.md"
    lines = [
        "# Pairwise Router-Judge Policy-Guard Audit",
        "",
        "This reruns the v125 natural-rate setup but lets source-disjoint calibration choose not only the judge model/rule, but also which routed policy families are allowed through. The candidate policy sets are all non-empty subsets of the routed policies, plus the no-op rule. This is a risk-control probe, not a final deployed policy.",
        "",
        f"Router source regression budget: `{args.router_regression_budget}`. Guard budgets: `{args.guard_regression_budgets}`. Policies: `{args.policies}`.",
        "",
        "| guard budget | trials | baseline | raw delta | guarded delta | raw rec/reg | guarded rec/reg | rec kept | reg kept | selected | policy rec/reg |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in aggregate:
        lines.append(
            f"| {row['guard_regression_budget']} | {row['trials']} | {row['baseline_acc']:.3f} | "
            f"{row['raw_router_delta']:+.3f} {row['raw_router_delta_ci95']} | "
            f"{row['guarded_delta']:+.3f} {row['guarded_delta_ci95']} | "
            f"{row['raw_recoveries']}/{row['raw_regressions']} | {row['guarded_recoveries']}/{row['guarded_regressions']} | "
            f"{row['recovery_retention']:.3f} | {row['regression_retention']:.3f} | {row['selected']} | {row['policy_rec_reg']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "The policy-family guard asks whether the extra budget2 recovery can be made less fragile by learning which upstream route families are worth trusting. Because the guard is selected from source problems only, a positive row is stronger than a post-hoc veto over the four observed regressions. A negative or flat row means the v125 budget1/budget2 tradeoff is probably the cleaner story.",
            "",
            f"Per-fold CSV: [{args.output_prefix}.csv]({args.output_prefix}.csv). Aggregate CSV: [{args.output_prefix}_aggregate.csv]({args.output_prefix}_aggregate.csv). Trial details: [{args.output_prefix}_details.csv]({args.output_prefix}_details.csv).",
        ]
    )
    md.write_text("\n".join(lines))
    print(md)
    print(md.read_text())


if __name__ == "__main__":
    main()
