#!/usr/bin/env python3
"""Smoke tests for deployed-mix verifier run report."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import json


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("deployed_mix_verifier_report", ROOT / "work" / "deployed_mix_verifier_report.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_score_predictions_tracks_missing_ids():
    mod = load_module()
    key = {
        "p1": {
            "dataset": "D",
            "correct_answers": ["7"],
            "baseline_answer": "3",
            "deployment_category": "recoverable_top5",
            "baseline_is_correct": False,
        }
    }
    scored, missing = mod.score_predictions(
        [{"packet_id": "p1", "answer": "7", "confidence": 0.9}, {"packet_id": "p2", "answer": "1"}],
        key,
    )
    assert len(scored) == 1
    assert scored[0]["correct"]
    assert missing == ["p2"]


def test_category_rows_groups_by_dataset_and_category():
    mod = load_module()
    rows = [
        {"dataset": "D", "category": "baseline_correct", "correct": True, "preserved_baseline": True, "confidence": 0.9},
        {"dataset": "D", "category": "baseline_correct", "correct": False, "preserved_baseline": False, "confidence": 0.1},
    ]
    [row] = mod.category_rows(rows)
    assert row["dataset"] == "D"
    assert row["total"] == 2
    assert row["correct"] == 1
    assert row["baseline_preserved"] == 1


def test_target_rows_uses_balanced_stats_and_observed_scores():
    mod = load_module()
    scored = [
        {"dataset": "MATH/Llama", "category": "baseline_correct", "correct": False, "preserved_baseline": False, "confidence": 0.5},
        {"dataset": "MATH/Llama", "category": "recoverable_top5", "correct": True, "preserved_baseline": False, "confidence": 0.5},
        {"dataset": "MATH/Llama", "category": "recoverable_top10_only", "correct": True, "preserved_baseline": False, "confidence": 0.5},
        {"dataset": "MATH/Llama", "category": "recoverable_top20_only", "correct": True, "preserved_baseline": False, "confidence": 0.5},
    ]
    rows = mod.target_rows(scored, ["outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv"])
    depth20 = next(row for row in rows if row["depth"] == 20)
    assert depth20["dataset"] == "MATH/Llama"
    assert depth20["baseline_regressions"] == 1
    assert depth20["tail_category"] == "recoverable_top20_only"
    assert depth20["tail_observed"] == 1


def test_expected_packet_counts_can_use_prompt_panel():
    mod = load_module()
    key = {
        "a": {"dataset": "D1"},
        "b": {"dataset": "D1"},
        "c": {"dataset": "D2"},
    }
    with TemporaryDirectory() as tmp:
        panel = Path(tmp) / "panel.jsonl"
        panel.write_text("\n".join(json.dumps(row) for row in [{"packet_id": "a"}, {"packet_id": "c", "dataset": "D2"}]))

        counts = mod.expected_packet_counts(key, [str(panel)])

        assert counts == {"D1": 1, "D2": 1}


def main():
    test_score_predictions_tracks_missing_ids()
    test_category_rows_groups_by_dataset_and_category()
    test_target_rows_uses_balanced_stats_and_observed_scores()
    test_expected_packet_counts_can_use_prompt_panel()
    print("ok")


if __name__ == "__main__":
    main()
