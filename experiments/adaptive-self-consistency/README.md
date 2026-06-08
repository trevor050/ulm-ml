# Adaptive Posterior Self-Consistency

## Question

Can posterior stopping beat fixed self-consistency without real answer traces?

## Verdict

No, parked.

## Answer So Far

The synthetic simulator is useful replay machinery, but not enough to justify an
active research claim. This becomes interesting again only with cached real-model
answer traces.

## Interesting Bit

The resurrection gate is clean: real traces, then beat fixed-budget and
oracle-ish stopping baselines.

## Commands

```bash
PYTHONPATH=src python experiments/adaptive-self-consistency/adaptive_consistency_synthetic.py
PYTHONPATH=src python experiments/adaptive-self-consistency/adaptive_consistency_replay.py traces.csv --max-samples 32
```

## Deeper Notes

- `docs/given-up/adaptive-self-consistency.md`
- `docs/adaptive-posterior-self-consistency.md`
