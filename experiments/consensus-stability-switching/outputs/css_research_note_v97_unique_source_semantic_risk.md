# v97: Unique-Source Semantic Risk-Control Pressure

**Date:** June 2, 2026

## Question

v96 showed that source-calibrated semantic risk control does not make hashed semantic scoring deployable on the balanced deployed-mix panels. Does the conclusion change when evaluation moves to lower-duplication deployed-mix packets?

## Setup

I reused the v96 source-calibrated semantic-risk wrapper and evaluated the completed balanced Gemma->Llama policies on the lower-duplication Llama unique32 packet set:

- train/calibrate source: `outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl`;
- evaluate target: `outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl`;
- target size: `74` packets over `74` unique source problems;
- recoverable target rows: `36` total;
- baseline-correct rows: `30`;
- sweep: `3` feature modes x `3` risk score fields x `3` seeds = `27` deployed policies.

Each policy was scored with the deployed-mix report harness at threshold `0`, because the accept/fallback threshold was already selected on source calibration data.

## Valid Llama Unique32 Result

Artifact: `outputs/semantic_risk_v97_llama_unique32_policy_aggregate.csv`.

Feature summary:

| feature | policies | mean deployed delta | max deployed delta | mean recoverable correct | mean baseline preserved | mean accept rate |
|---|---:|---:|---:|---:|---:|---:|
| both | 9 | -0.002 | +0.014 | 0.44/36 | 29.22/30 | 0.24 |
| numeric | 9 | -0.005 | +0.000 | 0.00/36 | 29.67/30 | 0.77 |
| text | 9 | -0.007 | +0.000 | 0.00/36 | 29.33/30 | 0.04 |

Best rows:

| policy | recoverable correct | baseline preserved | accept rate | deployed delta | CI low | decision |
|---|---:|---:|---:|---:|---:|---|
| both/probability seed60602 | 1/36 | 30/30 | 0.32 | +0.014 | +0.000 | uncertain_or_negative |
| both/probability seed60601 | 2/36 | 28/30 | 0.61 | +0.012 | -0.034 | uncertain_or_negative |

No policy passes the CI-positive deployed decision rule.

## Gemma Unique16 Artifact Hazard

The intended symmetric lower-duplication target, `outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl`, is not currently usable as a packet JSONL:

- `ls -lh` reports a `2.0M` file;
- `wc -l` reports `0`;
- Python iteration over the file yields `0` packet rows;
- v97 balanced Llama->Gemma runs therefore produced empty target summaries before the harness was patched.

I patched `work/semantic_risk_controlled_selector.py` so empty source or target packet files now fail loudly instead of silently emitting empty prediction artifacts.

The Gemma unique16 prompt assets and answer keys exist, but the packet JSONL must be rebuilt before it can be used for packet-level semantic scoring.

## Read

The valid lower-duplication Llama result strengthens v96 rather than reversing it. Balanced-source semantic risk control transfers poorly to unique-source Llama packets:

- source-calibrated thresholds preserve many baseline-correct rows;
- raw recovery mostly disappears;
- the only positive point estimates are tiny and CI-fragile;
- lower duplication does not rescue the current hashed semantic scorer.

This is an important pressure test because v96 could have been dismissed as a balanced-panel quirk. v97 shows that at least on Llama unique32, the stricter lower-duplication target remains negative.

## Claim Update

Do not claim semantic risk control has a lower-duplication positive result.

Do claim:

> Lower-duplication Llama evaluation keeps the semantic risk-control result negative. The next semantic-selector route needs stronger features and more positive calibration data, not merely a different threshold or a less-duplicated target panel.

Also document:

> The current Gemma unique16 packet JSONL is an artifact hazard and must be rebuilt before packet-level semantic scoring can use it.

## Artifacts

- `outputs/semantic_risk_v97_llama_unique32_policy_aggregate.csv`
- `outputs/semantic_risk_v97_train_balanced_gemma_test_unique32_llama_*_report.md`
- `outputs/semantic_risk_v97_train_balanced_gemma_test_unique32_llama_*_report_ci.csv`
- `outputs/semantic_risk_v97_train_balanced_gemma_test_unique32_llama_*_summary.csv`
- `work/semantic_risk_controlled_selector.py`
- `work/test_semantic_risk_controlled_selector.py`
- `outputs/semantic_risk_controlled_selector.py`
- `outputs/test_semantic_risk_controlled_selector.py`

## Representative Commands

```bash
python3 work/semantic_risk_controlled_selector.py \
  --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl \
  --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl \
  --train-label Gemma \
  --test-label Llama \
  --feature-mode both \
  --score-field semantic_cluster_probability \
  --include-problem \
  --seed 60602 \
  --output-prefix semantic_risk_v97_train_balanced_gemma_test_unique32_llama_both_probability_seed60602

python3 work/deployed_mix_verifier_report.py \
  --predictions outputs/semantic_risk_v97_train_balanced_gemma_test_unique32_llama_both_probability_seed60602_predictions.jsonl \
  --answer-keys \
    outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.answer_key.json \
    outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json \
    outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json \
  --category-stats \
    outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32_category_stats.csv \
    outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv \
  --expected-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.jsonl \
  --thresholds 0 \
  --bootstrap-rounds 500 \
  --output-prefix semantic_risk_v97_train_balanced_gemma_test_unique32_llama_both_probability_seed60602_report
```

Verification:

```bash
python3 work/test_semantic_risk_controlled_selector.py
python3 -m py_compile work/semantic_risk_controlled_selector.py work/test_semantic_risk_controlled_selector.py
```
