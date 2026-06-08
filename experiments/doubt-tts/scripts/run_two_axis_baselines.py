#!/usr/bin/env python3
"""Run and score question-only baselines for two-axis candidate routing."""

from __future__ import annotations

import argparse
import collections
import json
import math
import re
from pathlib import Path
from typing import Any

from audit_route_taxonomy_axes import compute_axis, validity_axis
from run_blinded_route_baselines import question_rule_route


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "work" / "probe" / "preregistered_benchmark_candidate_blind_inputs.jsonl"
DEFAULT_CANDIDATE = ROOT / "work" / "probe" / "preregistered_benchmark_candidate_locked.jsonl"
DEFAULT_PRED = ROOT / "work" / "probe" / "runs" / "candidate_two_axis_baseline_predictions.jsonl"
DEFAULT_SCORED = ROOT / "work" / "probe" / "runs" / "candidate_two_axis_baseline_scored_results.jsonl"
DEFAULT_JSON = ROOT / "work" / "probe" / "runs" / "candidate_two_axis_baseline_stats.json"
DEFAULT_REPORT = ROOT / "outputs" / "doubt_tts_candidate_two_axis_baselines.md"

VALIDITY_LABELS = ["answerable", "false_premise", "ambiguous"]
COMPUTE_LABELS = [
    "direct_answer",
    "premise_check",
    "retrieve_then_answer",
    "retrieve_then_premise_check",
    "deterministic_verify",
    "clarify",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def wilson_bounds(num: int, den: int, z: float = 1.96) -> tuple[float, float]:
    if den == 0:
        return (0.0, 0.0)
    p = num / den
    denom = 1 + z * z / den
    center = (p + z * z / (2 * den)) / denom
    radius = z * math.sqrt((p * (1 - p) + z * z / (4 * den)) / den) / denom
    return (max(0.0, center - radius), min(1.0, center + radius))


def fmt_prop(num: int, den: int) -> str:
    if den == 0:
        return "n/a"
    low, high = wilson_bounds(num, den)
    return f"{num}/{den} ({num / den:.3f}, 95% CI {low:.3f}-{high:.3f})"


def route_to_axes(route: str, question: str) -> tuple[str, str, str]:
    if route == "ordinary":
        return "answerable", "direct_answer", "single-route projection"
    if route == "false_premise_risk":
        return "false_premise", "premise_check", "single-route projection"
    if route == "ambiguous":
        return "ambiguous", "clarify", "single-route projection"
    if route == "verifier":
        return "answerable", "deterministic_verify", "single-route projection"
    if route == "retrieval_needed":
        return "answerable", "retrieve_then_answer", "single-route projection"
    return "answerable", "direct_answer", f"unknown route projection: {route}"


def overlap_heuristic(question: str) -> bool:
    q = question.lower()
    return bool(
        re.search(r"\b(after defeating|after beating|as the|hosted .* in|in .* hosted)\b", q)
        or " laureate in algebra" in q
    )


def two_axis_question_rule(question: str) -> tuple[str, str, str]:
    route, reason = question_rule_route(question)
    validity, action, projection_reason = route_to_axes(route, question)
    if route == "retrieval_needed" and overlap_heuristic(question):
        return (
            "false_premise",
            "retrieve_then_premise_check",
            f"{reason}; overlap heuristic: retrieval event with likely embedded premise",
        )
    return validity, action, f"{reason}; {projection_reason}"


def run_baselines(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        baselines = [
            ("always_answerable_direct", "answerable", "direct_answer", "constant baseline"),
            ("always_false_premise_check", "false_premise", "premise_check", "constant baseline"),
            ("always_retrieve_answer", "answerable", "retrieve_then_answer", "constant baseline"),
        ]
        for method, validity, action, reason in baselines:
            out.append({
                "id": row["id"],
                "method": method,
                "predicted_validity": validity,
                "predicted_compute_action": action,
                "reason": reason,
            })
        route, route_reason = question_rule_route(row["question"])
        validity, action, projection_reason = route_to_axes(route, row["question"])
        out.append({
            "id": row["id"],
            "method": "single_route_question_only_projection",
            "predicted_validity": validity,
            "predicted_compute_action": action,
            "reason": f"{route_reason}; {projection_reason}",
        })
        validity, action, reason = two_axis_question_rule(row["question"])
        out.append({
            "id": row["id"],
            "method": "two_axis_question_only_router",
            "predicted_validity": validity,
            "predicted_compute_action": action,
            "reason": reason,
        })
    return out


def key_rows(candidate_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out = {}
    for row in candidate_rows:
        out[row["id"]] = {
            "id": row["id"],
            "question": row["question"],
            "subtype": row["subtype"],
            "answerability": row["answerability"],
            "gold_route": row["gold_route"],
            "expected_validity": validity_axis(row["answerability"]),
            "expected_compute_action": compute_axis(row),
        }
    return out


def score(predictions: list[dict[str, Any]], keys: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    scored = []
    for pred in predictions:
        key = keys[pred["id"]]
        validity_correct = pred["predicted_validity"] == key["expected_validity"]
        compute_correct = pred["predicted_compute_action"] == key["expected_compute_action"]
        scored.append({
            **pred,
            **key,
            "validity_correct": validity_correct,
            "compute_correct": compute_correct,
            "joint_correct": validity_correct and compute_correct,
        })
    return scored


def group_by(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        groups[str(row[key])].append(row)
    return dict(groups)


def label_summary(rows: list[dict[str, Any]], expected_key: str, correct_key: str, labels: list[str]) -> dict[str, Any]:
    out = {}
    for label in labels:
        label_rows = [row for row in rows if row[expected_key] == label]
        correct = sum(bool(row[correct_key]) for row in label_rows)
        out[label] = {
            "n": len(label_rows),
            "correct": correct,
            "accuracy": correct / len(label_rows) if label_rows else 0.0,
        }
    return out


def summarize(scored: list[dict[str, Any]]) -> dict[str, Any]:
    methods = {}
    for method, rows in sorted(group_by(scored, "method").items()):
        validity = label_summary(rows, "expected_validity", "validity_correct", VALIDITY_LABELS)
        compute = label_summary(rows, "expected_compute_action", "compute_correct", COMPUTE_LABELS)
        present_validity = [row["accuracy"] for row in validity.values() if row["n"] > 0]
        present_compute = [row["accuracy"] for row in compute.values() if row["n"] > 0]
        methods[method] = {
            "n": len(rows),
            "joint_correct": sum(bool(row["joint_correct"]) for row in rows),
            "validity_correct": sum(bool(row["validity_correct"]) for row in rows),
            "compute_correct": sum(bool(row["compute_correct"]) for row in rows),
            "joint_accuracy": sum(bool(row["joint_correct"]) for row in rows) / len(rows),
            "validity_accuracy": sum(bool(row["validity_correct"]) for row in rows) / len(rows),
            "compute_accuracy": sum(bool(row["compute_correct"]) for row in rows) / len(rows),
            "macro_validity_accuracy": sum(present_validity) / len(present_validity),
            "macro_compute_accuracy": sum(present_compute) / len(present_compute),
            "validity": validity,
            "compute": compute,
        }
    return {"methods": methods}


def write_report(path: Path, payload: dict[str, Any]) -> None:
    methods = payload["methods"]
    lines = [
        "# Doubt-TTS Candidate Two-Axis Baselines",
        "",
        "These baselines score candidate rows on separate validity and compute-action axes. They see only the blinded question text.",
        "",
        "## Method Accuracy",
        "",
        "| method | n | joint accuracy | validity accuracy | compute-action accuracy | macro validity | macro compute |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for method, row in sorted(methods.items()):
        lines.append(
            f"| {method} | {row['n']} | {fmt_prop(row['joint_correct'], row['n'])} | "
            f"{fmt_prop(row['validity_correct'], row['n'])} | {fmt_prop(row['compute_correct'], row['n'])} | "
            f"{row['macro_validity_accuracy']:.3f} | {row['macro_compute_accuracy']:.3f} |"
        )

    lines.extend([
        "",
        "## Validity-Conditional Accuracy",
        "",
        "| method | answerable | false premise | ambiguous |",
        "|---|---:|---:|---:|",
    ])
    for method, row in sorted(methods.items()):
        validity = row["validity"]
        lines.append(
            f"| {method} | {fmt_prop(validity['answerable']['correct'], validity['answerable']['n'])} | "
            f"{fmt_prop(validity['false_premise']['correct'], validity['false_premise']['n'])} | "
            f"{fmt_prop(validity['ambiguous']['correct'], validity['ambiguous']['n'])} |"
        )

    lines.extend([
        "",
        "## Compute-Action Conditional Accuracy",
        "",
        "| method | direct answer | premise check | retrieve answer | retrieve premise check | deterministic verify | clarify |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for method, row in sorted(methods.items()):
        compute = row["compute"]
        lines.append(
            f"| {method} | "
            f"{fmt_prop(compute['direct_answer']['correct'], compute['direct_answer']['n'])} | "
            f"{fmt_prop(compute['premise_check']['correct'], compute['premise_check']['n'])} | "
            f"{fmt_prop(compute['retrieve_then_answer']['correct'], compute['retrieve_then_answer']['n'])} | "
            f"{fmt_prop(compute['retrieve_then_premise_check']['correct'], compute['retrieve_then_premise_check']['n'])} | "
            f"{fmt_prop(compute['deterministic_verify']['correct'], compute['deterministic_verify']['n'])} | "
            f"{fmt_prop(compute['clarify']['correct'], compute['clarify']['n'])} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        "- The single-route projection is the old five-route question-only baseline mapped onto the new axes.",
        "- The two-axis question-only router adds a lexical overlap heuristic for event questions with embedded opponent/host/winner premises.",
        "- These are still deterministic baselines, not model evidence.",
        "- A live model should beat the two-axis question-only router on joint accuracy and should improve false-premise validity recall without collapsing answerable specificity.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PRED)
    parser.add_argument("--scored", type=Path, default=DEFAULT_SCORED)
    parser.add_argument("--out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    input_path = args.input if args.input.is_absolute() else ROOT / args.input
    candidate_path = args.candidate if args.candidate.is_absolute() else ROOT / args.candidate
    pred_path = args.predictions if args.predictions.is_absolute() else ROOT / args.predictions
    scored_path = args.scored if args.scored.is_absolute() else ROOT / args.scored
    out_path = args.out if args.out.is_absolute() else ROOT / args.out
    report_path = args.report if args.report.is_absolute() else ROOT / args.report

    input_rows = read_jsonl(input_path)
    candidates = key_rows(read_jsonl(candidate_path))
    subset_keys = {row["id"]: candidates[row["id"]] for row in input_rows}
    predictions = run_baselines(input_rows)
    scored = score(predictions, subset_keys)
    payload = {
        "source": str(input_path.relative_to(ROOT) if input_path.is_relative_to(ROOT) else input_path),
        **summarize(scored),
    }

    write_jsonl(pred_path, predictions)
    write_jsonl(scored_path, scored)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_report(report_path, payload)
    print(f"wrote {display_path(pred_path)}")
    print(f"wrote {display_path(scored_path)}")
    print(f"wrote {display_path(out_path)}")
    print(f"wrote {display_path(report_path)}")


if __name__ == "__main__":
    main()
