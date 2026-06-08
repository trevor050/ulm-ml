#!/usr/bin/env python3
"""Audit duplicate problem families in hard cluster-packet datasets."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def normalize_question(text: str) -> str:
    text = re.sub(r"\[asy\].*?\[/asy\]", "[asy]", text, flags=re.DOTALL)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_packets(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def packet_ids_from_prompts(path: Path) -> set[str]:
    ids = set()
    with path.open() as f:
        for line in f:
            if line.strip():
                ids.add(json.loads(line)["packet_id"])
    return ids


def summarize(rows: list[dict], subset_ids: set[str] | None = None) -> dict:
    if subset_ids is not None:
        rows = [row for row in rows if row["packet_id"] in subset_ids]
    family_counts = Counter(normalize_question(row["question"]) for row in rows)
    repeats = [count for count in family_counts.values() if count > 1]
    return {
        "packets": len(rows),
        "unique_questions": len(family_counts),
        "largest_family": max(family_counts.values(), default=0),
        "repeated_families": len(repeats),
        "packets_in_repeated_families": sum(repeats),
    }


def family_rows(rows: list[dict], subset_ids: set[str] | None = None) -> list[dict]:
    if subset_ids is not None:
        rows = [row for row in rows if row["packet_id"] in subset_ids]
    by_question = defaultdict(list)
    for row in rows:
        by_question[normalize_question(row["question"])].append(row)

    out = []
    for idx, (question, members) in enumerate(
        sorted(by_question.items(), key=lambda item: (-len(item[1]), item[0]))
    ):
        answers = Counter(str(member["baseline_answer"]) for member in members)
        out.append(
            {
                "family_id": idx,
                "count": len(members),
                "packet_ids": " ".join(member["packet_id"] for member in members),
                "baseline_answers": "; ".join(f"{answer}:{count}" for answer, count in answers.most_common()),
                "question": question[:240],
            }
        )
    return out


def run(args: argparse.Namespace) -> None:
    packet_specs = [
        ("llama", OUT / "cluster_packets_math_llama_n128.jsonl", OUT / "cluster_verifier_prompts_math_llama_n128.jsonl"),
        ("gemma", OUT / "cluster_packets_math_gemma2b_n128.jsonl", OUT / "cluster_verifier_prompts_math_gemma2b_n128.jsonl"),
    ]

    summary = []
    all_family_rows = []
    all_rows = []
    all_prompt_ids = set()
    for label, packet_path, prompt_path in packet_specs:
        rows = load_packets(packet_path)
        prompt_ids = packet_ids_from_prompts(prompt_path)
        all_rows.extend(rows)
        all_prompt_ids.update(prompt_ids)
        for split, subset_ids in [("full_hard_packets", None), ("prepared_prompt_panel", prompt_ids)]:
            item = {"dataset": label, "split": split, **summarize(rows, subset_ids)}
            summary.append(item)
            for fam in family_rows(rows, subset_ids):
                all_family_rows.append({"dataset": label, "split": split, **fam})

    for split, subset_ids in [("full_hard_packets", None), ("prepared_prompt_panel", all_prompt_ids)]:
        summary.append({"dataset": "combined", "split": split, **summarize(all_rows, subset_ids)})
        for fam in family_rows(all_rows, subset_ids):
            all_family_rows.append({"dataset": "combined", "split": split, **fam})

    csv_path = OUT / f"{args.output_prefix}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)

    family_csv = OUT / f"{args.output_prefix}_families.csv"
    with family_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_family_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_family_rows)

    lines = [
        "# Hard-Packet Diversity Audit",
        "",
        "| dataset | split | packets | unique questions | largest family | repeated families | packets in repeated families |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['dataset']} | {row['split']} | {row['packets']} | {row['unique_questions']} | {row['largest_family']} | {row['repeated_families']} | {row['packets_in_repeated_families']} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "The prepared verifier panel is a cluster-failure panel, not a broad problem-diversity benchmark. Repeated problem families make the semantic-verifier result useful as evidence that the selected failures are recoverable, but not sufficient as a generalization claim.",
        "",
        f"Family details: [{family_csv.name}]({family_csv.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))

    print(md_path)
    print(csv_path)
    print(family_csv)
    print(md_path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="hard_packet_diversity_audit")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
