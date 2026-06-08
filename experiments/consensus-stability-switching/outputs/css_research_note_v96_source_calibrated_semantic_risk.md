# v96: Source-Calibrated Semantic Risk-Control Boundary

**Date:** June 2, 2026

## Question

v95 showed that hashed semantic cluster features contain raw recoverability signal, but the target-side threshold sweep was diagnostic rather than deployable. Can source-calibrated accept/fallback thresholds make the semantic scorer safe under cross-model deployment?

## Setup

I added `work/semantic_risk_controlled_selector.py`, which wraps the v95 hashed semantic scorer with a stricter policy:

1. split the source deployed-mix packets into fit and calibration packets, stratified by deployment category;
2. train the hashed semantic scorer on fit packets;
3. choose an accept threshold on held-out source calibration packets with `0` allowed baseline-correct regressions;
4. deploy cross-model, accepting the semantic answer only above the chosen source threshold and otherwise falling back to the baseline answer.

I swept:

- directions: Gemma->Llama and Llama->Gemma;
- features: `numeric`, `text`, `both`;
- risk score: `confidence`, `semantic_cluster_margin`, `semantic_cluster_probability`;
- seeds: `60601`, `60602`, `60603`.

That gives `54` source-calibrated policies. Each was scored as an already-deployed policy with the v74/v45 report harness at threshold `0` only, so there is no target-side threshold oracle.

## Aggregate Results

Artifact: `outputs/semantic_risk_v96_policy_aggregate.csv`.

Direction summary:

| direction | policies | mean deployed delta | max deployed delta | mean recoverable correct | mean baseline preserved | mean accept rate | CI-positive policies |
|---|---:|---:|---:|---:|---:|---:|---:|
| Gemma->Llama | 27 | +0.003 | +0.018 | 0.37/36 | 11.89/12 | 0.34 | 0 |
| Llama->Gemma | 27 | -0.025 | +0.007 | 1.22/36 | 10.37/12 | 0.35 | 0 |

Best individual rows by deployed delta:

| policy | recoverable correct | baseline preserved | accept rate | deployed delta | CI low | decision |
|---|---:|---:|---:|---:|---:|---|
| Gemma->Llama both/probability seed60601 | 3/36 | 11/12 | 0.51 | +0.018 | -0.071 | uncertain_or_negative |
| Gemma->Llama numeric/confidence seed60602 | 1/36 | 12/12 | 0.68 | +0.018 | +0.000 | uncertain_or_negative |
| Gemma->Llama numeric/margin seed60602 | 1/36 | 12/12 | 0.71 | +0.018 | +0.000 | uncertain_or_negative |
| Llama->Gemma numeric/confidence seed60602 | 1/36 | 12/12 | 0.31 | +0.007 | +0.000 | uncertain_or_negative |

The `+0.000` lower bounds are rounded; the report decision remains negative because the pre-specified rule requires a strictly positive lower 95% CI.

## Read

Source-calibrated risk control makes the semantic scorer safer, but it mostly kills the v95 raw recovery signal.

The best Gemma->Llama rows are tiny and fragile. They preserve baseline-correct rows, but recover only one to three of the 36 recoverable deployed-mix packets. Llama->Gemma is worse: it sometimes recovers more raw failures, but average deployed delta is negative because preservation/calibration transfer is weaker.

This closes the obvious objection to v95:

> Maybe target-side semantic scoring looked unsafe only because thresholds were not calibrated.

After source calibration over three seeds and three score choices, no tested semantic policy passes the deployed CI rule. The bottleneck is not merely picking a threshold on the same target panel. The current lightweight semantic scorer needs more positive calibration data, lower-overlap deployed-mix assets, or stronger semantic/process features.

## Claim Update

Do not claim source-calibrated hashed semantic scoring is a deployed method.

Do claim:

> A first-pass semantic scorer exposes recoverability signal, but source-calibrated risk control cannot yet turn that signal into a reliable deployed policy. This strengthens the adaptive-depth framing: the missing component is calibrated semantic verification or risk-controlled semantic ranking, not another local qwen/gemma prompt variant and not a shallow feature gate.

## Artifacts

- `work/semantic_risk_controlled_selector.py`
- `work/test_semantic_risk_controlled_selector.py`
- `outputs/semantic_risk_controlled_selector.py`
- `outputs/test_semantic_risk_controlled_selector.py`
- `outputs/semantic_risk_v96_policy_aggregate.csv`
- `outputs/semantic_risk_v96_train_*_report.md`
- `outputs/semantic_risk_v96_train_*_report_categories.csv`
- `outputs/semantic_risk_v96_train_*_report_ci.csv`
- `outputs/semantic_risk_v96_train_*_report_targets.csv`

## Representative Commands

```bash
python3 work/semantic_risk_controlled_selector.py \
  --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl \
  --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl \
  --train-label Gemma \
  --test-label Llama \
  --feature-mode both \
  --score-field semantic_cluster_probability \
  --include-problem \
  --seed 60601 \
  --output-prefix semantic_risk_v96_train_gemma_test_llama_both_probability_seed60601

python3 work/deployed_mix_verifier_report.py \
  --predictions outputs/semantic_risk_v96_train_gemma_test_llama_both_probability_seed60601_predictions.jsonl \
  --answer-keys \
    outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json \
    outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json \
  --category-stats \
    outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv \
    outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv \
  --expected-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl \
  --thresholds 0 \
  --bootstrap-rounds 500 \
  --output-prefix semantic_risk_v96_train_gemma_test_llama_both_probability_seed60601_report
```

Verification:

```bash
python3 work/test_semantic_risk_controlled_selector.py
python3 -m py_compile work/semantic_risk_controlled_selector.py work/test_semantic_risk_controlled_selector.py
```
