#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "work" / "calibrated_override_selector.py"
    spec = importlib.util.spec_from_file_location("calibrated_override_selector", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_threshold_choice_and_prediction_shape():
    mod = load_module()
    packets = mod.load_packets(str(ROOT / "outputs" / "cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl"))
    fit, calib = mod.split_train_calib(packets[:24], seed=123, calib_frac=0.3)
    model, info = mod.train_model(fit, steps=20, lr=0.02, l2=1e-2)
    sweep = [mod.score_policy(calib, model, t) for t in [-0.1, 0.0, 0.1]]
    threshold = mod.choose_threshold(sweep)
    pred = mod.choose_with_threshold(calib[0], model, threshold)
    assert info["clusters"] > 0
    assert threshold in {-0.1, 0.0, 0.1}
    assert pred["packet_id"] == calib[0]["packet_id"]
    assert "answer" in pred
    assert 0.0 <= pred["confidence"] <= 1.0
    assert "override" in pred


if __name__ == "__main__":
    test_threshold_choice_and_prediction_shape()
    print("ok")
