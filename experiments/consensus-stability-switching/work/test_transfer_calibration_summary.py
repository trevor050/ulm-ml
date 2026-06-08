#!/usr/bin/env python3
"""Smoke tests for transfer calibration aggregation."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("transfer_calibration_summary", ROOT / "work" / "transfer_calibration_summary.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_add_brier_gaps_uses_suite_seed_target():
    mod = load_module()
    rows = [
        {"suite": "s", "seed": "1", "target_model": "B", "transfer": "within", "target_candidate_brier": "0.2"},
        {"suite": "s", "seed": "1", "target_model": "B", "transfer": "cross", "target_candidate_brier": "0.25"},
    ]

    out = mod.add_brier_gaps(rows)

    assert abs(out[1]["candidate_brier_gap_vs_within"] - 0.05) < 1e-12


def test_summarize_keeps_cross_rows_only():
    mod = load_module()
    rows = [
        {
            "suite": "s",
            "train_model": "A",
            "target_model": "B",
            "transfer": "cross",
            "cluster_sum_gap_vs_within": "0.1",
            "candidate_auc_gap_vs_within": "-0.2",
            "candidate_brier_gap_vs_within": "0.03",
            "oracle_top20_gap_vs_within": "0.0",
        },
        {
            "suite": "s",
            "train_model": "B",
            "target_model": "B",
            "transfer": "within",
            "cluster_sum_gap_vs_within": "0.0",
            "candidate_auc_gap_vs_within": "0.0",
            "candidate_brier_gap_vs_within": "0.0",
            "oracle_top20_gap_vs_within": "0.0",
        },
    ]

    summary = mod.summarize(rows)

    assert len(summary) == 1
    assert summary[0]["train_model"] == "A"
    assert abs(summary[0]["cluster_gap_mean"] - 0.1) < 1e-12
    assert abs(summary[0]["auc_gap_mean"] - -0.2) < 1e-12


def main():
    test_add_brier_gaps_uses_suite_seed_target()
    test_summarize_keeps_cross_rows_only()
    print("ok")


if __name__ == "__main__":
    main()
