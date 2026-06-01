# Cyclic symmetry augmentation for sparse feature recovery

## Claim

A cheap way to make sparse feature recovery more reliable is to augment unlabeled
activation samples by known representation symmetries before fitting the sparse
dictionary. In a controlled cyclic-orbit benchmark, this consistently improved
feature recovery over fitting the same sparse NMF dictionary to the original
samples only.

This is meant as a small, falsifiable bridge between two active interpretability
threads:

- Sparse autoencoders are useful only when their features are stable and
  recoverable, not just low-reconstruction-loss. The 2025 position paper
  [Mechanistic Interpretability Should Prioritize Feature Consistency in
  SAEs](https://arxiv.org/abs/2505.20254) argues for measuring that directly.
- [Group Equivariance Meets Mechanistic Interpretability: Equivariant Sparse
  Autoencoders](https://arxiv.org/abs/2511.09432) studies SAEs that incorporate
  group structure. The experiment here asks a smaller question: before building
  a new SAE architecture, how far does pure group augmentation get us?

## Setup

The benchmark generates nonnegative observations from sparse latent features.
Ground-truth features are grouped into cyclic-shift orbits: if feature `f` is
present, then shifted variants of `f` are also valid dictionary atoms. The model
never sees feature labels. It sees only observations and, for the augmented
condition, the known cyclic action on coordinates.

Two fits are compared:

1. **Baseline:** sparse NMF on the sampled observations.
2. **Cyclic augmented:** sparse NMF on the same observations stacked with every
   cyclic shift under the known group action.

Evaluation uses ground truth only after training:

- `mean_best_cosine`: average best cosine match for each true atom.
- `frac_recovered_090`: fraction of true atoms with best cosine at least `0.90`.
- `orbit_closure`: label-free score measuring whether learned atoms are closed
  under the cyclic group.

## Result

The run below used 6 data seeds and 4 fit seeds per sample size, for 24 trials per
condition. Augmentation improved both feature recovery metrics at every sample
size.

| Samples | Method | Mean best cosine | True atoms recovered ≥0.90 | Orbit closure | Reconstruction MSE |
|---:|---|---:|---:|---:|---:|
| 40 | baseline | 0.803 | 0.481 | 0.339 | 0.0917 |
| 40 | cyclic augmented | **0.897** | **0.736** | **0.489** | 0.0958 |
| 70 | baseline | 0.861 | 0.653 | 0.414 | 0.0930 |
| 70 | cyclic augmented | **0.913** | **0.788** | **0.512** | 0.0919 |
| 120 | baseline | 0.882 | 0.741 | 0.441 | 0.0927 |
| 120 | cyclic augmented | **0.920** | **0.840** | **0.517** | 0.0899 |

The largest gain is in the lowest-data regime: with 40 observations, cyclic
augmentation raises the recovered-feature fraction from `0.481` to `0.736`, a
relative improvement of about 53%. Reconstruction loss alone is not a sufficient
selection criterion: the 40-sample augmented run recovers many more true atoms
while accepting slightly worse in-sample reconstruction MSE.

## Interpretation

This supports a practical hypothesis: when an activation space has an explicit or
learned group action, orbit augmentation can act as a low-compute feature
consistency regularizer. It forces the learner to spend capacity on full feature
orbits instead of one-off sample artifacts.

The result is not a claim about LLM activations yet. It is a fast toy result that
suggests a next experiment:

1. identify a transformation with an approximately known action in a real model
   activation space, such as token-position shifts in a controlled synthetic
   transformer task;
2. train matched SAEs with and without orbit augmentation;
3. select and report features using reconstruction, sparsity, cross-seed
   consistency, and orbit-closure metrics together.

## Reproduction

```bash
PYTHONPATH=src python experiments/symmetry_augmented_sparse_recovery.py --output /tmp/symmetry_sparse_summary.csv
```

The implementation lives in `src/ulm_ml/symmetry_sparse.py`; regression tests for
the generator and metrics live in `tests/test_symmetry_sparse.py`.
