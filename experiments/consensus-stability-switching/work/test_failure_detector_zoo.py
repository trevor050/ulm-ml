#!/usr/bin/env python3
"""Smoke tests for failure_detector_zoo helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("failure_detector_zoo", ROOT / "work" / "failure_detector_zoo.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_quadratic_features_include_raw_squares_and_pairs():
    mod = load_module()
    x = np.array([[2.0, 3.0], [4.0, 5.0]])
    out = mod.expand_features(x, "quadratic")
    assert out.shape == (2, 5)
    assert np.allclose(out[0], [2.0, 3.0, 4.0, 9.0, 6.0])


def test_precision_metrics_uses_visible_miss_gain():
    mod = load_module()
    rows = [
        {"visible_miss": True, "cluster_sum_correct": False},
        {"visible_miss": False, "cluster_sum_correct": True},
        {"visible_miss": True, "cluster_sum_correct": False},
    ]
    scores = np.array([0.9, 0.8, 0.1])
    metrics = mod.precision_at_rate(scores, rows, 1 / 3)
    assert metrics["precision"] == 1.0
    assert metrics["projected_perfect_acc"] == 2 / 3


def main():
    test_quadratic_features_include_raw_squares_and_pairs()
    test_precision_metrics_uses_visible_miss_gain()
    print("ok")


if __name__ == "__main__":
    main()
