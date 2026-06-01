# Research Log

Use this as the compact source of truth for experiments that matter.

## 2026-06-01

- Initialized the repository as a Codex-friendly ML research staging ground.
- Added a lightweight symmetry-augmented sparse feature recovery study. The
  result: cyclic group augmentation improves known-feature recovery in a
  controlled sparse dictionary benchmark, especially with only 40 observations
  (0.481 -> 0.736 of true atoms recovered at cosine >= 0.90). See
  `docs/symmetry-augmented-sparse-recovery.md` and
  `experiments/symmetry_augmented_sparse_recovery.py`.

