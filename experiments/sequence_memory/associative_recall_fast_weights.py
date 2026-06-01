"""Run a CPU-friendly associative-recall memory experiment.

Research question
-----------------
Can a tiny learned write gate on fast weights improve length extrapolation over
simple similarity retrieval when test sequences are longer than train sequences?

This script is designed for low-compute research staging: no GPUs, no external
data, and results saved as a small JSON file under ``artifacts/``.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from ulm_ml.paths import ARTIFACTS_DIR
from ulm_ml.sequence_memory import AssociativeRecallConfig, AssociativeRecallDataset
from ulm_ml.sequence_memory.models import (
    DeltaFastWeightsMemory,
    GatedFastWeightsMemory,
    RecencyMemory,
    ScalarFastWeightsMemory,
    cosine_accuracy,
    mean_squared_error,
)


def evaluate(model: object, dataset: AssociativeRecallDataset) -> dict[str, float]:
    cosine_scores = []
    losses = []
    for keys, values, query, target, _ in dataset:
        pred = model.predict(keys, values, query)  # type: ignore[attr-defined]
        cosine_scores.append(cosine_accuracy(pred, target))
        losses.append(mean_squared_error(pred, target))
    return {"cosine": float(np.mean(cosine_scores)), "mse": float(np.mean(losses))}


def run(config: AssociativeRecallConfig, *, epochs: int = 12) -> dict[str, object]:
    baselines = {
        "nearest_neighbor": RecencyMemory(temperature=40.0, recency_bias=0.0),
        "recency_biased": RecencyMemory(temperature=40.0, recency_bias=4.0),
    }
    fast_weights = GatedFastWeightsMemory(
        key_dim=config.key_dim,
        value_dim=config.value_dim,
        decay=1.0,
        lr=0.03,
        seed=config.seed,
    )

    train_losses: list[float] = []
    for _ in range(epochs):
        epoch_losses = []
        for keys, values, query, target, _ in AssociativeRecallDataset(config, split="train"):
            epoch_losses.append(fast_weights.train_batch(keys, values, query, target))
        train_losses.append(float(np.mean(epoch_losses)))

    models = {
        **baselines,
        "scalar_fast_weights": ScalarFastWeightsMemory(write_scale=0.5),
        "delta_fast_weights": DeltaFastWeightsMemory(),
        "gated_fast_weights": fast_weights,
    }
    evaluations: dict[str, dict[str, dict[str, float]]] = {}
    for name, model in models.items():
        evaluations[name] = {}
        for pairs in config.test_pairs:
            dataset = AssociativeRecallDataset(
                config,
                split="test",
                pairs=pairs,
                seed_offset=10_000 + pairs,
            )
            row = evaluate(model, dataset)
            row["pairs_per_key_dim"] = float(pairs / config.key_dim)
            evaluations[name][str(pairs)] = row

    return {
        "config": asdict(config),
        "epochs": epochs,
        "train_losses": train_losses,
        "gate_bias": float(fast_weights.gate_b),
        "gate_weight_norm": float(np.linalg.norm(fast_weights.gate_w)),
        "evaluations": evaluations,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--key-dims", type=int, nargs="+", default=[32])
    parser.add_argument("--train-size", type=int, default=4096)
    parser.add_argument("--test-size", type=int, default=2048)
    parser.add_argument(
        "--output", type=Path, default=ARTIFACTS_DIR / "sequence_memory_associative_recall.json"
    )
    args = parser.parse_args()

    results = []
    for key_dim in args.key_dims:
        config = AssociativeRecallConfig(
            seed=args.seed,
            key_dim=key_dim,
            train_size=args.train_size,
            test_size=args.test_size,
        )
        results.append(run(config, epochs=args.epochs))
    result: dict[str, object]
    if len(results) == 1:
        result = results[0]
    else:
        result = {"sweeps": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")

    if "evaluations" in result:
        print(json.dumps(result["evaluations"], indent=2))
    else:
        print(json.dumps(result, indent=2))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
