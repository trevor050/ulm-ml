import numpy as np

from ulm_ml.modular_arithmetic import (
    accuracy,
    encode_pairs,
    fit_ridge_classifier,
    make_modular_dataset,
    stratified_table_split,
)


def test_modular_addition_labels_wrap() -> None:
    dataset = make_modular_dataset(5)
    lookup = {tuple(pair): label for pair, label in zip(dataset.pairs, dataset.labels, strict=True)}
    assert lookup[(4, 4)] == 3
    assert lookup[(2, 3)] == 0


def test_stratified_split_keeps_every_label_in_train_and_test() -> None:
    dataset = make_modular_dataset(7)
    train_idx, test_idx = stratified_table_split(dataset.labels, train_fraction=0.3, seed=0)
    assert set(dataset.labels[train_idx]) == set(range(7))
    assert set(dataset.labels[test_idx]) == set(range(7))
    assert set(train_idx).isdisjoint(set(test_idx))


def test_full_character_features_solve_small_table_from_half_observations() -> None:
    dataset = make_modular_dataset(7)
    train_idx, test_idx = stratified_table_split(dataset.labels, train_fraction=0.5, seed=1)
    train_x = encode_pairs(
        dataset.pairs[train_idx],
        modulus=7,
        encoder="character_interactions",
    )
    test_x = encode_pairs(
        dataset.pairs[test_idx],
        modulus=7,
        encoder="character_interactions",
    )
    weights = fit_ridge_classifier(train_x, dataset.labels[train_idx], n_classes=7)
    assert np.isclose(accuracy(train_x, dataset.labels[train_idx], weights), 1.0)
    assert accuracy(test_x, dataset.labels[test_idx], weights) > 0.95


def test_pair_onehot_memorizer_does_not_generalize_to_unseen_pairs() -> None:
    dataset = make_modular_dataset(11)
    train_idx, test_idx = stratified_table_split(dataset.labels, train_fraction=0.2, seed=2)
    train_x = encode_pairs(dataset.pairs[train_idx], modulus=11, encoder="pair_onehot")
    test_x = encode_pairs(dataset.pairs[test_idx], modulus=11, encoder="pair_onehot")
    weights = fit_ridge_classifier(train_x, dataset.labels[train_idx], n_classes=11)
    assert accuracy(train_x, dataset.labels[train_idx], weights) == 1.0
    assert accuracy(test_x, dataset.labels[test_idx], weights) < 0.2
