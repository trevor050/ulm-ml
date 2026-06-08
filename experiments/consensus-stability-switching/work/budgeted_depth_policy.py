#!/usr/bin/env python3
"""Budgeted policy over skip/top5/top10/top20 compact cluster verification."""

from __future__ import annotations

import argparse
import csv
import importlib.util
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ADF = load_module("adaptive_depth_frontier", ROOT / "work" / "adaptive_depth_frontier.py")
IBF = load_module("iso_budget_depth_frontier", ROOT / "work" / "iso_budget_depth_frontier.py")


DATASETS = [
    ("MATH/Llama", ROOT / "work" / "MATH_Llama-3-8B-Instruct.json"),
    ("MATH/Gemma", ROOT / "work" / "MATH_Gemma-2B.json"),
]


def expected_utility(prob_recoverable: float, verifier_success: float, false_regress: float) -> float:
    return verifier_success * prob_recoverable - false_regress * (1.0 - prob_recoverable)


def greedy_select(candidates: list[dict], total_budget: float) -> list[dict]:
    selected = []
    used_rows = set()
    spent = 0.0
    for cand in sorted(candidates, key=lambda row: (row["density"], row["expected_utility"]), reverse=True):
        if cand["row_id"] in used_rows:
            continue
        if spent + cand["cost"] > total_budget:
            continue
        selected.append(cand)
        used_rows.add(cand["row_id"])
        spent += cand["cost"]
    return selected


def evaluate_policy(rows: list[dict], selected: list[dict], verifier_success: float, false_regress: float) -> dict:
    total = len(rows)
    recoverable = false_or_unhelpful = 0
    depth_counts = Counter()
    total_cost = 0.0
    for action in selected:
        row = rows[action["row_id"]]
        rank = row["correct_rank_sum"]
        is_recoverable = (not row["cluster_sum_correct"]) and rank is not None and int(rank) <= int(action["depth"])
        recoverable += int(is_recoverable)
        false_or_unhelpful += int(not is_recoverable)
        depth_counts[int(action["depth"])] += 1
        total_cost += float(action["cost"])
    cluster_sum = sum(float(row["cluster_sum_correct"]) for row in rows) / total
    delta = (verifier_success * recoverable - false_regress * false_or_unhelpful) / total
    return {
        "cluster_sum": cluster_sum,
        "projected_delta": delta,
        "projected_acc": cluster_sum + delta,
        "invoke_rate": len(selected) / total,
        "tokens_per_problem": total_cost / total,
        "recoverable_invoked_rate": recoverable / total,
        "false_or_unhelpful_invoked_rate": false_or_unhelpful / total,
        "depth5_rate": depth_counts[5] / total,
        "depth10_rate": depth_counts[10] / total,
        "depth20_rate": depth_counts[20] / total,
        "avg_depth_if_invoked": sum(depth * count for depth, count in depth_counts.items()) / max(1, len(selected)),
    }


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def compact_costs() -> dict[tuple[str, int], float]:
    costs = {}
    for (dataset, depth, policy), path in IBF.PROMPT_FILES.items():
        if policy != "compact" or depth not in {5, 10, 20}:
            continue
        costs[(dataset, depth)] = IBF.prompt_stats(path)["est_avg_tokens"]
    return costs


def prepare_dataset(dataset: str, data_path: Path, args: argparse.Namespace) -> tuple[list[dict], dict[int, np.ndarray], dict]:
    data = ADF.MB["load_data"](data_path)
    rng = ADF.random.Random(args.seed)
    problem_ids = list(range(len(data)))
    rng.shuffle(problem_ids)
    verifier_ids = problem_ids[: args.verifier_train_problems]
    calib_ids = problem_ids[args.verifier_train_problems : args.verifier_train_problems + args.calib_problems]
    test_ids = problem_ids[args.verifier_train_problems + args.calib_problems :]

    print(f"training candidate verifier for {dataset}", flush=True)
    verifier, _ = ADF.MB["train_candidate_verifier"](data, verifier_ids, args.verifier_samples_per_problem, args.seed)

    scored = {}
    for j, pid in enumerate(calib_ids + test_ids, 1):
        if j == 1 or j % 25 == 0:
            print(f"{dataset}: scoring problem {j}/{len(calib_ids)+len(test_ids)}", flush=True)
        samples = data[pid]["samples"]
        feats = [ADF.MB["candidate_features"](sample) for sample in samples]
        scored[pid] = (
            ADF.MB["predict_logistic"](verifier, np.array(feats, dtype=float)),
            [ADF.MB["extract_answer"](sample) for sample in samples],
        )

    calib_rows = ADF.build_rows(data, calib_ids, scored, args.n, args.calib_trials, args.seed + 501)
    test_rows = ADF.build_rows(data, test_ids, scored, args.n, args.test_trials, args.seed + 601)
    depth_scores = {}
    depth_aucs = {}
    for depth in args.depths:
        ADF.add_depth_label(calib_rows, depth)
        ADF.add_depth_label(test_rows, depth)
        model, _ = ADF.fit_depth_detector(calib_rows)
        scores = ADF.predict(model, test_rows)
        depth_scores[depth] = scores
        depth_aucs[depth] = ADF.FDD.auc(list(scores), [bool(row["recoverable_depth"]) for row in test_rows])
    return test_rows, depth_scores, depth_aucs


def make_candidates(dataset: str, rows: list[dict], depth_scores: dict[int, np.ndarray], costs: dict[tuple[str, int]], args: argparse.Namespace) -> list[dict]:
    candidates = []
    for row_id in range(len(rows)):
        for depth, scores in depth_scores.items():
            prob = float(scores[row_id])
            utility = expected_utility(prob, args.verifier_success, args.false_regress)
            cost = costs[(dataset, depth)]
            if utility <= 0:
                continue
            candidates.append(
                {
                    "row_id": row_id,
                    "depth": depth,
                    "prob_recoverable": prob,
                    "expected_utility": utility,
                    "cost": cost,
                    "density": utility / cost,
                }
            )
    return candidates


def make_oracle_candidates(
    dataset: str,
    rows: list[dict],
    depths: list[int],
    costs: dict[tuple[str, int]],
    verifier_success: float,
    false_regress: float,
) -> list[dict]:
    candidates = []
    for row_id, row in enumerate(rows):
        rank = row["correct_rank_sum"]
        for depth in depths:
            is_recoverable = (not row["cluster_sum_correct"]) and rank is not None and int(rank) <= int(depth)
            utility = verifier_success if is_recoverable else -false_regress
            if utility <= 0:
                continue
            cost = costs[(dataset, depth)]
            candidates.append(
                {
                    "row_id": row_id,
                    "depth": depth,
                    "prob_recoverable": 1.0,
                    "expected_utility": utility,
                    "cost": cost,
                    "density": utility / cost,
                }
            )
    return candidates


def best_fixed_rows(dataset: str, budgets: list[float], scenario: str) -> dict[float, dict]:
    rows = [row for row in read_csv(OUT / "iso_budget_depth_frontier.csv") if row["dataset"] == dataset and row["policy"] == "compact"]
    out = {}
    for budget in budgets:
        affordable = [row for row in rows if float(row["est_tokens_per_problem"]) <= budget + 1e-9]
        if affordable:
            out[budget] = max(affordable, key=lambda row: float(row["projected_acc"]))
    return out


def run_dataset(dataset: str, path: Path, args: argparse.Namespace, costs: dict[tuple[str, int]]) -> list[dict]:
    rows, depth_scores, depth_aucs = prepare_dataset(dataset, path, args)
    learned_candidates = make_candidates(dataset, rows, depth_scores, costs, args)
    oracle_candidates = make_oracle_candidates(dataset, rows, args.depths, costs, args.verifier_success, args.false_regress)
    fixed = best_fixed_rows(dataset, args.budgets, args.scenario)
    out_rows = []
    for budget in args.budgets:
        fixed_row = fixed.get(budget)
        for policy, candidates in [
            ("learned_utility_density", learned_candidates),
            ("oracle_utility_density", oracle_candidates),
        ]:
            selected = greedy_select(candidates, total_budget=budget * len(rows))
            result = evaluate_policy(rows, selected, args.verifier_success, args.false_regress)
            out_rows.append(
                {
                    "dataset": dataset,
                    "budget_tokens_per_problem": budget,
                    "policy": policy,
                    "projected_acc": result["projected_acc"],
                    "projected_delta": result["projected_delta"],
                    "cluster_sum": result["cluster_sum"],
                    "tokens_per_problem": result["tokens_per_problem"],
                    "invoke_rate": result["invoke_rate"],
                    "depth5_rate": result["depth5_rate"],
                    "depth10_rate": result["depth10_rate"],
                    "depth20_rate": result["depth20_rate"],
                    "avg_depth_if_invoked": result["avg_depth_if_invoked"],
                    "recoverable_invoked_rate": result["recoverable_invoked_rate"],
                    "false_or_unhelpful_invoked_rate": result["false_or_unhelpful_invoked_rate"],
                    "best_fixed_projected_acc": float(fixed_row["projected_acc"]) if fixed_row else "",
                    "best_fixed_depth": int(fixed_row["depth"]) if fixed_row else "",
                    "best_fixed_invoke_rate": float(fixed_row["invoke_rate"]) if fixed_row else "",
                    "best_fixed_tokens_per_problem": float(fixed_row["est_tokens_per_problem"]) if fixed_row else "",
                    "depth5_auc": depth_aucs[5],
                    "depth10_auc": depth_aucs[10],
                    "depth20_auc": depth_aucs[20],
                }
            )
    return out_rows


def write_outputs(rows: list[dict], args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / f"{args.output_prefix}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Budgeted Variable-Depth Policy",
        "",
        f"Verifier assumption: `{args.verifier_success:.2f}` success on recoverable invocations, `{args.false_regress:.2f}` false-regression on false/unhelpful invocations.",
        "",
        "This policy trains separate recoverability detectors for compact top-5, top-10, and top-20 inspection. For each test trial, it creates candidate actions and greedily spends a verifier-token budget on the highest predicted utility per token, allowing at most one depth per trial.",
        "",
        "| dataset | budget tok/problem | policy | variable-depth acc | fixed compact acc | chosen depths per problem | invoke | spent tok/problem |",
        "|---|---:|---|---:|---:|---|---:|---:|",
    ]
    for row in rows:
        fixed = f"{row['best_fixed_projected_acc']:.3f}" if row["best_fixed_projected_acc"] != "" else "n/a"
        depths = f"5:{row['depth5_rate']:.2f}, 10:{row['depth10_rate']:.2f}, 20:{row['depth20_rate']:.2f}"
        lines.append(
            f"| {row['dataset']} | {row['budget_tokens_per_problem']:.0f} | {row['policy']} | {row['projected_acc']:.3f} | {fixed} | "
            f"{depths} | {row['invoke_rate']:.2f} | {row['tokens_per_problem']:.0f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "This is a policy-level projection rather than a measured verifier result. The learned row tests whether detector scores can allocate depth under a shared token budget better than a single fixed compact operating point. The oracle row uses true recoverability labels and measures the remaining headroom if depth choice were perfect.",
        "",
        f"CSV: [{csv_path.name}]({csv_path.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(csv_path)
    print(md_path.read_text())


def run(args: argparse.Namespace) -> None:
    args.depths = [int(x) for x in args.depths.split(",") if x.strip()]
    args.budgets = [float(x) for x in args.budgets.split(",") if x.strip()]
    costs = compact_costs()
    rows = []
    for dataset, path in DATASETS:
        rows.extend(run_dataset(dataset, path, args, costs))
    write_outputs(rows, args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="budgeted_depth_policy")
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--calib-problems", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--calib-trials", type=int, default=48)
    parser.add_argument("--test-trials", type=int, default=12)
    parser.add_argument("--n", type=int, default=128)
    parser.add_argument("--depths", default="5,10,20")
    parser.add_argument("--budgets", default="128,256,512,1024")
    parser.add_argument("--scenario", default="external_80_2pct_false_regress")
    parser.add_argument("--verifier-success", type=float, default=0.8)
    parser.add_argument("--false-regress", type=float, default=0.02)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
