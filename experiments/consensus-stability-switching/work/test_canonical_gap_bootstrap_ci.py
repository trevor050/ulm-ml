#!/usr/bin/env python3
"""Smoke tests for canonical gap bootstrap helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("canonical_gap_bootstrap_ci", ROOT / "work" / "canonical_gap_bootstrap_ci.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_cluster_rank_aggregates_score_by_answer():
    mod = load_module()
    preds = ["a", "a", "b"]
    scores = np.array([0.4, 0.4, 0.7])
    labels = np.array([False, True, False])

    assert mod.cluster_rank(preds, scores, labels) == 1


def test_aggregate_computes_headroom_and_gain():
    mod = load_module()
    rows = [
        {
            "any_correct": 1.0,
            "cluster_sum": 0.0,
            "top2": 0.0,
            "top3": 1.0,
            "top5": 1.0,
            "top10": 1.0,
            "top20": 1.0,
            "top50": 1.0,
            "_miss_ranks": [3],
        },
        {
            "any_correct": 1.0,
            "cluster_sum": 1.0,
            "top2": 1.0,
            "top3": 1.0,
            "top5": 1.0,
            "top10": 1.0,
            "top20": 1.0,
            "top50": 1.0,
            "_miss_ranks": [],
        },
    ]

    out = mod.aggregate(rows)

    assert out["any_correct"] == 1.0
    assert out["cluster_sum"] == 0.5
    assert out["headroom"] == 0.5
    assert out["top20_gain"] == 0.5
    assert out["top20_headroom_closed"] == 1.0
    assert out["miss_rank_p50"] == 3


def test_bootstrap_returns_intervals_for_requested_keys():
    mod = load_module()
    rows = [
        {
            "any_correct": 1.0,
            "cluster_sum": 0.0,
            "top2": 0.0,
            "top3": 1.0,
            "top5": 1.0,
            "top10": 1.0,
            "top20": 1.0,
            "top50": 1.0,
            "_miss_ranks": [3],
        }
    ]

    ci = mod.bootstrap(rows, rounds=5, seed=1)

    assert "headroom" in ci
    assert ci["headroom"] == (1.0, 1.0)


def main():
    test_cluster_rank_aggregates_score_by_answer()
    test_aggregate_computes_headroom_and_gain()
    test_bootstrap_returns_intervals_for_requested_keys()
    print("ok")


if __name__ == "__main__":
    main()
