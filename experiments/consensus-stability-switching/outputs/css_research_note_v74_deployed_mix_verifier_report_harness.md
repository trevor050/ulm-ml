# v74 Deployed-Mix Verifier Report Harness

**Date:** June 1, 2026  
**Question:** Once real verifier predictions exist, can the benchmark produce one reviewer-readable report instead of scattered scorer outputs?

## Run

I added [deployed_mix_verifier_report.py](deployed_mix_verifier_report.py), a wrapper that joins:

- raw category accuracy and baseline preservation,
- v71 finite-sample target checks,
- confidence-threshold fallback,
- natural-rate weighted deployed delta,
- v45 stratified bootstrap CI decisions.

Smoke command using existing synthetic predictions:

```bash
python3 work/deployed_mix_verifier_report.py \
  --predictions outputs/synthetic_deployed_mix_llama_predictions.jsonl outputs/synthetic_deployed_mix_gemma_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json \
  --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv \
  --thresholds 0,0.5,0.75,0.9 \
  --bootstrap-rounds 100 \
  --output-prefix synthetic_deployed_mix_verifier_report
```

Primary artifact: [synthetic_deployed_mix_verifier_report.md](synthetic_deployed_mix_verifier_report.md).

## Result

The report now emits the exact sections the real verifier benchmark needs:

1. Coverage by dataset.
2. Raw category scores.
3. v71 target checks, including top20-only tail recovery.
4. Confidence-threshold CI decisions.
5. CSVs for categories, targets, and CI rows.

The synthetic smoke is not evidence about the method. It is plumbing validation: the report is complete, deterministic, and integrates the existing v39/v45/v71 machinery.

## Real Verifier Command Shape

After an endpoint produces prediction JSONL files, run:

```bash
python3 work/deployed_mix_verifier_report.py \
  --predictions outputs/<model>_llama_deployed_mix_predictions.jsonl outputs/<model>_gemma_deployed_mix_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json \
  --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv \
  --thresholds 0,0.5,0.75,0.9 \
  --bootstrap-rounds 1000 \
  --output-prefix <model>_deployed_mix_verifier_report
```

## Pass/Fail Read

A credible positive run should:

- be complete for both datasets,
- preserve already-correct baseline prompts,
- recover top5/top10/top20-only buckets separately,
- clear the v71 finite-sample target check,
- pass at least one lower-CI-positive threshold in the CI table,
- report balanced and source-unique checks separately if using unique-source assets.

## Caveat

This is a harness result, not a verifier result. The decisive evidence still requires model predictions from a real endpoint.
