# v104: Rich-Signal Semantic Calibration Pilot

## Question

v103 showed that expanded target-style calibration still cannot estimate a conservative one-dimensional threshold for the current hashed semantic scorer.

v104 tests a sharper objection:

> Was v103 just representation-starved by skinny cluster text?

The pilot reruns the Llama-to-expanded-Gemma target-style calibration audit with richer local semantic features:

- include the problem text,
- use `3` representatives per cluster instead of `1`,
- use `700` rationale characters instead of `360`,
- double the hash dimension to `65536`,
- train for `60` epochs with lower regularization.

## Harness

Generated aggregate:

- `outputs/semantic_target_calibration_v104_aggregate.md`
- `outputs/semantic_target_calibration_v104_all_rows.csv`
- `outputs/semantic_target_calibration_v104_summary.csv`

The pilot uses the expanded Gemma `48/category` target from v103 and runs:

- source packets: Llama unique-source and pooled Llama source packets,
- target packets: expanded Gemma `48/category`,
- overlap regime: problem-disjoint source filtering,
- features: rich `both`,
- seeds: `60601`, `60602`, `60603`,
- target calibration sizes: `1,2,4,8,16,24,all` packets/category,
- score fields: confidence, semantic probability, semantic margin,
- bootstrap rounds: `250`.

The aggregate compares these six rich runs to the matched v103 skinny problem-disjoint `both` rows.

## Result

Richer hashed semantic evidence does not improve the conservative target-calibrated result.

| family | source | rows | target-cal CI+ | clean point+ | oracle CI+ | best clean | best oracle |
|---|---|---:|---:|---:|---:|---:|---:|
| v103 skinny | pooled | 63 | 0 | 36 | 0 | +0.007, baseline 24/24 | +0.011, baseline 24/24 |
| v103 skinny | unique | 63 | 0 | 36 | 0 | +0.007, baseline 24/24 | +0.014, baseline 24/24 |
| v104 rich | pooled | 63 | 0 | 36 | 2 | +0.007, baseline 24/24 | +0.023, baseline 22/24 |
| v104 rich | unique | 63 | 0 | 36 | 2 | +0.007, baseline 24/24 | +0.018, baseline 24/24 |

The calibrated-policy result is unchanged: best clean rows recover exactly one held-out packet and have zero lower bound. Richer features do change the diagnostic held-out oracle behavior, and in the pooled case the best oracle becomes more active, but it also regresses baseline-correct packets.

## Read

v104 makes the semantic-selector stopline more specific:

> The current failure is not fixed by giving a hashed bag-of-words scorer more local problem/rationale text. Richer text changes raw/oracle behavior, but conservative target-calibrated thresholding still cannot produce a statistically positive deployed gain.

This does not prove semantic scoring is hopeless. It says the next positive route needs a material representation or policy change: process/proof-state features, symbolic answer checks, logprobs/hidden states, a stronger verifier endpoint, or a calibrated multi-feature gate that is not just one threshold on one semantic score.

## Caveats

- This is a pilot, not the full v101/v102-style matrix. It tests the most relevant expanded-target Llama-to-Gemma route.
- The expanded target is duplicated and category-balanced; it is a calibration-power pressure test rather than a generalization benchmark.
- The v104 oracle rows are target-label-selected and diagnostic only. They are not deployable policies.
- The first pooled-source command failed because shell quoting passed two source paths as one string. It was rerun successfully with proper argv separation; the aggregate includes the six successful rich runs.

## Reproduction

Representative rich run:

```bash
python3 work/semantic_target_calibration_audit.py \
  --source-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl \
  --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103.jsonl \
  --train-label Llama_unique_rich \
  --test-label Gemma_expanded48_v103 \
  --output-prefix semantic_target_calibration_v104_problem_unique_llama_to_expanded_gemma_rich_both_seed60601 \
  --feature-mode both \
  --include-problem \
  --representatives-per-cluster 3 \
  --rationale-chars 700 \
  --hash-dim 65536 \
  --epochs 60 \
  --lr 0.05 \
  --l2 1e-6 \
  --category-stats outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103_category_stats.csv \
  --calibration-per-category 1,2,4,8,16,24,all \
  --seed 60601 \
  --bootstrap-rounds 250 \
  --overlap-key problem \
  --exclude-test-problems-from-source
```

Aggregate:

```bash
python3 work/aggregate_semantic_target_calibration_v104.py
```
