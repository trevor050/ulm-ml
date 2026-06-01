"""Entropy-gated prototype replay for lightweight test-time adaptation.

The adapter in this module is intentionally small: it assumes a fixed feature
space and a source-trained linear classifier, then updates only class prototypes
from confident target-domain predictions.  It is designed for cheap research
loops where a full deep TTA implementation would be too expensive.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


@dataclass(frozen=True)
class EGPRConfig:
    """Configuration for :class:`EntropyGatedPrototypeReplay`.

    Attributes:
        entropy_quantile: Keep samples whose normalized entropy is below this
            running-source quantile.  Lower values adapt more conservatively.
        confidence_floor: Minimum predicted probability for a sample to be
            eligible for prototype replay.
        update_rate: Exponential moving-average rate used to update a class
            prototype with accepted target examples.
        prototype_logit_scale: Multiplier for prototype-similarity logits.
        source_logit_weight: Weight of the frozen source classifier logits in
            the adapted prediction.  Prototype logits receive weight
            ``1 - source_logit_weight``.
        min_accept_per_batch: If the entropy gate rejects every target sample,
            accept the best samples up to this count as long as they satisfy the
            confidence floor.  This avoids dead adapters on easy-but-calibrated
            batches.
    """

    entropy_quantile: float = 0.35
    confidence_floor: float = 0.55
    update_rate: float = 0.08
    prototype_logit_scale: float = 8.0
    source_logit_weight: float = 0.65
    min_accept_per_batch: int = 1

    def __post_init__(self) -> None:
        if not 0.0 < self.entropy_quantile <= 1.0:
            msg = "entropy_quantile must be in (0, 1]"
            raise ValueError(msg)
        if not 0.0 <= self.confidence_floor <= 1.0:
            msg = "confidence_floor must be in [0, 1]"
            raise ValueError(msg)
        if not 0.0 < self.update_rate <= 1.0:
            msg = "update_rate must be in (0, 1]"
            raise ValueError(msg)
        if self.prototype_logit_scale <= 0.0:
            msg = "prototype_logit_scale must be positive"
            raise ValueError(msg)
        if not 0.0 <= self.source_logit_weight <= 1.0:
            msg = "source_logit_weight must be in [0, 1]"
            raise ValueError(msg)
        if self.min_accept_per_batch < 0:
            msg = "min_accept_per_batch must be non-negative"
            raise ValueError(msg)


@dataclass(frozen=True)
class BatchAdaptationStats:
    """Diagnostics from one target-domain adaptation batch."""

    accepted: int
    entropy_threshold: float
    mean_entropy: float
    mean_confidence: float
    accepted_class_histogram: tuple[int, ...]


def softmax(logits: ArrayLike) -> FloatArray:
    """Compute a numerically stable row-wise softmax."""

    logits_array = np.asarray(logits, dtype=np.float64)
    shifted = logits_array - np.max(logits_array, axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / np.sum(exp, axis=1, keepdims=True)


def normalized_entropy(probabilities: ArrayLike) -> FloatArray:
    """Return entropy divided by ``log(num_classes)`` for each probability row."""

    probs = np.asarray(probabilities, dtype=np.float64)
    if probs.ndim != 2:
        msg = "probabilities must be a 2D array"
        raise ValueError(msg)
    num_classes = probs.shape[1]
    clipped = np.clip(probs, 1e-12, 1.0)
    return -np.sum(clipped * np.log(clipped), axis=1) / np.log(num_classes)


def l2_normalize(features: ArrayLike) -> FloatArray:
    """Normalize rows to unit length, leaving all-zero rows unchanged."""

    feature_array = np.asarray(features, dtype=np.float64)
    norms = np.linalg.norm(feature_array, axis=1, keepdims=True)
    safe_norms = np.where(norms == 0.0, 1.0, norms)
    return feature_array / safe_norms


class EntropyGatedPrototypeReplay:
    """Test-time adapter that replays confident target samples into prototypes.

    EGPR keeps the source model frozen and adapts a second prediction head made
    from class prototypes in the fixed feature space.  Target examples are
    pseudo-labeled by the source classifier.  Only low-entropy, high-confidence
    examples update prototypes, which is meant to capture useful covariate-shift
    movement without the collapse modes of all-sample entropy minimization.
    """

    def __init__(
        self,
        class_weight: ArrayLike,
        class_bias: ArrayLike,
        source_features: ArrayLike,
        source_labels: ArrayLike,
        config: EGPRConfig | None = None,
    ) -> None:
        self.config = config or EGPRConfig()
        self.class_weight = np.asarray(class_weight, dtype=np.float64)
        self.class_bias = np.asarray(class_bias, dtype=np.float64)
        self.classes_ = np.arange(self.class_weight.shape[0], dtype=np.int64)
        source_feature_array = np.asarray(source_features, dtype=np.float64)
        source_label_array = np.asarray(source_labels, dtype=np.int64)

        if self.class_weight.ndim != 2:
            msg = "class_weight must be a 2D array with shape (classes, features)"
            raise ValueError(msg)
        if self.class_bias.shape != (self.class_weight.shape[0],):
            msg = "class_bias must have shape (classes,)"
            raise ValueError(msg)
        if source_feature_array.shape[1] != self.class_weight.shape[1]:
            msg = "source feature dimension must match classifier feature dimension"
            raise ValueError(msg)

        self.prototypes = self._source_prototypes(source_feature_array, source_label_array)
        source_class_counts = np.bincount(source_label_array, minlength=len(self.classes_))
        self.prototype_counts = source_class_counts.astype(np.float64)
        source_probabilities = self.predict_source_proba(source_feature_array)
        self.source_entropy_reference = normalized_entropy(source_probabilities)

    def predict_source_logits(self, features: ArrayLike) -> FloatArray:
        """Return logits from the frozen source classifier."""

        feature_array = np.asarray(features, dtype=np.float64)
        return feature_array @ self.class_weight.T + self.class_bias

    def predict_source_proba(self, features: ArrayLike) -> FloatArray:
        """Return probabilities from the frozen source classifier."""

        return softmax(self.predict_source_logits(features))

    def predict_prototype_logits(self, features: ArrayLike) -> FloatArray:
        """Return cosine-similarity prototype logits for adapted prediction."""

        normalized_features = l2_normalize(features)
        normalized_prototypes = l2_normalize(self.prototypes)
        return self.config.prototype_logit_scale * (normalized_features @ normalized_prototypes.T)

    def predict_proba(self, features: ArrayLike) -> FloatArray:
        """Return adapted probabilities from source/prototype logit interpolation."""

        source_logits = self.predict_source_logits(features)
        prototype_logits = self.predict_prototype_logits(features)
        weight = self.config.source_logit_weight
        return softmax((weight * source_logits) + ((1.0 - weight) * prototype_logits))

    def adapt_batch(self, features: ArrayLike) -> BatchAdaptationStats:
        """Update prototypes from one unlabeled target batch and return diagnostics."""

        feature_array = np.asarray(features, dtype=np.float64)
        source_probabilities = self.predict_source_proba(feature_array)
        entropies = normalized_entropy(source_probabilities)
        confidences = np.max(source_probabilities, axis=1)
        pseudo_labels = np.argmax(source_probabilities, axis=1).astype(np.int64)
        threshold = float(np.quantile(self.source_entropy_reference, self.config.entropy_quantile))
        accepted_mask = (entropies <= threshold) & (confidences >= self.config.confidence_floor)

        if not np.any(accepted_mask) and self.config.min_accept_per_batch > 0:
            confident_order = np.argsort(entropies)
            accepted_indices: list[int] = []
            for index in confident_order:
                if confidences[index] >= self.config.confidence_floor:
                    accepted_indices.append(int(index))
                if len(accepted_indices) >= self.config.min_accept_per_batch:
                    break
            accepted_mask[accepted_indices] = True

        accepted_features = feature_array[accepted_mask]
        accepted_labels = pseudo_labels[accepted_mask]
        for class_index in np.unique(accepted_labels):
            class_features = accepted_features[accepted_labels == class_index]
            target_centroid = np.mean(class_features, axis=0)
            rate = self.config.update_rate
            self.prototypes[class_index] = ((1.0 - rate) * self.prototypes[class_index]) + (
                rate * target_centroid
            )
            self.prototype_counts[class_index] += class_features.shape[0]

        histogram = np.bincount(accepted_labels, minlength=len(self.classes_)).astype(int)
        return BatchAdaptationStats(
            accepted=int(np.sum(accepted_mask)),
            entropy_threshold=threshold,
            mean_entropy=float(np.mean(entropies)),
            mean_confidence=float(np.mean(confidences)),
            accepted_class_histogram=tuple(int(value) for value in histogram),
        )

    def _source_prototypes(self, features: FloatArray, labels: IntArray) -> FloatArray:
        prototypes = np.zeros((len(self.classes_), self.class_weight.shape[1]), dtype=np.float64)
        global_centroid = np.mean(features, axis=0)
        for class_index in self.classes_:
            class_features = features[labels == class_index]
            if class_features.size == 0:
                prototypes[class_index] = global_centroid
            else:
                prototypes[class_index] = np.mean(class_features, axis=0)
        return prototypes
