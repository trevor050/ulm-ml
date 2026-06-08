#!/usr/bin/env python3
"""Held-out calibration for pairwise router-judge predictions."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_score_module():
    spec = importlib.util.spec_from_file_location("score_pairwise_router_judge", ROOT / "work" / "score_pairwise_router_judge.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SCORER = load_score_module()


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


def load_predictions(path: Path) -> dict[str, dict]:
    out = {}
    with path.open() as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                row["pred_choice"] = SCORER.norm_choice(row.get("answer"))
                out[row["packet_id"]] = row
    return out


def merged_rows(manifest: dict[str, dict], prediction_paths: dict[str, Path]) -> list[dict]:
    by_model = {model: load_predictions(path) for model, path in prediction_paths.items()}
    rows = []
    for packet_id, meta in manifest.items():
        row = dict(meta)
        row["packet_id"] = packet_id
        for model, preds in by_model.items():
            pred = preds.get(packet_id, {})
            row[f"{model}_choice"] = pred.get("pred_choice", "INVALID")
        rows.append(row)
    return rows


def accepted(row: dict, model: str, rule: str) -> bool:
    choice = row[f"{model}_choice"]
    if rule == "never":
        return False
    if rule == "always":
        return True
    if rule == "B":
        return choice == "B"
    if rule == "B_or_BOTH":
        return choice in {"B", "BOTH"}
    if rule == "B_or_BOTH_not_invalid":
        return choice in {"B", "BOTH"} and choice != "INVALID"
    raise ValueError(rule)


def counts(rows: list[dict], model: str, rule: str) -> dict:
    baseline_correct = sum(row["baseline_correct"] for row in rows)
    correct = accepts = recoveries = regressions = 0
    for row in rows:
        accept = accepted(row, model, rule)
        if accept:
            accepts += 1
            row_correct = row["policy_correct"]
        else:
            row_correct = row["baseline_correct"]
        correct += int(row_correct)
        if accept and (not row["baseline_correct"]) and row["policy_correct"]:
            recoveries += 1
        if accept and row["baseline_correct"] and (not row["policy_correct"]):
            regressions += 1
    return {
        "rows": len(rows),
        "baseline_acc": baseline_correct / max(1, len(rows)),
        "gated_acc": correct / max(1, len(rows)),
        "gated_delta": (correct - baseline_correct) / max(1, len(rows)),
        "accepts": accepts,
        "recoveries": recoveries,
        "regressions": regressions,
    }


def choose_rule(source_rows: list[dict], models: list[str], rules: list[str], budget: int) -> tuple[str, str, dict]:
    best_model = models[0]
    best_rule = "never"
    best_counts = counts(source_rows, best_model, "never")
    best_key = (best_counts["recoveries"], -best_counts["regressions"], -best_counts["accepts"])
    for model in models:
        for rule in rules:
            row_counts = counts(source_rows, model, rule)
            if row_counts["regressions"] > budget:
                continue
            key = (row_counts["recoveries"], -row_counts["regressions"], -row_counts["accepts"])
            if key > best_key:
                best_model = model
                best_rule = rule
                best_counts = row_counts
                best_key = key
    return best_model, best_rule, best_counts


def load_natural_reference(
    path: Path,
    target: str,
    other: str,
    scope: str,
    score_mode: str,
    regression_budget: int,
) -> dict[int, dict]:
    out = {}
    with path.open() as f:
        for row in csv.DictReader(f):
            if (
                row["target"] == target
                and row["other"] == other
                and row["scope"] == scope
                and row["score_mode"] == score_mode
                and int(row["regression_budget"]) == regression_budget
            ):
                trials = int(row["test_trials"])
                baseline_correct = round(float(row["baseline_acc"]) * trials)
                upstream_recoveries = int(row["recoveries"])
                upstream_regressions = int(row["regressions"])
                out[int(row["heldout_seed"])] = {
                    "natural_trials": trials,
                    "natural_baseline_correct": baseline_correct,
                    "upstream_accepts": int(row["accepts"]),
                    "upstream_recoveries": upstream_recoveries,
                    "upstream_regressions": upstream_regressions,
                    "upstream_delta": (upstream_recoveries - upstream_regressions) / max(1, trials),
                }
    return out


def natural_counts(rows: list[dict], model: str, rule: str, reference: dict) -> dict:
    accepted_counts = counts(rows, model, rule)
    natural_trials = int(reference["natural_trials"])
    baseline_correct = int(reference["natural_baseline_correct"])
    correct = baseline_correct + accepted_counts["recoveries"] - accepted_counts["regressions"]
    return {
        "natural_trials": natural_trials,
        "baseline_acc": baseline_correct / max(1, natural_trials),
        "gated_acc": correct / max(1, natural_trials),
        "gated_delta": (correct - baseline_correct) / max(1, natural_trials),
        "accepts": accepted_counts["accepts"],
        "recoveries": accepted_counts["recoveries"],
        "regressions": accepted_counts["regressions"],
        "upstream_accepts": int(reference["upstream_accepts"]),
        "upstream_recoveries": int(reference["upstream_recoveries"]),
        "upstream_regressions": int(reference["upstream_regressions"]),
        "upstream_delta": float(reference["upstream_delta"]),
    }


def aggregate(rows: list[dict]) -> list[dict]:
    groups: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        groups[int(row["regression_budget"])].append(row)
    out = []
    for budget, vals in sorted(groups.items()):
        deltas = [float(row["gated_delta"]) for row in vals]
        total_trials = sum(int(row.get("natural_trials", row.get("test_rows", row.get("rows", 0)))) for row in vals)
        total_baseline_correct = sum(float(row["baseline_acc"]) * int(row.get("natural_trials", row.get("test_rows", 0))) for row in vals)
        total_correct = sum(float(row["gated_acc"]) * int(row.get("natural_trials", row.get("test_rows", 0))) for row in vals)
        out.append(
            {
                "regression_budget": budget,
                "heldout_seeds": len(vals),
                "total_trials": total_trials,
                "mean_delta": sum(deltas) / len(deltas),
                "pooled_delta": (total_correct - total_baseline_correct) / max(1, total_trials),
                "min_delta": min(deltas),
                "max_delta": max(deltas),
                "positive_seeds": sum(delta > 0 for delta in deltas),
                "total_accepts": sum(int(row["accepts"]) for row in vals),
                "total_recoveries": sum(int(row["recoveries"]) for row in vals),
                "total_regressions": sum(int(row["regressions"]) for row in vals),
                "total_upstream_accepts": sum(int(row.get("upstream_accepts", 0)) for row in vals),
                "total_upstream_recoveries": sum(int(row.get("upstream_recoveries", 0)) for row in vals),
                "total_upstream_regressions": sum(int(row.get("upstream_regressions", 0)) for row in vals),
                "mean_upstream_delta": sum(float(row.get("upstream_delta", 0.0)) for row in vals) / len(vals),
                "selected": "; ".join(f"{row['heldout_seed']}:{row['selected_model']}/{row['selected_rule']}" for row in vals),
            }
        )
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, title: str, read: str, args: argparse.Namespace, agg: list[dict], natural: bool) -> None:
    if natural:
        header = "| budget | pooled delta | mean delta | upstream delta | signs | judge accepts / upstream | recoveries | regressions | selected rules |"
        divider = "|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    else:
        header = "| budget | mean delta | min/max | signs | accepts | recoveries | regressions | selected rules |"
        divider = "|---:|---:|---:|---:|---:|---:|---:|---|"
    lines = [
        f"# {title}",
        "",
        read,
        "",
        header,
        divider,
    ]
    for row in agg:
        if natural:
            lines.append(
                f"| {row['regression_budget']} | {float(row['pooled_delta']):+.3f} | {float(row['mean_delta']):+.3f} | "
                f"{float(row['mean_upstream_delta']):+.3f} | {row['positive_seeds']}/{row['heldout_seeds']} | "
                f"{row['total_accepts']} / {row['total_upstream_accepts']} | {row['total_recoveries']} | {row['total_regressions']} | {row['selected']} |"
            )
        else:
            lines.append(
                f"| {row['regression_budget']} | {float(row['mean_delta']):+.3f} | {float(row['min_delta']):+.3f}/{float(row['max_delta']):+.3f} | "
                f"{row['positive_seeds']}/{row['heldout_seeds']} | {row['total_accepts']} | {row['total_recoveries']} | {row['total_regressions']} | {row['selected']} |"
            )
    lines.extend(
        [
            "",
            f"Per-fold CSV: [{path.stem}.csv]({path.stem}.csv). Aggregate CSV: [{path.stem}_aggregate.csv]({path.stem}_aggregate.csv).",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=OUT / "pairwise_router_judge_v120_budget0_all_manifest.csv")
    parser.add_argument("--mathstral", type=Path, default=OUT / "mathstral_pairwise_router_judge_v120_budget0_all_predictions.jsonl")
    parser.add_argument("--qwen14b", type=Path, default=OUT / "qwen14b_pairwise_router_judge_v120_budget0_all_predictions.jsonl")
    parser.add_argument("--gemma4", type=Path, default=OUT / "gemma4_pairwise_router_judge_v120_budget0_all_predictions.jsonl")
    parser.add_argument("--output-prefix", default="pairwise_router_judge_calibration_v121")
    parser.add_argument("--natural-output-prefix", default="")
    parser.add_argument("--natural-reference", type=Path, default=OUT / "cross_seed_router_problem_disjoint_frontier_v114.csv")
    parser.add_argument("--natural-target", default="MATH/Gemma")
    parser.add_argument("--natural-other", default="MATH/Llama")
    parser.add_argument("--natural-scope", default="pool_all")
    parser.add_argument("--natural-score-mode", default="learned_base")
    parser.add_argument("--natural-regression-budget", type=int, default=0)
    parser.add_argument("--regression-budgets", default="0,1,2,5")
    parser.add_argument("--rules", default="never,B,B_or_BOTH")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    rows = merged_rows(
        manifest,
        {
            "mathstral": args.mathstral,
            "qwen14b": args.qwen14b,
            "gemma4": args.gemma4,
        },
    )
    models = ["mathstral", "qwen14b", "gemma4"]
    rules = [rule.strip() for rule in args.rules.split(",") if rule.strip()]
    budgets = [int(val) for val in args.regression_budgets.split(",") if val.strip()]
    seeds = sorted({int(row["seed"]) for row in rows})
    summaries = []
    natural_summaries = []
    natural_reference = load_natural_reference(
        args.natural_reference,
        args.natural_target,
        args.natural_other,
        args.natural_scope,
        args.natural_score_mode,
        args.natural_regression_budget,
    )
    for heldout_seed in seeds:
        test_rows = [row for row in rows if int(row["seed"]) == heldout_seed]
        test_pids = {int(row["pid"]) for row in test_rows}
        source_rows = [row for row in rows if int(row["seed"]) != heldout_seed and int(row["pid"]) not in test_pids]
        for budget in budgets:
            model, rule, selector_counts = choose_rule(source_rows, models, rules, budget)
            test_counts = counts(test_rows, model, rule)
            summary = {
                "heldout_seed": heldout_seed,
                "regression_budget": budget,
                "source_rows": len(source_rows),
                "test_rows": len(test_rows),
                "selected_model": model,
                "selected_rule": rule,
                "selector_recoveries": selector_counts["recoveries"],
                "selector_regressions": selector_counts["regressions"],
                "baseline_acc": test_counts["baseline_acc"],
                "gated_acc": test_counts["gated_acc"],
                "gated_delta": test_counts["gated_delta"],
                "accepts": test_counts["accepts"],
                "recoveries": test_counts["recoveries"],
                "regressions": test_counts["regressions"],
            }
            summaries.append(summary)
            if heldout_seed in natural_reference:
                natural = natural_counts(test_rows, model, rule, natural_reference[heldout_seed])
                natural_summaries.append(
                    {
                        **summary,
                        "natural_trials": natural["natural_trials"],
                        "baseline_acc": natural["baseline_acc"],
                        "gated_acc": natural["gated_acc"],
                        "gated_delta": natural["gated_delta"],
                        "accepts": natural["accepts"],
                        "recoveries": natural["recoveries"],
                        "regressions": natural["regressions"],
                        "upstream_accepts": natural["upstream_accepts"],
                        "upstream_recoveries": natural["upstream_recoveries"],
                        "upstream_regressions": natural["upstream_regressions"],
                        "upstream_delta": natural["upstream_delta"],
                    }
                )
    agg = aggregate(summaries)
    out_md = OUT / f"{args.output_prefix}.md"
    write_csv(OUT / f"{args.output_prefix}.csv", summaries)
    write_csv(OUT / f"{args.output_prefix}_aggregate.csv", agg)
    write_markdown(
        out_md,
        "Pairwise Router-Judge Held-Out Calibration",
        "This v121 audit selects a pairwise judge model/rule on source accepted rows and evaluates on the held-out seed's accepted rows. Source rows also exclude held-out problem ids.",
        args,
        agg,
        natural=False,
    )
    if natural_summaries:
        natural_prefix = args.natural_output_prefix or f"{args.output_prefix}_natural"
        natural_agg = aggregate(natural_summaries)
        natural_md = OUT / f"{natural_prefix}.md"
        write_csv(OUT / f"{natural_prefix}.csv", natural_summaries)
        write_csv(OUT / f"{natural_prefix}_aggregate.csv", natural_agg)
        write_markdown(
            natural_md,
            "Pairwise Router-Judge Natural Trial Calibration",
            "This table converts the same source-selected pairwise judge policy back to the natural held-out trial denominator. Non-invoked trials stay on the baseline; upstream accepted router actions are kept only when the pairwise judge accepts the auxiliary answer.",
            args,
            natural_agg,
            natural=True,
        )
    print(out_md)
    print(out_md.read_text())


if __name__ == "__main__":
    main()
