#!/usr/bin/env python3
"""Build targeted richer pairwise-router judge probes from existing packets."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


DEFAULT_PACKET_IDS = [
    "pairwise_router_v125_budget2_all_0494_regression_s60601_p88_t0",
    "pairwise_router_v125_budget2_all_0499_regression_s60602_p63_t6",
    "pairwise_router_v125_budget2_all_0509_regression_s60603_p82_t2",
    "pairwise_router_v125_budget2_all_0510_regression_s60603_p82_t7",
    "pairwise_router_v125_budget2_all_0511_regression_s60603_p88_t4",
    "pairwise_router_v125_budget2_all_0366_recovery_s60602_p63_t0",
    "pairwise_router_v125_budget2_all_0367_recovery_s60602_p63_t3",
    "pairwise_router_v125_budget2_all_0068_neither_correct_s60601_p88_t1",
    "pairwise_router_v125_budget2_all_0069_neither_correct_s60601_p88_t3",
    "pairwise_router_v125_budget2_all_0070_neither_correct_s60601_p88_t5",
    "pairwise_router_v125_budget2_all_0071_neither_correct_s60601_p88_t6",
    "pairwise_router_v125_budget2_all_0072_neither_correct_s60601_p88_t7",
]


SYSTEM = (
    "You are a strict math answer adjudicator. You must decide which of two proposed final answers, "
    "A or B, is mathematically correct for the problem. If both are equivalent choose BOTH. If neither "
    "is correct choose NEITHER. Return JSON only."
)


def load_jsonl(path: Path) -> dict[str, dict]:
    rows = {}
    with path.open() as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                rows[row["packet_id"]] = row
    return rows


def load_manifest(path: Path) -> dict[str, dict]:
    with path.open() as f:
        return {row["packet_id"]: row for row in csv.DictReader(f)}


def parse_problem_from_prompt(prompt_row: dict) -> str:
    content = prompt_row["messages"][1]["content"]
    marker = "\n\nAnswer A, current baseline selector:\n"
    if not content.startswith("Problem:\n") or marker not in content:
        raise ValueError(f"unexpected prompt format for {prompt_row['packet_id']}")
    return content[len("Problem:\n") : content.index(marker)]


def user_prompt(problem: str, answer_a: str, answer_b: str, variant: str) -> str:
    base = (
        "Problem:\n"
        f"{problem}\n\n"
        "Answer A:\n"
        f"{answer_a}\n\n"
        "Answer B:\n"
        f"{answer_b}\n\n"
    )
    if variant == "solve_first":
        instruction = (
            "First solve the problem independently. Then compare your result to Answer A and Answer B. "
            "Do not choose an answer because it looks more plausible; choose it only if it matches the solved result. "
        )
    elif variant == "type_check":
        instruction = (
            "First identify what type of final answer the problem asks for, such as a number, digit, maximum value, "
            "or day of the week. Reject an option that is merely an intermediate value or has the wrong answer type. "
            "Then compare Answer A and Answer B to the required final answer. "
        )
    else:
        raise ValueError(variant)
    return (
        base
        + instruction
        + 'Return exactly JSON with keys "answer" and "confidence". '
        + 'The "answer" value must be one of "A", "B", "BOTH", or "NEITHER". '
        + "Use confidence from 0 to 1."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", type=Path, default=OUT / "pairwise_router_judge_v125_budget2_all_prompts.jsonl")
    parser.add_argument("--manifest", type=Path, default=OUT / "pairwise_router_judge_v125_budget2_all_manifest.csv")
    parser.add_argument("--output", type=Path, default=OUT / "pairwise_router_rich_probe_v130_prompts.jsonl")
    parser.add_argument("--manifest-output", type=Path, default=OUT / "pairwise_router_rich_probe_v130_manifest.csv")
    parser.add_argument("--packet-ids", default=",".join(DEFAULT_PACKET_IDS))
    parser.add_argument("--variants", default="solve_first,type_check")
    args = parser.parse_args()

    prompts = load_jsonl(args.prompts)
    manifest = load_manifest(args.manifest)
    packet_ids = [item.strip() for item in args.packet_ids.split(",") if item.strip()]
    variants = [item.strip() for item in args.variants.split(",") if item.strip()]
    missing = [packet_id for packet_id in packet_ids if packet_id not in prompts or packet_id not in manifest]
    if missing:
        raise ValueError(f"missing packet ids: {missing}")

    rows = []
    manifest_rows = []
    for packet_id in packet_ids:
        prompt_row = prompts[packet_id]
        meta = manifest[packet_id]
        problem = parse_problem_from_prompt(prompt_row)
        for variant in variants:
            rich_id = f"{packet_id}__{variant}"
            rows.append(
                {
                    "packet_id": rich_id,
                    "source_packet_id": packet_id,
                    "prompt_variant": variant,
                    "messages": [
                        {"role": "system", "content": SYSTEM},
                        {"role": "user", "content": user_prompt(problem, meta["baseline_answer"], meta["policy_answer"], variant)},
                    ],
                    "category": meta["category"],
                    "expected_choice": meta["expected_choice"],
                    "dataset": prompt_row.get("dataset", "MATH/Gemma"),
                    "auxiliary_dataset": prompt_row.get("auxiliary_dataset", "MATH/Llama"),
                    "seed": meta["seed"],
                    "pid": meta["pid"],
                    "trial": meta["trial"],
                    "policy": meta["policy"],
                }
            )
            manifest_copy = dict(meta)
            manifest_copy["packet_id"] = rich_id
            manifest_copy["source_packet_id"] = packet_id
            manifest_copy["prompt_variant"] = variant
            manifest_rows.append(manifest_copy)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    with args.manifest_output.open("w", newline="") as f:
        fieldnames = list(manifest_rows[0])
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(args.output)
    print(args.manifest_output)
    print(f"wrote {len(rows)} prompts from {len(packet_ids)} source packets and {len(variants)} variants")


if __name__ == "__main__":
    main()
