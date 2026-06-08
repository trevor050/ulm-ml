#!/usr/bin/env python3
"""Build answer-bearing cross-generator router rows for arbitrary direction."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_v118():
    spec = importlib.util.spec_from_file_location("cross_seed_router_symbolic_guard_audit", ROOT / "work" / "cross_seed_router_symbolic_guard_audit.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


V118 = load_v118()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-data", type=Path, required=True)
    parser.add_argument("--other-data", type=Path, required=True)
    parser.add_argument("--target-label", required=True)
    parser.add_argument("--other-label", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", default="60601,60602,60603")
    parser.add_argument("--n", type=int, default=128)
    parser.add_argument("--trials-per-problem", type=int, default=8)
    parser.add_argument("--verifier-train-problems", type=int, default=30)
    parser.add_argument("--audit-holdout-gap", type=int, default=24)
    parser.add_argument("--verifier-samples-per-problem", type=int, default=800)
    parser.add_argument("--policies", default="target_intersection_top10,target_intersection_top20,union_rank_top3")
    args = parser.parse_args()

    target = V118.V109.load_data(args.target_data)
    other = V118.V109.load_data(args.other_data)
    rows = []
    for seed in [int(seed) for seed in args.seeds.split(",") if seed.strip()]:
        rows.extend(V118.build_answer_rows_for_seed(args.target_label, args.other_label, target, other, seed, args))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print(args.output)
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
