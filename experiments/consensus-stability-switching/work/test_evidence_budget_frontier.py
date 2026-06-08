#!/usr/bin/env python3
"""Smoke tests for evidence-budget frontier projections."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("evidence_budget_frontier", ROOT / "work" / "evidence_budget_frontier.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_apply_evidence_rate_scales_successful_recoveries_only():
    mod = load_module()
    row = {
        "cluster_sum": 0.4,
        "recoverable_invoked_rate": 0.1,
        "false_or_unhelpful_invoked_rate": 0.2,
    }

    out = mod.project_with_evidence(row, verifier_success=0.8, false_regress=0.02, evidence_rate=0.5)

    assert abs(out["projected_delta"] - 0.036) < 1e-12
    assert abs(out["projected_acc"] - 0.436) < 1e-12


def test_dataset_visibility_key_maps_frontier_dataset_names():
    mod = load_module()
    rates = {
        "Llama diverse": {"correct_rep_top1_rate": 0.9},
        "Gemma diverse": {"correct_rep_top1_rate": 0.8},
    }

    assert mod.visibility_rate_for_dataset("MATH/Llama", rates, "correct_rep_top1_rate") == 0.9
    assert mod.visibility_rate_for_dataset("MATH/Gemma", rates, "correct_rep_top1_rate") == 0.8


def main():
    test_apply_evidence_rate_scales_successful_recoveries_only()
    test_dataset_visibility_key_maps_frontier_dataset_names()
    print("ok")


if __name__ == "__main__":
    main()
