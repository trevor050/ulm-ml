"""Synthetic associative-recall tasks for studying cheap memory updates.

The task intentionally avoids language-model scale.  Each example is a sequence of
``(key, value)`` pairs followed by a query key; the learner must output the value
paired with the query.  At test time we can ask about longer contexts than seen in
training, which makes this a compact probe of whether an update rule has learned a
useful key-value memory rather than a fixed positional shortcut.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AssociativeRecallConfig:
    """Configuration for the synthetic associative-recall distribution."""

    key_dim: int = 32
    value_dim: int = 16
    train_pairs: int = 8
    test_pairs: tuple[int, ...] = (8, 16, 32, 64)
    train_size: int = 4096
    val_size: int = 1024
    test_size: int = 2048
    batch_size: int = 128
    key_noise: float = 0.05
    value_noise: float = 0.05
    seed: int = 0

    def __post_init__(self) -> None:
        if self.key_dim <= 0 or self.value_dim <= 0:
            raise ValueError("key_dim and value_dim must be positive")
        if self.train_pairs <= 0 or min(self.test_pairs, default=1) <= 0:
            raise ValueError("number of pairs must be positive")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.key_noise < 0 or self.value_noise < 0:
            raise ValueError("noise levels must be non-negative")


def _unit_normal(rng: np.random.Generator, shape: tuple[int, ...]) -> np.ndarray:
    x = rng.normal(size=shape).astype(np.float32)
    norm = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / np.maximum(norm, 1e-6)


def generate_associative_recall_batch(
    rng: np.random.Generator,
    *,
    batch_size: int,
    pairs: int,
    key_dim: int,
    value_dim: int,
    key_noise: float = 0.05,
    value_noise: float = 0.05,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate a batch of associative-recall examples.

    Returns ``keys, values, query, target, target_index``.  The keys and values have
    shapes ``[batch, pairs, dim]``; query and target have shapes ``[batch, dim]``.
    """

    if pairs <= 0:
        raise ValueError("pairs must be positive")

    keys = _unit_normal(rng, (batch_size, pairs, key_dim))
    values = _unit_normal(rng, (batch_size, pairs, value_dim))
    target_index = rng.integers(0, pairs, size=batch_size)
    batch_indices = np.arange(batch_size)

    query = keys[batch_indices, target_index].copy()
    if key_noise:
        query = query + rng.normal(scale=key_noise, size=query.shape).astype(np.float32)
        query = query / np.maximum(np.linalg.norm(query, axis=-1, keepdims=True), 1e-6)

    target = values[batch_indices, target_index].copy()
    if value_noise:
        values = values + rng.normal(scale=value_noise, size=values.shape).astype(np.float32)
        values = values / np.maximum(np.linalg.norm(values, axis=-1, keepdims=True), 1e-6)

    return (
        keys.astype(np.float32),
        values.astype(np.float32),
        query.astype(np.float32),
        target.astype(np.float32),
        target_index,
    )


class AssociativeRecallDataset:
    """Deterministic iterable batches for one split of associative recall."""

    def __init__(
        self,
        config: AssociativeRecallConfig,
        *,
        split: str,
        pairs: int | None = None,
        size: int | None = None,
        seed_offset: int = 0,
    ) -> None:
        self.config = config
        self.split = split
        self.pairs = config.train_pairs if pairs is None else pairs
        if size is None:
            size = {"train": config.train_size, "val": config.val_size, "test": config.test_size}[
                split
            ]
        self.size = size
        self.seed = config.seed + seed_offset

    def __iter__(
        self,
    ) -> Iterator[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        rng = np.random.default_rng(self.seed)
        remaining = self.size
        while remaining > 0:
            batch_size = min(self.config.batch_size, remaining)
            remaining -= batch_size
            yield generate_associative_recall_batch(
                rng,
                batch_size=batch_size,
                pairs=self.pairs,
                key_dim=self.config.key_dim,
                value_dim=self.config.value_dim,
                key_noise=self.config.key_noise,
                value_noise=self.config.value_noise,
            )
