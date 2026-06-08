#!/usr/bin/env python3
"""Guard sweeps for pairwise router-judge decisions.

This script reuses the v125 natural-rate pipeline, then asks whether simple
deployable guards can reduce judge-induced regressions without erasing the
pairwise recovery signal.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import pairwise_router_judge_natural_rate as NAT


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
MODELS = ["mathstral", "qwen14b", "gemma4"]
CANDIDATE_CHOICES = {"B", "BOTH"}


def other_choices(row: dict, selected_model: str) -> list[str]:
    return [row[f"{model}_choice"] for model in MODELS if model != selected_model]


def guard_permits(row: dict, selected_model: str, guard: str) -> bool:
    choices = other_choices(row, selected_model)
    all_choices = [row[f"{model}_choice"] for model in MODELS]
    if guard == "none":
        return True
    if guard == "other_candidate":
        return any(choice in CANDIDATE_CHOICES for choice in choices)
    if guard == "other_b":
        return any(choice == "B" for choice in choices)
    if guard == "union_other_candidate":
        return str(row["policy"]) != "union_rank_top3" or any(choice in CANDIDATE_CHOICES for choice in choices)
    if guard == "union_other_b":
        return str(row["policy"]) != "union_rank_top3" or any(choice == "B" for choice in choices)
    if guard == "qwen_union_other_candidate":
        if selected_model == "qwen14b" and str(row["policy"]) == "union_rank_top3":
            return any(choice in CANDIDATE_CHOICES for choice in choices)
        return True
    if guard == "qwen_union_other_b":
        if selected_model == "qwen14b" and str(row["policy"]) == "union_rank_top3":
            return any(choice == "B" for choice in choices)
        return True
    if guard == "two_b":
        return sum(choice == "B" for choice in all_choices) >= 2
    if guard == "all_candidate":
        return all(choice in CANDIDATE_CHOICES for choice in all_choices)
    if guard == "no_union":
        return str(row["policy"]) != "union_rank_top3"
    if guard == "no_qwen_union":
        return not (selected_model == "qwen14b" and str(row["policy"]) == "union_rank_top3")
    raise ValueError(guard)


def guarded_accept(row: dict, selected_model: str, selected_rule: str, guard: str) -> bool:
    return NAT.CAL.accepted(row, selected_model, selected_rule) and guard_permits(row, selected_model, guard)


def guarded_counts(rows: list[dict], selected_model: str, selected_rule: str, guard: str) -> dict:
    accepts = recoveries = regressions = 0
    for row in rows:
        accept = guarded_accept(row, selected_model, selected_rule, guard)
        accepts += int(accept)
        recoveries += int(accept and (not row["baseline_correct"]) and row["policy_correct"])
        regressions += int(accept and row["baseline_correct"] and (not row["policy_correct"]))
    return {"accepts": accepts, "recoveries": recoveries, "regressions": regressions}


def choose_guard(
    source_rows: list[dict],
    selected_model: str,
    selected_rule: str,
    guards: list[str],
    budget: int,
) -> tuple[str, dict]:
    best_guard = ""
    best_counts: dict | None = None
    best_key: tuple[int, int, int] | None = None
    for guard in guards:
        counts = guarded_counts(source_rows, selected_model, selected_rule, guard)
        if counts["regressions"] > budget:
            continue
        key = (counts["recoveries"], -counts["regressions"], -counts["accepts"])
        if best_key is None or key > best_key:
            best_guard = guard
            best_counts = counts
            best_key = key
    if best_counts is None:
        raise ValueError(f"no guard satisfies source regression budget {budget} for {selected_model}/{selected_rule}")
    return best_guard, best_counts


def summarize_fold(
    eval_rows: list[dict],
    selected_model: str,
    selected_rule: str,
    guard: str,
    packet_lookup: dict,
    merged_by_packet: dict,
) -> tuple[dict, list[dict]]:
    baseline_correct = raw_correct = guarded_correct = 0
    raw_accepts = raw_recoveries = raw_regressions = 0
    guarded_accepts = guarded_recoveries = guarded_regressions = 0
    details = []
    for row in eval_rows:
        baseline = bool(row["baseline_correct"])
        raw = bool(row["gated_correct"])
        baseline_correct += int(baseline)
        raw_correct += int(raw)
        guarded = baseline
        packet_id = ""
        judge_choice = "NOT_ROUTED"
        accepted = False
        if row["accept"]:
            raw_accepts += 1
            raw_recoveries += int((not baseline) and raw)
            raw_regressions += int(baseline and not raw)
            key = (int(row["seed"]), int(row["pid"]), int(row["trial"]), str(row["policy"]))
            packet_id = packet_lookup.get(key, "")
            if not packet_id:
                raise KeyError(f"missing pairwise packet for accepted action: {row}")
            pairwise_row = merged_by_packet[packet_id]
            judge_choice = pairwise_row[f"{selected_model}_choice"]
            accepted = guarded_accept(pairwise_row, selected_model, selected_rule, guard)
            if accepted:
                guarded = raw
                guarded_accepts += 1
                guarded_recoveries += int((not baseline) and guarded)
                guarded_regressions += int(baseline and not guarded)
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
                "guarded_accept": accepted,
                "policy": row["policy"],
                "packet_id": packet_id,
                "judge_model": selected_model,
                "judge_rule": selected_rule,
                "guard": guard,
                "judge_choice": judge_choice,
            }
        )
    total = len(eval_rows)
    counts = {
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
    }
    return counts, details


def aggregate(summary_rows: list[dict], detail_rows: list[dict], bootstrap_rounds: int) -> list[dict]:
    groups: dict[tuple[str, int, str], list[dict]] = defaultdict(list)
    for row in summary_rows:
        groups[(row["mode"], int(row["pairwise_budget"]), row["guard"])].append(row)
    details_by_key: dict[tuple[str, int, str], list[dict]] = defaultdict(list)
    for row in detail_rows:
        details_by_key[(row["mode"], int(row["pairwise_budget"]), row["guard"])].append(row)
    out = []
    for key, rows in sorted(groups.items()):
        mode, pairwise_budget, guard = key
        details = details_by_key[key]
        ci = NAT.bootstrap_ci(details, "guarded_correct", bootstrap_rounds, 61270 + pairwise_budget + len(guard))
        trials = sum(int(row["trials"]) for row in rows)
        baseline = sum(float(row["baseline_acc"]) * int(row["trials"]) for row in rows)
        raw = sum(float(row["raw_router_acc"]) * int(row["trials"]) for row in rows)
        guarded = sum(float(row["guarded_acc"]) * int(row["trials"]) for row in rows)
        out.append(
            {
                "mode": mode,
                "pairwise_budget": pairwise_budget,
                "guard": guard,
                "folds": len(rows),
                "trials": trials,
                "baseline_acc": baseline / max(1, trials),
                "raw_router_delta": (raw - baseline) / max(1, trials),
                "guarded_delta": (guarded - baseline) / max(1, trials),
                "guarded_delta_ci95": f"[{ci[0]:+.3f}, {ci[1]:+.3f}]",
                "delta_vs_raw_router": (guarded - raw) / max(1, trials),
                "raw_recoveries": sum(int(row["raw_recoveries"]) for row in rows),
                "raw_regressions": sum(int(row["raw_regressions"]) for row in rows),
                "guarded_accepts": sum(int(row["guarded_accepts"]) for row in rows),
                "guarded_recoveries": sum(int(row["guarded_recoveries"]) for row in rows),
                "guarded_regressions": sum(int(row["guarded_regressions"]) for row in rows),
                "selected": "; ".join(
                    f"{row['heldout_seed']}:{row['selected_model']}/{row['selected_rule']}/{row['selected_guard']}"
                    for row in rows
                ),
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
    preferred = [row for row in rows if row["mode"] == "source_selected_guard"]
    fixed = [
        row
        for row in rows
        if row["mode"] == "fixed_guard"
        and row["guard"] in {"none", "qwen_union_other_candidate", "two_b", "no_qwen_union", "no_union"}
    ]
    lines = [
        "# Pairwise Router-Judge Guard Sweep",
        "",
        "This audit stress-tests the v125/v126 higher-budget pairwise result with simple deployable guards. The guard sees only pairwise judge choices and the router policy name; it does not see correctness labels on the held-out fold.",
        "",
        f"Answer rows: `{args.answer_rows}`. Manifest: `{args.manifest}`.",
        "",
        "## Source-Selected Guard",
        "",
        "| pairwise budget | guard budget | delta | CI | rec/reg | accepts | selected |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in preferred:
        guard_budget = row["guard"].split("guard_budget_")[-1]
        lines.append(
            f"| {row['pairwise_budget']} | {guard_budget} | {row['guarded_delta']:+.3f} | {row['guarded_delta_ci95']} | "
            f"{row['guarded_recoveries']}/{row['guarded_regressions']} | {row['guarded_accepts']} | {row['selected']} |"
        )
    lines.extend(
        [
            "",
            "## Fixed Guards",
            "",
            "| pairwise budget | guard | delta | CI | rec/reg | accepts | selected |",
            "|---:|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in fixed:
        lines.append(
            f"| {row['pairwise_budget']} | `{row['guard']}` | {row['guarded_delta']:+.3f} | {row['guarded_delta_ci95']} | "
            f"{row['guarded_recoveries']}/{row['guarded_regressions']} | {row['guarded_accepts']} | {row['selected']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "`none` is the original v125 pairwise gate. `qwen_union_other_candidate` keeps qwen decisions except it requires another judge to also accept the candidate when the action is the riskier `union_rank_top3` policy. This is the cleanest non-oracle guard because v126 localized every budget-2 regression to qwen `B` on `union_rank_top3`.",
            "",
            f"Aggregate CSV: `{args.output_prefix}_aggregate.csv`. Per-fold CSV: `{args.output_prefix}.csv`. Trial details: `{args.output_prefix}_details.csv`.",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--answer-rows", type=Path, default=OUT / "cross_seed_answer_rows_gemma_with_llama_v125.jsonl")
    parser.add_argument("--manifest", type=Path, default=OUT / "pairwise_router_judge_v125_budget2_all_manifest.csv")
    parser.add_argument("--mathstral", type=Path, default=OUT / "mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl")
    parser.add_argument("--qwen14b", type=Path, default=OUT / "qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl")
    parser.add_argument("--gemma4", type=Path, default=OUT / "gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl")
    parser.add_argument("--output-prefix", default="pairwise_router_judge_guard_sweep_v127")
    parser.add_argument("--router-score-mode", default="base_utility")
    parser.add_argument("--router-regression-budget", type=int, default=2)
    parser.add_argument("--pairwise-regression-budgets", default="1,2")
    parser.add_argument("--guard-regression-budgets", default="0,1,2")
    parser.add_argument("--rules", default="never,B,B_or_BOTH")
    parser.add_argument("--policies", default="target_intersection_top10,target_intersection_top20,union_rank_top3")
    parser.add_argument("--target", default="MATH/Gemma")
    parser.add_argument("--other", default="MATH/Llama")
    parser.add_argument("--seeds", default="60601,60602,60603")
    parser.add_argument("--min-fit-examples", type=int, default=16)
    parser.add_argument("--bootstrap-rounds", type=int, default=5000)
    args = parser.parse_args()

    policies = {policy.strip() for policy in args.policies.split(",") if policy.strip()}
    answer_rows = NAT.load_answer_rows(args.answer_rows, policies, args.target, args.other)
    manifest = NAT.load_manifest(args.manifest)
    packet_lookup = NAT.build_packet_lookup(manifest)
    merged = NAT.CAL.merged_rows(manifest, NAT.prediction_paths(args))
    merged_by_packet = {row["packet_id"]: row for row in merged}
    rules = [rule.strip() for rule in args.rules.split(",") if rule.strip()]
    pairwise_budgets = [int(val) for val in args.pairwise_regression_budgets.split(",") if val.strip()]
    guard_budgets = [int(val) for val in args.guard_regression_budgets.split(",") if val.strip()]
    guards = [
        "none",
        "qwen_union_other_candidate",
        "qwen_union_other_b",
        "other_candidate",
        "other_b",
        "union_other_candidate",
        "union_other_b",
        "two_b",
        "all_candidate",
        "no_qwen_union",
        "no_union",
    ]
    natural_by_seed = {
        seed: NAT.natural_fold_rows(answer_rows, seed, args.router_score_mode, args.router_regression_budget, args)
        for seed in sorted({int(row["seed"]) for row in answer_rows})
    }
    test_pids_by_seed = {seed: {int(row["pid"]) for row in fold_rows} for seed, fold_rows in natural_by_seed.items()}
    rule_rows = NAT.choose_pairwise_rules(merged, pairwise_budgets, MODELS, rules, test_pids_by_seed)

    summary_rows = []
    detail_rows = []
    for rule_row in rule_rows:
        seed = int(rule_row["heldout_seed"])
        source_rows = [
            row
            for row in merged
            if int(row["seed"]) != seed and int(row["pid"]) not in test_pids_by_seed[seed]
        ]
        selected_model = rule_row["selected_model"]
        selected_rule = rule_row["selected_rule"]
        for guard in guards:
            counts, details = summarize_fold(
                natural_by_seed[seed],
                selected_model,
                selected_rule,
                guard,
                packet_lookup,
                merged_by_packet,
            )
            row = {
                **rule_row,
                "mode": "fixed_guard",
                "pairwise_budget": rule_row["regression_budget"],
                "guard": guard,
                "selected_guard": guard,
                "source_guard_recoveries": "",
                "source_guard_regressions": "",
                **counts,
            }
            summary_rows.append(row)
            detail_rows.extend(
                {
                    **detail,
                    **rule_row,
                    "mode": "fixed_guard",
                    "pairwise_budget": rule_row["regression_budget"],
                    "guard": guard,
                    "selected_guard": guard,
                }
                for detail in details
            )
        for guard_budget in guard_budgets:
            selected_guard, source_counts = choose_guard(source_rows, selected_model, selected_rule, guards, guard_budget)
            counts, details = summarize_fold(
                natural_by_seed[seed],
                selected_model,
                selected_rule,
                selected_guard,
                packet_lookup,
                merged_by_packet,
            )
            guard_name = f"guard_budget_{guard_budget}"
            row = {
                **rule_row,
                "mode": "source_selected_guard",
                "pairwise_budget": rule_row["regression_budget"],
                "guard": guard_name,
                "selected_guard": selected_guard,
                "source_guard_recoveries": source_counts["recoveries"],
                "source_guard_regressions": source_counts["regressions"],
                **counts,
            }
            summary_rows.append(row)
            detail_rows.extend(
                {
                    **detail,
                    **rule_row,
                    "mode": "source_selected_guard",
                    "pairwise_budget": rule_row["regression_budget"],
                    "guard": guard_name,
                    "selected_guard": selected_guard,
                }
                for detail in details
            )

    agg = aggregate(summary_rows, detail_rows, args.bootstrap_rounds)
    out_prefix = OUT / args.output_prefix
    write_csv(out_prefix.with_suffix(".csv"), summary_rows)
    write_csv(OUT / f"{args.output_prefix}_aggregate.csv", agg)
    write_csv(OUT / f"{args.output_prefix}_details.csv", detail_rows)
    md = OUT / f"{args.output_prefix}.md"
    write_markdown(md, args, agg)
    print(md)
    print(md.read_text())


if __name__ == "__main__":
    main()
