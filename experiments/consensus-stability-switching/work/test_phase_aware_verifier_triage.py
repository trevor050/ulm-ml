#!/usr/bin/env python3
"""Smoke tests for phase-aware verifier triage."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("phase_aware_verifier_triage", ROOT / "work" / "phase_aware_verifier_triage.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def row(regime: str, any_correct: float, cluster_sum: float, top20_gain: float, closed: float = 1.0) -> dict:
    return {
        "dataset": "D",
        "n": "128",
        "majority_regime": regime,
        "regime_votes": f"{regime}:3",
        "any_correct_mean": str(any_correct),
        "cluster_sum_mean": str(cluster_sum),
        "headroom_mean": str(any_correct - cluster_sum),
        "top20_mean": str(cluster_sum + top20_gain),
        "top20_gain_mean": str(top20_gain),
        "top20_headroom_closed_mean": str(closed),
    }


def test_break_even_success_increases_with_regression():
    mod = load_module()
    assert round(mod.break_even_success(0.38, 0.02), 3) == 0.033
    assert mod.break_even_success(0.38, 0.05) > mod.break_even_success(0.38, 0.02)


def test_action_labels_match_regimes():
    mod = load_module()
    assert mod.action_label(row("coverage-limited", 0.31, 0.04, 0.22), 0.8, 0.02) == "defer/generate-coverage"
    assert mod.action_label(row("shallow/surfaced", 0.99, 0.86, 0.13), 0.8, 0.02) == "defer/mostly-surfaced"
    assert mod.action_label(row("depth-limited", 0.83, 0.44, 0.34, 0.89), 0.8, 0.02) == "spend/depth-20"


def test_best_targets_finds_first_spend():
    mod = load_module()
    rows = mod.triage_rows(
        [
            row("mixed", 0.67, 0.40, 0.27),
            row("depth-limited", 0.83, 0.44, 0.34, 0.89),
        ],
        verifier_success=0.8,
        false_regress=0.02,
    )
    out = mod.best_depth_targets(rows)[0]
    assert out["first_spend_n"] == 128
    assert out["final_action"] == "spend/depth-20"


def main():
    test_break_even_success_increases_with_regression()
    test_action_labels_match_regimes()
    test_best_targets_finds_first_spend()
    print("ok")


if __name__ == "__main__":
    main()
