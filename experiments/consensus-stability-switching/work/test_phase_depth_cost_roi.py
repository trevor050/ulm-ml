#!/usr/bin/env python3
"""Smoke tests for phase-depth cost ROI."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("phase_depth_cost_roi", ROOT / "work" / "phase_depth_cost_roi.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def marginal_row(dataset: str = "MATH/Llama") -> dict:
    return {
        "dataset": dataset,
        "n": "128",
        "majority_regime": "depth-limited",
        "top5_gain": "0.20",
        "top10_gain": "0.30",
        "top20_gain": "0.36",
        "depth_label": "deep-top20",
    }


def costs(dataset: str = "MATH/Llama") -> dict:
    return {
        (dataset, 5): {"avg_prompt_tokens": 500.0, "p90_prompt_chars": 2100, "count": 10},
        (dataset, 10): {"avg_prompt_tokens": 900.0, "p90_prompt_chars": 3600, "count": 10},
        (dataset, 20): {"avg_prompt_tokens": 2100.0, "p90_prompt_chars": 8400, "count": 10},
    }


def test_cost_rows_computes_marginal_roi():
    mod = load_module()
    rows = mod.cost_rows([marginal_row()], costs())
    depth20 = next(row for row in rows if row["depth"] == 20)
    assert round(depth20["marginal_gain"], 3) == 0.06
    assert round(depth20["marginal_tokens"], 3) == 1200.0
    assert round(depth20["tokens_per_marginal_point"], 3) == 20000.0
    assert round(depth20["marginal_gain_per_1k_tokens"], 3) == 0.05


def test_transition_rows_picks_best_marginal_depth():
    mod = load_module()
    rows = mod.cost_rows([marginal_row()], costs())
    trans = mod.transition_rows(rows)[0]
    assert trans["best_marginal_depth"] == 5
    assert round(trans["top20_tokens_per_marginal_point"], 3) == 20000.0


def test_prompt_token_stats_reads_user_message(tmp_path: Path):
    mod = load_module()
    path = tmp_path / "prompts.jsonl"
    rows = [
        {"messages": [{"role": "system", "content": "x"}, {"role": "user", "content": "a" * 40}]},
        {"messages": [{"role": "user", "content": "b" * 80}]},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    stats = mod.prompt_token_stats(path, chars_per_token=4.0)
    assert stats["count"] == 2
    assert stats["avg_prompt_tokens"] == 15.0
    assert stats["p90_prompt_chars"] == 80


def main():
    tmp = ROOT / "outputs" / ".tmp_test_phase_depth_cost_roi"
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        test_cost_rows_computes_marginal_roi()
        test_transition_rows_picks_best_marginal_depth()
        test_prompt_token_stats_reads_user_message(tmp)
    finally:
        for path in tmp.glob("*"):
            path.unlink()
        tmp.rmdir()
    print("ok")


if __name__ == "__main__":
    main()
