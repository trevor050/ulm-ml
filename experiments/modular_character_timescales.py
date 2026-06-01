"""CPU-only probe for memorization-vs-character generalization in modular tables.

Run from the repository root without installing the package:
    PYTHONPATH=src python experiments/modular_character_timescales.py
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from ulm_ml.modular_arithmetic import (
    EncoderName,
    accuracy,
    encode_pairs,
    fit_ridge_classifier,
    make_modular_dataset,
    stratified_table_split,
)
from ulm_ml.paths import ARTIFACTS_DIR


@dataclass(frozen=True)
class TrialResult:
    modulus: int
    train_fraction: float
    seed: int
    encoder: str
    max_frequency: int | str
    n_features: int
    train_accuracy: float
    test_accuracy: float


def run_trial(
    *,
    modulus: int,
    train_fraction: float,
    seed: int,
    encoder: EncoderName,
    max_frequency: int | None,
    ridge: float,
) -> TrialResult:
    dataset = make_modular_dataset(modulus)
    train_idx, test_idx = stratified_table_split(
        dataset.labels,
        train_fraction=train_fraction,
        seed=seed,
    )
    train_x = encode_pairs(
        dataset.pairs[train_idx],
        modulus=modulus,
        encoder=encoder,
        max_frequency=max_frequency,
    )
    test_x = encode_pairs(
        dataset.pairs[test_idx],
        modulus=modulus,
        encoder=encoder,
        max_frequency=max_frequency,
    )
    weights = fit_ridge_classifier(
        train_x,
        dataset.labels[train_idx],
        n_classes=modulus,
        ridge=ridge,
    )
    return TrialResult(
        modulus=modulus,
        train_fraction=train_fraction,
        seed=seed,
        encoder=encoder,
        max_frequency=max_frequency if max_frequency is not None else "full",
        n_features=train_x.shape[1],
        train_accuracy=accuracy(train_x, dataset.labels[train_idx], weights),
        test_accuracy=accuracy(test_x, dataset.labels[test_idx], weights),
    )


def default_grid(modulus: int) -> list[tuple[EncoderName, int | None]]:
    candidate_frequencies = [1, 2, 4]
    valid_frequencies = [
        frequency for frequency in candidate_frequencies if frequency <= modulus // 2
    ]
    return [
        ("pair_onehot", None),
        ("separable_onehot", None),
        *[("character_interactions", frequency) for frequency in valid_frequencies],
        ("character_interactions", None),
    ]


def summarize(results: list[TrialResult]) -> str:
    grouped: dict[tuple[int, float, str, int | str, int], list[float]] = {}
    for result in results:
        key = (
            result.modulus,
            result.train_fraction,
            result.encoder,
            result.max_frequency,
            result.n_features,
        )
        grouped.setdefault(key, []).append(result.test_accuracy)

    lines = [
        "modulus train_frac encoder                 k/full features test_acc_mean test_acc_min",
        "------- ---------- ----------------------- ------ -------- ------------- ------------",
    ]
    for key in sorted(grouped, key=lambda item: (item[0], item[1], item[2], str(item[3]), item[4])):
        modulus, train_fraction, encoder, max_frequency, n_features = key
        values = grouped[key]
        lines.append(
            f"{modulus:7d} {train_fraction:10.2f} {encoder:23s} "
            f"{str(max_frequency):>6s} {n_features:8d} "
            f"{sum(values) / len(values):13.3f} {min(values):12.3f}"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--moduli", nargs="+", type=int, default=[31, 43])
    parser.add_argument("--train-fractions", nargs="+", type=float, default=[0.10, 0.20, 0.35])
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    parser.add_argument("--ridge", type=float, default=1e-6)
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTIFACTS_DIR / "modular_character_timescales.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results: list[TrialResult] = []
    for modulus in args.moduli:
        for train_fraction in args.train_fractions:
            for seed in args.seeds:
                for encoder, max_frequency in default_grid(modulus):
                    results.append(
                        run_trial(
                            modulus=modulus,
                            train_fraction=train_fraction,
                            seed=seed,
                            encoder=encoder,
                            max_frequency=max_frequency,
                            ridge=args.ridge,
                        )
                    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(TrialResult.__dataclass_fields__))
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)

    print(summarize(results))
    print(f"\nwrote {len(results)} rows to {args.output}")


if __name__ == "__main__":
    main()
