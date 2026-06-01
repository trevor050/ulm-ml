# Sequence-memory experiments

This folder contains small CPU-friendly probes for sequence-model memory rules.

## Associative recall fast weights

Run:

```bash
python experiments/sequence_memory/associative_recall_fast_weights.py --epochs 12
```

The experiment trains only a tiny scalar/vector write gate for a fast-weights
key-value memory on synthetic `(key, value)` sequences with 8 pairs, then evaluates
on 8/16/32/64-pair sequences. Results are written to
`artifacts/sequence_memory_associative_recall.json`.

The intended use is research triage: if a cheap update rule cannot survive this
controlled length-extrapolation probe, it is unlikely to merit a larger neural
implementation; if it does, the next step is to replace the hand-coded keys and
values with learned projections inside a small recurrent/linear-attention model.
