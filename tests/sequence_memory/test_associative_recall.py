import numpy as np

from ulm_ml.sequence_memory import AssociativeRecallConfig, generate_associative_recall_batch
from ulm_ml.sequence_memory.models import (
    GatedFastWeightsMemory,
    RecencyMemory,
    ScalarFastWeightsMemory,
    cosine_accuracy,
)


def test_generated_query_targets_one_of_the_keys() -> None:
    rng = np.random.default_rng(123)
    keys, values, query, target, target_index = generate_associative_recall_batch(
        rng,
        batch_size=16,
        pairs=5,
        key_dim=8,
        value_dim=4,
        key_noise=0.0,
        value_noise=0.0,
    )

    assert keys.shape == (16, 5, 8)
    assert values.shape == (16, 5, 4)
    assert np.allclose(query, keys[np.arange(16), target_index])
    assert np.allclose(target, values[np.arange(16), target_index])


def test_recency_memory_retrieves_exact_queries() -> None:
    rng = np.random.default_rng(123)
    keys, values, query, target, _ = generate_associative_recall_batch(
        rng,
        batch_size=64,
        pairs=8,
        key_dim=32,
        value_dim=8,
        key_noise=0.0,
        value_noise=0.0,
    )
    pred = RecencyMemory(temperature=80.0).predict(keys, values, query)

    assert cosine_accuracy(pred, target) > 0.98


def test_fast_weights_training_step_reduces_loss_on_reused_batch() -> None:
    config = AssociativeRecallConfig(key_dim=16, value_dim=8, batch_size=64, seed=7)
    rng = np.random.default_rng(config.seed)
    keys, values, query, target, _ = generate_associative_recall_batch(
        rng,
        batch_size=config.batch_size,
        pairs=config.train_pairs,
        key_dim=config.key_dim,
        value_dim=config.value_dim,
        key_noise=config.key_noise,
        value_noise=config.value_noise,
    )
    model = GatedFastWeightsMemory(config.key_dim, config.value_dim, lr=0.05, seed=0)
    first = model.train_batch(keys, values, query, target)
    for _ in range(50):
        last = model.train_batch(keys, values, query, target)

    assert last < first


def test_scalar_fast_weights_memory_has_fixed_write_scale() -> None:
    rng = np.random.default_rng(9)
    keys, values, query, _, _ = generate_associative_recall_batch(
        rng,
        batch_size=8,
        pairs=4,
        key_dim=12,
        value_dim=5,
        key_noise=0.0,
        value_noise=0.0,
    )

    active = ScalarFastWeightsMemory(write_scale=0.5).predict(keys, values, query)
    inactive = ScalarFastWeightsMemory(write_scale=0.0).predict(keys, values, query)

    assert active.shape == (8, 5)
    assert np.linalg.norm(active) > 0.0
    assert np.allclose(inactive, 0.0)
