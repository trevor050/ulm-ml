#!/usr/bin/env python3
"""Smoke tests for cross-model transfer seed-sweep aggregation."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "cross_model_verifier_transfer_seed_sweep",
        ROOT / "work" / "cross_model_verifier_transfer_seed_sweep.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_mean_std_population():
    mod = load_module()
    mean, std = mod.mean_std([1.0, 3.0])

    assert mean == 2.0
    assert std == 1.0


def test_summarize_groups_transfer_rows():
    mod = load_module()
    rows = [
        {
            "train_model": "A",
            "target_model": "B",
            "transfer": "cross",
            "cluster_sum": 0.2,
            "cluster_sum_gap_vs_within": -0.1,
            "candidate_auc_gap_vs_within": -0.2,
            "oracle_top20_gap_vs_within": 0.0,
        },
        {
            "train_model": "A",
            "target_model": "B",
            "transfer": "cross",
            "cluster_sum": 0.4,
            "cluster_sum_gap_vs_within": 0.1,
            "candidate_auc_gap_vs_within": 0.0,
            "oracle_top20_gap_vs_within": 0.2,
        },
    ]

    out = mod.summarize(rows)[0]

    assert out["seeds"] == 2
    assert abs(out["cluster_sum_mean"] - 0.3) < 1e-12
    assert abs(out["cluster_gap_mean"]) < 1e-12
    assert abs(out["auc_gap_mean"] - -0.1) < 1e-12
    assert abs(out["top20_gap_mean"] - 0.1) < 1e-12


def main():
    test_mean_std_population()
    test_summarize_groups_transfer_rows()
    print("ok")


if __name__ == "__main__":
    main()
