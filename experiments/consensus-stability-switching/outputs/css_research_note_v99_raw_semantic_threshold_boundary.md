# v99: Raw Semantic Threshold Boundary

## Question

v98 showed that source-calibrated semantic risk control is not deployable on lower-duplication targets. But that leaves an important ambiguity:

> Are the raw semantic scores useless, or is source-side threshold calibration failing to pick the right accept/fallback boundary?

v99 answers this with a target-side threshold diagnostic. It is intentionally an oracle diagnostic, not a deployable policy: train the raw hashed semantic scorer, score a target packet set, then sweep target thresholds over `confidence`, `semantic_cluster_probability`, and `semantic_cluster_margin`.

## Harness

New script:

- `work/semantic_threshold_diagnostic.py`
- `outputs/semantic_threshold_diagnostic.py`

The script loads raw prediction JSONL, replaces the fallback score with each requested score field, sweeps target thresholds, computes natural-rate weighted deployed delta, and bootstraps only the best row per score field. This separates raw ranking headroom from source-calibrated threshold transfer.

Aggregate artifact:

- `outputs/raw_semantic_v99_threshold_best_aggregate.csv`

The run covers:

- transfer setups: balanced Llama -> rebuilt Gemma unique16, rebuilt Gemma unique16 -> Llama unique32, Llama unique32 -> rebuilt Gemma unique16,
- feature modes: `numeric`, `text`, `both`,
- seeds: `60601`, `60602`, `60603`,
- threshold score fields: `confidence`, `semantic_cluster_probability`, `semantic_cluster_margin`.

That yields `81` best-threshold rows.

## Results

Target-side oracle thresholding finds `4/81` lower-CI-positive rows.

Top rows:

| setup | feature | score field | seed | delta | CI | recoverable | baseline preserved | accept |
|---|---|---|---:|---:|---:|---:|---:|---:|
| rebuilt Gemma -> Llama unique32 | both | semantic_cluster_probability | 60601 | +0.063 | +0.022..+0.117 | 5/36 | 30/30 | 0.49 |
| balanced Llama -> rebuilt Gemma | numeric | confidence | 60603 | +0.044 | +0.011..+0.089 | 4/48 | 16/16 | 0.34 |
| balanced Llama -> rebuilt Gemma | numeric | semantic_cluster_margin | 60603 | +0.044 | +0.011..+0.089 | 4/48 | 16/16 | 0.37 |
| balanced Llama -> rebuilt Gemma | numeric | semantic_cluster_probability | 60601 | +0.033 | +0.011..+0.066 | 3/48 | 16/16 | 0.53 |

Mean by setup:

| setup | rows | mean delta | max delta | pass rows | mean recoveries | mean baseline regressions |
|---|---:|---:|---:|---:|---:|---:|
| balanced Llama -> rebuilt Gemma | 27 | +0.012 | +0.044 | 3 | 1.07 | 0.00 |
| rebuilt Gemma -> Llama unique32 | 27 | +0.008 | +0.063 | 1 | 0.85 | 0.19 |
| Llama unique32 -> rebuilt Gemma | 27 | +0.007 | +0.029 | 0 | 0.89 | 0.22 |

Mean by feature:

| feature | mean delta | max delta | pass rows | mean recoveries | mean baseline regressions |
|---|---:|---:|---:|---:|---:|
| numeric | +0.014 | +0.044 | 3 | 1.30 | 0.00 |
| text | +0.002 | +0.014 | 0 | 0.11 | 0.00 |
| both | +0.011 | +0.063 | 1 | 1.41 | 0.41 |

Mean by threshold score:

| score field | mean delta | max delta | pass rows | mean recoveries | mean baseline regressions |
|---|---:|---:|---:|---:|---:|
| confidence | +0.008 | +0.044 | 1 | 1.04 | 0.30 |
| semantic_cluster_margin | +0.009 | +0.044 | 1 | 0.89 | 0.07 |
| semantic_cluster_probability | +0.010 | +0.063 | 2 | 0.89 | 0.04 |

## Read

v99 changes the boundary from "the raw semantic scorer is dead" to:

> Raw semantic scoring has small lower-duplication headroom under target-side oracle thresholding, but the source-calibrated v98 gate cannot select that threshold safely.

This matters because v98's negative result is not purely a representation failure. The best v99 row recovers `5/36` Llama unique recoverable packets with zero baseline regressions and a positive lower CI. The best Gemma-target rows recover `3-4/48` with zero baseline regressions and positive lower CIs.

But v99 is not deployable evidence. It chooses thresholds on the target packet set. The source-calibrated v98 sweep is still the deployable test, and it remains negative. Therefore the next semantic-selector path is not "add more hashed features" by default. It is:

1. enlarge and diversify low-overlap calibration data,
2. calibrate accept/fallback thresholds against baseline-regression risk more directly,
3. test whether the v99 target thresholds can be predicted from source or held-out metadata,
4. or replace hashed text with a stronger semantic representation.

## Reproduction

Representative raw scorer row:

```bash
python3 work/text_cluster_semantic_scorer.py \
  --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl \
  --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl \
  --train-label Gemma_unique16_rebuilt_v98 \
  --test-label Llama_unique32 \
  --feature-mode both \
  --include-problem \
  --seed 60601 \
  --output-prefix raw_semantic_v99_unique_gemma_rebuilt_to_unique_llama_both_seed60601
```

Target-threshold diagnostic:

```bash
python3 work/semantic_threshold_diagnostic.py \
  --predictions outputs/raw_semantic_v99_unique_gemma_rebuilt_to_unique_llama_both_seed60601_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.answer_key.json \
  --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32_category_stats.csv \
  --bootstrap-rounds 500 \
  --output-prefix raw_semantic_v99_unique_gemma_rebuilt_to_unique_llama_both_seed60601_threshold_diag
```
