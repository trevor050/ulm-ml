#!/usr/bin/env python3
"""Build blinded deployed-mix verifier prompt assignments."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

DATASETS = {
    "MATH/Llama": {
        "prompts": OUT / "cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.jsonl",
        "answer_key": OUT / "cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json",
    },
    "MATH/Gemma": {
        "prompts": OUT / "cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.jsonl",
        "answer_key": OUT / "cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json",
    },
}


def dataset_paths(args: argparse.Namespace) -> dict[str, dict[str, Path]]:
    return {
        "MATH/Llama": {
            "prompts": args.llama_prompts,
            "answer_key": args.llama_answer_key,
        },
        "MATH/Gemma": {
            "prompts": args.gemma_prompts,
            "answer_key": args.gemma_answer_key,
        },
    }


def load_prompts(path: Path) -> dict[str, dict]:
    rows = {}
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            rows[row["packet_id"]] = row
    return rows


def select_packet_ids(answer_key_path: Path, per_category: int) -> list[tuple[str, str]]:
    key = json.loads(answer_key_path.read_text())
    by_category: dict[str, list[str]] = defaultdict(list)
    for packet_id, meta in sorted(key.items()):
        by_category[str(meta["deployment_category"])].append(packet_id)
    selected = []
    for category in sorted(by_category):
        selected.extend((category, packet_id) for packet_id in by_category[category][:per_category])
    return selected


def round_robin_chunks(rows: list[dict], chunks: int) -> list[list[dict]]:
    out = [[] for _ in range(chunks)]
    for i, row in enumerate(rows):
        out[i % chunks].append(row)
    return out


def run(args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel_rows = []
    manifest_rows = []
    for dataset, paths in dataset_paths(args).items():
        prompts = load_prompts(paths["prompts"])
        for category, packet_id in select_packet_ids(paths["answer_key"], args.per_category):
            prompt_row = dict(prompts[packet_id])
            prompt_row["dataset"] = dataset
            panel_rows.append(prompt_row)
            manifest_rows.append({"dataset": dataset, "packet_id": packet_id, "heldout_category": category})

    panel_rows.sort(key=lambda row: (row["packet_id"], row["dataset"]))
    panel_path = OUT / f"{args.output_prefix}_prompts.jsonl"
    with panel_path.open("w") as f:
        for row in panel_rows:
            f.write(json.dumps(row) + "\n")

    manifest_path = OUT / f"{args.output_prefix}_manifest.csv"
    with manifest_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["dataset", "packet_id", "heldout_category"])
        writer.writeheader()
        writer.writerows(manifest_rows)

    assignment_paths = []
    for i, chunk in enumerate(round_robin_chunks(panel_rows, args.chunks)):
        path = OUT / f"{args.output_prefix}_assignment_{i:02d}.jsonl"
        assignment_paths.append(path)
        with path.open("w") as f:
            for row in chunk:
                f.write(json.dumps(row) + "\n")

    lines = [
        "# Blind Deployed-Mix Panel Assignments",
        "",
        f"Panel size: `{len(panel_rows)}` prompts, `{args.per_category}` per deployment category per dataset.",
        "",
        "The assignment files contain only `dataset`, `packet_id`, and prompt messages. Deployment categories and answer keys are excluded from judge-facing files.",
        "",
        f"Panel prompts: [{panel_path.name}]({panel_path.name}).",
        f"Held-out manifest: [{manifest_path.name}]({manifest_path.name}).",
        "",
        "## Assignments",
        "",
    ]
    for path in assignment_paths:
        lines.append(f"- [{path.name}]({path.name})")
    md_path = OUT / f"{args.output_prefix}_assignments.md"
    md_path.write_text("\n".join(lines))

    print(md_path)
    print(panel_path)
    print(manifest_path)
    for path in assignment_paths:
        print(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", default="blind_deployed_mix_v66")
    parser.add_argument("--per-category", type=int, default=2)
    parser.add_argument("--chunks", type=int, default=6)
    parser.add_argument("--llama-prompts", type=Path, default=DATASETS["MATH/Llama"]["prompts"])
    parser.add_argument("--gemma-prompts", type=Path, default=DATASETS["MATH/Gemma"]["prompts"])
    parser.add_argument("--llama-answer-key", type=Path, default=DATASETS["MATH/Llama"]["answer_key"])
    parser.add_argument("--gemma-answer-key", type=Path, default=DATASETS["MATH/Gemma"]["answer_key"])
    run(parser.parse_args())


if __name__ == "__main__":
    main()
