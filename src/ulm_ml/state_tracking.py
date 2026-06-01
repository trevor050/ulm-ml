"""Small state-tracking probes for linear-time sequence models.

The utilities in this module intentionally avoid heavyweight deep-learning
frameworks.  They are meant for fast falsification of architectural priors on
algorithmic sequence tasks before spending GPU time on a full model.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


@dataclass(frozen=True)
class SequenceBatch:
    """A padded batch of binary sequences and their unpadded lengths."""

    tokens: IntArray
    lengths: IntArray

    @property
    def counts(self) -> IntArray:
        """Number of one-bits in each sequence."""

        return self.tokens.sum(axis=1).astype(np.int64)


def make_binary_count_batch(
    n_sequences: int,
    lengths: Iterable[int],
    rng: np.random.Generator,
) -> SequenceBatch:
    """Sample padded binary sequences with lengths drawn from ``lengths``."""

    length_values = np.asarray(list(lengths), dtype=np.int64)
    if length_values.ndim != 1 or len(length_values) == 0:
        raise ValueError("lengths must contain at least one integer")
    if np.any(length_values <= 0):
        raise ValueError("all sequence lengths must be positive")

    sampled_lengths = rng.choice(length_values, size=n_sequences, replace=True)
    tokens = np.zeros((n_sequences, int(sampled_lengths.max())), dtype=np.int64)
    for row, length in enumerate(sampled_lengths):
        tokens[row, :length] = rng.integers(0, 2, size=int(length))
    return SequenceBatch(tokens=tokens, lengths=sampled_lengths)


def count_feature(batch: SequenceBatch) -> FloatArray:
    """Return the raw count as a deliberately weak non-periodic baseline."""

    return batch.counts[:, None].astype(np.float64)


def positive_exponential_features(
    batch: SequenceBatch,
    n_channels: int = 32,
    max_decay: float = 0.995,
) -> FloatArray:
    """Compute positive leaky-integrator features.

    Each channel follows ``h_t = lambda * h_{t-1} + x_t`` with
    ``lambda in [0, max_decay]``.  This is a compact proxy for the monotone,
    positive-eigenvalue memory available to many stable diagonal recurrences.
    """

    if n_channels <= 0:
        raise ValueError("n_channels must be positive")
    if not 0 <= max_decay < 1:
        raise ValueError("max_decay must be in [0, 1)")

    lambdas = np.linspace(0.0, max_decay, n_channels, dtype=np.float64)
    hidden = np.zeros((batch.tokens.shape[0], n_channels), dtype=np.float64)
    for step in range(batch.tokens.shape[1]):
        active = (step < batch.lengths)[:, None]
        updated = hidden * lambdas + batch.tokens[:, step, None]
        hidden = np.where(active, updated, hidden)
    return hidden


def root_of_unity_features(
    batch: SequenceBatch,
    moduli: Iterable[int] = range(2, 9),
) -> FloatArray:
    """Encode counts as real-valued roots-of-unity phase features.

    For each modulus ``m`` this returns ``cos(2*pi*c/m), sin(2*pi*c/m)``,
    where ``c`` is the count of one-bits.  Equivalently, this is the final
    state of the selective recurrence ``z_t = exp(2*pi*i*x_t/m) z_{t-1}``.
    """

    modulus_values = np.asarray(list(moduli), dtype=np.int64)
    if modulus_values.ndim != 1 or len(modulus_values) == 0:
        raise ValueError("moduli must contain at least one integer")
    if np.any(modulus_values < 2):
        raise ValueError("all moduli must be at least 2")

    counts = batch.counts.astype(np.float64)
    features: list[FloatArray] = []
    for modulus in modulus_values:
        angle = 2.0 * np.pi * counts / float(modulus)
        features.extend((np.cos(angle), np.sin(angle)))
    return np.stack(features, axis=1).astype(np.float64)


def root_of_unity_predict(batch: SequenceBatch, modulus: int) -> IntArray:
    """Decode a modulus from the corresponding root-of-unity state.

    The decoder chooses the residue whose prototype phase has largest dot
    product with the observed phase.  This is a linear readout over the two
    real phase coordinates.
    """

    if modulus < 2:
        raise ValueError("modulus must be at least 2")
    features = root_of_unity_features(batch, moduli=[modulus])
    phases = features[:, 0] + 1j * features[:, 1]
    residues = np.arange(modulus)
    prototypes = np.exp(2j * np.pi * residues / modulus)
    scores = np.real(phases[:, None] * np.conj(prototypes[None, :]))
    return scores.argmax(axis=1).astype(np.int64)


def fit_ridge_classifier(features: FloatArray, labels: IntArray, n_classes: int) -> FloatArray:
    """Fit a one-vs-all ridge classifier and return its weight matrix."""

    if n_classes < 2:
        raise ValueError("n_classes must be at least 2")
    design = np.c_[np.ones(features.shape[0]), features]
    targets = np.eye(n_classes, dtype=np.float64)[labels]
    penalty = 1e-4 * np.eye(design.shape[1], dtype=np.float64)
    return np.linalg.solve(design.T @ design + penalty, design.T @ targets)


def predict_ridge_classifier(features: FloatArray, weights: FloatArray) -> IntArray:
    """Predict classes from ridge-classifier weights."""

    design = np.c_[np.ones(features.shape[0]), features]
    return (design @ weights).argmax(axis=1).astype(np.int64)
