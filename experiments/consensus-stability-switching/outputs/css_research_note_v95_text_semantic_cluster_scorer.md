# v95: Hashed Semantic Cluster-Scorer Boundary

**Date:** June 2, 2026

## Question

After the local chat-verifier stopline in v83/v84/v92/v94, is the failure only an interface/model problem, or can a lightweight trained semantic cluster scorer recover buried deployed-mix failures?

## Setup

I added `work/text_cluster_semantic_scorer.py`, a dependency-light supervised cluster scorer that uses sparse hashed features over:

- candidate answer text,
- top representative rationale text,
- optionally the original problem text,
- optional numeric cluster features such as support, rank, and scores.

It trains a weighted logistic model on visible cluster labels from one generator trace and emits answer/confidence predictions for the other trace. I ran the full deployed-mix scoring harness, including v71 target checks and v45 confidence-threshold bootstrap CIs.

The key stress settings were:

- train Gemma deployed-mix packets, test Llama packets;
- train Llama deployed-mix packets, test Gemma packets;
- feature modes `numeric`, `text`, and `both`;
- the same runs after removing train packets whose `orig_dset_idx` appears in the test set.

The overlap-filter is intentionally harsh: it keeps only `18/72` Gemma train packets for Llama testing and `19/72` Llama train packets for Gemma testing.

## Aggregate Results

`outputs/text_cluster_semantic_v95_policy_aggregate.csv` summarizes all 12 policies.

| policy | test | recoverable correct | baseline preserved | best deployed delta | CI low | v71 positive |
|---|---|---:|---:|---:|---:|---|
| Gemma->Llama numeric no-overlap | Llama | 2/36 | 12/12 | +0.036 | +0.000 | false |
| Gemma->Llama both | Llama | 5/36 | 11/12 | +0.023 | -0.065 | true |
| Gemma->Llama numeric | Llama | 2/36 | 12/12 | +0.012 | +0.000 | true |
| Gemma->Llama text | Llama | 6/36 | 6/12 | +0.008 | +0.000 | false |
| Llama->Gemma numeric | Gemma | 5/36 | 10/12 | +0.003 | -0.075 | false |
| all other tested policies | mixed | <=4/36 | <=10/12 | <=0.000 or negative | <=0.000 | false |

None of the policies passes the conservative lower-CI-positive deployed decision rule. The `+0.000` lower bounds are rounded; the report decision remains `uncertain_or_negative` because the pre-specified rule requires a strictly positive lower bound.

## Read

This is a useful partial negative:

- semantic text features do expose some real recoverability signal;
- unlike v78/v82 surface-feature gates, text features can sometimes recover top10/top20 deployed-mix failures;
- the signal is not deployable yet because raw recovery comes with bad preservation or fragile confidence;
- overlap-filtered training is badly underpowered and mostly collapses, which is important because the current balanced Llama/Gemma deployed-mix assets share many source problems.

The strongest non-overlap Llama row is conservative but tiny: Gemma->Llama numeric no-overlap preserves all `12/12` baseline-correct rows and gets `2/36` recoverable rows, with best natural-rate deployed delta `+0.036`, but it fails v71 target evidence and does not pass the strict CI rule. The best raw semantic row, Gemma->Llama text, gets `6/36` recoverable rows but preserves only `6/12` baseline-correct rows.

For Gemma, the best raw row is Llama->Gemma numeric with `5/36` recoverable rows and `10/12` baseline preservation, but its best deployed delta is only `+0.003` with negative lower CI.

## Claim Update

Do not claim hashed semantic scoring solves cluster verification.

Do claim:

> Lightweight semantic cluster scoring recovers some visible deployed-mix failures, including a small amount of top10/top20 signal, but it is not calibration-safe under cross-model deployment. This strengthens the paper's bottleneck claim: the gap is not just hidden answer coverage, and it is not closed by shallow features, local chat verifiers, binary cluster judging, or a first-pass hashed semantic selector.

This makes the next experiment sharper: either use a substantially stronger measured verifier, or build a risk-controlled semantic selector with a much larger/less-overlapped calibration set. The current v95 assets are evidence for signal plus calibration failure, not a positive deployed method.

## Artifacts

- `work/text_cluster_semantic_scorer.py`
- `work/test_text_cluster_semantic_scorer.py`
- `outputs/text_cluster_semantic_scorer.py`
- `outputs/test_text_cluster_semantic_scorer.py`
- `outputs/text_cluster_semantic_v95_policy_aggregate.csv`
- `outputs/text_cluster_semantic_v95_*_report.md`
- `outputs/text_cluster_semantic_v95_*_report_categories.csv`
- `outputs/text_cluster_semantic_v95_*_report_ci.csv`
- `outputs/text_cluster_semantic_v95_*_report_targets.csv`

## Commands

Representative training/scoring command:

```bash
python3 work/text_cluster_semantic_scorer.py \
  --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl \
  --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl \
  --train-label Gemma \
  --test-label Llama \
  --feature-mode both \
  --include-problem \
  --output-prefix text_cluster_semantic_v95_train_gemma_test_llama_both
```

Representative overlap-filter command:

```bash
python3 work/text_cluster_semantic_scorer.py \
  --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl \
  --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl \
  --train-label Gemma \
  --test-label Llama \
  --feature-mode both \
  --include-problem \
  --exclude-test-problems-from-train \
  --output-prefix text_cluster_semantic_v95_train_gemma_test_llama_both_nooverlap
```

Representative deployed-mix report command:

```bash
python3 work/deployed_mix_verifier_report.py \
  --predictions outputs/text_cluster_semantic_v95_train_gemma_test_llama_both_predictions.jsonl \
  --answer-keys \
    outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json \
    outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json \
  --category-stats \
    outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv \
    outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv \
  --expected-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl \
  --thresholds 0,0.5,0.75,0.9 \
  --bootstrap-rounds 500 \
  --output-prefix text_cluster_semantic_v95_train_gemma_test_llama_both_report
```

Verification:

```bash
python3 work/test_text_cluster_semantic_scorer.py
python3 -m py_compile work/text_cluster_semantic_scorer.py work/test_text_cluster_semantic_scorer.py
```
