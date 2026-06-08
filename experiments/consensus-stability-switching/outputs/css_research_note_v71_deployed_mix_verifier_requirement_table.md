# v71 Deployed-Mix Verifier Requirement Table

**Date:** June 1, 2026  
**Question:** What does the next real verifier run actually have to score on the current 12-prompt/category deployed-mix smoke set?

## Run

I converted the deployed-mix natural category rates into finite-sample smoke targets.

```bash
python3 work/deployed_mix_verifier_requirement_table.py \
  --output-prefix deployed_mix_verifier_requirement_table \
  --max-baseline-regressions 3
```

Primary artifact: [deployed_mix_verifier_requirement_table.md](deployed_mix_verifier_requirement_table.md).

## Result

The smoke target is concrete now:

| dataset | depth | 1 baseline regression: uniform successes/category | 1 baseline regression: tail-only target |
|---|---:|---:|---|
| MATH/Llama | top10 | `2/12` | top10-only `5/12` |
| MATH/Llama | top20 | `2/12` | top20-only `6/12` |
| MATH/Gemma | top10 | `2/12` | top10-only `3/12` |
| MATH/Gemma | top20 | `1/12` | top20-only `4/12` |

Interpretation:

- The current deployed-mix smoke can show a positive point estimate with only a small number of recoveries if baseline regressions are low.
- But a positive top20 point estimate can be won mostly by shallower recoveries. Therefore the real verifier report must separate top5, top10-only, and top20-only recovery.
- The tail-only column is the sharper deep-depth bar: if shallower buckets do not help, the verifier needs `6/12` Llama top20-only recoveries or `4/12` Gemma top20-only recoveries to offset one already-correct regression.

## Read

This makes the next real verifier benchmark less squishy. A credible report should include:

1. Baseline-correct regression count.
2. Recovery rate in `recoverable_top5`, `recoverable_top10_only`, and `recoverable_top20_only`.
3. Confidence-threshold fallback results from the v39 scorer.
4. The v45 lower-CI-positive decision.
5. A separate statement of whether top20-only recoveries were actually observed.

The current smoke set is enough to reject a completely useless verifier and enough to detect a medium effect. It is not enough for a broad positive claim if the point estimate is marginal.

## Caveat

This is a finite-sample point-estimate target table, not a replacement for the stratified bootstrap CI. It should be used as the front page for the next verifier run, with v45 deciding whether the result is strong enough to call positive.
