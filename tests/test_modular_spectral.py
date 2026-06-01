import numpy as np

from ulm_ml.modular_spectral import (
    make_train_mask,
    modular_addition_grid,
    ridge_probe_accuracy,
    split_diagnostics,
    sum_counts,
)


def test_modular_addition_grid_targets():
    a, b, targets = modular_addition_grid(5)
    assert a.shape == b.shape == targets.shape == (25,)
    assert targets[(a == 4) & (b == 3)][0] == 2


def test_sum_balanced_split_covers_every_sum():
    mask = make_train_mask(11, 0.2, seed=7, kind="sum_balanced")
    counts = sum_counts(11, mask)
    assert np.min(counts) >= 1
    assert np.max(counts) - np.min(counts) <= 1


def test_fourier_probe_generalizes_from_balanced_split():
    mask = make_train_mask(11, 0.2, seed=3, kind="sum_balanced")
    train_acc, test_acc = ridge_probe_accuracy(11, mask)
    assert train_acc == 1.0
    assert test_acc == 1.0


def test_operand_block_has_bad_coverage_diagnostics():
    mask = make_train_mask(17, 0.08, seed=0, kind="operand_block")
    diagnostics = split_diagnostics(17, mask)
    assert diagnostics.missing_sums > 0
    assert diagnostics.sum_count_cv > 0.0
