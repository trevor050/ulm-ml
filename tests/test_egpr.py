import numpy as np

from ulm_ml.egpr import EGPRConfig, EntropyGatedPrototypeReplay, normalized_entropy, softmax


def test_softmax_rows_sum_to_one() -> None:
    probabilities = softmax(np.array([[1.0, 2.0, 3.0], [1000.0, 1001.0, 1002.0]]))

    assert np.allclose(probabilities.sum(axis=1), 1.0)
    assert np.all(probabilities > 0.0)


def test_normalized_entropy_bounds() -> None:
    probabilities = np.array([[1.0, 0.0], [0.5, 0.5]])

    entropy = normalized_entropy(probabilities)

    assert np.isclose(entropy[0], 0.0)
    assert np.isclose(entropy[1], 1.0)


def test_egpr_updates_only_accepted_prototypes() -> None:
    source_features = np.array([[2.0, 0.0], [1.8, 0.1], [-2.0, 0.0], [-1.8, -0.1]])
    source_labels = np.array([0, 0, 1, 1])
    class_weight = np.array([[2.0, 0.0], [-2.0, 0.0]])
    class_bias = np.array([0.0, 0.0])
    adapter = EntropyGatedPrototypeReplay(
        class_weight,
        class_bias,
        source_features,
        source_labels,
        EGPRConfig(entropy_quantile=0.5, confidence_floor=0.7, update_rate=0.5),
    )
    before = adapter.prototypes.copy()

    stats = adapter.adapt_batch(np.array([[3.0, 1.0], [0.0, 0.0]]))

    assert stats.accepted == 1
    assert adapter.prototypes[0, 0] > before[0, 0]
    assert np.allclose(adapter.prototypes[1], before[1])


def test_egpr_can_disable_adaptation_for_no_adapt_baseline() -> None:
    source_features = np.array([[2.0, 0.0], [1.8, 0.1], [-2.0, 0.0], [-1.8, -0.1]])
    source_labels = np.array([0, 0, 1, 1])
    class_weight = np.array([[2.0, 0.0], [-2.0, 0.0]])
    class_bias = np.array([0.0, 0.0])
    adapter = EntropyGatedPrototypeReplay(
        class_weight,
        class_bias,
        source_features,
        source_labels,
        EGPRConfig(adaptation_enabled=False),
    )
    before = adapter.prototypes.copy()

    stats = adapter.adapt_batch(np.array([[3.0, 1.0], [-3.0, -1.0]]))

    assert stats.accepted == 0
    assert np.allclose(adapter.prototypes, before)


def test_egpr_all_replay_bypasses_entropy_gate_but_keeps_confidence_floor() -> None:
    source_features = np.array([[2.0, 0.0], [1.8, 0.1], [-2.0, 0.0], [-1.8, -0.1]])
    source_labels = np.array([0, 0, 1, 1])
    class_weight = np.array([[2.0, 0.0], [-2.0, 0.0]])
    class_bias = np.array([0.0, 0.0])
    adapter = EntropyGatedPrototypeReplay(
        class_weight,
        class_bias,
        source_features,
        source_labels,
        EGPRConfig(
            entropy_quantile=0.01,
            confidence_floor=0.0,
            use_entropy_gate=False,
            min_accept_per_batch=0,
        ),
    )

    stats = adapter.adapt_batch(np.array([[0.2, 0.0], [0.0, 0.0], [-0.2, 0.0]]))

    assert stats.accepted == 3
