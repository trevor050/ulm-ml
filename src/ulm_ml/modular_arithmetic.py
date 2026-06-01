"""Lightweight modular-arithmetic datasets and spectral baselines.

The utilities here intentionally avoid heavyweight deep-learning dependencies so that
small grokking-related hypotheses can be checked on CPU in seconds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

EncoderName = Literal["pair_onehot", "separable_onehot", "character_interactions"]


@dataclass(frozen=True)
class ModularDataset:
    """A full binary operation table over integers modulo ``modulus``."""

    pairs: NDArray[np.int64]
    labels: NDArray[np.int64]
    modulus: int
    operation: str


def make_modular_dataset(
    modulus: int,
    operation: Literal["add", "subtract"] = "add",
) -> ModularDataset:
    """Return all ordered input pairs and labels for a modular binary operation."""

    if modulus < 2:
        msg = "modulus must be at least 2"
        raise ValueError(msg)
    left, right = np.meshgrid(np.arange(modulus), np.arange(modulus), indexing="ij")
    pairs = np.column_stack([left.ravel(), right.ravel()]).astype(np.int64)
    if operation == "add":
        labels = (pairs[:, 0] + pairs[:, 1]) % modulus
    elif operation == "subtract":
        labels = (pairs[:, 0] - pairs[:, 1]) % modulus
    else:
        msg = f"unsupported operation: {operation}"
        raise ValueError(msg)
    return ModularDataset(
        pairs=pairs,
        labels=labels.astype(np.int64),
        modulus=modulus,
        operation=operation,
    )


def stratified_table_split(
    labels: NDArray[np.int64],
    *,
    train_fraction: float,
    seed: int,
) -> tuple[NDArray[np.int64], NDArray[np.int64]]:
    """Split a complete modular table while preserving every output class in train.

    For each residue class, the same fraction of examples is sampled for training.
    This removes a boring failure mode where a classifier never sees a label.
    """

    if not 0 < train_fraction < 1:
        msg = "train_fraction must be in (0, 1)"
        raise ValueError(msg)
    rng = np.random.default_rng(seed)
    train_parts: list[NDArray[np.int64]] = []
    test_parts: list[NDArray[np.int64]] = []
    for label in np.unique(labels):
        idx = np.flatnonzero(labels == label)
        rng.shuffle(idx)
        n_train = max(1, min(len(idx) - 1, int(round(train_fraction * len(idx)))))
        train_parts.append(idx[:n_train])
        test_parts.append(idx[n_train:])
    train_idx = np.concatenate(train_parts)
    test_idx = np.concatenate(test_parts)
    rng.shuffle(train_idx)
    rng.shuffle(test_idx)
    return train_idx.astype(np.int64), test_idx.astype(np.int64)


def encode_pairs(
    pairs: NDArray[np.int64],
    *,
    modulus: int,
    encoder: EncoderName,
    max_frequency: int | None = None,
) -> NDArray[np.float64]:
    """Encode modular pairs with memorizing or character-interaction features.

    ``character_interactions`` uses real Fourier-product terms for each frequency
    ``k``: cos(kx)cos(ky), cos(kx)sin(ky), sin(kx)cos(ky), sin(kx)sin(ky). These
    are enough for a linear readout to compose cyclic characters such as
    cos(k(x+y)) and sin(k(x+y)), but they do not include the output label.
    """

    if pairs.ndim != 2 or pairs.shape[1] != 2:
        msg = "pairs must have shape (n_examples, 2)"
        raise ValueError(msg)
    if encoder == "pair_onehot":
        encoded = np.zeros((len(pairs), modulus * modulus), dtype=np.float64)
        encoded[np.arange(len(pairs)), pairs[:, 0] * modulus + pairs[:, 1]] = 1.0
        return encoded
    if encoder == "separable_onehot":
        encoded = np.zeros((len(pairs), 2 * modulus), dtype=np.float64)
        encoded[np.arange(len(pairs)), pairs[:, 0]] = 1.0
        encoded[np.arange(len(pairs)), modulus + pairs[:, 1]] = 1.0
        return encoded
    if encoder != "character_interactions":
        msg = f"unsupported encoder: {encoder}"
        raise ValueError(msg)

    frequency_count = max_frequency if max_frequency is not None else modulus // 2
    if frequency_count < 1 or frequency_count > modulus // 2:
        msg = "max_frequency must be in [1, modulus // 2]"
        raise ValueError(msg)
    x = pairs[:, 0].astype(np.float64)
    y = pairs[:, 1].astype(np.float64)
    blocks = [np.ones((len(pairs), 1), dtype=np.float64)]
    for frequency in range(1, frequency_count + 1):
        phase_x = 2.0 * np.pi * frequency * x / modulus
        phase_y = 2.0 * np.pi * frequency * y / modulus
        cos_x = np.cos(phase_x)
        sin_x = np.sin(phase_x)
        cos_y = np.cos(phase_y)
        sin_y = np.sin(phase_y)
        blocks.append(
            np.column_stack(
                [
                    cos_x * cos_y,
                    cos_x * sin_y,
                    sin_x * cos_y,
                    sin_x * sin_y,
                ]
            )
        )
    return np.column_stack(blocks)


def fit_ridge_classifier(
    features: NDArray[np.float64],
    labels: NDArray[np.int64],
    *,
    n_classes: int,
    ridge: float = 1e-6,
) -> NDArray[np.float64]:
    """Fit a one-vs-all ridge classifier by solving the primal normal equations."""

    targets = np.eye(n_classes, dtype=np.float64)[labels]
    gram = features.T @ features
    penalty = ridge * np.eye(gram.shape[0], dtype=np.float64)
    return np.linalg.solve(gram + penalty, features.T @ targets)


def accuracy(
    features: NDArray[np.float64],
    labels: NDArray[np.int64],
    weights: NDArray[np.float64],
) -> float:
    """Return multiclass accuracy for linear logits ``features @ weights``."""

    predictions = np.argmax(features @ weights, axis=1)
    return float(np.mean(predictions == labels))
