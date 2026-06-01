"""Small CPU-friendly baselines for associative recall.

The goal is not to compete with full neural sequence models.  These baselines make
one narrow question easy to test: how does the *memory update rule* affect length
generalization when a sequence is nothing but key-value writes plus a final query?
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class RecencyMemory:
    """Similarity lookup with a configurable recency bias.

    ``recency_bias = 0`` is ordinary softmax nearest-neighbor retrieval.  Positive
    values imitate transformer-like recency preference by adding a linear logit
    bonus to later positions.  This is deliberately simple and parameter-free.
    """

    temperature: float = 20.0
    recency_bias: float = 0.0

    def predict(self, keys: np.ndarray, values: np.ndarray, query: np.ndarray) -> np.ndarray:
        logits = self.temperature * np.einsum("bpd,bd->bp", keys, query)
        if self.recency_bias:
            positions = np.linspace(0.0, 1.0, keys.shape[1], dtype=np.float32)
            logits = logits + self.recency_bias * positions[None, :]
        weights = _softmax(logits)
        return np.einsum("bp,bpv->bv", weights, values)


@dataclass
class GatedFastWeightsMemory:
    """Fast-weights key-value memory with a scalar learned write gate.

    The memory update is an online outer product:

    ``M_t = decay * M_{t-1} + gate(k_t, v_t) * k_t v_t^T``.

    Retrieval is ``q^T M_T``.  The gate is trained by finite-difference-free Adam on
    synthetic batches.  Because this class only learns a few scalar/vector
    parameters, it is intentionally cheap enough for CPU experimentation.
    """

    key_dim: int
    value_dim: int
    decay: float = 1.0
    lr: float = 0.03
    seed: int = 0

    def __post_init__(self) -> None:
        if not 0.0 <= self.decay <= 1.0:
            raise ValueError("decay must lie in [0, 1]")
        rng = np.random.default_rng(self.seed)
        self.gate_w = rng.normal(scale=0.02, size=(self.key_dim + self.value_dim)).astype(
            np.float32
        )
        self.gate_b = np.float32(0.0)
        self._adam_m_w = np.zeros_like(self.gate_w)
        self._adam_v_w = np.zeros_like(self.gate_w)
        self._adam_m_b = np.float32(0.0)
        self._adam_v_b = np.float32(0.0)
        self._step = 0

    def _gate(self, keys: np.ndarray, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        features = np.concatenate([keys, values], axis=-1)
        pre = np.einsum("bpf,f->bp", features, self.gate_w) + self.gate_b
        gate = 1.0 / (1.0 + np.exp(-pre))
        return gate.astype(np.float32), features

    def predict(self, keys: np.ndarray, values: np.ndarray, query: np.ndarray) -> np.ndarray:
        gate, _ = self._gate(keys, values)
        powers = self.decay ** np.arange(keys.shape[1] - 1, -1, -1, dtype=np.float32)
        weighted_values = values * gate[..., None] * powers[None, :, None]
        memory = np.einsum("bpd,bpv->bdv", keys, weighted_values)
        return np.einsum("bd,bdv->bv", query, memory)

    def train_batch(
        self, keys: np.ndarray, values: np.ndarray, query: np.ndarray, target: np.ndarray
    ) -> float:
        gate, features = self._gate(keys, values)
        powers = self.decay ** np.arange(keys.shape[1] - 1, -1, -1, dtype=np.float32)
        scores = np.einsum("bpd,bd->bp", keys, query)
        coefficients = gate * powers[None, :] * scores
        pred = np.einsum("bp,bpv->bv", coefficients, values)

        error = pred - target
        loss = float(np.mean(np.sum(error * error, axis=-1)))

        batch_size = keys.shape[0]
        grad_pred = 2.0 * error / batch_size
        grad_coefficients = np.einsum("bv,bpv->bp", grad_pred, values)
        grad_gate = grad_coefficients * powers[None, :] * scores
        grad_pre = grad_gate * gate * (1.0 - gate)
        grad_w = np.einsum("bp,bpf->f", grad_pre, features).astype(np.float32)
        grad_b = np.float32(np.sum(grad_pre))
        self._adam_update(grad_w, grad_b)
        return loss

    def _adam_update(self, grad_w: np.ndarray, grad_b: np.float32) -> None:
        beta1 = 0.9
        beta2 = 0.999
        eps = 1e-8
        self._step += 1

        self._adam_m_w = beta1 * self._adam_m_w + (1.0 - beta1) * grad_w
        self._adam_v_w = beta2 * self._adam_v_w + (1.0 - beta2) * (grad_w * grad_w)
        m_hat_w = self._adam_m_w / (1.0 - beta1**self._step)
        v_hat_w = self._adam_v_w / (1.0 - beta2**self._step)
        self.gate_w -= self.lr * m_hat_w / (np.sqrt(v_hat_w) + eps)

        self._adam_m_b = np.float32(beta1 * self._adam_m_b + (1.0 - beta1) * grad_b)
        self._adam_v_b = np.float32(beta2 * self._adam_v_b + (1.0 - beta2) * (grad_b * grad_b))
        m_hat_b = self._adam_m_b / (1.0 - beta1**self._step)
        v_hat_b = self._adam_v_b / (1.0 - beta2**self._step)
        self.gate_b = np.float32(self.gate_b - self.lr * m_hat_b / (np.sqrt(v_hat_b) + eps))


@dataclass
class DeltaFastWeightsMemory:
    """Parameter-free fast weights with an online delta-rule correction.

    Rather than writing ``k_t v_t^T`` blindly, the update writes only the residual
    value not already predicted by the current memory:

    ``M_t = decay * M_{t-1} + lr * k_t (v_t - k_t^T M_{t-1})^T``.

    This is the linear associative-memory update used as a useful foil for the
    learned gate: it directly attacks fast-weight cross-talk without storing all
    previous tokens for softmax retrieval.
    """

    decay: float = 1.0
    lr: float = 1.0

    def predict(self, keys: np.ndarray, values: np.ndarray, query: np.ndarray) -> np.ndarray:
        batch_size, _, key_dim = keys.shape
        value_dim = values.shape[-1]
        memory = np.zeros((batch_size, key_dim, value_dim), dtype=np.float32)
        for position in range(keys.shape[1]):
            key = keys[:, position, :]
            value = values[:, position, :]
            current = np.einsum("bd,bdv->bv", key, memory)
            residual = value - current
            memory = self.decay * memory + self.lr * np.einsum("bd,bv->bdv", key, residual)
        return np.einsum("bd,bdv->bv", query, memory)


def cosine_accuracy(pred: np.ndarray, target: np.ndarray) -> float:
    """Mean cosine similarity, used as a scale-free recall score."""

    numerator = np.sum(pred * target, axis=-1)
    denominator = np.linalg.norm(pred, axis=-1) * np.linalg.norm(target, axis=-1)
    return float(np.mean(numerator / np.maximum(denominator, 1e-8)))


def mean_squared_error(pred: np.ndarray, target: np.ndarray) -> float:
    return float(np.mean(np.sum((pred - target) ** 2, axis=-1)))


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits, axis=-1, keepdims=True)
    exp = np.exp(shifted)
    return exp / np.sum(exp, axis=-1, keepdims=True)
