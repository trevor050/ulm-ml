"""Train a tiny MLP on modular-addition splits and log coverage diagnostics.

This is deliberately not a grokking run. It is a reproducible learned-model sanity
check for the stronger oracle claim from ``modular_spectral_probe.py``: do split
coverage cards predict when even a small nonlinear model has a path to
generalization?
"""

from __future__ import annotations

import argparse
import csv
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPClassifier

from ulm_ml.modular_arithmetic import encode_pairs, make_modular_dataset
from ulm_ml.modular_spectral import SplitKind, make_train_mask, split_diagnostics
from ulm_ml.paths import ARTIFACTS_DIR


@dataclass(frozen=True)
class MLPProbeRow:
    modulus: int
    fraction: float
    actual_fraction: float
    seed: int
    split: str
    hidden_units: int
    max_iter: int
    train_size: int
    missing_sums: int
    sum_count_cv: float
    design_condition: float
    train_accuracy: float
    test_accuracy: float
    n_iter: int
    converged: bool


def train_probe(
    *,
    modulus: int,
    fraction: float,
    seed: int,
    split: SplitKind,
    hidden_units: int,
    max_iter: int,
) -> MLPProbeRow:
    """Train one separable-input MLP and return accuracy plus split diagnostics."""

    dataset = make_modular_dataset(modulus)
    train_mask = make_train_mask(modulus, fraction, seed=seed, kind=split)
    features = encode_pairs(
        dataset.pairs,
        modulus=modulus,
        encoder="separable_onehot",
    )
    diagnostics = split_diagnostics(modulus, train_mask)
    model = MLPClassifier(
        hidden_layer_sizes=(hidden_units,),
        activation="relu",
        solver="adam",
        alpha=1e-4,
        batch_size=min(128, int(np.sum(train_mask))),
        learning_rate_init=0.01,
        max_iter=max_iter,
        random_state=seed,
        n_iter_no_change=max(25, max_iter // 10),
        tol=1e-5,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(features[train_mask], dataset.labels[train_mask])
    train_predictions = model.predict(features[train_mask])
    test_predictions = model.predict(features[~train_mask])
    converged = not any(isinstance(warning.message, ConvergenceWarning) for warning in caught)
    return MLPProbeRow(
        modulus=modulus,
        fraction=fraction,
        actual_fraction=diagnostics.train_fraction,
        seed=seed,
        split=split,
        hidden_units=hidden_units,
        max_iter=max_iter,
        train_size=diagnostics.train_size,
        missing_sums=diagnostics.missing_sums,
        sum_count_cv=diagnostics.sum_count_cv,
        design_condition=diagnostics.design_condition,
        train_accuracy=float(np.mean(train_predictions == dataset.labels[train_mask])),
        test_accuracy=float(np.mean(test_predictions == dataset.labels[~train_mask])),
        n_iter=int(model.n_iter_),
        converged=converged,
    )


def run_sweep(
    *,
    modulus: int,
    fractions: list[float],
    seeds: list[int],
    splits: list[SplitKind],
    hidden_units: int,
    max_iter: int,
) -> list[MLPProbeRow]:
    """Run a deterministic learned-model split sweep."""

    rows: list[MLPProbeRow] = []
    for fraction in fractions:
        for seed in seeds:
            for split in splits:
                rows.append(
                    train_probe(
                        modulus=modulus,
                        fraction=fraction,
                        seed=seed,
                        split=split,
                        hidden_units=hidden_units,
                        max_iter=max_iter,
                    )
                )
    return rows


def summarize(rows: list[MLPProbeRow]) -> str:
    """Return a compact split-level accuracy summary."""

    grouped: dict[tuple[float, str], list[MLPProbeRow]] = {}
    for row in rows:
        grouped.setdefault((row.fraction, row.split), []).append(row)
    lines = [
        "fraction split        mean_test_acc mean_missing_sums mean_sum_cv",
        "-------- ------------ ------------- ---------------- -------------",
    ]
    for (fraction, split), group in sorted(grouped.items()):
        lines.append(
            f"{fraction:8.2f} {split:12s} "
            f"{np.mean([row.test_accuracy for row in group]):13.3f} "
            f"{np.mean([row.missing_sums for row in group]):16.2f} "
            f"{np.mean([row.sum_count_cv for row in group]):13.3f}"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modulus", type=int, default=31)
    parser.add_argument("--fractions", type=float, nargs="+", default=[0.10, 0.20, 0.35])
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument(
        "--splits",
        nargs="+",
        choices=["random", "sum_balanced", "operand_block"],
        default=["random", "sum_balanced", "operand_block"],
    )
    parser.add_argument("--hidden-units", type=int, default=128)
    parser.add_argument("--max-iter", type=int, default=500)
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTIFACTS_DIR / "modular_mlp_split_probe.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = run_sweep(
        modulus=args.modulus,
        fractions=args.fractions,
        seeds=args.seeds,
        splits=args.splits,
        hidden_units=args.hidden_units,
        max_iter=args.max_iter,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(MLPProbeRow.__dataclass_fields__))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
    print(summarize(rows))
    print(f"\nwrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
