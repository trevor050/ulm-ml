# EGPR Prototype Replay

Status: `given_up`

EGPR is given up as an adaptation method.

## What Remains Useful

`src/ulm_ml/egpr.py` is still a useful scaffold for studying no-label adaptation
safety. It has source-only, prototype no-adapt, all-replay, and gated replay
paths, plus a first `adaptation_risk_score` diagnostic.

## Why It Is Given Up

`docs/egpr-brief.md` reports the important negative result: online prototype
updates usually hurt on the shifted digits benchmark, and the frozen prototype
head often matches or beats replay. That kills the original accuracy-improvement
claim.

## Revival Gate

Do not revive EGPR by tweaking replay thresholds for a prettier accuracy table.
Revive only if the no-label risk diagnostic predicts harmful adaptation well
enough to trigger a source-only fallback before damage.

The next acceptable command should evaluate safety prediction, not just replay
accuracy:

```bash
PYTHONPATH=src python experiments/egpr-prototype-replay/egpr_digits_tta.py --seeds 0 1 2 3 4 --output artifacts/egpr_digits_tta.json
```

The revival metric is whether fallback improves or preserves source-only
accuracy on harmful shifts while still allowing adaptation on genuinely safe
batches.
