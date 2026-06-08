#!/usr/bin/env python3
"""Smoke tests for deployed-mix policy confidence intervals."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("deployed_mix_policy_ci", ROOT / "work" / "deployed_mix_policy_ci.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_weighted_policy_metrics_uses_natural_rates_and_baseline():
    mod = load_module()
    rows = [
        {"dataset": "D", "category": "recoverable", "accepted": True, "deployed_correct": True, "baseline_preserved": False},
        {"dataset": "D", "category": "recoverable", "accepted": True, "deployed_correct": False, "baseline_preserved": False},
        {"dataset": "D", "category": "baseline_correct", "accepted": False, "deployed_correct": True, "baseline_preserved": True},
        {"dataset": "D", "category": "baseline_correct", "accepted": True, "deployed_correct": False, "baseline_preserved": False},
    ]
    rates = {"D": {"recoverable": 0.25, "baseline_correct": 0.75}}

    [point] = mod.weighted_policy_metrics(rows, rates)

    assert point["dataset"] == "D"
    assert point["total"] == 4
    assert abs(point["accept_rate"] - 0.625) < 1e-12
    assert abs(point["deployed_accuracy"] - 0.5) < 1e-12
    assert abs(point["baseline_preservation"] - 0.375) < 1e-12
    assert abs(point["deployed_delta"] - -0.25) < 1e-12


def test_bootstrap_ci_passes_when_every_stratum_improves():
    mod = load_module()
    rows = [
        {"dataset": "D", "category": "recoverable", "accepted": True, "deployed_correct": True, "baseline_preserved": False},
        {"dataset": "D", "category": "recoverable", "accepted": True, "deployed_correct": True, "baseline_preserved": False},
        {"dataset": "D", "category": "baseline_correct", "accepted": False, "deployed_correct": True, "baseline_preserved": True},
        {"dataset": "D", "category": "baseline_correct", "accepted": False, "deployed_correct": True, "baseline_preserved": True},
    ]
    rates = {"D": {"recoverable": 0.4, "baseline_correct": 0.6}}

    [point] = mod.bootstrap_ci(rows, rates, threshold=0.5, rounds=25, seed=1)

    assert point["threshold"] == 0.5
    assert abs(point["deployed_delta"] - 0.4) < 1e-12
    assert point["delta_ci_low"] > 0
    assert point["delta_ci_high"] > 0
    assert point["decision"] == "pass_lower_ci_positive"


def test_bootstrap_ci_flags_uncertain_when_lower_bound_is_not_positive():
    mod = load_module()
    rows = [
        {"dataset": "D", "category": "recoverable", "accepted": False, "deployed_correct": False, "baseline_preserved": True},
        {"dataset": "D", "category": "recoverable", "accepted": False, "deployed_correct": False, "baseline_preserved": True},
    ]
    rates = {"D": {"recoverable": 1.0, "baseline_correct": 0.0}}

    [point] = mod.bootstrap_ci(rows, rates, threshold=0.9, rounds=25, seed=1)

    assert point["deployed_delta"] == 0.0
    assert point["delta_ci_low"] == 0.0
    assert point["decision"] == "uncertain_or_negative"


def main():
    test_weighted_policy_metrics_uses_natural_rates_and_baseline()
    test_bootstrap_ci_passes_when_every_stratum_improves()
    test_bootstrap_ci_flags_uncertain_when_lower_bound_is_not_positive()
    print("ok")


if __name__ == "__main__":
    main()
