# Cluster Selectability v14: LLM Cluster-Verifier Smoke Test

**Status:** v14 research note, June 1, 2026  
**Question:** can an LLM judge recover hard cluster failures by reading cluster packets?

## Why This Matters

The biggest remaining method hole is the lack of a real cluster-packet verifier. The PC with the RTX 4070 remained unreachable, so I could not run a local Ollama/GPU verifier. As a fallback, I ran a small blind in-thread LLM-judge smoke test on the prepared cluster-verifier prompts.

This is not a final method result. It is a first datapoint that cluster packets contain reasoning evidence a capable verifier can use.

## Setup

Inputs:

- [MATH/Llama verifier prompts](cluster_verifier_prompts_math_llama_n128.jsonl)
- [MATH/Gemma verifier prompts](cluster_verifier_prompts_math_gemma2b_n128.jsonl)

Smoke-test subset:

- first 5 Llama hard packets,
- first 5 Gemma hard packets,
- 10 packets total.

Protocol:

1. Read only the prompt JSONL files.
2. Do not open answer keys or labeled packet files before prediction.
3. For each packet, choose the final answer whose cluster is best supported by the visible reasoning.
4. Write predictions to JSONL.
5. Score against answer keys afterward.

Prediction file:

- [llm_manual_smoke_predictions.jsonl](llm_manual_smoke_predictions.jsonl)

Scoring report:

- [llm_manual_smoke_cluster_verifier.md](llm_manual_smoke_cluster_verifier.md)

## Result

| judge | total | overall accuracy | Llama accuracy | Gemma accuracy |
|---|---:|---:|---:|---:|
| manual blind LLM judge | 10 | 1.000 | 1.000 | 1.000 |

Baselines on the hard-packet task:

| baseline | Llama | Gemma |
|---|---:|---:|
| mean-score selector | 0.233 | 0.317 |
| learned shallow hard-packet selector | 0.567 | 0.733 |

The smoke-test LLM judge beats these baselines on the tiny subset.

## What The LLM Used

The successful cases included:

- rejecting high-support clusters with invalid repeated/out-of-range integers,
- recognizing complementary-pair sums of `11` in the integer-placement problem,
- computing the repeating decimal cycle for `6/13`,
- distinguishing exact unrounded area `53650` from the requested nearest-thousand answer `54000`.

This is exactly the kind of semantic cluster evidence the shallow selectors lacked.

## Caveats

This result should be treated as promising but weak:

- only 10 packets,
- manually judged in-thread rather than run through an external model API,
- not independent enough to be a final benchmark,
- not deployed on ordinary candidate sets,
- packets are conditioned on `cluster_sum` failure and force a correct cluster into view when necessary.

An attempted three-agent 40-prompt blind panel became operationally messy when judge agents spawned invalid chunk subagents, so I closed them and ran a smaller controlled smoke test instead.

## Interpretation

The result supports the next-method hypothesis:

> Cluster packets contain semantic evidence that a stronger verifier can exploit.

It does **not** solve the deployed problem. The hard parts remain:

1. scaling the verifier test to all hard packets,
2. using a reproducible external/local model,
3. beating the learned shallow hard-packet baseline on enough examples,
4. combining the verifier with a failure detector without regressing `cluster_sum` hits.

## Next Experiment

When the PC wakes or another model endpoint is available:

```bash
python3 outputs/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_llama_n128.jsonl \
  --output outputs/cluster_verifier_prompts_math_llama_n128_full.jsonl
```

Run a real model over all prompts, then score:

```bash
python3 outputs/evaluate_cluster_verifier_predictions.py \
  --predictions outputs/model_predictions.jsonl \
  --answer-key outputs/cluster_verifier_prompts_math_llama_n128.answer_key.json \
  --output outputs/model_predictions_eval.md
```

The fair target is not `cluster_sum` on hard packets, because that is zero by construction. The fair target is the learned shallow hard-packet selector:

- Llama: beat `0.567`.
- Gemma: beat `0.733`.

## Current Verdict

This is the first positive method-shaped evidence after many negative selector experiments. It does not prove the method, but it makes the next experiment worth running:

> A semantic cluster-packet verifier may recover hard selector failures that shallow cluster features miss.
