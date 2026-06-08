#!/usr/bin/env python3
"""Smoke tests for generation-vs-verification budget helpers."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "generation_vs_verification_budget",
        ROOT / "work" / "generation_vs_verification_budget.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Args:
    seed = 1
    verifier_train_problems = 1
    audit_holdout_gap = 1
    chars_per_token = 4.0
    base_n = 2


def test_split_test_ids_is_deterministic_suffix_after_train_and_gap():
    mod = load_module()

    ids = mod.split_test_ids(8, seed=7, verifier_train_problems=2, audit_holdout_gap=1)

    assert len(ids) == 5
    assert ids == mod.split_test_ids(8, seed=7, verifier_train_problems=2, audit_holdout_gap=1)


def test_avg_sample_tokens_uses_test_split_and_requested_n():
    mod = load_module()
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "data.json"
        data = [{"samples": ["a" * 4, "b" * 8, "c" * 12]} for _ in range(5)]
        path.write_text(json.dumps(data))

        out = mod.avg_sample_tokens(path, [1, 2], Args)

    assert out[1] == 1.0
    assert out[2] == 1.5


def test_summarize_against_verification_uses_base_delta():
    mod = load_module()
    rows = [
        {"dataset": "D", "n": 2, "cluster_sum": 0.5, "any_correct": 0.7, "extra_sample_tokens_vs_base": 0, "cluster_sum_delta_vs_base": 0.0, "any_correct_delta_vs_base": 0.0},
        {"dataset": "D", "n": 4, "cluster_sum": 0.55, "any_correct": 0.9, "extra_sample_tokens_vs_base": 100, "cluster_sum_delta_vs_base": 0.05, "any_correct_delta_vs_base": 0.2},
    ]
    rb = {16.0: {"delta_mean": "0.2", "acc_mean": "0.7"}}
    args = Args()
    args.compare_ns = [4]
    args.compare_budgets = [16]

    out = mod.summarize_against_verification(rows, rb, args)

    assert len(out) == 1
    assert abs(out[0]["generation_cluster_sum_delta"] - 0.05) < 1e-12
    assert out[0]["rank_bucket_delta"] == 0.2


def main():
    test_split_test_ids_is_deterministic_suffix_after_train_and_gap()
    test_avg_sample_tokens_uses_test_split_and_requested_n()
    test_summarize_against_verification_uses_base_delta()
    print("ok")


if __name__ == "__main__":
    main()
