# v29 Cascade Scoring Harness

## Question

v28 defines a compact-first/full-fallback budget target, but a reviewer can reasonably ask:

> How will the real verifier fallback policy be measured once compact and full predictions exist?

## Artifact

New scorer:

```bash
python3 work/score_verifier_cascade.py \
  --answer-key outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.answer_key.json \
  --compact-predictions outputs/<model>_llama_top20_diverse_compact_predictions.jsonl \
  --full-predictions outputs/<model>_llama_top20_diverse_full_predictions.jsonl \
  --output-prefix outputs/<model>_llama_top20_diverse_cascade_eval \
  --thresholds 0.3,0.5,0.7,0.9
```

Test:

```bash
python3 work/test_score_verifier_cascade.py
```

Copied snapshots:

- `outputs/score_verifier_cascade.py`
- `outputs/test_score_verifier_cascade.py`

## What It Measures

For each confidence threshold, the scorer reports compact-only accuracy, full-only accuracy, cascade accuracy, fallback rate, low-confidence fallback rate, and missing/invalid prediction fallback rate.

This converts the v28 oracle budget target into a measurable verifier property:

```text
Can compact-run confidence or disagreement trigger full prompts on a small enough fraction of cases while approaching full-prompt accuracy?
```

## Interpretation

This is not a result because no external/local verifier run is available yet. It is the harness that prevents the next verifier experiment from being another isolated accuracy number. The first serious run should produce compact predictions and full predictions for the same packet IDs, then score the confidence cascade against the answer key.
