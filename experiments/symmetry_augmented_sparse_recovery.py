"""Run the cyclic symmetry augmentation sparse-recovery experiment.

This script is intentionally CPU-light. It compares sparse dictionary recovery
from scarce observations against the same observations augmented by every known
cyclic transform.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ulm_ml.paths import ARTIFACTS_DIR
from ulm_ml.symmetry_sparse import (
    OrbitSparseConfig,
    cyclic_augment,
    feature_recovery,
    fit_nmf_dictionary,
    make_orbit_dictionary,
    orbit_closure_score,
    sample_observations,
)


@dataclass(frozen=True)
class TrialResult:
    n_samples: int
    method: str
    data_seed: int
    fit_seed: int
    mean_best_cosine: float
    frac_recovered_090: float
    orbit_closure: float
    reconstruction_mse: float
    n_iter: int


def run_trial(
    config: OrbitSparseConfig,
    true_dictionary: np.ndarray,
    *,
    n_samples: int,
    data_seed: int,
    fit_seed: int,
    augment: bool,
) -> TrialResult:
    observations, _ = sample_observations(true_dictionary, n_samples, config, seed=data_seed)
    fit_observations = cyclic_augment(observations, config) if augment else observations
    learned, mse, n_iter = fit_nmf_dictionary(
        fit_observations, config.n_features, seed=fit_seed
    )
    mean_best, frac_090 = feature_recovery(learned, true_dictionary)
    return TrialResult(
        n_samples=n_samples,
        method="cyclic_augmented" if augment else "baseline",
        data_seed=data_seed,
        fit_seed=fit_seed,
        mean_best_cosine=mean_best,
        frac_recovered_090=frac_090,
        orbit_closure=orbit_closure_score(learned, config),
        reconstruction_mse=mse,
        n_iter=n_iter,
    )


def run_experiment(
    sample_sizes: tuple[int, ...] = (40, 70, 120),
    n_data_seeds: int = 6,
    n_fit_seeds: int = 4,
) -> list[TrialResult]:
    config = OrbitSparseConfig()
    true_dictionary = make_orbit_dictionary(config)
    results: list[TrialResult] = []
    for n_samples in sample_sizes:
        for data_seed_index in range(n_data_seeds):
            data_seed = 100 + data_seed_index
            for fit_seed in range(n_fit_seeds):
                for augment in (False, True):
                    results.append(
                        run_trial(
                            config,
                            true_dictionary,
                            n_samples=n_samples,
                            data_seed=data_seed,
                            fit_seed=fit_seed,
                            augment=augment,
                        )
                    )
    return results


def summarize(results: list[TrialResult]) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    keys = sorted({(result.n_samples, result.method) for result in results})
    for n_samples, method in keys:
        group = [r for r in results if r.n_samples == n_samples and r.method == method]
        rows.append(
            {
                "n_samples": n_samples,
                "method": method,
                "trials": len(group),
                "mean_best_cosine": float(np.mean([r.mean_best_cosine for r in group])),
                "frac_recovered_090": float(np.mean([r.frac_recovered_090 for r in group])),
                "orbit_closure": float(np.mean([r.orbit_closure for r in group])),
                "reconstruction_mse": float(np.mean([r.reconstruction_mse for r in group])),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=ARTIFACTS_DIR / "symmetry_sparse_summary.csv"
    )
    args = parser.parse_args()

    rows = summarize(run_experiment())
    write_csv(args.output, rows)
    for row in rows:
        print(
            f"n={row['n_samples']:>3} {row['method']:<16} "
            f"cos={row['mean_best_cosine']:.3f} "
            f"frac90={row['frac_recovered_090']:.3f} "
            f"closure={row['orbit_closure']:.3f} "
            f"mse={row['reconstruction_mse']:.4f}"
        )


if __name__ == "__main__":
    main()
