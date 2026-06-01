# Cyclic symmetry augmentation for sparse feature recovery

Portfolio status: `full_research`. The hardened version with false-symmetry
control is summarized in `docs/full-research/symmetry-sparse-recovery.md`.

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

- `unique_mean_cosine`: one-to-one optimal assignment cosine between learned and
  true atoms. This is the headline metric because one learned atom cannot explain
  multiple true atoms.
- `unique_frac_recovered_090`: fraction of true atoms whose assigned learned atom
  has cosine at least `0.90`.
- `loose_frac_recovered_090`: loose best-match diagnostic. It can overstate
  recovery because multiple true atoms may choose the same learned atom.
- `orbit_closure`: label-free score measuring whether learned atoms are closed
  under the cyclic group.

## Result

The run below used 6 data seeds and 4 fit seeds per sample size, for 24 trials per
condition. Augmentation improved the strict one-to-one recovery metric at every
sample size, although the stricter metric also shows that the original loose
best-match score substantially overstated absolute recovery.

| Samples | Method | Unique mean cosine | Unique recovered >=0.90 | Loose recovered >=0.90 | Orbit closure | Reconstruction MSE |
|---:|---|---:|---:|---:|---:|---:|
| 40 | baseline | 0.410 | 0.373 | 0.481 | 0.339 | 0.0917 |
| 40 | cyclic augmented | **0.506** | **0.486** | **0.736** | **0.489** | 0.0958 |
| 70 | baseline | 0.464 | 0.448 | 0.653 | 0.414 | 0.0930 |
| 70 | cyclic augmented | **0.529** | **0.509** | **0.788** | **0.512** | 0.0919 |
| 120 | baseline | 0.491 | 0.488 | 0.741 | 0.441 | 0.0927 |
| 120 | cyclic augmented | **0.532** | **0.510** | **0.840** | **0.517** | 0.0899 |

The largest gain is in the lowest-data regime: with 40 observations, cyclic
augmentation raises the strict recovered-feature fraction from `0.373` to
`0.486`, a relative improvement of about 30%. The loose metric reports a much
larger improvement (`0.481` to `0.736`), which should be read as a diagnostic for
cluster proximity rather than true atom recovery. Reconstruction loss alone is
not a sufficient selection criterion: the 40-sample augmented run recovers more
strictly assigned true atoms while accepting slightly worse in-sample
reconstruction MSE.

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
   consistency, unique recovery, and orbit-closure metrics together.

## Reproduction

```bash
PYTHONPATH=src python experiments/symmetry_augmented_sparse_recovery.py --output /tmp/symmetry_sparse_summary.csv
```

The implementation lives in `src/ulm_ml/symmetry_sparse.py`; regression tests for
the generator and metrics live in `tests/test_symmetry_sparse.py`.
