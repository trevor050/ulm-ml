#!/usr/bin/env python3
"""Smoke tests for verifier-quality target helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "rank_bucket_verifier_quality_targets",
        ROOT / "work" / "rank_bucket_verifier_quality_targets.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_quality_threshold_solves_reference_equation():
    mod = load_module()
    needed = mod.quality_threshold(
        cluster_sum=0.40,
        recoverable_rate=0.20,
        false_rate=0.30,
        target_acc=0.55,
        fixed_false_regress=0.02,
    )
    ceiling = mod.false_regress_ceiling(
        cluster_sum=0.40,
        recoverable_rate=0.20,
        false_rate=0.30,
        target_acc=0.55,
        fixed_success=0.80,
    )

    assert round(needed, 6) == 0.78
    assert round(ceiling, 6) == 0.033333


def test_build_target_rows_uses_cross_model_cross_seed_only():
    mod = load_module()

    class Args:
        success_reference = 0.80
        false_regress_reference = 0.02

    rows = [
        {
            "transfer_kind": "cross_model_cross_seed",
            "model_transfer": "cross",
            "seed_transfer": "cross",
            "train_dataset": "A",
            "target_dataset": "B",
            "budget_tokens_per_problem": "128",
            "cluster_sum": "0.4",
            "recoverable_invoked_rate": "0.2",
            "false_or_unhelpful_invoked_rate": "0.3",
            "projected_acc": "0.554",
            "best_fixed_projected_acc": "0.55",
            "acc_gap_vs_within_same_seed": "-0.01",
        },
        {
            "transfer_kind": "cross_model_same_seed",
            "model_transfer": "cross",
            "seed_transfer": "same",
            "train_dataset": "A",
            "target_dataset": "B",
            "budget_tokens_per_problem": "128",
            "cluster_sum": "0.1",
            "recoverable_invoked_rate": "0.1",
            "false_or_unhelpful_invoked_rate": "0.1",
            "projected_acc": "0.1",
            "best_fixed_projected_acc": "0.1",
            "acc_gap_vs_within_same_seed": "0",
        },
    ]

    out = mod.build_target_rows(rows, Args())

    assert len(out) == 1
    assert out[0]["direction"] == "A -> B"
    assert round(out[0]["success_required_vs_fixed_at_false_ref"], 6) == 0.78
    assert out[0]["passes_fixed_at_reference"] is True
    assert out[0]["passes_within_at_reference"] is False


def main():
    test_quality_threshold_solves_reference_equation()
    test_build_target_rows_uses_cross_model_cross_seed_only()
    print("ok")


if __name__ == "__main__":
    main()
