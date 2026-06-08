# Sequence-Memory Interference

## Question

Where do compact fast-weight memory rules break under associative-recall load?

## Verdict

Yes, keep going.

## Answer So Far

Fast-weight, delta, gated, and orthogonalized memories show visible
load/interference curves against retrieval baselines.

## Interesting Bit

This is more useful as a failure benchmark than as a toy success demo.

## Command


```bash
PYTHONPATH=src python experiments/sequence-memory-interference/associative_recall_fast_weights.py --epochs 8 --key-dims 16 32 64 --train-size 2048 --test-size 1024
```

## Deeper Notes

- `docs/full-research/sequence-memory-interference.md`
- `docs/sequence-memory-fast-weights.md`
