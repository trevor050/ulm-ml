#!/usr/bin/env python3
"""Dependency-light symbolic/process feature scorer for deployed-mix packets."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
import re
import warnings
from fractions import Fraction
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


TCS = load_module("text_cluster_semantic_scorer", ROOT / "work" / "text_cluster_semantic_scorer.py")
SDMV = TCS.SDMV

FRAC_RE = re.compile(r"\\frac\{(-?\d+)\}\{(-?\d+)\}")
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?(?:/-?\d+)?")
EQUATION_RE = re.compile(r"([0-9][0-9\s+\-*/().^{}\\frac]*?)=([0-9][0-9\s+\-*/().^{}\\frac]*)(?=[^0-9]|$)")
SAFE_EXPR_RE = re.compile(r"^[0-9\s+\-*/().]+$")


def parse_fraction(text: object) -> Fraction | None:
    raw = str(text or "").strip()
    if not raw:
        return None
    raw = FRAC_RE.sub(lambda m: f"{m.group(1)}/{m.group(2)}", raw)
    raw = raw.replace("$", "").replace(",", "").strip()
    if raw.startswith("\\boxed{") and raw.endswith("}"):
        raw = raw[7:-1]
    if not re.fullmatch(r"-?\d+(?:/\-?\d+|\.\d+)?", raw):
        return None
    try:
        return Fraction(raw)
    except (ValueError, ZeroDivisionError):
        return None


def expr_to_fraction(expr: str) -> Fraction | None:
    text = FRAC_RE.sub(lambda m: f"({m.group(1)})/({m.group(2)})", expr)
    text = text.replace("\\cdot", "*").replace("\\times", "*").replace("^", "**")
    text = text.replace("{", "(").replace("}", ")")
    text = text.replace("$", "").strip()
    if "**" in text or not SAFE_EXPR_RE.fullmatch(text):
        return None
    if re.search(r"\d\s*\(", text) or re.search(r"\)\s*\d", text):
        return None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            value = eval(text, {"__builtins__": {}}, {})
    except Exception:
        return None
    try:
        return Fraction(value).limit_denominator(10**6)
    except (ValueError, ZeroDivisionError):
        return None


def arithmetic_stats(text: str, max_checks: int = 12) -> dict[str, float]:
    checks = true = false = 0
    for match in EQUATION_RE.finditer(text.replace("\n", " ")):
        if checks >= max_checks:
            break
        left = expr_to_fraction(match.group(1))
        right = expr_to_fraction(match.group(2))
        if left is None or right is None:
            continue
        checks += 1
        if left == right:
            true += 1
        else:
            false += 1
    return {
        "arith_checks": float(checks),
        "arith_true": float(true),
        "arith_false": float(false),
        "arith_true_frac": true / checks if checks else 0.0,
        "arith_false_frac": false / checks if checks else 0.0,
    }


def answer_shape(answer: object, baseline: object) -> dict[str, float]:
    raw = str(answer or "")
    frac = parse_fraction(raw)
    baseline_frac = parse_fraction(baseline)
    nums = NUMBER_RE.findall(raw)
    out = {
        "answer_len_log": math.log1p(len(raw)),
        "answer_numeric_count": float(len(nums)),
        "answer_is_parseable_number": 1.0 if frac is not None else 0.0,
        "answer_has_frac": 1.0 if "/" in raw or "\\frac" in raw else 0.0,
        "answer_has_decimal": 1.0 if "." in raw else 0.0,
        "answer_has_alpha": 1.0 if re.search(r"[A-Za-z]", raw) else 0.0,
        "answer_has_setlike": 1.0 if any(ch in raw for ch in "{}[](),") else 0.0,
        "answer_has_radical": 1.0 if "sqrt" in raw or "√" in raw else 0.0,
        "answer_exact_baseline_match": 1.0 if raw == str(baseline or "") else 0.0,
        "answer_numeric_baseline_match": 0.0,
        "answer_numeric_abs_log": 0.0,
        "answer_numeric_den_log": 0.0,
        "answer_numeric_is_integer": 0.0,
        "answer_numeric_is_negative": 0.0,
    }
    if frac is not None:
        out["answer_numeric_abs_log"] = math.log1p(abs(float(frac)))
        out["answer_numeric_den_log"] = math.log1p(abs(frac.denominator))
        out["answer_numeric_is_integer"] = 1.0 if frac.denominator == 1 else 0.0
        out["answer_numeric_is_negative"] = 1.0 if frac < 0 else 0.0
        out["answer_numeric_baseline_match"] = 1.0 if baseline_frac is not None and frac == baseline_frac else 0.0
    return out


def feature_dict(packet: dict, cluster: dict, args: argparse.Namespace) -> dict[str, float]:
    feats = TCS.numeric_features(packet, cluster)
    feats.update(answer_shape(cluster.get("answer"), packet.get("baseline_answer")))
    rep_stats = []
    for rep in cluster.get("representatives", [])[: args.representatives_per_cluster]:
        rep_stats.append(arithmetic_stats(str(rep.get("text") or ""), args.max_arithmetic_checks))
    for key in ["arith_checks", "arith_true", "arith_false", "arith_true_frac", "arith_false_frac"]:
        vals = [row[key] for row in rep_stats]
        feats[f"rep_{key}_mean"] = sum(vals) / len(vals) if vals else 0.0
        feats[f"rep_{key}_max"] = max(vals) if vals else 0.0
    feats["rep_has_arithmetic"] = 1.0 if any(row["arith_checks"] > 0 for row in rep_stats) else 0.0
    return feats


def cluster_rows(packets: list[dict], args: argparse.Namespace) -> list[tuple[dict[str, float], int, dict, dict]]:
    rows = []
    for packet in packets:
        for cluster in packet["clusters"]:
            rows.append((feature_dict(packet, cluster, args), 1 if cluster.get("is_correct_cluster") else 0, packet, cluster))
    return rows


def vectorize(rows: list[tuple[dict[str, float], int, dict, dict]]) -> tuple[list[str], np.ndarray, np.ndarray]:
    names = sorted({name for feats, _, _, _ in rows for name in feats})
    name_idx = {name: i for i, name in enumerate(names)}
    x = np.zeros((len(rows), len(names)), dtype=np.float64)
    y = np.zeros(len(rows), dtype=np.float64)
    for i, (feats, label, _, _) in enumerate(rows):
        y[i] = label
        for name, value in feats.items():
            x[i, name_idx[name]] = float(value)
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std[std < 1e-9] = 1.0
    x = (x - mean) / std
    return names, x, y


def train(rows: list[tuple[dict[str, float], int, dict, dict]], args: argparse.Namespace) -> dict:
    names, x, y = vectorize(rows)
    weights = np.zeros(x.shape[1], dtype=np.float64)
    bias = 0.0
    pos_rate = float(y.mean()) if len(y) else 0.0
    pos_weight = 0.5 / max(pos_rate, 1e-6)
    neg_weight = 0.5 / max(1.0 - pos_rate, 1e-6)
    rng = random.Random(args.seed)
    order = list(range(len(y)))
    for epoch in range(args.epochs):
        rng.shuffle(order)
        lr = args.lr / math.sqrt(epoch + 1.0)
        for i in order:
            z = float(x[i].dot(weights) + bias)
            pred = 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, z))))
            sample_weight = pos_weight if y[i] else neg_weight
            grad = sample_weight * (pred - y[i])
            weights -= lr * (grad * x[i] + args.l2 * weights)
            bias -= lr * grad
    train_feats = np.array([list(feature_dict(packet, cluster, args).values()) for _, _, packet, cluster in rows], dtype=object)
    del train_feats
    raw = np.zeros((len(rows), len(names)), dtype=np.float64)
    name_idx = {name: i for i, name in enumerate(names)}
    for i, (feats, _, _, _) in enumerate(rows):
        for name, value in feats.items():
            raw[i, name_idx[name]] = float(value)
    mean = raw.mean(axis=0)
    std = raw.std(axis=0)
    std[std < 1e-9] = 1.0
    return {"names": names, "mean": mean, "std": std, "weights": weights, "bias": bias, "positive_rate": pos_rate}


def predict_prob(model: dict, feats: dict[str, float]) -> float:
    vec = np.zeros(len(model["names"]), dtype=np.float64)
    name_idx = {name: i for i, name in enumerate(model["names"])}
    for name, value in feats.items():
        i = name_idx.get(name)
        if i is not None:
            vec[i] = float(value)
    vec = (vec - model["mean"]) / model["std"]
    z = float(vec.dot(model["weights"]) + model["bias"])
    return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, z))))


def choose_packet(packet: dict, model: dict, args: argparse.Namespace) -> dict:
    scored = []
    for cluster in packet["clusters"]:
        prob = predict_prob(model, feature_dict(packet, cluster, args))
        scored.append((prob, cluster))
    scored.sort(key=lambda item: (-item[0], int(item[1].get("rank_by_sum") or 999)))
    top, best = scored[0]
    second = scored[1][0] if len(scored) > 1 else 0.0
    return {
        "packet_id": packet["packet_id"],
        "answer": best["answer"],
        "confidence": top / max(1e-12, top + second),
        "symbolic_cluster_probability": top,
        "symbolic_cluster_margin": top - second,
        "selected_rank_by_sum": best.get("rank_by_sum"),
        "selected_support": best.get("support"),
        "selected_is_correct_cluster": bool(best.get("is_correct_cluster")),
        "model": f"symbolic_features_train={args.train_label}",
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summary_rows(predictions: list[dict], test_packets: list[dict]) -> list[dict]:
    keys = {packet["packet_id"]: TCS.answer_key_for_packet(packet) for packet in test_packets}
    scored = [SDMV.score_prediction(pred, keys[pred["packet_id"]]) for pred in predictions]
    by_cat: dict[tuple[str, str], list[dict]] = {}
    for row in scored:
        by_cat.setdefault((row["dataset"], row["category"]), []).append(row)
    out = []
    for (dataset, category), vals in sorted(by_cat.items()):
        out.append(
            {
                "dataset": dataset,
                "category": category,
                "n": len(vals),
                "correct": sum(row["correct"] for row in vals),
                "correct_rate": sum(row["correct"] for row in vals) / max(1, len(vals)),
                "baseline_preserved": sum(row["preserved_baseline"] for row in vals),
                "baseline_preservation": sum(row["preserved_baseline"] for row in vals) / max(1, len(vals)),
                "avg_confidence": SDMV.mean_confidence(vals),
            }
        )
    return out


def run(args: argparse.Namespace) -> None:
    train_packets = TCS.load_packets(args.train_packets)
    test_packets = TCS.load_packets(args.test_packets)
    raw_train_n = len(train_packets)
    if args.exclude_test_problems_from_train:
        train_packets = TCS.exclude_overlapping_problems(train_packets, test_packets)
    rows = cluster_rows(train_packets, args)
    model = train(rows, args)
    predictions = [choose_packet(packet, model, args) for packet in test_packets]
    summary = summary_rows(predictions, test_packets)

    OUT.mkdir(parents=True, exist_ok=True)
    pred_path = OUT / f"{args.output_prefix}_predictions.jsonl"
    summary_csv = OUT / f"{args.output_prefix}_summary.csv"
    write_jsonl(pred_path, predictions)
    write_csv(summary_csv, summary)
    lines = [
        "# Symbolic Feature Scorer",
        "",
        f"Train: `{args.train_label}` on `{len(train_packets)}` packets / `{len(rows)}` clusters.",
        f"Test: `{args.test_label}` on `{len(test_packets)}` packets.",
        f"Training positive cluster rate: `{model['positive_rate']:.3f}`.",
    ]
    if args.exclude_test_problems_from_train:
        lines.append(f"Problem-overlap filter kept `{len(train_packets)}` of `{raw_train_n}` train packets.")
    lines += [
        "",
        "| dataset | category | n | correct | correct rate | baseline preserved | preservation | avg confidence |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['dataset']} | {row['category']} | {row['n']} | {row['correct']} | {row['correct_rate']:.3f} | "
            f"{row['baseline_preserved']} | {row['baseline_preservation']:.3f} | {row['avg_confidence']:.3f} |"
        )
    lines += [
        "",
        "## Read",
        "",
        "This dependency-light scorer uses only cluster numeric features, answer-shape features, baseline numeric equivalence, and simple arithmetic-equation consistency checks in representative rationales. It is a local signal audit, not a measured LLM verifier.",
        "",
        f"Predictions: [{pred_path.name}]({pred_path.name}). Summary CSV: [{summary_csv.name}]({summary_csv.name}).",
    ]
    md_path = OUT / f"{args.output_prefix}.md"
    md_path.write_text("\n".join(lines))
    print(md_path)
    print(pred_path)
    print(summary_csv)
    print(md_path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-packets", type=Path, required=True)
    parser.add_argument("--test-packets", type=Path, required=True)
    parser.add_argument("--train-label", required=True)
    parser.add_argument("--test-label", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--l2", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=60601)
    parser.add_argument("--representatives-per-cluster", type=int, default=3)
    parser.add_argument("--max-arithmetic-checks", type=int, default=12)
    parser.add_argument("--exclude-test-problems-from-train", action="store_true")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
