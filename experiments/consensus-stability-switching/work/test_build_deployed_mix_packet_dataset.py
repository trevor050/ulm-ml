#!/usr/bin/env python3
"""Smoke tests for deployed-mix packet categorization."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "build_deployed_mix_packet_dataset",
        ROOT / "work" / "build_deployed_mix_packet_dataset.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def cluster(correct: bool, rank: int) -> dict:
    return {"is_correct_cluster": correct, "rank_by_sum": rank}


def test_deployed_category_names_regression_and_depth_cases():
    mod = load_module()

    assert mod.deployed_category([cluster(True, 1), cluster(False, 2)], 20) == ("baseline_correct", 1)
    assert mod.deployed_category([cluster(False, 1), cluster(True, 4)], 20) == ("recoverable_top5", 4)
    assert mod.deployed_category([cluster(False, 1), cluster(True, 8)], 20) == ("recoverable_top10_only", 8)
    assert mod.deployed_category([cluster(False, 1), cluster(True, 15)], 20) == ("recoverable_top20_only", 15)
    assert mod.deployed_category([cluster(False, 1), cluster(True, 25)], 20) == ("no_visible_top20", 25)
    assert mod.deployed_category([cluster(False, 1), cluster(False, 2)], 20) == ("no_correct_generated", None)


def test_wanted_category_respects_target():
    mod = load_module()
    counts = {"baseline_correct": 1}
    class Args:
        target_per_category = 2

    assert mod.wanted_category("baseline_correct", counts, Args)
    counts["baseline_correct"] = 2
    assert not mod.wanted_category("baseline_correct", counts, Args)


def main():
    test_deployed_category_names_regression_and_depth_cases()
    test_wanted_category_respects_target()
    print("ok")


if __name__ == "__main__":
    main()
