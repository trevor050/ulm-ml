#!/usr/bin/env python3
"""Reuse pairwise predictions for overlapping accepted router actions."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def load_manifest(path: Path) -> dict[str, dict]:
    with path.open() as f:
        return {row["packet_id"]: row for row in csv.DictReader(f)}


def action_key(row: dict) -> tuple[str, str, str, str]:
    return (str(row["seed"]), str(row["pid"]), str(row["trial"]), str(row["policy"]))


def load_predictions(path: Path) -> dict[str, dict]:
    out = {}
    if not path.exists():
        return out
    with path.open() as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                out[row["packet_id"]] = row
    return out


def existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids = set()
    with path.open() as f:
        for line in f:
            if line.strip():
                ids.add(json.loads(line)["packet_id"])
    return ids


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--source-predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_manifest = load_manifest(args.source_manifest)
    target_manifest = load_manifest(args.target_manifest)
    source_predictions = load_predictions(args.source_predictions)
    by_key = {}
    for packet_id, meta in source_manifest.items():
        pred = source_predictions.get(packet_id)
        if pred is not None:
            by_key[action_key(meta)] = pred

    done = existing_ids(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    reused = 0
    with args.output.open("a") as f:
        for target_packet, target_meta in target_manifest.items():
            if target_packet in done:
                continue
            pred = by_key.get(action_key(target_meta))
            if pred is None:
                continue
            out = dict(pred)
            out["packet_id"] = target_packet
            out["remapped_from_packet_id"] = pred["packet_id"]
            f.write(json.dumps(out) + "\n")
            reused += 1
    print(f"reused={reused} output={args.output}")


if __name__ == "__main__":
    main()
