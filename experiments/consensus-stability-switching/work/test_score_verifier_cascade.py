#!/usr/bin/env python3
"""Smoke tests for compact/full verifier cascade scoring."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("score_verifier_cascade", ROOT / "work" / "score_verifier_cascade.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows))


def test_confidence_threshold_falls_back_to_full_prediction():
    mod = load_module()
    key = {
        "a": {"correct_answers": ["1"]},
        "b": {"correct_answers": ["2"]},
        "c": {"correct_answers": ["3"]},
    }
    compact = {
        "a": {"packet_id": "a", "answer": "1", "confidence": 0.9},
        "b": {"packet_id": "b", "answer": "0", "confidence": 0.2},
        "c": {"packet_id": "c", "answer": "0", "confidence": 0.8},
    }
    full = {
        "b": {"packet_id": "b", "answer": "2", "confidence": 0.7},
    }

    rows = mod.evaluate_thresholds(key, compact, full, thresholds=[0.5])

    row = rows[0]
    assert row["compact_accuracy"] == 1 / 3
    assert row["cascade_accuracy"] == 2 / 3
    assert row["fallback_rate"] == 1 / 3


def test_missing_or_invalid_compact_prediction_triggers_fallback():
    mod = load_module()
    key = {
        "a": {"correct_answers": ["1"]},
        "b": {"correct_answers": ["2"]},
    }
    compact = {
        "a": {"packet_id": "a", "answer": None, "confidence": None},
    }
    full = {
        "a": {"packet_id": "a", "answer": "1", "confidence": 0.8},
        "b": {"packet_id": "b", "answer": "2", "confidence": 0.8},
    }

    rows = mod.evaluate_thresholds(key, compact, full, thresholds=[0.5])

    assert rows[0]["cascade_accuracy"] == 1.0
    assert rows[0]["fallback_rate"] == 1.0


def test_cli_writes_report():
    mod = load_module()
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        key_path = tmp_path / "key.json"
        compact_path = tmp_path / "compact.jsonl"
        full_path = tmp_path / "full.jsonl"
        output_prefix = tmp_path / "cascade_eval"
        key_path.write_text(json.dumps({"a": {"correct_answers": ["1"]}}))
        write_jsonl(compact_path, [{"packet_id": "a", "answer": "0", "confidence": 0.1}])
        write_jsonl(full_path, [{"packet_id": "a", "answer": "1", "confidence": 0.8}])

        mod.run(
            mod.argparse.Namespace(
                answer_key=key_path,
                compact_predictions=compact_path,
                full_predictions=full_path,
                output_prefix=str(output_prefix),
                thresholds="0.5",
            )
        )

        assert output_prefix.with_suffix(".md").exists()
        assert output_prefix.with_suffix(".csv").exists()


def main():
    test_confidence_threshold_falls_back_to_full_prediction()
    test_missing_or_invalid_compact_prediction_triggers_fallback()
    test_cli_writes_report()
    print("ok")


if __name__ == "__main__":
    main()
