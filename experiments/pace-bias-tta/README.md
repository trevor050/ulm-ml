# PACE Bias-Only TTA

## Question

Is bias-only adaptation enough for a standalone test-time adaptation project?

## Verdict

No, parked.

## Answer So Far

PACE is useful only as a narrow label-prior-drift diagnostic. It does not repair
feature corruption and should not be treated as an independent method.

## Interesting Bit

It is a good negative control for separating prior shift from real feature
damage.

## Command

```bash
PYTHONPATH=src python experiments/pace-bias-tta/pace_bias_tta.py --seeds 0 1 2 3 4 --out-dir artifacts/pace_bias_tta
```

## Deeper Notes

- `docs/given-up/pace-bias-tta.md`
- `docs/pace-bias-tta-report.md`
