#!/usr/bin/env python3
"""Build one-prompt-per-answer-cluster binary verifier panels."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


CLUSTER_RATIONALE_PROMPT = """You are judging one candidate answer cluster for a math problem.
The cluster contains sampled rationales that all reached the same final answer.
Decide whether that final answer is mathematically correct for the problem.
Return strict JSON only: {"answer": "yes", "confidence": 0.0}.
Use answer "yes" only if the final answer is correct; otherwise use "no"."""


ANSWER_CHECK_PROMPT = """You are checking one candidate final answer for a math problem.
Solve the problem independently, compare against the candidate final answer, and decide if they are mathematically equivalent.
Most candidate answers are wrong. Return "yes" only when the candidate answer is correct.
Return strict JSON only: {"answer": "yes", "confidence": 0.0}."""


def truncate(text: str, limit: int) -> str:
    text = text.strip()
    if not limit or len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n...[truncated]"


def read_ids(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    if path.suffix == ".csv":
        with path.open(newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return set()
        field = "packet_id" if "packet_id" in rows[0] else list(rows[0])[0]
        return {row[field] for row in rows if row.get(field)}
    return {line.strip() for line in path.read_text().splitlines() if line.strip()}


def make_prompt(packet: dict, cluster: dict, args: argparse.Namespace) -> str:
    system_prompt = ANSWER_CHECK_PROMPT if args.style == "answer_check" else CLUSTER_RATIONALE_PROMPT
    lines = [
        system_prompt,
        "",
        "Problem:",
        str(packet.get("question") or "").strip(),
        "",
        "Candidate final answer:",
        str(cluster["answer"]),
    ]
    if args.style == "cluster_rationale":
        lines += [
            "",
            f"Cluster support count: {cluster['support']}",
            "Representative rationales:",
        ]
        reps = cluster["representatives"]
        if args.representatives_per_cluster:
            reps = reps[: args.representatives_per_cluster]
        for i, rep in enumerate(reps, 1):
            lines += [
                f"[{i}] verifier_score={rep['score']:.4f}",
                truncate(rep["text"], args.rationale_chars),
                "",
            ]
    lines += [
        'Return only JSON with answer "yes" or "no" and confidence in [0,1].',
    ]
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    wanted = read_ids(args.ids)
    rows = []
    key = {}
    with args.packets.open() as f:
        for line in f:
            if not line.strip():
                continue
            packet = json.loads(line)
            source_packet_id = packet["packet_id"]
            if wanted is not None and source_packet_id not in wanted:
                continue
            for cluster in packet["clusters"][: args.top_k]:
                rank = int(cluster["rank_by_sum"])
                judge_id = f"{source_packet_id}::cluster{rank:02d}"
                rows.append(
                    {
                        "packet_id": judge_id,
                        "source_packet_id": source_packet_id,
                        "cluster_rank": rank,
                        "candidate_answer": cluster["answer"],
                        "dataset": args.dataset,
                        "messages": [{"role": "user", "content": make_prompt(packet, cluster, args)}],
                    }
                )
                key[judge_id] = {
                    "source_packet_id": source_packet_id,
                    "dataset": args.dataset,
                    "deployment_category": packet.get("deployment_category"),
                    "baseline_answer": packet.get("baseline_answer"),
                    "baseline_is_correct": packet.get("baseline_is_correct"),
                    "correct_answers": packet.get("correct_answers_in_visible", []),
                    "candidate_answer": cluster["answer"],
                    "cluster_rank": rank,
                    "is_correct_cluster": bool(cluster.get("is_correct_cluster")),
                }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    key_path = args.output.with_suffix(".answer_key.json")
    key_path.write_text(json.dumps(key, indent=2))
    print(args.output)
    print(key_path)
    print(f"wrote {len(rows)} cluster-judge prompts")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--ids", type=Path)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--representatives-per-cluster", type=int, default=1)
    parser.add_argument("--rationale-chars", type=int, default=220)
    parser.add_argument("--style", choices=["cluster_rationale", "answer_check"], default="cluster_rationale")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
