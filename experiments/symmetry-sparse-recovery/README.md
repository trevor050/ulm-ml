# Symmetry-Augmented Sparse Recovery

## Question

Does the right cyclic symmetry help recover sparse features under a strict
one-to-one metric?

## Verdict

Yes, keep going.

## Answer So Far

Correct cyclic augmentation improves strict recovery, while a size-matched
shuffled-action control fails. Loose best-match recovery is only diagnostic.

## Interesting Bit

The headline metric has to be unique one-to-one recovery, otherwise the result
looks better than it is.

## Command

```bash
PYTHONPATH=src python experiments/symmetry-sparse-recovery/symmetry_augmented_sparse_recovery.py
```

## Deeper Notes

- `docs/full-research/symmetry-sparse-recovery.md`
- `docs/symmetry-augmented-sparse-recovery.md`
