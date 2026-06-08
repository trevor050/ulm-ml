# v98: Rebuilt Unique-Source Semantic Risk-Control Boundary

## Question

v97 found that the valid Llama unique32 lower-duplication target stayed negative, but the intended symmetric Gemma unique16 packet JSONL was unusable: it existed on disk yet loaded as zero packet rows. v98 asks whether rebuilding that target under a fresh prefix changes the semantic-risk story.

## Rebuilt Gemma Unique16 Target

The Gemma unique-source deployed-mix target was rebuilt under a new v98 prefix, leaving the old artifact untouched.

Artifacts:

- `outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl`
- `outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.md`
- `outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98_category_stats.csv`
- `outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98_compact.jsonl`
- `outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98_compact.answer_key.json`
- `outputs/deployed_mix_unique32_llama_unique16_gemma_rebuilt_v98_representativeness.md`

The rebuilt packet set has `96` rows, `96` unique source problems, and exactly `16` packets in each deployed-mix category:

| category | selected packets | natural rate |
|---|---:|---:|
| baseline_correct | 16 | 0.228 |
| recoverable_top5 | 16 | 0.177 |
| recoverable_top10_only | 16 | 0.113 |
| recoverable_top20_only | 16 | 0.080 |
| no_visible_top20 | 16 | 0.082 |
| no_correct_generated | 16 | 0.321 |

Paired with the existing Llama unique32 target, the representativeness audit reports one packet per source within each model. The remaining caveats are Llama rare-category sparsity and cross-model source overlap: `52` shared source problems out of `96` Gemma / `74` Llama unique problems.

## Semantic-Risk Sweep

v98 reruns source-calibrated semantic risk control over three lower-duplication transfer setups:

1. balanced Llama source -> rebuilt Gemma unique16 target,
2. rebuilt Gemma unique16 source -> Llama unique32 target,
3. Llama unique32 source -> rebuilt Gemma unique16 target.

Each setup sweeps:

- feature modes: `numeric`, `text`, `both`,
- risk scores: `confidence`, `semantic_cluster_probability`, `semantic_cluster_margin`,
- seeds: `60601`, `60602`, `60603`.

That gives `81` selector/report pairs. Each report uses threshold `0` in `work/deployed_mix_verifier_report.py` after the source-calibrated selector has already applied its accept/fallback threshold.

Aggregate artifact:

- `outputs/semantic_risk_v98_rebuilt_unique_policy_aggregate.csv`

## Results

No policy passes the lower-CI-positive deployed decision rule.

Top point-estimate rows:

| setup | feature | score | seed | deployed delta | CI low | recoverable | baseline preserved | accept |
|---|---|---|---:|---:|---:|---:|---:|---:|
| unique Gemma -> unique Llama | numeric | probability | 60601 | +0.051 | -0.007 | 6/36 | 27/30 | 0.70 |
| unique Gemma -> unique Llama | both | probability | 60603 | +0.035 | +0.000 | 3/36 | 30/30 | 0.39 |
| unique Gemma -> unique Llama | text | margin | 60603 | +0.035 | +0.000 | 3/36 | 28/30 | 0.12 |
| unique Gemma -> unique Llama | both | probability | 60601 | +0.027 | +0.000 | 2/36 | 30/30 | 0.36 |
| balanced Llama -> unique Gemma | numeric | probability | 60601 | +0.022 | +0.000 | 2/48 | 16/16 | 0.42 |

Mean by setup:

| setup | rows | mean delta | max delta | mean recoveries | mean baseline regressions |
|---|---:|---:|---:|---:|---:|
| balanced Llama -> unique Gemma | 27 | -0.024 | +0.022 | 1.44 | 2.63 |
| unique Gemma -> unique Llama | 27 | -0.006 | +0.051 | 1.26 | 1.81 |
| unique Llama -> unique Gemma | 27 | -0.002 | +0.011 | 0.37 | 0.63 |

Mean by feature:

| feature | mean delta | max delta | mean recoveries | mean baseline regressions |
|---|---:|---:|---:|---:|
| numeric | +0.000 | +0.051 | 2.00 | 1.67 |
| text | -0.021 | +0.035 | 0.52 | 1.96 |
| both | -0.012 | +0.035 | 0.56 | 1.44 |

There are `8` zero-baseline-regression policies with at least one recoverable hit. The strongest clean row is unique Gemma -> unique Llama with `both` features and `semantic_cluster_probability` at seed `60603`: `3/36` recoverable hits, `30/30` baseline preservation, deployed delta `+0.035`, and CI low rounded to `+0.000`. This is not enough to call positive under the pre-specified v45 rule.

## Read

v98 closes the v97 artifact objection. The symmetric Gemma unique-source target now exists, loads correctly, has balanced categories, and yields a real lower-duplication pressure test.

The semantic scorer still has shallow signal. It can recover some visible failures, especially when training on rebuilt Gemma unique packets and testing on Llama unique32. But the signal is not deployable under conservative source calibration: the best point-estimate row regresses `3/30` already-correct Llama packets, and the best zero-regression rows are too small to clear the lower-CI-positive rule.

This makes the boundary sharper:

> Lower-duplication evaluation does not rescue the current hashed semantic risk-control family. The next positive route needs either a materially stronger verifier, more positive low-overlap calibration data, or a better semantic representation than hashed prompt/rationale text plus shallow numeric cluster features.

## Reproduction

Rebuild Gemma unique16:

```bash
python3 work/build_deployed_mix_packet_dataset.py \
  --data work/MATH_Gemma-2B.json \
  --dataset-label MATH_Gemma-deployed-mix-top20-unique16-rebuilt-v98 \
  --output-prefix cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98 \
  --target-per-category 16 \
  --trials-per-problem 64 \
  --max-packets-per-problem 1 \
  --verifier-train-problems 10 \
  --audit-holdout-gap 0
```

Make compact prompts and representativeness audit:

```bash
python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl \
  --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98_compact.jsonl \
  --representatives-per-cluster 1 \
  --rationale-chars 420

python3 work/audit_deployed_mix_representativeness.py \
  --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl \
  --output-prefix deployed_mix_unique32_llama_unique16_gemma_rebuilt_v98_representativeness
```

Representative semantic-risk row:

```bash
python3 work/semantic_risk_controlled_selector.py \
  --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl \
  --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl \
  --train-label Gemma_unique16_rebuilt_v98 \
  --test-label Llama_unique32 \
  --feature-mode both \
  --score-field semantic_cluster_probability \
  --include-problem \
  --seed 60603 \
  --output-prefix semantic_risk_v98_unique_gemma_rebuilt_to_unique_llama_both_probability_seed60603

python3 work/deployed_mix_verifier_report.py \
  --predictions outputs/semantic_risk_v98_unique_gemma_rebuilt_to_unique_llama_both_probability_seed60603_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.answer_key.json \
  --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32_category_stats.csv \
  --expected-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.jsonl \
  --thresholds 0 \
  --bootstrap-rounds 500 \
  --output-prefix semantic_risk_v98_unique_gemma_rebuilt_to_unique_llama_both_probability_seed60603_report
```
