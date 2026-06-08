# v39 - Deployed-Mix Threshold/Fallback Scoring

**Status:** June 1, 2026. Scorer upgrade and runbook for turning deployed-mix verifier predictions into a policy-level result.

## Why This Exists

Raw verifier accuracy is the wrong deployment metric for this project.

The method only matters if a verifier can:

1. preserve already-correct `cluster_sum` defaults,
2. recover visible correct clusters at top-5/top-10/top-20 depth,
3. avoid spending confidence on no-visible/no-correct cases,
4. expose enough uncertainty to fall back to the baseline answer or escalate to fuller evidence.

v37 built the balanced deployed-mix prompt assets. v38 gave the break-even algebra. v39 wires the scorer so an external/local verifier run can be evaluated as a deployed policy rather than as a flat packet-accuracy table.

## Scorer Behavior

`work/score_deployed_mix_verifier.py` now reports three layers:

- raw category accuracy and baseline preservation,
- confidence-threshold fallback sweep,
- natural-rate weighted deployed rows for MATH/Llama and MATH/Gemma.

For a threshold `t`, any prediction with `confidence < t` falls back to the original baseline answer. This turns model confidence into a preservation/recovery tradeoff.

The threshold CSV emits category rows plus:

```text
weighted:MATH/Llama
weighted:MATH/Gemma
```

These weighted rows use the natural deployed-mix category rates from:

```text
outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv
outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv
```

The important field is:

```text
deployed_delta = natural_weighted_deployed_accuracy - natural_baseline_correct_rate
```

That is the number the paper should use once real verifier predictions exist.

## Command

After generating predictions for both deployed-mix prompt files:

```bash
python3 work/score_deployed_mix_verifier.py \
  --predictions outputs/<model>_llama_deployed_mix_predictions.jsonl outputs/<model>_gemma_deployed_mix_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json \
  --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv \
  --thresholds 0,0.25,0.5,0.75,0.9 \
  --output-prefix <model>_deployed_mix_verifier
```

Expected outputs:

```text
outputs/<model>_deployed_mix_verifier.md
outputs/<model>_deployed_mix_verifier.csv
outputs/<model>_deployed_mix_verifier_details.jsonl
outputs/<model>_deployed_mix_verifier_thresholds.csv
```

## Synthetic Smoke

I also generated synthetic predictions only to validate scorer plumbing:

```text
outputs/synthetic_deployed_mix_llama_predictions.jsonl
outputs/synthetic_deployed_mix_gemma_predictions.jsonl
outputs/synthetic_deployed_mix_verifier_eval.md
outputs/synthetic_deployed_mix_verifier_eval.csv
outputs/synthetic_deployed_mix_verifier_eval_details.jsonl
outputs/synthetic_deployed_mix_verifier_eval_thresholds.csv
```

These are not benchmark evidence. They deliberately encode a toy high-confidence recovery / low-confidence fallback pattern so the threshold machinery can be sanity-checked before spending model calls.

The smoke confirms the output shape:

| threshold | weighted row | total | accept rate | deployed accuracy | baseline preservation | deployed delta |
|---:|---|---:|---:|---:|---:|---:|
| 0.00 | MATH/Llama | 72 | 1.000 | 0.817 | 0.611 | +0.389 |
| 0.75 | MATH/Llama | 72 | 0.743 | 0.743 | 0.685 | +0.315 |
| 0.90 | MATH/Llama | 72 | 0.428 | 0.428 | 1.000 | +0.000 |
| 0.00 | MATH/Gemma | 72 | 1.000 | 0.641 | 0.658 | +0.342 |
| 0.75 | MATH/Gemma | 72 | 0.562 | 0.562 | 0.737 | +0.263 |
| 0.90 | MATH/Gemma | 72 | 0.299 | 0.299 | 1.000 | +0.000 |

The `0.90` threshold falls back to the baseline on all non-baseline synthetic cases, so deployed delta returns to zero. This is the desired safety sanity check.

## What This Adds To The Pitch

Before v39, the decisive missing benchmark was underspecified as "run a verifier." That is too vague.

After v39, the decisive benchmark is:

> Run an external/local verifier on the deployed-mix compact top-20 prompts, require confidence, sweep fallback thresholds, and report natural-rate weighted deployed delta.

This makes the result falsifiable:

- If recovery is high but baseline preservation is poor, the method fails as deployed policy.
- If recovery is modest but preservation is near-perfect, v38 says even low recovery can be enough.
- If confidence cannot separate recoverable from harmful invocations, compact/full cascade claims should be removed or reframed.
- If threshold fallback returns cleanly to baseline at high `t`, the method has a safety knob even before full-prompt escalation.

## Verification

```bash
python3 work/test_score_deployed_mix_verifier.py
python3 work/score_deployed_mix_verifier.py \
  --predictions outputs/synthetic_deployed_mix_llama_predictions.jsonl outputs/synthetic_deployed_mix_gemma_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json \
  --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv \
  --thresholds 0,0.5,0.75,0.9 \
  --output-prefix synthetic_deployed_mix_verifier_eval
```

Both commands passed locally after the scorer update.
