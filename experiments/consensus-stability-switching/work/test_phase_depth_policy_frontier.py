#!/usr/bin/env python3
"""Smoke tests for phase-depth policy frontier."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("phase_depth_policy_frontier", ROOT / "work" / "phase_depth_policy_frontier.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def rows() -> list[dict]:
    base = {
        "dataset": "MATH/Tiny",
        "n": "128",
        "majority_regime": "depth-limited",
        "depth_label": "deep-top20",
    }
    return [
        {**base, "depth": "5", "cumulative_gain": "0.20", "avg_prompt_tokens": "500"},
        {**base, "depth": "10", "cumulative_gain": "0.30", "avg_prompt_tokens": "900"},
        {**base, "depth": "20", "cumulative_gain": "0.36", "avg_prompt_tokens": "2100"},
    ]


def test_policy_keeps_no_verifier_when_value_is_too_low():
    mod = load_module()
    out = mod.policy_rows(rows(), [1000.0], success=0.8, false_regress=0.02)[0]
    assert out["chosen_depth"] == 0
    assert out["utility"] == 0.0


def test_policy_can_choose_middle_depth_by_utility():
    mod = load_module()
    out = mod.policy_rows(rows(), [16000.0], success=0.8, false_regress=0.02)[0]
    assert out["chosen_depth"] == 10
    assert round(out["projected_delta"], 3) == 0.226


def test_top20_threshold_uses_extra_delta_and_tokens():
    mod = load_module()
    threshold = mod.threshold_rows(rows(), success=0.8, false_regress=0.02)[0]
    assert round(threshold["top20_extra_delta"], 3) == 0.049
    assert round(threshold["top20_extra_tokens"], 3) == 1200.0
    assert round(threshold["top20_beats_top10_value_threshold"], 3) == round(1200.0 / (0.82 * 0.06), 3)


def main():
    test_policy_keeps_no_verifier_when_value_is_too_low()
    test_policy_can_choose_middle_depth_by_utility()
    test_top20_threshold_uses_extra_delta_and_tokens()
    print("ok")


if __name__ == "__main__":
    main()
