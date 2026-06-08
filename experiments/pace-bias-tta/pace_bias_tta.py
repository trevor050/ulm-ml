"""Bias-only test-time adaptation on a small corrupted-digits benchmark.

This script asks a deliberately cheap research question: can a conservative
entropy objective plus a source-prior anchor make unlabeled test-time adaptation
less collapse-prone when only a class-bias vector is updated?
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd
from scipy.ndimage import rotate
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils import check_random_state

from ulm_ml.paths import ARTIFACTS_DIR
from ulm_ml.tta import BiasAdapterConfig, adapt_bias, class_prior, entropy, softmax


def corrupt_digits(
    images: np.ndarray,
    *,
    rng: np.random.RandomState,
    rotation: float,
    noise: float,
    contrast: float,
) -> np.ndarray:
    """Apply a deterministic-family covariate shift to 8x8 digit images."""

    shifted = np.empty_like(images, dtype=np.float64)
    for index, image in enumerate(images):
        angle = rng.uniform(-rotation, rotation)
        shifted[index] = rotate(image, angle=angle, reshape=False, order=1, mode="nearest")
    shifted = contrast * shifted + rng.normal(0.0, noise, size=shifted.shape)
    return np.clip(shifted, 0.0, 16.0)


def make_stream_indices(
    y: np.ndarray,
    *,
    rng: np.random.RandomState,
    mode: str,
) -> np.ndarray:
    """Return ordered test indices for balanced or prior-shifted streams."""

    if mode == "balanced":
        indices = np.arange(len(y))
        rng.shuffle(indices)
        return indices

    if mode != "head_heavy":
        raise ValueError(f"Unknown stream mode: {mode}")

    # Oversample low digits to create a stream whose prior conflicts with the
    # source prior. This probes whether prior anchoring is robust or brittle.
    weights = np.where(y < 5, 3.0, 1.0)
    weights /= weights.sum()
    return rng.choice(np.arange(len(y)), size=len(y), replace=True, p=weights)


def evaluate_method(
    logits: np.ndarray,
    y: np.ndarray,
    prior: np.ndarray,
    *,
    batch_size: int,
    config: BiasAdapterConfig,
) -> dict[str, float]:
    """Evaluate one adaptation objective over an unlabeled test stream."""

    adapted_chunks: list[np.ndarray] = []
    bias_norms: list[float] = []
    for start in range(0, len(y), batch_size):
        batch_logits = logits[start : start + batch_size]
        adapted, bias = adapt_bias(batch_logits, prior, config)
        adapted_chunks.append(adapted)
        bias_norms.append(float(np.linalg.norm(bias)))

    adapted_logits = np.vstack(adapted_chunks)
    probs = softmax(adapted_logits)
    predictions = probs.argmax(axis=1)
    predicted_prior = np.bincount(predictions, minlength=len(prior)) / len(predictions)
    return {
        "accuracy": float(accuracy_score(y, predictions)),
        "nll": float(log_loss(y, probs, labels=np.arange(len(prior)))),
        "entropy": float(entropy(probs).mean()),
        "bias_l2": float(np.mean(bias_norms)),
        "predicted_prior_l1_from_source": float(np.abs(predicted_prior - prior).sum()),
    }


def run_once(
    seed: int, stream_mode: str, batch_size: int, shift_type: str
) -> list[dict[str, float | int | str]]:
    rng = check_random_state(seed)
    digits = load_digits()
    images = digits.images.astype(np.float64)
    y = digits.target.astype(np.int64)
    x_train, x_test, y_train, y_test, images_train, images_test = train_test_split(
        images.reshape(len(images), -1),
        y,
        images,
        test_size=0.45,
        random_state=seed,
        stratify=y,
    )

    scaler = StandardScaler().fit(x_train)
    model = LogisticRegression(max_iter=2000, C=0.35, solver="lbfgs")
    model.fit(scaler.transform(x_train), y_train)
    prior = class_prior(y_train, n_classes=10, smoothing=1.0)

    stream_indices = make_stream_indices(y_test, rng=rng, mode=stream_mode)
    stream_y = y_test[stream_indices]
    if shift_type == "image_corruption":
        shifted_images = corrupt_digits(
            images_test[stream_indices], rng=rng, rotation=22.0, noise=2.8, contrast=0.72
        )
        shifted_x = scaler.transform(shifted_images.reshape(len(shifted_images), -1))
        logits = model.decision_function(shifted_x)
    elif shift_type == "logit_prior_drift":
        shifted_x = scaler.transform(images_test[stream_indices].reshape(len(stream_indices), -1))
        logits = model.decision_function(shifted_x)
        drift = np.array([2.5, 1.8, 1.1, 0.4, -0.3, -0.8, -1.2, -1.6, -2.0, -2.4])
        logits = logits + (drift - drift.mean())
    else:
        raise ValueError(f"Unknown shift type: {shift_type}")

    configs = {
        "source": BiasAdapterConfig(objective="source"),
        "entropy": BiasAdapterConfig(objective="entropy", steps=35, learning_rate=0.35),
        "conservative": BiasAdapterConfig(
            objective="conservative", steps=35, learning_rate=0.35, entropy_floor=0.55
        ),
        "pace": BiasAdapterConfig(
            objective="pace",
            steps=35,
            learning_rate=0.35,
            entropy_floor=0.55,
            prior_weight=2.0,
            confidence_quantile=0.5,
        ),
    }

    rows: list[dict[str, float | int | str]] = []
    true_stream_prior = np.bincount(stream_y, minlength=10) / len(stream_y)
    for name, config in configs.items():
        metrics = evaluate_method(logits, stream_y, prior, batch_size=batch_size, config=config)
        rows.append(
            {
                "seed": seed,
                "stream_mode": stream_mode,
                "shift_type": shift_type,
                "method": name,
                "batch_size": batch_size,
                "true_prior_l1_from_source": float(np.abs(true_stream_prior - prior).sum()),
                **metrics,
            }
        )
    return rows


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    metric_cols = [
        "accuracy",
        "nll",
        "entropy",
        "bias_l2",
        "predicted_prior_l1_from_source",
        "true_prior_l1_from_source",
    ]
    summary = (
        results.groupby(["shift_type", "stream_mode", "method"], as_index=False)[metric_cols]
        .agg(["mean", "std"])
        .reset_index()
    )
    summary.columns = ["_".join(col).strip("_") for col in summary.columns.to_flat_index()]
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--out-dir", type=Path, default=ARTIFACTS_DIR / "pace_bias_tta")
    args = parser.parse_args()

    rows: list[dict[str, float | int | str]] = []
    for seed in args.seeds:
        for shift_type in ["logit_prior_drift", "image_corruption"]:
            for stream_mode in ["balanced", "head_heavy"]:
                rows.extend(run_once(seed, stream_mode, args.batch_size, shift_type))

    results = pd.DataFrame(rows)
    summary = summarize(results)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.out_dir / "results.csv", index=False)
    summary.to_csv(args.out_dir / "summary.csv", index=False)
    (args.out_dir / "config.json").write_text(
        json.dumps({"seeds": args.seeds, "batch_size": args.batch_size}, indent=2) + "\n"
    )
    print(summary.to_string(index=False))
    print(f"\nWrote {args.out_dir}")


if __name__ == "__main__":
    main()
