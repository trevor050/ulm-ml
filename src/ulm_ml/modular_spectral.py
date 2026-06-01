"""Spectral probes and split diagnostics for modular arithmetic experiments.

The utilities here are intentionally small-compute: they turn modular addition into a
closed-form Fourier/ridge probe so split pathologies can be studied before spending
GPU time on long grokking runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

SplitKind = Literal["random", "sum_balanced", "operand_block"]


@dataclass(frozen=True)
class SplitDiagnostics:
    """Coverage diagnostics for a modular-addition train split."""

    train_size: int
    modulus: int
    train_fraction: float
    min_sum_count: int
    max_sum_count: int
    missing_sums: int
    sum_count_cv: float
    design_condition: float


def modular_addition_grid(
    modulus: int,
) -> tuple[NDArray[np.int_], NDArray[np.int_], NDArray[np.int_]]:
    """Return flattened ``a``, ``b``, and ``(a + b) mod modulus`` arrays."""

    if modulus < 3:
        raise ValueError("modulus must be at least 3")
    a, b = np.meshgrid(np.arange(modulus), np.arange(modulus), indexing="ij")
    targets = (a + b) % modulus
    return a.ravel(), b.ravel(), targets.ravel()


def make_train_mask(
    modulus: int,
    train_fraction: float,
    *,
    seed: int = 0,
    kind: SplitKind = "random",
) -> NDArray[np.bool_]:
    """Construct a reproducible train mask over the full modular-addition grid.

    ``sum_balanced`` allocates nearly equal examples to every latent sum residue.
    ``operand_block`` is a deliberately bad control that trains on the lexicographically
    first examples and therefore under-covers many sum residues at small fractions.
    """

    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be strictly between 0 and 1")

    rng = np.random.default_rng(seed)
    _, _, sums = modular_addition_grid(modulus)
    total = modulus * modulus
    train_size = max(modulus, int(round(total * train_fraction)))
    train_size = min(train_size, total - 1)
    mask = np.zeros(total, dtype=bool)

    if kind == "random":
        mask[rng.choice(total, size=train_size, replace=False)] = True
        return mask

    if kind == "operand_block":
        a, b, _ = modular_addition_grid(modulus)
        width = max(1, int(np.ceil(np.sqrt(train_size))))
        candidates = np.flatnonzero((a < width) & (b < width))
        mask[candidates[:train_size]] = True
        return mask

    if kind != "sum_balanced":
        raise ValueError(f"unknown split kind: {kind}")

    base, extra = divmod(train_size, modulus)
    chosen: list[int] = []
    for residue in range(modulus):
        residue_indices = np.flatnonzero(sums == residue)
        quota = base + int(residue < extra)
        chosen.extend(rng.choice(residue_indices, size=quota, replace=False).tolist())
    mask[np.asarray(chosen, dtype=int)] = True
    return mask


def sum_counts(modulus: int, train_mask: NDArray[np.bool_]) -> NDArray[np.int_]:
    """Count how often each latent sum residue appears in the train split."""

    _, _, sums = modular_addition_grid(modulus)
    return np.bincount(sums[train_mask], minlength=modulus)


def addition_fourier_features(
    a: NDArray[np.int_], b: NDArray[np.int_], modulus: int
) -> NDArray[np.float64]:
    """Oracle real Fourier features of the latent sum coordinate ``(a + b) mod p``.

    The first column is a bias. For frequencies 1..floor((p-1)/2), the feature map
    includes cosine and sine components. This is the minimum real Fourier basis needed
    to represent one-hot modular sums when ``p`` is odd. Unlike operand-only character
    interactions, this diagnostic explicitly computes the latent sum coordinate; use it
    to test split/data geometry, not to claim a model learned the representation.
    """

    sums = (a + b) % modulus
    columns: list[NDArray[np.float64]] = [np.ones_like(sums, dtype=float)]
    for freq in range(1, (modulus // 2) + 1):
        angle = 2 * np.pi * freq * sums / modulus
        columns.append(np.cos(angle))
        columns.append(np.sin(angle))
    return np.column_stack(columns)


def one_hot(labels: NDArray[np.int_], num_classes: int) -> NDArray[np.float64]:
    """Return a dense one-hot matrix."""

    encoded = np.zeros((labels.size, num_classes), dtype=float)
    encoded[np.arange(labels.size), labels] = 1.0
    return encoded


def ridge_probe_accuracy(
    modulus: int,
    train_mask: NDArray[np.bool_],
    *,
    l2: float = 1e-6,
) -> tuple[float, float]:
    """Fit a closed-form ridge probe and return train/test accuracy."""

    a, b, targets = modular_addition_grid(modulus)
    features = addition_fourier_features(a, b, modulus)
    train_x = features[train_mask]
    train_y = one_hot(targets[train_mask], modulus)
    gram = train_x.T @ train_x
    weights = np.linalg.solve(gram + l2 * np.eye(gram.shape[0]), train_x.T @ train_y)
    predictions = np.argmax(features @ weights, axis=1)
    train_acc = float(np.mean(predictions[train_mask] == targets[train_mask]))
    test_acc = float(np.mean(predictions[~train_mask] == targets[~train_mask]))
    return train_acc, test_acc


def split_diagnostics(modulus: int, train_mask: NDArray[np.bool_]) -> SplitDiagnostics:
    """Summarize train-split coverage and Fourier design conditioning."""

    counts = sum_counts(modulus, train_mask)
    a, b, _ = modular_addition_grid(modulus)
    train_x = addition_fourier_features(a[train_mask], b[train_mask], modulus)
    singular_values = np.linalg.svd(train_x, compute_uv=False)
    condition = float(singular_values[0] / max(singular_values[-1], np.finfo(float).eps))
    return SplitDiagnostics(
        train_size=int(np.sum(train_mask)),
        modulus=modulus,
        train_fraction=float(np.mean(train_mask)),
        min_sum_count=int(np.min(counts)),
        max_sum_count=int(np.max(counts)),
        missing_sums=int(np.sum(counts == 0)),
        sum_count_cv=float(np.std(counts) / max(np.mean(counts), np.finfo(float).eps)),
        design_condition=condition,
    )


def coverage_card(
    split: str,
    diagnostics: SplitDiagnostics,
    *,
    train_acc: float,
    test_acc: float,
) -> str:
    """Format a compact latent-coverage card for a modular-addition split."""

    return (
        f"split={split} "
        f"fraction={diagnostics.train_fraction:.3f} "
        f"train_size={diagnostics.train_size} "
        f"missing_sums={diagnostics.missing_sums} "
        f"sum_count_cv={diagnostics.sum_count_cv:.3f} "
        f"design_condition={diagnostics.design_condition:.2f} "
        f"train_acc={train_acc:.3f} "
        f"test_acc={test_acc:.3f}"
    )


def run_split_sweep(
    modulus: int,
    fractions: list[float],
    seeds: list[int],
    kinds: list[SplitKind] | None = None,
) -> list[dict[str, float | int | str]]:
    """Run a small split sweep for the Fourier ridge probe."""

    split_kinds = kinds or ["random", "sum_balanced", "operand_block"]
    rows: list[dict[str, float | int | str]] = []
    for fraction in fractions:
        for seed in seeds:
            for kind in split_kinds:
                mask = make_train_mask(modulus, fraction, seed=seed, kind=kind)
                train_acc, test_acc = ridge_probe_accuracy(modulus, mask)
                diagnostics = split_diagnostics(modulus, mask)
                rows.append(
                    {
                        "modulus": modulus,
                        "fraction": fraction,
                        "actual_fraction": diagnostics.train_fraction,
                        "seed": seed,
                        "split": kind,
                        "train_size": diagnostics.train_size,
                        "train_acc": train_acc,
                        "test_acc": test_acc,
                        "min_sum_count": diagnostics.min_sum_count,
                        "max_sum_count": diagnostics.max_sum_count,
                        "missing_sums": diagnostics.missing_sums,
                        "sum_count_cv": diagnostics.sum_count_cv,
                        "design_condition": diagnostics.design_condition,
                    }
                )
    return rows
