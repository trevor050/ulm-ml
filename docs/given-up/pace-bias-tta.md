# PACE Bias-Only TTA

Status: `given_up`

PACE is given up as a standalone research project. It survives only as a narrow
diagnostic baseline for class-prior or logit-prior drift.

## What Remains Useful

`src/ulm_ml/tta.py` implements a small NumPy-only bias adapter with source,
entropy, conservative entropy, and PACE objectives. `docs/pace-bias-tta-report.md`
shows the right narrow behavior: bias-only adaptation can help an additive logit
prior drift, and it fails on feature corruption.

## Why It Is Given Up

The positive result is too narrow for a standalone project. It does not repair
feature damage, and the source-prior anchor is brittle when the target class
prior moves. Calling it general test-time adaptation would be fake.

## Revival Gate

Revive only as part of a broader adaptation-safety or calibration project. The
minimum gate is an online prior estimator plus an abstain rule that refuses
feature-damage batches.

Baseline command:

```bash
PYTHONPATH=src python experiments/pace-bias-tta/pace_bias_tta.py --seeds 0 1 2 3 4 --out-dir artifacts/pace_bias_tta
```

It is publishable only if the method can say when bias adaptation is appropriate,
not merely show a small win on a hand-built logit drift.
