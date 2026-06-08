#!/usr/bin/env python3
"""Score validity/action predictions against the separate blinded label key."""

from __future__ import annotations

import argparse
import collections
import json
import math
from pathlib import Path
from typing import Any

from audit_route_taxonomy_axes import compute_axis, validity_axis


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KEY = ROOT / "work" / "probe" / "preregistered_benchmark_candidate_label_key.jsonl"
DEFAULT_OUT = ROOT / "work" / "probe" / "runs" / "two_axis_scored_results.jsonl"
DEFAULT_STATS = ROOT / "work" / "probe" / "runs" / "two_axis_score_stats.json"
DEFAULT_REPORT = ROOT / "outputs" / "doubt_tts_two_axis_score_report.md"

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


def exact_mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(b, c) + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def normalize_validity(value: Any) -> str:
    text = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "valid": "answerable",
        "ordinary": "answerable",
        "retrieval_required": "answerable",
        "verifier_solvable": "answerable",
        "false": "false_premise",
        "false_premise_risk": "false_premise",
        "invalid_premise": "false_premise",
        "underspecified": "ambiguous",
        "clarify": "ambiguous",
        "needs_clarification": "ambiguous",
    }
    text = aliases.get(text, text)
    return text if text in VALIDITY_LABELS else "__invalid__"


def normalize_compute_action(value: Any) -> str:
    text = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "ordinary": "direct_answer",
        "answer": "direct_answer",
        "answer_directly": "direct_answer",
        "false_premise": "premise_check",
        "false_premise_risk": "premise_check",
        "false_premise_check": "premise_check",
        "presupposition_check": "premise_check",
        "retrieve": "retrieve_then_answer",
        "retrieval": "retrieve_then_answer",
        "retrieval_needed": "retrieve_then_answer",
        "search": "retrieve_then_answer",
        "retrieve_premise": "retrieve_then_premise_check",
        "retrieve_then_check": "retrieve_then_premise_check",
        "retrieval_premise_check": "retrieve_then_premise_check",
        "evidence_then_premise_check": "retrieve_then_premise_check",
        "verify": "deterministic_verify",
        "verifier": "deterministic_verify",
        "verification": "deterministic_verify",
        "ask_clarification": "clarify",
        "clarification": "clarify",
        "ambiguous": "clarify",
    }
    text = aliases.get(text, text)
    return text if text in COMPUTE_LABELS else "__invalid__"


def prediction_method(pred: dict[str, Any]) -> str:
    return str(pred.get("method") or "prediction")


def key_by_id(key_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out = {}
    for row in key_rows:
        expected_validity = row.get("expected_validity") or validity_axis(str(row.get("answerability", "")))
        expected_action = row.get("expected_compute_action") or compute_axis(row)
        out[row["id"]] = {
            "id": row["id"],
            "input_hash": row.get("input_hash"),
            "subtype": row.get("subtype"),
            "answerability": row.get("answerability"),
            "gold_route": row.get("gold_route"),
            "expected_validity": expected_validity,
            "expected_compute_action": expected_action,
        }
    return out


def score(predictions: list[dict[str, Any]], key_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = key_by_id(key_rows)
    methods = sorted({prediction_method(pred) for pred in predictions}) or ["prediction"]
    seen: dict[str, set[str]] = {method: set() for method in methods}
    out: list[dict[str, Any]] = []

    for pred in predictions:
        method = prediction_method(pred)
        row_id = pred.get("id") or pred.get("question_id")
        predicted_validity = normalize_validity(pred.get("predicted_validity", pred.get("validity", "")))
        predicted_action = normalize_compute_action(
            pred.get("predicted_compute_action", pred.get("compute_action", pred.get("action", "")))
        )
        if row_id not in keys:
            out.append({
                "id": row_id,
                "method": method,
                "expected_validity": "__missing_key__",
                "expected_compute_action": "__missing_key__",
                "predicted_validity": predicted_validity,
                "predicted_compute_action": predicted_action,
                "validity_correct": False,
                "compute_correct": False,
                "joint_correct": False,
                "error": "prediction id not found in label key",
                "raw_prediction": pred,
            })
            continue
        if row_id in seen[method]:
            key = keys[row_id]
            out.append({
                **key,
                "method": method,
                "predicted_validity": predicted_validity,
                "predicted_compute_action": predicted_action,
                "validity_correct": False,
                "compute_correct": False,
                "joint_correct": False,
                "error": "duplicate prediction id",
                "raw_prediction": pred,
            })
            continue
        seen[method].add(row_id)
        key = keys[row_id]
        validity_correct = predicted_validity == key["expected_validity"]
        compute_correct = predicted_action == key["expected_compute_action"]
        out.append({
            **key,
            "method": method,
            "predicted_validity": predicted_validity,
            "predicted_compute_action": predicted_action,
            "validity_correct": validity_correct,
            "compute_correct": compute_correct,
            "joint_correct": validity_correct and compute_correct,
            "raw_prediction": pred,
        })

    for method in methods:
        for row_id, key in keys.items():
            if row_id not in seen[method]:
                out.append({
                    **key,
                    "method": method,
                    "predicted_validity": "__missing_prediction__",
                    "predicted_compute_action": "__missing_prediction__",
                    "validity_correct": False,
                    "compute_correct": False,
                    "joint_correct": False,
                    "error": "missing prediction",
                })
    return out


def group_by(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        groups[str(row.get(key, ""))].append(row)
    return dict(groups)


def label_summary(rows: list[dict[str, Any]], expected_key: str, correct_key: str, labels: list[str]) -> dict[str, Any]:
    out = {}
    for label in labels:
        label_rows = [row for row in rows if row.get(expected_key) == label]
        correct = sum(bool(row.get(correct_key)) for row in label_rows)
        out[label] = {
            "n": len(label_rows),
            "correct": correct,
            "accuracy": correct / len(label_rows) if label_rows else 0.0,
        }
    return out


def confusion(rows: list[dict[str, Any]], expected_key: str, predicted_key: str, labels: list[str]) -> dict[str, Any]:
    extra_predictions = sorted({
        str(row.get(predicted_key, ""))
        for row in rows
        if str(row.get(predicted_key, "")) not in labels
    })
    columns = labels + extra_predictions
    matrix = {expected: {predicted: 0 for predicted in columns} for expected in labels}
    for row in rows:
        expected = str(row.get(expected_key, "__missing__"))
        predicted = str(row.get(predicted_key, "__missing__"))
        matrix.setdefault(expected, {col: 0 for col in columns})
        matrix[expected].setdefault(predicted, 0)
        matrix[expected][predicted] += 1
    return {"columns": columns, "matrix": matrix}


def summarize(scored: list[dict[str, Any]]) -> dict[str, Any]:
    methods = {}
    for method, rows in sorted(group_by(scored, "method").items()):
        validity = label_summary(rows, "expected_validity", "validity_correct", VALIDITY_LABELS)
        compute = label_summary(rows, "expected_compute_action", "compute_correct", COMPUTE_LABELS)
        present_validity = [row["accuracy"] for row in validity.values() if row["n"] > 0]
        present_compute = [row["accuracy"] for row in compute.values() if row["n"] > 0]
        methods[method] = {
            "n": len(rows),
            "joint_correct": sum(bool(row.get("joint_correct")) for row in rows),
            "validity_correct": sum(bool(row.get("validity_correct")) for row in rows),
            "compute_correct": sum(bool(row.get("compute_correct")) for row in rows),
            "joint_accuracy": sum(bool(row.get("joint_correct")) for row in rows) / len(rows) if rows else 0.0,
            "validity_accuracy": sum(bool(row.get("validity_correct")) for row in rows) / len(rows) if rows else 0.0,
            "compute_accuracy": sum(bool(row.get("compute_correct")) for row in rows) / len(rows) if rows else 0.0,
            "macro_validity_accuracy": sum(present_validity) / len(present_validity) if present_validity else 0.0,
            "macro_compute_accuracy": sum(present_compute) / len(present_compute) if present_compute else 0.0,
            "validity": validity,
            "compute": compute,
            "validity_confusion": confusion(rows, "expected_validity", "predicted_validity", VALIDITY_LABELS),
            "compute_confusion": confusion(rows, "expected_compute_action", "predicted_compute_action", COMPUTE_LABELS),
            "errors": collections.Counter(str(row.get("error")) for row in rows if row.get("error")),
        }
    return {"methods": methods}


def paired_comparison(scored: list[dict[str, Any]], method_a: str, method_b: str, correct_key: str) -> dict[str, Any]:
    by_method_id = {(row.get("method"), row.get("id")): row for row in scored}
    ids = sorted({row.get("id") for row in scored if row.get("method") in {method_a, method_b}})
    a_only = 0
    b_only = 0
    both_correct = 0
    both_wrong = 0
    usable = 0
    for row_id in ids:
        a = by_method_id.get((method_a, row_id))
        b = by_method_id.get((method_b, row_id))
        if not a or not b:
            continue
        usable += 1
        ac = bool(a.get(correct_key))
        bc = bool(b.get(correct_key))
        if ac and bc:
            both_correct += 1
        elif ac and not bc:
            a_only += 1
        elif not ac and bc:
            b_only += 1
        else:
            both_wrong += 1
    return {
        "method_a": method_a,
        "method_b": method_b,
        "metric": correct_key,
        "n": usable,
        "a_only": a_only,
        "b_only": b_only,
        "both_correct": both_correct,
        "both_wrong": both_wrong,
        "net_a_b": a_only - b_only,
        "exact_p": exact_mcnemar_p(a_only, b_only),
    }


def write_report(
    path: Path,
    payload: dict[str, Any],
    predictions_paths: list[Path],
    key_path: Path,
    scored_path: Path,
    stats_path: Path,
) -> None:
    methods = payload["methods"]
    prediction_text = ", ".join(f"`{display_path(path)}`" for path in predictions_paths)
    lines = [
        "# Doubt-TTS Two-Axis Score Report",
        "",
        f"Predictions: {prediction_text}",
        f"Label key: `{display_path(key_path)}`",
        f"Scored rows: `{display_path(scored_path)}`",
        f"Stats JSON: `{display_path(stats_path)}`",
        "",
        "The scorer uses the separate label key. The model-facing blind input file must not contain label, source, evidence, subtype, or answerability fields.",
        "",
        "## Method Accuracy",
        "",
        "| method | n | joint accuracy | validity accuracy | compute-action accuracy | macro validity | macro compute | errors |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for method, row in sorted(methods.items()):
        errors = ", ".join(f"{name}:{count}" for name, count in row["errors"].items()) or "none"
        lines.append(
            f"| {method} | {row['n']} | {fmt_prop(row['joint_correct'], row['n'])} | "
            f"{fmt_prop(row['validity_correct'], row['n'])} | {fmt_prop(row['compute_correct'], row['n'])} | "
            f"{row['macro_validity_accuracy']:.3f} | {row['macro_compute_accuracy']:.3f} | {errors} |"
        )

    lines.extend(["", "## Validity-Conditional Accuracy", "", "| method | answerable | false premise | ambiguous |", "|---|---:|---:|---:|"])
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

    lines.extend(["", "## Confusion Matrices", ""])
    for method, row in sorted(methods.items()):
        for title, key in [("Validity", "validity_confusion"), ("Compute Action", "compute_confusion")]:
            confusion_payload = row[key]
            columns = confusion_payload["columns"]
            labels = VALIDITY_LABELS if title == "Validity" else COMPUTE_LABELS
            lines.extend([
                f"### {method} / {title}",
                "",
                "| expected \\ predicted | " + " | ".join(columns) + " |",
                "|---|" + "|".join("---:" for _ in columns) + "|",
            ])
            matrix = confusion_payload["matrix"]
            for expected in labels:
                counts = matrix.get(expected, {})
                lines.append(f"| {expected} | " + " | ".join(str(counts.get(predicted, 0)) for predicted in columns) + " |")
            lines.append("")

    if payload.get("comparisons"):
        lines.extend([
            "## Paired Exact Tests",
            "",
            "| metric | method A | method B | n | A only | B only | net A-B | exact p |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ])
        for row in payload["comparisons"]:
            lines.append(
                f"| {row['metric']} | {row['method_a']} | {row['method_b']} | {row['n']} | "
                f"{row['a_only']} | {row['b_only']} | {row['net_a_b']:+d} | {row['exact_p']:.4g} |"
            )
        lines.append("")

    lines.extend([
        "## Interpretation",
        "",
        "- Joint accuracy requires both validity and compute action to be correct.",
        "- Validity false-premise recall is measured over all false-premise rows, including rows whose compute action is retrieval-backed premise checking.",
        "- Compute-action `retrieve_then_premise_check` recall is the key overlap metric missing from the older one-label route setup.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, nargs="+", required=True)
    parser.add_argument("--key", type=Path, default=DEFAULT_KEY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--stats", type=Path, default=DEFAULT_STATS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--compare", nargs=2, action="append", metavar=("METHOD_A", "METHOD_B"), default=[])
    args = parser.parse_args()

    prediction_paths = [path if path.is_absolute() else ROOT / path for path in args.predictions]
    key_path = args.key if args.key.is_absolute() else ROOT / args.key
    out_path = args.out if args.out.is_absolute() else ROOT / args.out
    stats_path = args.stats if args.stats.is_absolute() else ROOT / args.stats
    report_path = args.report if args.report.is_absolute() else ROOT / args.report

    predictions = []
    for path in prediction_paths:
        predictions.extend(read_jsonl(path))
    scored = score(predictions, read_jsonl(key_path))
    payload = {
        "source_predictions": [display_path(path) for path in prediction_paths],
        "source_key": display_path(key_path),
        **summarize(scored),
        "comparisons": [],
    }
    for method_a, method_b in args.compare:
        for metric in ["joint_correct", "validity_correct", "compute_correct"]:
            payload["comparisons"].append(paired_comparison(scored, method_a, method_b, metric))

    write_jsonl(out_path, scored)
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    stats_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_report(report_path, payload, prediction_paths, key_path, out_path, stats_path)
    print(f"wrote {display_path(out_path)}")
    print(f"wrote {display_path(stats_path)}")
    print(f"wrote {display_path(report_path)}")


if __name__ == "__main__":
    main()
