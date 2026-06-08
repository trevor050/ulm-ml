# v94 Qwen3:14B Binary Cluster-Judge Stopline

**Date:** June 2, 2026  
**Question:** Does the v93 fast binary cluster-judge interface become useful with a stronger local model (`qwen3:14b`)?

## Setup

v93 added a reusable independent cluster-scoring harness and tested it with `mathstral:7b`. The harness was operationally good but semantically negative:

- rationale-conditioned binary judging: `90/109` yes labels, `0/6` selected correct clusters;
- answer-check binary judging: `107/109` no labels, `0/6` selected correct clusters.

v94 reruns the same `109` one-cluster prompts with `qwen3:14b`, a stronger local model that had previously failed the full deployed-mix multi-cluster panels in v83/v84.

Remote endpoint:

```bash
ssh -4 -o BatchMode=yes -o ExitOnForwardFailure=yes -o ConnectTimeout=8 \
  -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 192.168.1.151
```

The hostname `trevors-pc.local` was flaky again; direct `192.168.1.151` worked.

## Panel

Same six v75/v76 recoverable failures:

```text
cluster_packets_math_gemma2b_n128_deployed_mix_top20-0004  recoverable_top5
cluster_packets_math_gemma2b_n128_deployed_mix_top20-0012  recoverable_top20_only
cluster_packets_math_gemma2b_n128_deployed_mix_top20-0023  recoverable_top10_only
cluster_packets_math_llama_n128_deployed_mix_top20-0000    recoverable_top5
cluster_packets_math_llama_n128_deployed_mix_top20-0004    recoverable_top10_only
cluster_packets_math_llama_n128_deployed_mix_top20-0007    recoverable_top20_only
```

The binary panels score all visible clusters from those packets:

- `60` Gemma cluster prompts,
- `49` Llama cluster prompts,
- `109` total prompts.

## Interface A: Answer-Check Binary Judge

Prompt shape: problem plus candidate final answer, no sampled rationale. The model is asked to solve independently and answer yes/no.

Artifacts:

- predictions: [qwen3_14b_v94_binary_answer_check_recoverable_gemma_predictions.jsonl](qwen3_14b_v94_binary_answer_check_recoverable_gemma_predictions.jsonl), [qwen3_14b_v94_binary_answer_check_recoverable_llama_predictions.jsonl](qwen3_14b_v94_binary_answer_check_recoverable_llama_predictions.jsonl)
- collapsed summary: [qwen3_14b_v94_binary_answer_check_recoverable_summary.md](qwen3_14b_v94_binary_answer_check_recoverable_summary.md)
- cluster details: [qwen3_14b_v94_binary_answer_check_recoverable_cluster_details.csv](qwen3_14b_v94_binary_answer_check_recoverable_cluster_details.csv)
- deployed-mix report: [qwen3_14b_v94_binary_answer_check_recoverable_report.md](qwen3_14b_v94_binary_answer_check_recoverable_report.md)

Result:

- Raw labels: `108` no, `1` yes.
- Invalid confidence rows: `0`.
- Collapsed selected correct clusters: `0/6`.
- Deployed recoveries: `0/3` Gemma, `0/3` Llama.

The model is too conservative. It says no to every buried correct cluster. It does say yes once, but to a wrong Gemma recoverable top10 candidate.

## Interface B: Rationale-Conditioned Binary Judge

Prompt shape: problem, candidate final answer, support count, and one sampled rationale.

Artifacts:

- predictions: [qwen3_14b_v94_binary_cluster_judge_recoverable_gemma_predictions.jsonl](qwen3_14b_v94_binary_cluster_judge_recoverable_gemma_predictions.jsonl), [qwen3_14b_v94_binary_cluster_judge_recoverable_llama_predictions.jsonl](qwen3_14b_v94_binary_cluster_judge_recoverable_llama_predictions.jsonl)
- collapsed summary: [qwen3_14b_v94_binary_cluster_judge_recoverable_summary.md](qwen3_14b_v94_binary_cluster_judge_recoverable_summary.md)
- cluster details: [qwen3_14b_v94_binary_cluster_judge_recoverable_cluster_details.csv](qwen3_14b_v94_binary_cluster_judge_recoverable_cluster_details.csv)
- deployed-mix report: [qwen3_14b_v94_binary_cluster_judge_recoverable_report.md](qwen3_14b_v94_binary_cluster_judge_recoverable_report.md)

Result:

- Raw labels: `85` no, `24` yes.
- Invalid confidence rows: `0`.
- Collapsed selected correct clusters: `0/6`.
- Deployed recoveries: `0/3` Gemma, `0/3` Llama.

Rationales make qwen less conservative, but not discriminative. It still selects the wrong cluster on all six hard packets, and the Gemma side regresses all three baselines under the collapsed prediction report.

## Runtime

The binary interface remains operationally attractive:

| interface | prompts | total eval seconds | avg eval tokens |
|---|---:|---:|---:|
| answer-check Gemma | 60 | 17.79 | 15.0 |
| answer-check Llama | 49 | 14.53 | 15.0 |
| rationale Gemma | 60 | 18.16 | 15.2 |
| rationale Llama | 49 | 14.70 | 15.1 |

So the failure is not a throughput problem. The interface is fast enough to be useful for a stronger endpoint; `qwen3:14b` just does not supply useful cluster probabilities on these packets.

## Read

v94 closes the obvious follow-up to v93:

```text
Maybe binary cluster scoring is good, but mathstral is too weak.
```

On the exact same hard recoverable set, `qwen3:14b` also recovers `0/6`. The two binary styles fail differently:

- answer-check is over-conservative and misses every buried correct cluster;
- rationale-conditioned judging becomes less conservative but still selects wrong clusters.

This strengthens the stopline for the available local Ollama stack. The reusable binary harness remains valuable, but local `qwen3:14b` is not the missing measured verifier. The next credible route needs either a materially stronger endpoint, a trained semantic cluster scorer, or a verifier objective that produces calibrated probabilities rather than brittle yes/no labels.
