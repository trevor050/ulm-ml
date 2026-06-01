"""Run the modular-addition spectral split probe.

This is a CPU-only experiment designed to finish in seconds. It writes a compact CSV
that can guide whether a much more expensive grokking run is worth launching.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ulm_ml.modular_spectral import run_split_sweep
from ulm_ml.paths import ARTIFACTS_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modulus", type=int, default=31)
    parser.add_argument("--fractions", type=float, nargs="+", default=[0.05, 0.08, 0.10, 0.15])
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(8)))
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTIFACTS_DIR / "modular_spectral_probe.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = run_split_sweep(args.modulus, args.fractions, args.seeds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    grouped: dict[tuple[float, str], list[float]] = {}
    for row in rows:
        key = (float(row["fraction"]), str(row["split"]))
        grouped.setdefault(key, []).append(float(row["test_acc"]))
    print(f"wrote {len(rows)} rows to {args.output}")
    for (fraction, split), values in sorted(grouped.items()):
        mean = sum(values) / len(values)
        print(f"fraction={fraction:.2f} split={split:>12} mean_test_acc={mean:.3f}")


if __name__ == "__main__":
    main()
