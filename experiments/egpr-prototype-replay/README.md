# EGPR Prototype Replay

## Question

Can entropy-gated prototype replay improve test-time adaptation without labels?

## Verdict

No, parked.

## Answer So Far

True no-adapt baselines beat or match online prototype replay on the
shifted-digits suite. Threshold tweaking is not enough to revive this as a
method.

## Interesting Bit

The failure signal may still be useful for predicting when adaptation is unsafe.

## Command

```bash
PYTHONPATH=src python experiments/egpr-prototype-replay/egpr_digits_tta.py --seeds 0 1 2 3 4 --output artifacts/egpr_digits_tta.json
```

## Deeper Notes

- `docs/given-up/egpr-prototype-replay.md`
- `docs/egpr-brief.md`
