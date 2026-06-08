#!/usr/bin/env python3
"""Smoke tests for token-budget generation-vs-verification comparison."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "token_budget_generation_vs_verification",
        ROOT / "work" / "token_budget_generation_vs_verification.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_best_generation_filters_budget_and_oracle():
    mod = load_module()
    rows = [
        {"dataset": "D", "policy": "a", "extra_sample_tokens_per_problem": "10", "delta_cluster_sum_vs_base": "0.1", "delta_any_correct_vs_base": "0.0"},
        {"dataset": "D", "policy": "b", "extra_sample_tokens_per_problem": "20", "delta_cluster_sum_vs_base": "0.2", "delta_any_correct_vs_base": "0.0"},
        {"dataset": "D", "policy": "oracle_hidden_gain", "extra_sample_tokens_per_problem": "5", "delta_cluster_sum_vs_base": "0.5", "delta_any_correct_vs_base": "0.0"},
    ]

    best = mod.best_generation(rows, "D", 15, include_oracle=False)
    oracle = mod.best_generation(rows, "D", 15, include_oracle=True)

    assert best["policy"] == "a"
    assert oracle["policy"] == "oracle_hidden_gain"


def test_build_rows_matches_verifier_budget():
    mod = load_module()
    gen = [{"dataset": "D", "policy": "a", "extra_sample_tokens_per_problem": "10", "delta_cluster_sum_vs_base": "0.1", "delta_any_correct_vs_base": "0.2"}]
    ver = [{"dataset": "D", "budget_tokens_per_problem": "512", "delta_mean": "0.3", "acc_mean": "0.7", "spent_tokens_mean": "511"}]

    rows = mod.build_rows(gen, ver, [512.0])

    assert rows[0]["rank_bucket_delta"] == 0.3
    assert rows[0]["best_generation_delta"] == 0.1


def main():
    test_best_generation_filters_budget_and_oracle()
    test_build_rows_matches_verifier_budget()
    print("ok")


if __name__ == "__main__":
    main()
