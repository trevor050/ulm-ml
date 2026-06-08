#!/usr/bin/env python3
"""Smoke tests for cluster packet visibility controls."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("build_cluster_packet_dataset", ROOT / "work" / "build_cluster_packet_dataset.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_cluster(answer, correct):
    return {
        "answer": answer,
        "support": 1,
        "support_frac": 0.1,
        "sum_score": 1.0,
        "max_score": 1.0,
        "mean_score": 1.0,
        "is_correct_cluster": correct,
        "rank_by_sum": None,
        "representatives": [{"score": 1.0, "is_correct_candidate": correct, "text": answer}],
    }


def test_packetize_can_preserve_strict_topk_without_correct_injection():
    mod = load_module()
    args = argparse.Namespace(dataset_label="test", n=128, top_k=2, rationale_chars=100, representatives_per_cluster=3, force_correct_visible=False)
    clusters = [make_cluster("wrong1", False), make_cluster("wrong2", False), make_cluster("right", True)]

    packet = mod.packetize({"question": "q", "gt_answer": "right"}, clusters, args, "p0")

    assert packet["correct_answers_in_visible"] == []
    assert [cluster["answer"] for cluster in packet["clusters"]] == ["wrong1", "wrong2"]


def test_packetize_keeps_legacy_force_correct_visible_behavior():
    mod = load_module()
    args = argparse.Namespace(dataset_label="test", n=128, top_k=2, rationale_chars=100, representatives_per_cluster=3, force_correct_visible=True)
    clusters = [make_cluster("wrong1", False), make_cluster("wrong2", False), make_cluster("right", True)]

    packet = mod.packetize({"question": "q", "gt_answer": "right"}, clusters, args, "p0")

    assert packet["correct_answers_in_visible"] == ["right"]
    assert [cluster["answer"] for cluster in packet["clusters"]] == ["wrong1", "right"]


def test_eligibility_can_require_natural_correct_visibility():
    mod = load_module()
    clusters = [make_cluster("wrong1", False), make_cluster("wrong2", False), make_cluster("right", True)]
    for rank, cluster in enumerate(clusters, start=1):
        cluster["rank_by_sum"] = rank
    loose_args = argparse.Namespace(top_k=2, require_correct_visible=False, min_correct_rank=0, max_correct_rank=0)
    strict_args = argparse.Namespace(top_k=2, require_correct_visible=True, min_correct_rank=0, max_correct_rank=0)

    assert mod.packet_is_eligible(clusters, loose_args)
    assert not mod.packet_is_eligible(clusters, strict_args)


def test_eligibility_can_filter_correct_rank_range():
    mod = load_module()
    clusters = [make_cluster("wrong1", False), make_cluster("wrong2", False), make_cluster("right", True)]
    for rank, cluster in enumerate(clusters, start=1):
        cluster["rank_by_sum"] = rank
    args = argparse.Namespace(top_k=3, require_correct_visible=True, min_correct_rank=4, max_correct_rank=0)

    assert not mod.packet_is_eligible(clusters, args)


def test_problem_packet_limit_blocks_after_cap():
    mod = load_module()
    counts = {}
    unlimited = argparse.Namespace(max_packets_per_problem=0)
    limited = argparse.Namespace(max_packets_per_problem=1)

    assert mod.problem_has_capacity("p1", counts, unlimited)
    assert mod.problem_has_capacity("p1", counts, limited)
    counts["p1"] = 1
    assert not mod.problem_has_capacity("p1", counts, limited)


def main():
    test_packetize_can_preserve_strict_topk_without_correct_injection()
    test_packetize_keeps_legacy_force_correct_visible_behavior()
    test_eligibility_can_require_natural_correct_visibility()
    test_eligibility_can_filter_correct_rank_range()
    test_problem_packet_limit_blocks_after_cap()
    print("ok")


if __name__ == "__main__":
    main()
