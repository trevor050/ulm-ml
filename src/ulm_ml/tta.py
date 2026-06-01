"""Lightweight test-time adaptation utilities for logit/bias adapters.

The module intentionally stays NumPy-only so that small adaptation ideas can be
prototyped without a GPU or autograd framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

ObjectiveName = Literal["source", "entropy", "conservative", "pace"]


@dataclass(frozen=True)
class BiasAdapterConfig:
    """Configuration for unlabeled bias-only test-time adaptation."""

    objective: ObjectiveName = "pace"
    steps: int = 20
    learning_rate: float = 0.2
    entropy_floor: float = 0.35
    prior_weight: float = 1.0
    confidence_quantile: float = 0.5
    eps: float = 1e-8


def softmax(logits: NDArray[np.float64]) -> NDArray[np.float64]:
    """Return row-wise softmax probabilities."""

    shifted = logits - logits.max(axis=1, keepdims=True)
    exp_logits = np.exp(shifted)
    return exp_logits / exp_logits.sum(axis=1, keepdims=True)


def entropy(probs: NDArray[np.float64], eps: float = 1e-8) -> NDArray[np.float64]:
    """Return per-row categorical entropy."""

    clipped = np.clip(probs, eps, 1.0)
    return -np.sum(clipped * np.log(clipped), axis=1)


def class_prior(
    labels: NDArray[np.int64], n_classes: int, smoothing: float = 1.0
) -> NDArray[np.float64]:
    """Estimate a smoothed class prior from integer labels."""

    counts = np.bincount(labels, minlength=n_classes).astype(np.float64) + smoothing
    return counts / counts.sum()


def _entropy_grad_logits(
    probs: NDArray[np.float64], active: NDArray[np.bool_], eps: float
) -> NDArray[np.float64]:
    """Gradient of mean active entropy with respect to logits."""

    if not np.any(active):
        return np.zeros(probs.shape[1], dtype=np.float64)
    active_probs = np.clip(probs[active], eps, 1.0)
    active_entropy = entropy(active_probs, eps)[:, None]
    per_example = -active_probs * (np.log(active_probs) + active_entropy)
    return per_example.mean(axis=0)


def _prior_grad_logits(
    probs: NDArray[np.float64], anchor_prior: NDArray[np.float64], eps: float
) -> NDArray[np.float64]:
    """Gradient of KL(mean_probs || anchor_prior) with respect to a shared bias."""

    batch_prior = np.clip(probs.mean(axis=0), eps, 1.0)
    anchor = np.clip(anchor_prior, eps, 1.0)
    grad_batch_prior = np.log(batch_prior / anchor) + 1.0
    # For each example, J_softmax @ grad_batch_prior; average over examples.
    dot = probs @ grad_batch_prior
    return np.mean(probs * (grad_batch_prior[None, :] - dot[:, None]), axis=0)


def adapt_bias(
    logits: NDArray[np.float64],
    anchor_prior: NDArray[np.float64],
    config: BiasAdapterConfig,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Adapt a shared class-bias vector on an unlabeled batch of logits.

    Returns the adapted logits and the learned bias. ``source`` is a no-op.
    ``entropy`` minimizes prediction entropy directly. ``conservative`` stops
    pushing examples once their entropy is below ``entropy_floor``. ``pace`` adds
    a class-prior KL anchor on the most confident half of the batch by default.
    """

    logits = np.asarray(logits, dtype=np.float64)
    anchor_prior = np.asarray(anchor_prior, dtype=np.float64)
    if config.objective == "source":
        return logits.copy(), np.zeros(logits.shape[1], dtype=np.float64)

    bias = np.zeros(logits.shape[1], dtype=np.float64)
    for _ in range(config.steps):
        probs = softmax(logits + bias)
        ent = entropy(probs, config.eps)
        if config.objective == "entropy":
            active = np.ones(logits.shape[0], dtype=bool)
        else:
            active = ent > config.entropy_floor
        grad = _entropy_grad_logits(probs, active, config.eps)

        if config.objective == "pace" and config.prior_weight > 0.0:
            confidence = probs.max(axis=1)
            threshold = np.quantile(confidence, config.confidence_quantile)
            confident = confidence >= threshold
            prior_probs = probs[confident] if np.any(confident) else probs
            grad += config.prior_weight * _prior_grad_logits(prior_probs, anchor_prior, config.eps)

        bias -= config.learning_rate * grad
        bias -= bias.mean()  # remove non-identifiable common offset

    return logits + bias, bias
