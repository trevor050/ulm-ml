#!/usr/bin/env python3
"""Smoke tests for canonical selectability/depth table generation."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("make_canonical_selectability_depth_table", ROOT / "work" / "make_canonical_selectability_depth_table.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_canonical_rows_include_expected_datasets_and_depth_values():
    mod = load_module()
    rows = {row["dataset"]: row for row in mod.canonical_rows()}

    assert set(rows) == {"MATH/Llama", "MATH/Gemma"}
    assert abs(rows["MATH/Llama"]["selector"] - 0.44819819819819817) < 1e-12
    assert abs(rows["MATH/Gemma"]["top20"] - 0.6351351351351352) < 1e-12
    assert rows["MATH/Llama"]["miss_p90"] == "21"


def test_markdown_mentions_provenance_drift():
    mod = load_module()
    rows = mod.canonical_rows()
    text = mod.markdown(rows, Path("canonical_selectability_depth_table.csv"))

    assert "Provenance Drift Check" in text
    assert "0.846" in text
    assert "0.852" in text


def main():
    test_canonical_rows_include_expected_datasets_and_depth_values()
    test_markdown_mentions_provenance_drift()
    print("ok")


if __name__ == "__main__":
    main()
