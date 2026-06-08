#!/usr/bin/env python3
"""Smoke tests for prompt-panel filtering."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "filter_verifier_prompt_panel",
        ROOT / "work" / "filter_verifier_prompt_panel.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_read_ids_from_text_and_csv():
    mod = load_module()
    with TemporaryDirectory() as tmp:
        text = Path(tmp) / "ids.txt"
        csv_path = Path(tmp) / "ids.csv"
        text.write_text("a\nb\n")
        csv_path.write_text("packet_id,category\na,x\nb,y\n")

        assert mod.read_ids(text) == ["a", "b"]
        assert mod.read_ids(csv_path) == ["a", "b"]


def test_load_prompt_rows_and_dataset_inference():
    mod = load_module()
    with TemporaryDirectory() as tmp:
        prompts = Path(tmp) / "prompts.jsonl"
        prompts.write_text(json.dumps({"packet_id": "cluster_packets_math_llama_x", "messages": []}) + "\n")

        rows = mod.load_prompt_rows([prompts])

        assert sorted(rows) == ["cluster_packets_math_llama_x"]
        assert mod.dataset_for_packet("cluster_packets_math_gemma2b_x") == "MATH/Gemma"


def main():
    test_read_ids_from_text_and_csv()
    test_load_prompt_rows_and_dataset_inference()
    print("ok")


if __name__ == "__main__":
    main()
