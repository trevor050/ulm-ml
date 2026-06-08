# v23 Buried Top-20 Verifier Pilot

## Question

v21 projected gains from adaptive top-20 verification, and v22 prepared strict top-20 rank11-20 prompt assets. The next question is whether buried clusters are actually readable, even in a small pilot:

> When the correct cluster is naturally visible only at rank 11-20, can a reasoning judge recover it from the prompt?

## Cheap Baseline Difficulty

I evaluated simple non-semantic selectors on the rank-stratified buried packet sets.

| packet set | packets | support | max score | mean score | cheap sanity |
|---|---:|---:|---:|---:|---:|
| Llama top10 rank6-10 | 30 | 0.000 | 0.000 | 0.000 | 0.000 |
| Gemma top10 rank6-10 | 30 | 0.000 | 0.067 | 0.033 | 0.000 |
| Llama top20 rank11-20 | 30 | 0.000 | 0.000 | 0.000 | 0.000 |
| Gemma top20 rank11-20 | 30 | 0.000 | 0.000 | 0.033 | 0.033 |

Artifacts:

- `outputs/cluster_packets_math_llama_n128_top10_rank6_10_strict_baselines.md`
- `outputs/cluster_packets_math_gemma2b_n128_top10_rank6_10_strict_baselines.md`
- `outputs/cluster_packets_math_llama_n128_top20_rank11_20_strict_baselines.md`
- `outputs/cluster_packets_math_gemma2b_n128_top20_rank11_20_strict_baselines.md`

These packets are doing their job: cheap reranking is basically dead.

## Blind Pilot

I ran a small blind in-thread/subagent pilot on 40 strict buried top-20 prompts:

- 20 Llama packets from `outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_strict.jsonl`
- 20 Gemma packets from `outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_strict.jsonl`

Judges saw prompt JSONL only, not answer keys or packet labels. The combined prediction file is:

```text
outputs/pilot_depth_judge_top20_rank11_20_predictions.jsonl
```

Scored result:

| pilot | total | accuracy | Llama | Gemma |
|---|---:|---:|---:|---:|
| blind in-thread/subagent buried top20 pilot | 40 | 1.000 | 1.000 | 1.000 |

One initial string mismatch was `-2` versus `-2/1`; the scorer now canonicalizes simple numeric fractions.

## Caveats

This is not a benchmark result:

- It is in-thread/subagent judging, not a reproducible external model.
- The 40 packets cover only 13 unique source problems: 5 Llama and 8 Gemma.
- The Llama 15-19 slice is a repeated family, all with answer `128/3`.
- The judges are strong reasoning models and the prompt distribution is conditioned on a correct cluster being visible.

## Interpretation

Despite the caveats, the pilot is useful. It says the buried top-20 prompts are not nonsense: when a correct cluster is buried at rank 11-20, the reasoning evidence can still be readable enough for a semantic judge to recover it. Combined with the cheap-baseline collapse, this supports the core method target:

> The problem is not that buried clusters are unreadable; it is building a reproducible verifier and invoking it only when the extra depth is worth the cost.

The next required step remains an external/local verifier run on these same strict prompt files.
