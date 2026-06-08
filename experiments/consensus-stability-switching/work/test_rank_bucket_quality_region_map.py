#!/usr/bin/env python3
"""Smoke tests for rank-bucket quality region map helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "rank_bucket_quality_region_map",
        ROOT / "work" / "rank_bucket_quality_region_map.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def toy_row():
    return {
        "direction": "A -> B",
        "train_dataset": "A",
        "target_dataset": "B",
        "budget_tokens_per_problem": "128",
        "cluster_sum_mean": "0.4",
        "recoverable_invoked_rate_mean": "0.2",
        "false_or_unhelpful_invoked_rate_mean": "0.3",
        "fixed_compact_acc_at_reference": "0.55",
        "within_same_allocator_acc_at_reference": "0.56",
    }


def test_frange_inclusive():
    mod = load_module()
    assert mod.frange(0.5, 0.6, 0.05) == [0.5, 0.55, 0.6]


def test_region_summary_counts_grid_passes():
    mod = load_module()
    out = mod.summarize_row(toy_row(), success_grid=[0.5, 0.8, 1.0], false_grid=[0.0, 0.02, 0.1])

    assert out["grid_points"] == 9
    assert out["fixed_pass_points"] == 5
    assert round(out["fixed_pass_fraction"], 6) == round(5 / 9, 6)
    assert out["fixed_best_false_at_80"] == 0.02
    assert out["within_pass_points"] == 4


def main():
    test_frange_inclusive()
    test_region_summary_counts_grid_passes()
    print("ok")


if __name__ == "__main__":
    main()
