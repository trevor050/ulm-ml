#!/usr/bin/env python3
"""Smoke tests for short-trace baseline selectors."""

from __future__ import annotations

import importlib.util
import random
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("short_trace_baseline", ROOT / "work" / "short_trace_baseline.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_group_stats_marks_cluster_correct_if_any_member_correct():
    mod = load_module()
    preds = ["1", "1", "2"]
    scores = np.array([0.1, 0.2, 0.9])
    lengths = np.array([5, 3, 10])
    labels = np.array([False, True, False])

    groups = mod.group_stats(preds, scores, lengths, labels)

    assert groups["1"]["correct"]
    assert groups["1"]["min_length"] == 3
    assert not groups["2"]["correct"]


def test_make_trial_scores_shortest_exact_and_cluster_separately():
    mod = load_module()
    row = {
        "samples": ["x", "longer answer 1 with proof", "medium answer 2"],
        "is_corrects": [False, True, False],
    }
    answers = ["1", "1", "2"]
    scores = np.array([0.1, 0.2, 0.9])

    trial = mod.make_trial(row, scores, answers, n=3, rng=random.Random(0))

    assert not trial["shortest_sample_exact"]
    assert trial["shortest_sample_cluster"]
    assert not trial["cluster_sum"]


def test_make_trial_handles_shortest_sample_without_extracted_answer():
    mod = load_module()
    row = {
        "samples": ["x", "longer answer 1 with proof"],
        "is_corrects": [False, True],
    }
    answers = [None, "1"]
    scores = np.array([0.1, 0.2])

    trial = mod.make_trial(row, scores, answers, n=2, rng=random.Random(0))

    assert not trial["shortest_sample_cluster"]


def main():
    test_group_stats_marks_cluster_correct_if_any_member_correct()
    test_make_trial_scores_shortest_exact_and_cluster_separately()
    test_make_trial_handles_shortest_sample_without_extracted_answer()
    print("ok")


if __name__ == "__main__":
    main()
