import numpy as np

from ulm_ml.symmetry_sparse import (
    OrbitSparseConfig,
    cyclic_augment,
    feature_recovery,
    make_orbit_dictionary,
    orbit_closure_score,
    sample_observations,
)


def test_orbit_dictionary_contains_cyclic_shifts() -> None:
    config = OrbitSparseConfig(ambient_dim=12, orbit_size=3, n_orbits=2, sparsity=2)
    dictionary = make_orbit_dictionary(config)

    assert dictionary.shape == (6, 12)
    np.testing.assert_allclose(dictionary[1], np.roll(dictionary[0], config.shift))
    np.testing.assert_allclose(dictionary[2], np.roll(dictionary[0], 2 * config.shift))


def test_cyclic_augment_stacks_every_group_action() -> None:
    config = OrbitSparseConfig(ambient_dim=8, orbit_size=4, n_orbits=1)
    observations = np.arange(16, dtype=np.float64).reshape(2, 8)

    augmented = cyclic_augment(observations, config)

    assert augmented.shape == (8, 8)
    np.testing.assert_array_equal(augmented[:2], observations)
    np.testing.assert_array_equal(augmented[2:4], np.roll(observations, config.shift, axis=1))


def test_metrics_recognize_ground_truth_dictionary() -> None:
    config = OrbitSparseConfig()
    dictionary = make_orbit_dictionary(config)
    observations, codes = sample_observations(dictionary, 5, config, seed=7)

    assert observations.shape == (5, config.ambient_dim)
    assert codes.shape == (5, config.n_features)
    mean_best, frac_090 = feature_recovery(dictionary, dictionary)
    assert mean_best > 0.999
    assert frac_090 == 1.0
    assert orbit_closure_score(dictionary, config) > 0.99
