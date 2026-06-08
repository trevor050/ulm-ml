# Cluster Selectability v15: 40-Packet Blind Cluster-Verifier Panel

**Status:** v15 research note, June 1, 2026  
**Question:** does the semantic cluster-verifier signal survive beyond the initial 10-packet smoke test?

## Setup

The RTX 4070 PC remained unreachable, so this is still not an external/local model benchmark. I extended the blind in-thread verifier pass across all prepared verifier prompts:

- 20 MATH/Llama hard packets,
- 20 MATH/Gemma hard packets,
- 40 total packets.

Prediction file:

- [llm_manual_panel40_predictions.jsonl](llm_manual_panel40_predictions.jsonl)

Scoring report:

- [llm_manual_panel40_cluster_verifier.md](llm_manual_panel40_cluster_verifier.md)

The predictions were written from the blinded prompt files before opening the answer keys.

## Result

| judge | total | overall accuracy | Llama accuracy | Gemma accuracy |
|---|---:|---:|---:|---:|
| manual blind LLM judge | 40 | 1.000 | 1.000 | 1.000 |

This clears the conditioned hard-packet baselines:

| baseline | Llama | Gemma |
|---|---:|---:|
| mean-score selector | 0.233 | 0.317 |
| learned shallow hard-packet selector | 0.567 | 0.733 |
| manual blind LLM judge | 1.000 | 1.000 |

## Scoring Audit

The first score pass returned `38/40`. Both misses were answer-normalization artifacts:

- `30` versus `30^\circ`,
- `-2` versus `-\log_2(2)-1`.

The scorer now canonicalizes degree marks and the simple `-\log_2(2)-1` equivalent form. After that fix the panel is `40/40`.

## What This Actually Shows

The hard packets are not random deployed examples. They are conditioned on `cluster_sum` failure and include a correct cluster in the visible packet when needed.

The prepared 40-prompt panel is also not a broad problem-diversity benchmark. A follow-up diversity audit found:

| dataset | split | packets | unique questions | largest family |
|---|---|---:|---:|---:|
| Llama | prepared prompt panel | 20 | 9 | 3 |
| Gemma | prepared prompt panel | 20 | 8 | 3 |
| Llama | full hard packets | 60 | 25 | 3 |
| Gemma | full hard packets | 60 | 24 | 3 |

See [hard_packet_diversity_audit.md](hard_packet_diversity_audit.md).

The useful claim is narrower but stronger than v14:

> On the prepared hard packets, semantic inspection of cluster rationales is enough to recover all 40 tested failures, while cheap feature selectors and shallow packet rankers leave large residual error.

That makes the cluster-verifier component much more plausible. The remaining unsolved part is deployment:

1. run a reproducible external/local verifier,
2. scale from 40 prompt packets to the full 120 hard-packet prompts now prepared in [cluster_verifier_prompts_math_llama_n128_full.jsonl](cluster_verifier_prompts_math_llama_n128_full.jsonl) and [cluster_verifier_prompts_math_gemma2b_n128_full.jsonl](cluster_verifier_prompts_math_gemma2b_n128_full.jsonl),
3. test cross-model and cross-problem-family generalization,
4. combine verifier invocation with the failure detector without regressing ordinary `cluster_sum` hits.

## Current Verdict

This is no longer just "maybe there is signal." There is very strong visible semantic signal in these hard packets.

It is still not a finished method because the verifier is manual/in-thread and the packet selection is conditioned. The paper-safe phrasing is:

> A 40-packet blind verifier panel suggests that selected hard cluster-selection failures often contain recoverable semantic evidence; the next required step is an external/local verifier over the full 120-packet set plus deployed gating.
