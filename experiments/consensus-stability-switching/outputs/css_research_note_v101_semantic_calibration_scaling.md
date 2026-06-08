# v101: Semantic Calibration Scaling Boundary

## Question

v100 localized the semantic-scorer failure to threshold transfer: target-oracle thresholds could recover visible hard packets, while source thresholds could not safely deploy the same raw scores.

v101 asks the next sharper question:

> Does changing the amount and composition of source calibration data close the semantic threshold-transfer gap?

It also separates two overlap regimes:

- **packet-disjoint:** v100-compatible; source and target packet ids differ, but the same underlying MATH problem can appear across generator traces.
- **problem-disjoint:** stricter; source packets whose `orig_dset_idx` appears in the target panel are removed before fit/calibration.

## Harness

New scripts:

- `work/semantic_calibration_scaling_audit.py`
- `work/aggregate_semantic_calibration_v101.py`

Generated aggregate:

- `outputs/semantic_calibration_v101_aggregate.md`
- `outputs/semantic_calibration_v101_all_rows.csv`
- `outputs/semantic_calibration_v101_summary.csv`
- `outputs/semantic_calibration_v101_direction_summary.csv`

The sweep covers:

- overlap regimes: `packet`, `problem`,
- source compositions: unique Gemma -> unique Llama, unique Llama -> rebuilt unique Gemma, pooled Gemma -> unique Llama, pooled Llama -> rebuilt unique Gemma,
- features: `numeric`, `text`, `both`,
- seeds: `60601`, `60602`, `60603`,
- calibration sizes: `1,2,4,8,all` packets per deployed-mix category,
- score fields: confidence, semantic cluster probability, semantic cluster margin.

This gives `72` scorer runs and `1080` source-threshold rows.

## Result

No source-calibrated threshold passes the pre-registered lower-CI-positive deployed rule.

| overlap | source rows | source CI+ | source point+ | source clean point+ | target-oracle rows | target-oracle CI+ | best source delta | best clean delta | best oracle delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| packet-disjoint | 540 | 0 | 22 | 3 | 108 | 1 | +0.038, baseline 27/30 | +0.011, baseline 16/16 | +0.053, baseline 29/30 |
| problem-disjoint | 540 | 0 | 34 | 0 | 108 | 3 | +0.041, baseline 15/16 | +0.000, baseline 30/30 | +0.062, baseline 15/16 |

Best source-calibrated rows:

| overlap | setup | field | calib/category | delta | CI low | recoveries | baseline |
|---|---|---|---:|---:|---:|---:|---:|
| packet | unique rebuilt Gemma -> unique Llama | semantic probability | 1 | +0.038 | -0.033 | 5 | 27/30 |
| problem | unique Llama -> rebuilt unique Gemma | confidence | 1 | +0.041 | -0.006 | 5 | 15/16 |

Best clean source-calibrated rows:

| overlap | setup | field | calib/category | delta | CI low | recoveries | baseline |
|---|---|---|---:|---:|---:|---:|---:|
| packet | unique Llama -> rebuilt unique Gemma | confidence | 4 | +0.011 | +0.000 | 1 | 16/16 |
| problem | pooled rebuilt Gemma -> unique Llama | confidence | 4 | +0.000 | +0.000 | 0 | 30/30 |

Best target-oracle rows:

| overlap | setup | field | delta | CI low | recoveries | baseline |
|---|---|---|---:|---:|---:|---:|
| packet | pooled rebuilt Gemma -> unique Llama | semantic probability | +0.053 | -0.003 | 5 | 29/30 |
| problem | unique Llama -> rebuilt unique Gemma | semantic probability | +0.062 | +0.022 | 6 | 15/16 |

Direction summary makes the boundary clearer:

- Packet-disjoint source calibration has a few tiny clean point-positive rows, but no CI-positive row. The best clean row is only `+0.011`.
- Problem-disjoint source calibration has **zero** clean point-positive rows. The best clean row is no-op.
- Problem-disjoint target-oracle thresholding still has `3/108` lower-CI-positive unique run/field rows, all from unique Llama -> rebuilt unique Gemma.

## Read

v101 is a stronger negative result for the semantic-selector route:

> More or differently composed source calibration does not currently make the semantic scorer deployable. The raw scorer can still contain recoverable target-side signal, but source-calibrated accept/fallback thresholds fail to preserve already-correct baselines on target.

This matters because it blocks the optimistic v100 interpretation. v100's target-oracle headroom was not enough; once threshold choice is forced to come from source calibration, all CI-positive deployed claims disappear. Under stricter problem-disjoint calibration, even clean point-positive source rows disappear.

The correct claim is now narrower and more reviewer-resistant:

1. answer-cluster depth remains a real diagnostic bottleneck,
2. projected rank-bucket allocation remains the stronger method story,
3. local LLM verifier variants remain negative,
4. shallow semantic selector replacement has raw signal but fails deployed risk calibration,
5. solving this likely requires either a stronger verifier endpoint or a calibration set much closer to the target deployment distribution.

## Reproduction

Representative problem-disjoint calibration-scaling run:

```bash
python3 work/semantic_calibration_scaling_audit.py \
  --source-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl \
  --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl \
  --train-label Llama_unique32 \
  --test-label Gemma_unique16_rebuilt_v98 \
  --output-prefix semantic_calibration_v101_problem_unique_llama_to_unique_gemma_rebuilt_numeric_seed60601 \
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
python3 work/aggregate_semantic_calibration_v101.py
```
