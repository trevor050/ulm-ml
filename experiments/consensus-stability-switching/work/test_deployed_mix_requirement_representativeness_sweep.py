#!/usr/bin/env python3
"""Smoke tests for deployed-mix requirement representativeness sweep."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("deployed_mix_requirement_representativeness_sweep", ROOT / "work" / "deployed_mix_requirement_representativeness_sweep.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def stats() -> dict[str, dict[str, float]]:
    return {
        "baseline_correct": {"natural_rate": 0.4, "selected_count": 16},
        "recoverable_top5": {"natural_rate": 0.2, "selected_count": 16},
        "recoverable_top10_only": {"natural_rate": 0.1, "selected_count": 8},
        "recoverable_top20_only": {"natural_rate": 0.05, "selected_count": 4},
    }


def test_rows_for_config_handles_uneven_tail_count():
    mod = load_module()
    rows = mod.rows_for_config("unique", "D", stats(), baseline_regressions=1)
    depth20 = next(row for row in rows if row["depth"] == 20)
    assert depth20["config"] == "unique"
    assert depth20["tail_category"] == "recoverable_top20_only"
    assert depth20["tail_selected_count"] == 4
    assert depth20["tail_only_successes_label"] in {"1", "2", "3", "4", ">4"}


def test_make_rows_finds_existing_configs():
    mod = load_module()
    rows = mod.make_rows(1)
    assert any(row["config"] == "balanced" and row["dataset"] == "MATH/Llama" for row in rows)
    assert any(row["config"] == "unique16" and row["dataset"] == "MATH/Gemma" for row in rows)


def main():
    test_rows_for_config_handles_uneven_tail_count()
    test_make_rows_finds_existing_configs()
    print("ok")


if __name__ == "__main__":
    main()
