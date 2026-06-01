import numpy as np

from ulm_ml.tta import BiasAdapterConfig, adapt_bias, class_prior, entropy, softmax


def test_softmax_rows_sum_to_one() -> None:
    probs = softmax(np.array([[1.0, 2.0, 3.0], [1001.0, 1002.0, 1003.0]]))
    np.testing.assert_allclose(probs.sum(axis=1), np.ones(2))
    assert np.all(probs > 0.0)


def test_class_prior_is_smoothed() -> None:
    prior = class_prior(np.array([0, 0, 2]), n_classes=4, smoothing=1.0)
    np.testing.assert_allclose(prior, np.array([3, 1, 2, 1]) / 7)


def test_entropy_adapter_reduces_entropy_on_uncertain_logits() -> None:
    logits = np.array([[0.2, 0.1, -0.1], [0.0, 0.1, 0.2]], dtype=float)
    before = entropy(softmax(logits)).mean()
    adapted, bias = adapt_bias(
        logits,
        np.ones(3) / 3,
        BiasAdapterConfig(objective="entropy", steps=15, learning_rate=0.5),
    )
    after = entropy(softmax(adapted)).mean()
    assert after < before
    np.testing.assert_allclose(bias.mean(), 0.0, atol=1e-12)


def test_source_adapter_is_noop() -> None:
    logits = np.array([[1.0, 0.0], [0.0, 1.0]])
    adapted, bias = adapt_bias(logits, np.ones(2) / 2, BiasAdapterConfig(objective="source"))
    np.testing.assert_allclose(adapted, logits)
    np.testing.assert_allclose(bias, np.zeros(2))
