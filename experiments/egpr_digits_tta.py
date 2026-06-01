"""Run a small entropy-gated prototype replay experiment on shifted digits.

This script is designed to be cheap enough for a cloud coding agent: it uses the
scikit-learn digits dataset, a fixed PCA feature space, and online batches of
synthetically corrupted target images.  It compares source-only predictions,
naive all-confident prototype replay, and entropy-gated prototype replay (EGPR).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import numpy as np  # noqa: E402
from numpy.typing import NDArray  # noqa: E402
from sklearn.datasets import load_digits  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import accuracy_score  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from ulm_ml.egpr import EGPRConfig, EntropyGatedPrototypeReplay  # noqa: E402
from ulm_ml.paths import ARTIFACTS_DIR  # noqa: E402

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


@dataclass(frozen=True)
class CorruptionConfig:
    """Parameters for deterministic target-domain corruptions."""

    noise_sigma: float = 2.5
    occlusion_size: int = 2
    brightness_shift: float = 1.0


@dataclass(frozen=True)
class ExperimentResult:
    """Serializable result for one corruption setting."""

    seed: int
    corruption: str
    source_only_accuracy: float
    prototype_no_adapt_accuracy: float
    all_replay_accuracy: float
    egpr_accuracy: float
    all_replay_accepted: int
    egpr_accepted: int
    egpr_mean_entropy: float
    egpr_mean_confidence: float


def corrupt_digits(
    images: FloatArray,
    corruption: str,
    rng: np.random.Generator,
    config: CorruptionConfig,
) -> FloatArray:
    """Apply a synthetic covariate shift to flat 8x8 digit images."""

    image_cube = images.reshape(-1, 8, 8).astype(np.float64).copy()
    if corruption == "gaussian_noise":
        image_cube += rng.normal(0.0, config.noise_sigma, size=image_cube.shape)
    elif corruption == "top_left_occlusion":
        size = config.occlusion_size
        image_cube[:, :size, :size] = 0.0
    elif corruption == "brightness_shift":
        image_cube += config.brightness_shift
    elif corruption == "mixed_shift":
        image_cube += rng.normal(0.0, config.noise_sigma * 0.75, size=image_cube.shape)
        size = config.occlusion_size
        image_cube[:, -size:, -size:] = 0.0
        image_cube += config.brightness_shift
    else:
        msg = f"unknown corruption: {corruption}"
        raise ValueError(msg)
    return np.clip(image_cube, 0.0, 16.0).reshape(images.shape)


def stream_batches(features: FloatArray, batch_size: int) -> Sequence[FloatArray]:
    """Split features into deterministic online batches."""

    return [features[start : start + batch_size] for start in range(0, len(features), batch_size)]


def evaluate_online(
    adapter: EntropyGatedPrototypeReplay,
    features: FloatArray,
    labels: IntArray,
    batch_size: int,
):
    """Predict then adapt on each target batch, returning accuracy and stats."""

    predictions: list[IntArray] = []
    accepted = 0
    entropies = []
    confidences = []
    for batch in stream_batches(features, batch_size):
        probabilities = adapter.predict_proba(batch)
        predictions.append(np.argmax(probabilities, axis=1).astype(np.int64))
        stats = adapter.adapt_batch(batch)
        accepted += stats.accepted
        entropies.append(stats.mean_entropy)
        confidences.append(stats.mean_confidence)
    predicted_labels = np.concatenate(predictions)
    return (
        float(accuracy_score(labels, predicted_labels)),
        accepted,
        float(np.mean(entropies)),
        float(np.mean(confidences)),
    )


def summarize_results(results: Sequence[ExperimentResult]) -> list[dict[str, float | str | int]]:
    """Return mean/std accuracy rows for every corruption and method."""

    rows: list[dict[str, float | str | int]] = []
    methods = [
        ("source_only", "source_only_accuracy"),
        ("prototype_no_adapt", "prototype_no_adapt_accuracy"),
        ("all_replay", "all_replay_accuracy"),
        ("egpr", "egpr_accuracy"),
    ]
    corruptions = sorted({result.corruption for result in results})
    for corruption in corruptions:
        group = [result for result in results if result.corruption == corruption]
        for method, field in methods:
            values = np.array([getattr(result, field) for result in group], dtype=np.float64)
            rows.append(
                {
                    "corruption": corruption,
                    "method": method,
                    "seeds": len(group),
                    "accuracy_mean": float(values.mean()),
                    "accuracy_std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
                }
            )
    return rows


def run_experiment(
    seed: int,
    batch_size: int,
    output_path: Path | None,
    corruptions: Sequence[str],
) -> list[ExperimentResult]:
    """Train the source model once, then evaluate online target adaptation."""

    rng = np.random.default_rng(seed)
    digits = load_digits()
    x_train, x_test, y_train, y_test = train_test_split(
        digits.data.astype(np.float64),
        digits.target.astype(np.int64),
        test_size=0.35,
        random_state=seed,
        stratify=digits.target,
    )
    featurizer = make_pipeline(
        StandardScaler(),
        PCA(n_components=32, random_state=seed, whiten=True),
    )
    x_train_features = featurizer.fit_transform(x_train)
    classifier = LogisticRegression(max_iter=2_000, random_state=seed, C=1.5)
    classifier.fit(x_train_features, y_train)

    results: list[ExperimentResult] = []
    for corruption in corruptions:
        x_target = corrupt_digits(x_test, corruption, rng, CorruptionConfig())
        x_target_features = featurizer.transform(x_target)
        source_probabilities = classifier.predict_proba(x_target_features)
        source_accuracy = float(accuracy_score(y_test, np.argmax(source_probabilities, axis=1)))

        prototype_no_adapt_adapter = EntropyGatedPrototypeReplay(
            classifier.coef_,
            classifier.intercept_,
            x_train_features,
            y_train,
            EGPRConfig(adaptation_enabled=False),
        )
        prototype_no_adapt_accuracy, _, _, _ = evaluate_online(
            prototype_no_adapt_adapter, x_target_features, y_test, batch_size=batch_size
        )

        all_replay_adapter = EntropyGatedPrototypeReplay(
            classifier.coef_,
            classifier.intercept_,
            x_train_features,
            y_train,
            EGPRConfig(
                confidence_floor=0.0,
                update_rate=0.08,
                use_entropy_gate=False,
                min_accept_per_batch=0,
            ),
        )
        all_replay_accuracy, all_replay_accepted, _, _ = evaluate_online(
            all_replay_adapter, x_target_features, y_test, batch_size=batch_size
        )

        egpr_adapter = EntropyGatedPrototypeReplay(
            classifier.coef_,
            classifier.intercept_,
            x_train_features,
            y_train,
            EGPRConfig(),
        )
        egpr_accuracy, accepted, mean_entropy, mean_confidence = evaluate_online(
            egpr_adapter, x_target_features, y_test, batch_size=batch_size
        )
        results.append(
            ExperimentResult(
                seed=seed,
                corruption=corruption,
                source_only_accuracy=source_accuracy,
                prototype_no_adapt_accuracy=prototype_no_adapt_accuracy,
                all_replay_accuracy=all_replay_accuracy,
                egpr_accuracy=egpr_accuracy,
                all_replay_accepted=all_replay_accepted,
                egpr_accepted=accepted,
                egpr_mean_entropy=mean_entropy,
                egpr_mean_confidence=mean_confidence,
            )
        )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps([asdict(result) for result in results], indent=2) + "\n")
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--seeds", type=int, nargs="+")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTIFACTS_DIR / "egpr_digits_tta_results.json",
        help="JSON output path. Use /dev/null to skip keeping artifacts.",
    )
    parser.add_argument(
        "--corruption",
        action="append",
        dest="corruptions",
        choices=["gaussian_noise", "top_left_occlusion", "brightness_shift", "mixed_shift"],
        help="Corruption to evaluate. May be supplied multiple times.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = None if str(args.output) == "/dev/null" else args.output
    corruptions = args.corruptions or [
        "gaussian_noise",
        "top_left_occlusion",
        "brightness_shift",
        "mixed_shift",
    ]
    seeds = args.seeds or [args.seed]
    results: list[ExperimentResult] = []
    for seed in seeds:
        results.extend(run_experiment(seed, args.batch_size, None, corruptions))
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "results": [asdict(result) for result in results],
            "summary": summarize_results(results),
        }
        output_path.write_text(json.dumps(payload, indent=2) + "\n")
    for result in results:
        print(
            f"seed={result.seed:<2d} {result.corruption:18s} "
            f"source={result.source_only_accuracy:.3f} "
            f"proto_no_adapt={result.prototype_no_adapt_accuracy:.3f} "
            f"all_replay={result.all_replay_accuracy:.3f} "
            f"egpr={result.egpr_accuracy:.3f} accepted={result.egpr_accepted}"
        )
    if len(results) > len(corruptions):
        print(json.dumps(summarize_results(results), indent=2))


if __name__ == "__main__":
    main()
