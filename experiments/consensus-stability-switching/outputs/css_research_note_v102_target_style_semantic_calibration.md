# v102: Target-Style Semantic Calibration Boundary

## Question

v101 showed that source-calibrated semantic thresholds do not transfer, even when source calibration size and composition are varied.

v102 asks the stronger follow-up:

> If the semantic scorer is trained on source packets but thresholded on labeled target-style calibration packets, does held-out target performance become deployable?

This is not a deployable zero-label method. It is a sample-efficiency diagnostic for whether the current hashed semantic scorer can be rescued by same-distribution calibration.

## Harness

New scripts:

- `work/semantic_target_calibration_audit.py`
- `work/aggregate_semantic_target_calibration_v102.py`

Generated aggregate:

- `outputs/semantic_target_calibration_v102_aggregate.md`
- `outputs/semantic_target_calibration_v102_all_rows.csv`
- `outputs/semantic_target_calibration_v102_summary.csv`
- `outputs/semantic_target_calibration_v102_direction_summary.csv`

The sweep mirrors v101:

- overlap regimes: packet-disjoint and problem-disjoint source training,
- source compositions: unique Gemma, unique Llama, pooled Gemma, pooled Llama,
- features: numeric, text, both,
- seeds: `60601`, `60602`, `60603`,
- target calibration sizes: `1,2,4,8,all` packets/category,
- score fields: confidence, semantic probability, semantic margin.

Each run trains on source packets, chooses the accept/fallback threshold on a labeled target calibration split, and evaluates on held-out target packets.

## Result

No target-style calibrated threshold policy passes the lower-CI-positive held-out deployed rule.

| overlap | rows | target-cal CI+ | target-cal point+ | target-cal clean point+ | held-out oracle CI+ | best target-cal delta | best clean delta | best oracle delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| packet-disjoint | 540 | 0 | 1 | 1 | 6 | +0.024, baseline 15/15 | +0.024, baseline 15/15 | +0.076, baseline 15/15 |
| problem-disjoint | 540 | 0 | 18 | 0 | 3 | +0.025, baseline 11/12 | +0.000, baseline 29/29 | +0.066, baseline 8/8 |

Best target-calibrated rows:

| overlap | setup | field | calib/category | delta | CI low | recoveries | baseline |
|---|---|---|---:|---:|---:|---:|---:|
| packet | pooled Llama -> rebuilt unique Gemma | confidence | 1 | +0.024 | +0.000 | 2 | 15/15 |
| problem | pooled Llama -> rebuilt unique Gemma | confidence | 4 | +0.025 | -0.027 | 3 | 11/12 |

Best clean target-calibrated rows:

| overlap | setup | field | calib/category | delta | CI low | recoveries | baseline |
|---|---|---|---:|---:|---:|---:|---:|
| packet | pooled Llama -> rebuilt unique Gemma | confidence | 1 | +0.024 | +0.000 | 2 | 15/15 |
| problem | pooled rebuilt Gemma -> unique Llama | confidence | 1 | +0.000 | +0.000 | 0 | 29/29 |

Best held-out target-oracle rows:

| overlap | setup | field | delta | CI low | recoveries | baseline |
|---|---|---|---:|---:|---:|---:|
| packet | pooled rebuilt Gemma -> unique Llama | semantic probability | +0.076 | +0.000 | 3 | 15/15 |
| problem | unique Llama -> rebuilt unique Gemma | confidence | +0.066 | +0.000 | 3 | 8/8 |

## Read

v102 is a second stopline for the cheap semantic-selector route:

> Same-distribution threshold calibration helps only weakly at this panel size. It does not produce a held-out CI-positive deployed policy.

The result is stricter than v101 in one way and softer in another:

- Softer: target-style calibration is allowed to see labeled target-distribution packets.
- Stricter: evaluation is held out from that target calibration split.

The conclusion is still negative. Packet-disjoint target-style calibration has one tiny clean point-positive row (`+0.024`) with zero lower bound. Problem-disjoint clean target-calibrated rows are all no-op. Held-out target-oracle rows show that some raw signal remains, but not enough to estimate a safe threshold from these small calibration panels.

The semantic path now needs a material change:

1. a stronger verifier endpoint,
2. substantially more labeled target-style calibration data,
3. richer features such as logprobs, proof-state/process features, symbolic checks, or better rationale retrieval,
4. or a different decision rule than one-dimensional threshold fallback.

## Reproduction

Representative problem-disjoint target-style calibration run:

```bash
python3 work/semantic_target_calibration_audit.py \
  --source-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl \
  --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl \
  --train-label Llama_unique32 \
  --test-label Gemma_unique16_rebuilt_v98 \
  --output-prefix semantic_target_calibration_v102_problem_unique_llama_to_unique_gemma_rebuilt_numeric_seed60601 \
  --feature-mode numeric \
  --category-stats outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98_category_stats.csv \
  --calibration-per-category 1,2,4,8,all \
  --seed 60601 \
  --bootstrap-rounds 250 \
  --dedupe-problems \
  --overlap-key problem \
  --exclude-test-problems-from-source
```

Aggregate:

```bash
python3 work/aggregate_semantic_target_calibration_v102.py
```
