"""Probe phase-valued state channels for modular state tracking.

Run with:
    python experiments/phase_state_tracking.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ulm_ml.state_tracking import (
    SequenceBatch,
    count_feature,
    fit_ridge_classifier,
    make_binary_count_batch,
    positive_exponential_features,
    predict_ridge_classifier,
    root_of_unity_predict,
)


@dataclass(frozen=True)
class AccuracyRow:
    task: str
    method: str
    in_distribution: float
    extrapolation: float
    seeds: int


def _ridge_accuracy(
    train: SequenceBatch,
    test_id: SequenceBatch,
    test_ood: SequenceBatch,
    modulus: int,
    feature_name: str,
) -> tuple[float, float]:
    feature_fn = count_feature if feature_name == "count" else positive_exponential_features
    labels = train.counts % modulus
    weights = fit_ridge_classifier(feature_fn(train), labels, n_classes=modulus)
    id_pred = predict_ridge_classifier(feature_fn(test_id), weights)
    ood_pred = predict_ridge_classifier(feature_fn(test_ood), weights)
    id_acc = np.mean(id_pred == test_id.counts % modulus)
    ood_acc = np.mean(ood_pred == test_ood.counts % modulus)
    return float(id_acc), float(ood_acc)


def run_probe(
    moduli: tuple[int, ...] = (2, 3, 5, 7),
    seeds: int = 5,
    train_size: int = 4_000,
    test_size: int = 2_000,
) -> list[AccuracyRow]:
    """Run the modular-counting probe and aggregate over seeds."""

    rows: list[AccuracyRow] = []
    methods = ("count", "positive-exp", "root-of-unity")
    for modulus in moduli:
        by_method: dict[str, list[tuple[float, float]]] = {method: [] for method in methods}
        for seed in range(seeds):
            rng = np.random.default_rng(seed)
            train = make_binary_count_batch(train_size, range(8, 65), rng)
            test_id = make_binary_count_batch(test_size, range(8, 65), rng)
            test_ood = make_binary_count_batch(test_size, range(65, 513), rng)

            for method in ("count", "positive-exp"):
                by_method[method].append(_ridge_accuracy(train, test_id, test_ood, modulus, method))

            id_acc = np.mean(root_of_unity_predict(test_id, modulus) == test_id.counts % modulus)
            ood_acc = np.mean(root_of_unity_predict(test_ood, modulus) == test_ood.counts % modulus)
            by_method["root-of-unity"].append((float(id_acc), float(ood_acc)))

        for method, values in by_method.items():
            accuracy = np.asarray(values, dtype=np.float64)
            rows.append(
                AccuracyRow(
                    task=f"count mod {modulus}",
                    method=method,
                    in_distribution=float(accuracy[:, 0].mean()),
                    extrapolation=float(accuracy[:, 1].mean()),
                    seeds=seeds,
                )
            )
    return rows


def format_markdown(rows: list[AccuracyRow]) -> str:
    """Format result rows as a compact Markdown table."""

    lines = [
        "| task | method | train/test lengths 8-64 | extrapolate lengths 65-512 | seeds |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.task} | {row.method} | {row.in_distribution:.3f} | "
            f"{row.extrapolation:.3f} | {row.seeds} |"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_markdown(run_probe()))
