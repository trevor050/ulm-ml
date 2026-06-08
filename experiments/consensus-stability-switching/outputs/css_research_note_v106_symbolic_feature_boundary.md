# v106: Symbolic Feature Boundary

## Question

v105 left a reasonable next objection:

> Maybe hashed semantic text is the wrong cheap signal. Do answer-shape and arithmetic/process consistency features make the selector safer?

v106 tests that locally without a live LLM endpoint. It trains a dependency-light cluster scorer on Llama unique-source packets and evaluates on the expanded Gemma `48/category` target panel from v103, using the same target-style threshold/fallback protocol and natural-rate deployed delta rule as v103-v105.

## Signal

The scorer uses no ground-truth answer at deployment time. Cluster features are:

- existing rank/support/score features,
- answer-shape features such as parseable number, fraction/decimal/integer/negative flags, length, setlike/radical/alphabetic flags,
- exact and numeric equivalence to the baseline answer,
- simple arithmetic-equation consistency checks over representative rationales, using only safe fraction arithmetic over numeric expressions.

This is not a full symbolic verifier. It is a cheap local audit of whether answer/process structure gives a materially different signal from the current hashed semantic family.

## Harness

Generated artifacts:

- `work/symbolic_feature_scorer.py`
- `work/raw_prediction_target_calibration_audit.py`
- `outputs/symbolic_feature_scorer_v106.py`
- `outputs/raw_prediction_target_calibration_audit_v106.py`
- `outputs/symbolic_features_v106_llama_to_expanded_gemma_seed60601_predictions.jsonl`
- `outputs/symbolic_features_v106_llama_to_expanded_gemma_seed60602_predictions.jsonl`
- `outputs/symbolic_features_v106_llama_to_expanded_gemma_seed60603_predictions.jsonl`
- `outputs/symbolic_features_v106_target_calibration_seed60601.csv`
- `outputs/symbolic_features_v106_target_calibration_seed60602.csv`
- `outputs/symbolic_features_v106_target_calibration_seed60603.csv`

Setup:

- source packets: `outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl`
- target packets: `outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103.jsonl`
- seeds: `60601,60602,60603`
- score fields: confidence, symbolic cluster probability, symbolic cluster margin
- target calibration sizes: `1,2,4,8,16,24,all`
- bootstrap rounds: `250`

## Raw Selector Behavior

Blindly accepting the symbolic-feature scorer is unsafe. It finds a little shallow top-5 signal, but trades off baseline preservation.

| seed | baseline preserved | recoverable top5 | top10-only | top20-only |
|---:|---:|---:|---:|---:|
| 60601 | 45/48 | 3/48 | 0/48 | 0/48 |
| 60602 | 40/48 | 4/48 | 0/48 | 0/48 |
| 60603 | 38/48 | 7/48 | 1/48 | 0/48 |

The most active seed recovers `8/144` recoverable packets, but only preserves `38/48` already-correct baseline packets and still recovers `0/48` top20-only tails.

## Target-Calibrated Result

Conservative target-style thresholding mostly falls back to the baseline. No row clears the lower-CI-positive deployed rule.

| seed | best clean calibrated delta | CI | recoveries | baseline | best held-out oracle delta | oracle baseline |
|---:|---:|---:|---:|---:|---:|---:|
| 60601 | +0.007 | 0.000..0.021 | 1/72 | 24/24 | +0.014 | 24/24 |
| 60602 | +0.004 | 0.000..0.012 | 1/120 | 40/40 | +0.011 | 44/44 |
| 60603 | +0.007 | 0.000..0.021 | 1/72 | 24/24 | +0.013 | 37/40 |

The best clean calibrated rows recover exactly one held-out recoverable packet and have a zero lower bound. Diagnostic oracle rows are also small; the most active oracle row recovers `7/120` but preserves only `37/40` baseline-correct packets and remains CI-negative.

## Read

v106 closes the cheap-symbolic/process-feature version of the post-v105 escape hatch:

> Simple answer-shape, baseline-equivalence, and arithmetic-consistency features do not produce a conservative held-out deployed policy on the expanded Gemma target panel.

The negative boundary is narrow but useful. It does not say symbolic verification is hopeless. It says the dependency-light local version is not enough. The next materially different route still needs a stronger signal source: a real symbolic equivalence engine tied to problem semantics, logprobs/hidden states, richer process/proof features, or a stronger measured verifier endpoint.

## Reproduction

```bash
python3 work/symbolic_feature_scorer.py \
  --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl \
  --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103.jsonl \
  --train-label Llama_unique32 \
  --test-label Gemma_expanded48_v103 \
  --output-prefix symbolic_features_v106_llama_to_expanded_gemma_seed60601 \
  --exclude-test-problems-from-train \
  --seed 60601

python3 work/raw_prediction_target_calibration_audit.py \
  --predictions outputs/symbolic_features_v106_llama_to_expanded_gemma_seed60601_predictions.jsonl \
  --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103.jsonl \
  --category-stats outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103_category_stats.csv \
  --score-fields confidence symbolic_cluster_probability symbolic_cluster_margin \
  --calibration-per-category 1,2,4,8,16,24,all \
  --bootstrap-rounds 250 \
  --seed 60601 \
  --output-prefix symbolic_features_v106_target_calibration_seed60601
```
