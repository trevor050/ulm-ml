# v93 Binary Cluster-Judge Interface

**Date:** June 2, 2026  
**Question:** If multi-cluster chat selection is too brittle, does scoring each answer cluster independently make `mathstral:7b` a useful verifier?

## Motivation

v92 showed that asking `mathstral:7b` to choose among 20 clusters is not enough: one rich Gemma top20-only recovery appears, but it disappears under the slim interface, Llama regresses, and rich full-panel expansion is CPU/tail-latency blocked.

The natural alternative is a non-generative cluster-scoring interface:

```text
for each candidate cluster:
  ask whether this cluster's final answer is correct
choose the candidate with the highest yes-confidence
```

This tests whether the failure is caused by multi-way choice, answer-copying, and prompt length rather than verifier ability.

## Harness

I added:

- [make_binary_cluster_judge_prompts.py](make_binary_cluster_judge_prompts.py): builds one prompt per visible answer cluster.
- [score_binary_cluster_judge.py](score_binary_cluster_judge.py): collapses cluster-level yes/no predictions into one selected answer per source packet, then emits ordinary prediction JSONL for the existing deployed-mix report harness.
- [test_binary_cluster_judge.py](test_binary_cluster_judge.py): smoke test for prompt IDs, answer keys, collapse policy, and selected-answer output.

Important scoring detail: the collapse policy uses positive yes-confidence only. A `"no"` answer scores `0`, not `1 - confidence`. This avoids treating `"no", confidence: 0` as high evidence for correctness.

## Panel

I reused the six v75/v76 recoverable failures:

```text
cluster_packets_math_gemma2b_n128_deployed_mix_top20-0004  recoverable_top5
cluster_packets_math_gemma2b_n128_deployed_mix_top20-0012  recoverable_top20_only
cluster_packets_math_gemma2b_n128_deployed_mix_top20-0023  recoverable_top10_only
cluster_packets_math_llama_n128_deployed_mix_top20-0000    recoverable_top5
cluster_packets_math_llama_n128_deployed_mix_top20-0004    recoverable_top10_only
cluster_packets_math_llama_n128_deployed_mix_top20-0007    recoverable_top20_only
```

This creates `109` binary prompts rather than `120` because several Llama packets have fewer than 20 visible clusters in the saved packet artifact.

## Interface A: Cluster-Rationale Binary Judge

Prompt shape: problem, candidate final answer, support count, and one truncated representative rationale.

Artifacts:

- prompts: [mathstral_v93_binary_cluster_judge_recoverable_gemma_prompts.jsonl](mathstral_v93_binary_cluster_judge_recoverable_gemma_prompts.jsonl), [mathstral_v93_binary_cluster_judge_recoverable_llama_prompts.jsonl](mathstral_v93_binary_cluster_judge_recoverable_llama_prompts.jsonl)
- predictions: [mathstral_7b_v93_binary_cluster_judge_recoverable_gemma_predictions.jsonl](mathstral_7b_v93_binary_cluster_judge_recoverable_gemma_predictions.jsonl), [mathstral_7b_v93_binary_cluster_judge_recoverable_llama_predictions.jsonl](mathstral_7b_v93_binary_cluster_judge_recoverable_llama_predictions.jsonl)
- collapsed summary: [mathstral_7b_v93_binary_cluster_judge_recoverable_summary.md](mathstral_7b_v93_binary_cluster_judge_recoverable_summary.md)
- deployed-mix report: [mathstral_7b_v93_binary_cluster_judge_recoverable_report.md](mathstral_7b_v93_binary_cluster_judge_recoverable_report.md)

Operationally, this is much cheaper than v92 rich multi-cluster prompts:

| dataset | prompts | avg JSONL chars | max JSONL chars |
|---|---:|---:|---:|
| Gemma recoverable | 60 | 1180 | 1301 |
| Llama recoverable | 49 | 1435 | 1547 |

Runtime was also acceptable: about `17.0s` total eval duration across all `109` cluster prompts.

Result:

- Raw labels: `90` yes, `19` no.
- Invalid confidence rows: `0`.
- Collapsed selected correct clusters: `0/6`.
- Deployed report recoveries: `0/3` Gemma, `0/3` Llama.

The model is too permissive when rationales are present. It says yes to almost everything, including the wrong high-rank clusters.

## Interface B: Answer-Check Binary Judge

Prompt shape: problem and candidate final answer only, no rationale. Instruction: solve independently and compare.

Artifacts:

- prompts: [mathstral_v93_binary_answer_check_recoverable_gemma_prompts.jsonl](mathstral_v93_binary_answer_check_recoverable_gemma_prompts.jsonl), [mathstral_v93_binary_answer_check_recoverable_llama_prompts.jsonl](mathstral_v93_binary_answer_check_recoverable_llama_prompts.jsonl)
- predictions: [mathstral_7b_v93_binary_answer_check_recoverable_gemma_predictions.jsonl](mathstral_7b_v93_binary_answer_check_recoverable_gemma_predictions.jsonl), [mathstral_7b_v93_binary_answer_check_recoverable_llama_predictions.jsonl](mathstral_7b_v93_binary_answer_check_recoverable_llama_predictions.jsonl)
- collapsed summary: [mathstral_7b_v93_binary_answer_check_recoverable_summary.md](mathstral_7b_v93_binary_answer_check_recoverable_summary.md)
- deployed-mix report: [mathstral_7b_v93_binary_answer_check_recoverable_report.md](mathstral_7b_v93_binary_answer_check_recoverable_report.md)

Prompt sizes were even smaller:

| dataset | prompts | avg JSONL chars | max JSONL chars |
|---|---:|---:|---:|
| Gemma recoverable | 60 | 854 | 959 |
| Llama recoverable | 49 | 1113 | 1205 |

Runtime was again acceptable: about `15.6s` total eval duration across all `109` prompts.

Result:

- Raw labels: `107` no, `2` yes.
- Invalid confidence rows: `0`.
- Collapsed selected correct clusters: `0/6`.
- Deployed report recoveries: `0/3` Gemma, `0/3` Llama.

The answer-check variant flips the failure mode. It is too conservative and mostly says no. On the one Gemma top10 case where it says yes to the correct answer, it also says yes to a wrong higher-rank answer with equal confidence, so the collapse policy still selects the wrong cluster.

## Read

The independent cluster-scoring interface is operationally promising but not semantically sufficient for `mathstral:7b`.

What v93 adds:

- It removes the objection that v92 failed only because the model had to choose among 20 clusters in one long prompt.
- It shows a cheap per-cluster interface can run quickly on the available local endpoint.
- It provides a reusable harness for future verifier endpoints.
- It gives another negative control: rationale-conditioned judging is over-permissive, while answer-only checking is over-conservative.

What it does not show:

- No measured recovery improvement: both binary interfaces remain `0/6` on the v75/v76 recoverable failures.
- No deployed positive result: since recovery is zero on the targeted recoverable set, expanding to baseline/no-correct categories would only measure regression behavior, not rescue ability.
- No reason to keep iterating local `mathstral:7b` prompt variants unless the endpoint, model, or scoring objective changes materially.

The next credible positive route is a stronger verifier model or a trained/non-generative semantic scorer that can produce calibrated per-cluster probabilities. The new binary harness is useful for that route, but `mathstral:7b` is still not the verifier.
