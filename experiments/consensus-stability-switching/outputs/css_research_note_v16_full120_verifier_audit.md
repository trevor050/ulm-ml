# Cluster Selectability v16: Full 120-Packet Verifier Audit

**Status:** v16 research note, June 1, 2026  
**Question:** does the semantic cluster-verifier signal survive on the full hard-packet prompt set?

## Setup

The remote RTX 4070 PC remained unreachable and no local/API model runtime was available, so this is still not a reproducible external model benchmark.

I generated full blinded verifier prompts for both hard-packet datasets:

- [cluster_verifier_prompts_math_llama_n128_full.jsonl](cluster_verifier_prompts_math_llama_n128_full.jsonl), 60 prompts.
- [cluster_verifier_prompts_math_gemma2b_n128_full.jsonl](cluster_verifier_prompts_math_gemma2b_n128_full.jsonl), 60 prompts.

Then I built a prompt-family digest from the prompt files only:

- [full_verifier_prompt_family_digest.md](full_verifier_prompt_family_digest.md)

The 120 full prompts collapse to 33 unique problem families across both models. This is a hard selector-failure panel, not a broad MATH benchmark.

## Full 120 Result

Prediction file:

- [llm_manual_full120_predictions.jsonl](llm_manual_full120_predictions.jsonl)

Trace-key score:

- [llm_manual_full120_cluster_verifier.md](llm_manual_full120_cluster_verifier.md)

| judge | total | overall accuracy | Llama accuracy | Gemma accuracy |
|---|---:|---:|---:|---:|
| manual in-thread cluster verifier | 120 | 0.925 | 0.950 | 0.900 |

Baselines on conditioned hard packets:

| baseline | Llama | Gemma |
|---|---:|---:|
| mean-score selector | 0.233 | 0.317 |
| learned shallow hard-packet selector | 0.567 | 0.733 |
| manual in-thread cluster verifier | 0.950 | 0.900 |

## Visibility / Label Audit

The raw 111/120 score understates the semantic-verifier result because all 9 trace-key disagreements occur when the manual mathematical answer is not present in the visible candidate set under the current normalizer, or when the trace label is malformed/equivalent in a way the scorer cannot fairly credit.

Audit report:

- [llm_manual_full120_panel_audit.md](llm_manual_full120_panel_audit.md)

| group | correct | total | accuracy |
|---|---:|---:|---:|
| all | 111 | 120 | 0.925 |
| Llama | 57 | 60 | 0.950 |
| Gemma | 54 | 60 | 0.900 |
| manual answer visible after normalization | 111 | 111 | 1.000 |
| manual answer not visible after normalization | 0 | 9 | 0.000 |

The disagreements include:

- rational-root prompts where the mathematically complete answer is `-4,-2,-1,1,2,4`, but the visible/trace-labeled clusters contain partial or malformed lists,
- geometry prompts where `32-8\pi` is correct but trace labels select `-8`,
- a geometric-series prompt where `128/3` is correct but the trace label is a malformed summation fragment,
- equivalent-answer problems like `25` versus `5^2` or `1/8` versus a malformed `8` label.

## Interpretation

This is the strongest evidence so far for the cluster-verifier hypothesis:

> In hard `cluster_sum` failures where the correct mathematical answer is visible, semantic inspection of cluster rationales recovered every tested case in the full 120-prompt panel.

But it also exposes a benchmark hygiene requirement:

> Cluster-verifier evaluations must report answer visibility and trace-label quality. Otherwise verifier failures, parser failures, and packet-construction failures get conflated.

## Relation To Recent Test-Time Scaling Work

Recent test-time scaling papers emphasize adaptive sampling, confidence, and discriminative verification. See [related_work_recent_test_time_scaling.md](related_work_recent_test_time_scaling.md). This sprint's angle is complementary: before optimizing the inference budget, measure whether repeated sampling already produced the correct answer cluster and whether the deployed selector can surface it.

## Current Verdict

The original CSS/router idea is not the contribution. The contribution is now a sharper diagnostic and method target:

1. measure cluster selectability gap,
2. detect likely selector failures,
3. invoke semantic cluster verification only when useful,
4. audit whether the correct answer is actually visible and correctly labeled,
5. report deployed net gain after verifier cost and regression risk.

The next truly decisive experiment is still a reproducible external/local model verifier on the full 120 prompts, followed by detector-gated deployed evaluation.
