import numpy as np

from ulm_ml.state_tracking import (
    SequenceBatch,
    fit_ridge_classifier,
    make_binary_count_batch,
    positive_exponential_features,
    predict_ridge_classifier,
    root_of_unity_predict,
)


def test_binary_batch_respects_lengths() -> None:
    rng = np.random.default_rng(0)
    batch = make_binary_count_batch(16, [3, 5], rng)

    assert batch.tokens.shape[0] == 16
    assert set(batch.lengths.tolist()) <= {3, 5}
    for row, length in enumerate(batch.lengths):
        assert np.all(batch.tokens[row, length:] == 0)


def test_positive_exponential_features_shape() -> None:
    batch = SequenceBatch(
        tokens=np.array([[1, 0, 1], [0, 1, 0]], dtype=np.int64),
        lengths=np.array([3, 2], dtype=np.int64),
    )

    features = positive_exponential_features(batch, n_channels=7)

    assert features.shape == (2, 7)
    assert np.all(np.isfinite(features))


def test_root_of_unity_predicts_modular_count_exactly() -> None:
    batch = SequenceBatch(
        tokens=np.array(
            [
                [1, 0, 1, 1, 0, 0],
                [1, 1, 1, 1, 1, 0],
                [0, 0, 0, 0, 0, 0],
            ],
            dtype=np.int64,
        ),
        lengths=np.array([4, 5, 6], dtype=np.int64),
    )

    assert np.array_equal(root_of_unity_predict(batch, 3), batch.counts % 3)
    assert np.array_equal(root_of_unity_predict(batch, 5), batch.counts % 5)


def test_ridge_classifier_learns_linearly_separable_toy_data() -> None:
    features = np.array([[-1.0], [-0.5], [0.5], [1.0]], dtype=np.float64)
    labels = np.array([0, 0, 1, 1], dtype=np.int64)

    weights = fit_ridge_classifier(features, labels, n_classes=2)

    assert np.array_equal(predict_ridge_classifier(features, weights), labels)
