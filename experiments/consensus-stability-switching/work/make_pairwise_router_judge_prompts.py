#!/usr/bin/env python3
"""Build pairwise baseline-vs-auxiliary router judge prompts from v118 rows."""

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


V118 = load_module("cross_seed_router_symbolic_guard_audit", "work/cross_seed_router_symbolic_guard_audit.py")
V113 = V118.V113
V109 = V118.V109
ROUTER = V118.ROUTER


SYSTEM = (
    "You are a strict math answer adjudicator. Given one math problem and two proposed final answers, "
    "choose which final answer is mathematically correct. Do not reward style. If both answers are "
    "equivalent, choose BOTH. If neither is correct, choose NEITHER. Return JSON only."
)


def load_data(path: Path) -> list[dict]:
    with path.open() as f:
        return json.load(f)


def load_answer_rows(path: Path, policies: set[str], target: str, other: str) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row["policy"] not in policies:
                continue
            if row.get("target") != target or row.get("other") != other:
                continue
            row["seed"] = int(row["seed"])
            row["pid"] = int(row["pid"])
            row["trial"] = int(row["trial"])
            row["changed"] = bool(row["changed"])
            row["baseline_correct"] = bool(row["baseline_correct"])
            row["policy_correct"] = bool(row["policy_correct"])
            row["utility_label"] = int(row["utility_label"])
            rows.append(row)
    if not rows:
        wanted = ",".join(sorted(policies))
        raise ValueError(
            f"no answer rows matched path={path} target={target!r} other={other!r} policies={wanted!r}"
        )
    return rows


def chosen_rows(rows: list[dict], args: argparse.Namespace) -> list[dict]:
    chosen = []
    for heldout_seed in [int(seed) for seed in args.seeds.split(",") if seed.strip()]:
        prepared = V118.prepare_problem_disjoint(rows, heldout_seed, args.score_mode, args)
        threshold, _selector_counts = V113.choose_threshold(prepared["train_rows"], prepared["train_scores"], args.regression_budget)
        grouped: dict[tuple[str, str, int, int, int], list[tuple[dict, float]]] = defaultdict(list)
        for row, score in zip(prepared["test_rows"], prepared["test_scores"], strict=True):
            grouped[V113.trial_key(row)].append((row, float(score)))
        for key, vals in sorted(grouped.items()):
            accepted = [
                (row, score)
                for row, score in vals
                if threshold is not None and row["changed"] and score >= threshold
            ]
            if not accepted:
                continue
            row, score = max(accepted, key=lambda pair: (pair[1], str(pair[0]["policy"])))
            out = dict(row)
            out["router_score"] = score
            out["threshold"] = threshold
            out["heldout_seed"] = heldout_seed
            chosen.append(out)
    return chosen


def category(row: dict) -> str:
    if row["baseline_correct"] and not row["policy_correct"]:
        return "regression"
    if (not row["baseline_correct"]) and row["policy_correct"]:
        return "recovery"
    if row["baseline_correct"] and row["policy_correct"]:
        return "both_correct"
    return "neither_correct"


def expected_choice(row: dict) -> str:
    cat = category(row)
    if cat == "regression":
        return "A"
    if cat == "recovery":
        return "B"
    if cat == "both_correct":
        return "BOTH"
    return "NEITHER"


def make_messages(question: str, baseline_answer: object, policy_answer: object) -> list[dict]:
    user = (
        "Problem:\n"
        f"{question}\n\n"
        "Answer A, current baseline selector:\n"
        f"{baseline_answer}\n\n"
        "Answer B, auxiliary-generator candidate:\n"
        f"{policy_answer}\n\n"
        'Return exactly JSON with keys "answer" and "confidence". '
        'The "answer" value must be one of "A", "B", "BOTH", or "NEITHER". '
        'Use confidence from 0 to 1.'
    )
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def stratified_sample(rows: list[dict], args: argparse.Namespace) -> list[dict]:
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_cat[category(row)].append(row)
    rng = random.Random(args.sample_seed)
    sampled = []
    for cat, vals in sorted(by_cat.items()):
        by_pid: dict[int, list[dict]] = defaultdict(list)
        for row in vals:
            by_pid[int(row["pid"])].append(row)
        pids = list(by_pid)
        rng.shuffle(pids)
        cat_rows = []
        for pid in pids:
            candidates = sorted(by_pid[pid], key=lambda row: float(row["router_score"]), reverse=True)
            cat_rows.append(candidates[0])
            if len(cat_rows) >= args.per_category:
                break
        if len(cat_rows) < args.per_category:
            seen = {(int(row["seed"]), int(row["pid"]), int(row["trial"]), row["policy"]) for row in cat_rows}
            extras = sorted(vals, key=lambda row: float(row["router_score"]), reverse=True)
            for row in extras:
                key = (int(row["seed"]), int(row["pid"]), int(row["trial"]), row["policy"])
                if key in seen:
                    continue
                cat_rows.append(row)
                seen.add(key)
                if len(cat_rows) >= args.per_category:
                    break
        sampled.extend(cat_rows)
    sampled.sort(key=lambda row: (category(row), int(row["seed"]), int(row["pid"]), int(row["trial"])))
    return sampled


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--answer-rows", type=Path, default=OUT / "cross_seed_router_symbolic_guard_v118_answer_rows.jsonl")
    parser.add_argument("--data", type=Path, default=ROOT / "work" / "MATH_Gemma-2B.json")
    parser.add_argument("--target", default="MATH/Gemma")
    parser.add_argument("--other", default="MATH/Llama")
    parser.add_argument("--output", type=Path, default=OUT / "pairwise_router_judge_v119_prompts.jsonl")
    parser.add_argument("--manifest", type=Path, default=OUT / "pairwise_router_judge_v119_manifest.csv")
    parser.add_argument("--score-mode", default="base_utility")
    parser.add_argument("--regression-budget", type=int, default=0)
    parser.add_argument("--policies", default="target_intersection_top10,target_intersection_top20,union_rank_top3")
    parser.add_argument("--seeds", default="60601,60602,60603")
    parser.add_argument("--min-fit-examples", type=int, default=16)
    parser.add_argument("--per-category", type=int, default=20)
    parser.add_argument("--sample-seed", type=int, default=60604)
    parser.add_argument("--packet-prefix", default="pairwise_router_v119")
    parser.add_argument("--dataset-label", default="MATH/Gemma")
    args = parser.parse_args()

    policies = {policy.strip() for policy in args.policies.split(",") if policy.strip()}
    rows = load_answer_rows(args.answer_rows, policies, args.target, args.other)
    data = load_data(args.data)
    chosen = chosen_rows(rows, args)
    sampled = stratified_sample(chosen, args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f, args.manifest.open("w", newline="") as mf:
        fieldnames = [
            "packet_id",
            "category",
            "expected_choice",
            "seed",
            "pid",
            "trial",
            "policy",
            "baseline_correct",
            "policy_correct",
            "baseline_answer",
            "policy_answer",
            "router_score",
            "threshold",
        ]
        writer = csv.DictWriter(mf, fieldnames=fieldnames)
        writer.writeheader()
        for idx, row in enumerate(sampled, start=1):
            packet_id = f"{args.packet_prefix}_{idx:04d}_{category(row)}_s{row['seed']}_p{row['pid']}_t{row['trial']}"
            question = data[int(row["pid"])]["question"]
            prompt = {
                "packet_id": packet_id,
                "messages": make_messages(question, row["baseline_answer"], row["policy_answer"]),
                "category": category(row),
                "expected_choice": expected_choice(row),
                "dataset": args.dataset_label,
                "auxiliary_dataset": args.other,
                "seed": row["seed"],
                "pid": row["pid"],
                "trial": row["trial"],
                "policy": row["policy"],
            }
            f.write(json.dumps(prompt) + "\n")
            writer.writerow(
                {
                    "packet_id": packet_id,
                    "category": category(row),
                    "expected_choice": expected_choice(row),
                    "seed": row["seed"],
                    "pid": row["pid"],
                    "trial": row["trial"],
                    "policy": row["policy"],
                    "baseline_correct": row["baseline_correct"],
                    "policy_correct": row["policy_correct"],
                    "baseline_answer": row["baseline_answer"],
                    "policy_answer": row["policy_answer"],
                    "router_score": row["router_score"],
                    "threshold": row["threshold"],
                }
            )
    counts = defaultdict(int)
    for row in sampled:
        counts[category(row)] += 1
    print(args.output)
    print(args.manifest)
    print(dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
