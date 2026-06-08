# v37 Deployed-Mix Verifier Assets

**Date:** June 1, 2026  
**Question:** can the next verifier benchmark measure deployed regression risk, not only hard buried-packet recovery?

## Result

The project now has strict natural top-20 deployed-mix verifier packet sets for both MATH/Llama and MATH/Gemma. These are balanced stress-test sets, not natural deployment priors: each contains 12 packets in each of six categories.

| dataset | packets | prompt variant | avg chars | p90 chars | max chars |
|---|---:|---|---:|---:|---:|
| MATH/Llama | 72 | compact top-20, 1 representative/cluster, 420 chars | 8629 | 11117 | 11823 |
| MATH/Gemma | 72 | compact top-20, 1 representative/cluster, 420 chars | 8977 | 10785 | 11611 |

## Categories

| category | purpose |
|---|---|
| `baseline_correct` | false-regression risk: cheap selector is already correct |
| `recoverable_top5` | correct cluster visible near the top |
| `recoverable_top10_only` | correct cluster visible only after top-5 |
| `recoverable_top20_only` | correct cluster visible only after top-10 |
| `no_visible_top20` | correct cluster exists but is deeper than top-20 |
| `no_correct_generated` | no correct cluster exists in the sample |

Natural trial rates from the packet-building sweep:

| dataset | baseline_correct | top5 | top10_only | top20_only | no_visible_top20 | no_correct_generated |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.428 | 0.216 | 0.099 | 0.074 | 0.038 | 0.145 |
| MATH/Gemma | 0.299 | 0.159 | 0.103 | 0.080 | 0.100 | 0.259 |

## Why This Matters

The earlier buried rank11-20 packets are good for testing whether a verifier can recover deep correct clusters when recovery is possible. They do not measure deployment risk.

The deployed-mix packets make the missing benchmark concrete:

```text
Can the verifier recover visible mistakes without corrupting already-correct defaults,
and can confidence/abstention identify unhelpful invocations?
```

This is the benchmark needed to replace the current projected `80% success / 2% false-regression` sensitivity model.

## Assets

Packets:

- [MATH/Llama deployed mix packets](cluster_packets_math_llama_n128_deployed_mix_top20.jsonl)
- [MATH/Gemma deployed mix packets](cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl)
- [MATH/Llama category stats](cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv)
- [MATH/Gemma category stats](cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv)

Compact prompts and answer keys:

- [MATH/Llama deployed mix compact prompts](cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.jsonl)
- [MATH/Llama deployed mix answer key](cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json)
- [MATH/Gemma deployed mix compact prompts](cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.jsonl)
- [MATH/Gemma deployed mix answer key](cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json)

Scorer:

- `work/score_deployed_mix_verifier.py`
- `work/test_score_deployed_mix_verifier.py`

## Commands

Build packets:

```bash
python3 work/test_build_deployed_mix_packet_dataset.py

python3 work/build_deployed_mix_packet_dataset.py \
  --data work/MATH_Llama-3-8B-Instruct.json \
  --dataset-label MATH_Llama-deployed-mix-top20 \
  --output-prefix cluster_packets_math_llama_n128_deployed_mix_top20 \
  --target-per-category 12 \
  --trials-per-problem 24 \
  --max-packets-per-problem 2

python3 work/build_deployed_mix_packet_dataset.py \
  --data work/MATH_Gemma-2B.json \
  --dataset-label MATH_Gemma-deployed-mix-top20 \
  --output-prefix cluster_packets_math_gemma2b_n128_deployed_mix_top20 \
  --target-per-category 12 \
  --trials-per-problem 24 \
  --max-packets-per-problem 2
```

Build compact prompts:

```bash
python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.jsonl \
  --representatives-per-cluster 1 \
  --rationale-chars 420

python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.jsonl \
  --representatives-per-cluster 1 \
  --rationale-chars 420
```

After a model endpoint produces predictions, score category behavior:

```bash
python3 work/score_deployed_mix_verifier.py \
  --predictions outputs/<model>_llama_deployed_mix_predictions.jsonl outputs/<model>_gemma_deployed_mix_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json \
  --output-prefix <model>_deployed_mix_verifier
```

## Read

This does not solve the missing external-verifier problem, but it removes ambiguity about what the decisive benchmark should be. The next model run can now report:

- recovery accuracy by depth,
- baseline-preservation rate on already-correct defaults,
- behavior on no-visible/no-correct invocations,
- confidence separation for fallback/abstention.

That is the difference between a hard-packet demo and a regression-aware deployed method test.
