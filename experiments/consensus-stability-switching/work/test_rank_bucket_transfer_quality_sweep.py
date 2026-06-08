#!/usr/bin/env python3
"""Smoke tests for rank-bucket transfer quality sweep helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "rank_bucket_transfer_quality_sweep",
        ROOT / "work" / "rank_bucket_transfer_quality_sweep.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_annotate_gaps_keys_by_quality():
    mod = load_module()
    rows = [
        {
            "seed": 1,
            "quality": "s0.8_r0.02",
            "target_dataset": "B",
            "transfer": "within",
            "budget_tokens_per_problem": 1024.0,
            "projected_acc": 0.70,
            "projected_delta": 0.20,
        },
        {
            "seed": 1,
            "quality": "s0.8_r0.02",
            "target_dataset": "B",
            "transfer": "cross",
            "budget_tokens_per_problem": 1024.0,
            "projected_acc": 0.66,
            "projected_delta": 0.18,
        },
        {
            "seed": 1,
            "quality": "s0.5_r0.05",
            "target_dataset": "B",
            "transfer": "within",
            "budget_tokens_per_problem": 1024.0,
            "projected_acc": 0.55,
            "projected_delta": 0.10,
        },
    ]

    out = mod.annotate_gaps(rows)

    assert abs(out[1]["acc_gap_vs_within"] - -0.04) < 1e-12
    assert abs(out[1]["delta_gap_vs_within"] - -0.02) < 1e-12


def test_aggregate_keeps_quality_separate():
    mod = load_module()
    template = {
        "seed": 1,
        "train_dataset": "A",
        "target_dataset": "B",
        "transfer": "cross",
        "budget_tokens_per_problem": 1024.0,
        "projected_acc": 0.5,
        "projected_delta": 0.2,
        "acc_gap_vs_within": -0.1,
        "delta_gap_vs_within": -0.1,
        "invoke_rate": 0.8,
        "depth5_rate": 0.1,
        "depth10_rate": 0.6,
        "depth20_rate": 0.1,
        "tokens_per_problem": 1000.0,
    }
    rows = [
        {"quality": "s0.5_r0.05", "verifier_success": 0.5, "false_regress": 0.05, **template},
        {"quality": "s0.8_r0.02", "verifier_success": 0.8, "false_regress": 0.02, **template},
    ]

    out = mod.aggregate(rows)

    assert len(out) == 2
    assert {row["quality"] for row in out} == {"s0.5_r0.05", "s0.8_r0.02"}


def main():
    test_annotate_gaps_keys_by_quality()
    test_aggregate_keeps_quality_separate()
    print("ok")


if __name__ == "__main__":
    main()
