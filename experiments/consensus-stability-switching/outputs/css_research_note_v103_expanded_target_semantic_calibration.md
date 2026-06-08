# v103: Expanded-Target Semantic Calibration Boundary

## Question

v102 allowed labeled target-style calibration but used small lower-duplication target panels. That left a clean objection:

> Did target-style semantic calibration fail only because the held-out target split was too small?

v103 expands the Gemma target deployed-mix packet set to `48/category` and repeats the Llama-to-Gemma semantic threshold audit. This is still not deployable as a zero-label method; it is a sample-efficiency diagnostic for whether the current hashed semantic scorer can estimate a safe fallback threshold when given more labeled target-style packets.

## Assets

Expanded target packet set:

- `outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103.jsonl`
- `outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103.md`
- `outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103_category_stats.csv`

The expanded target has `288` packets, balanced to `48/category`.

| category | natural count | natural rate | selected count |
|---|---:|---:|---:|
| baseline_correct | 1006 | 0.192 | 48 |
| recoverable_top5 | 866 | 0.165 | 48 |
| recoverable_top10_only | 554 | 0.106 | 48 |
| recoverable_top20_only | 384 | 0.073 | 48 |
| no_visible_top20 | 550 | 0.105 | 48 |
| no_correct_generated | 1888 | 0.360 | 48 |

Llama expansion was attempted at `48/category` and `24/category`, but both builds were too slow locally and were killed. The v103 sweep therefore uses existing Llama source packet sets and evaluates only expanded Gemma as the target.

## Harness

Generated aggregate:

- `outputs/semantic_target_calibration_v103_aggregate.md`
- `outputs/semantic_target_calibration_v103_all_rows.csv`
- `outputs/semantic_target_calibration_v103_summary.csv`
- `outputs/semantic_target_calibration_v103_direction_summary.csv`

Sweep dimensions:

- source packets: Llama unique-source and pooled Llama source packets,
- target packets: expanded Gemma `48/category`,
- overlap regimes: packet-disjoint and problem-disjoint source filtering,
- features: numeric, text, both,
- seeds: `60601`, `60602`, `60603`,
- target calibration sizes: `1,2,4,8,16,24,all` packets/category,
- score fields: confidence, semantic probability, semantic margin,
- bootstrap rounds: `250`.

## Result

No target-calibrated threshold policy passes the lower-CI-positive held-out deployed rule.

| overlap | rows | target-cal CI+ | target-cal point+ | clean point+ | test>=60 rows | oracle CI+ | best target-calibrated | best held-out oracle |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| packet-disjoint | 378 | 0 | 226 | 209 | 378 | 5 | +0.007, CI low 0.000, baseline 24/24, n=144 | +0.034, CI low +0.014, baseline 24/24, n=144 |
| problem-disjoint | 378 | 0 | 226 | 209 | 378 | 5 | +0.007, CI low 0.000, baseline 24/24, n=144 | +0.034, CI low +0.014, baseline 24/24, n=144 |

The positive target-calibrated rows are tiny. The best clean calibrated threshold recovers exactly `1/72` held-out recoverable packets while preserving all `24/24` baseline-correct packets, giving natural-rate deployed delta `+0.0069` with a zero lower bound. The held-out oracle threshold can recover `5/72` recoverable packets with the same `24/24` preservation, giving natural-rate deployed delta `+0.0344` with positive lower bound.

## Read

v103 rules out the easy "small target calibration panel" rescue for the current one-dimensional hashed semantic threshold family.

The result is not "there is no signal." The held-out oracle threshold passes, and many target-calibrated rows recover one packet without baseline regression. The result is narrower and more useful:

> With duplicated expanded target-style calibration, the current semantic score can sometimes make a tiny clean move, but it cannot estimate a conservative threshold that gives a statistically positive deployed gain.

This shifts the semantic-selector boundary from "need a little more calibration" to "need materially richer signal or a different policy class." Plausible next changes are richer target labels/features, process/proof-state evidence, symbolic checks, calibrated multi-feature gates, or a stronger measured verifier endpoint.

## Caveats

- Expanded Gemma is balanced and duplicated; it is a power/sample-size pressure test, not a broad generalization benchmark.
- Llama target expansion was not completed locally, so v103 is one-directional: Llama source to expanded Gemma target.
- Packet-disjoint and problem-disjoint aggregates match here; source exclusion is not the limiting factor for this Llama-to-Gemma setup.
- The "oracle" threshold is selected on held-out target labels and is diagnostic only. It should be used to localize headroom, not as deployable evidence.

## Reproduction

Target packet build:

```bash
python3 work/build_deployed_mix_packet_dataset.py \
  --data work/MATH_Gemma-2B.json \
  --dataset-label MATH_Gemma-deployed-mix-top20-expanded48-v103 \
  --output-prefix cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103 \
  --target-per-category 48 \
  --trials-per-problem 96 \
  --verifier-train-problems 80 \
  --verifier-samples-per-problem 8000 \
  --n 128 \
  --top-k 20
```

Representative problem-disjoint calibration run:

```bash
python3 work/semantic_target_calibration_audit.py \
  --source-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl \
  --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103.jsonl \
  --train-label Llama_unique32 \
  --test-label Gemma_expanded48_v103 \
  --output-prefix semantic_target_calibration_v103_problem_unique_llama_to_expanded_gemma_numeric_seed60601 \
  --feature-mode numeric \
  --category-stats outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103_category_stats.csv \
  --calibration-per-category 1,2,4,8,16,24,all \
  --seed 60601 \
  --bootstrap-rounds 250 \
  --overlap-key problem \
  --exclude-test-problems-from-source
```

Aggregate:

```bash
python3 work/aggregate_semantic_target_calibration_v103.py
```
