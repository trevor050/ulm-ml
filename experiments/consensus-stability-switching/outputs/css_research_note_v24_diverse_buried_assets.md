# v24 Diverse Buried Top-20 Assets

## Motivation

The v23 pilot showed that buried rank11-20 clusters can be semantically recoverable, but the prompt slice was too repetitive: 40 judged packets covered only 13 unique source problems. That is fine for a readability check, not for a reviewer-resistant verifier benchmark.

I added `--max-packets-per-problem` to the packet builder and regenerated strict buried top-20 assets with at most one packet per source problem.

## New Assets

Strict natural-visible, rank11-20, one packet per source problem:

- `outputs/cluster_packets_math_llama_n128_top20_rank11_20_diverse.jsonl`
- `outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse.jsonl`
- `outputs/cluster_packets_math_gemma2b_n128_top20_rank11_20_diverse.jsonl`
- `outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse.jsonl`

Audit: `outputs/diverse_depth_packet_audit.md`.

## Diversity Result

| set | packets | unique source problems | max per source | correct rank min/median/max |
|---|---:|---:|---:|---|
| Llama diverse | 27 | 27 | 1 | 11 / 13 / 20 |
| Gemma diverse | 40 | 40 | 1 | 11 / 13.5 / 18 |
| Llama previous repeated | 30 | 8 | 6 | 11 / 13.0 / 20 |
| Gemma previous repeated | 30 | 11 | 7 | 11 / 15.5 / 20 |

Llama only yields 27 eligible unique source problems after scanning 80 trials per held-out problem; that scarcity is itself useful to report.

## Cheap Baselines

| set | packets | support | max score | mean score | cheap sanity |
|---|---:|---:|---:|---:|---:|
| Llama diverse top20 rank11-20 | 27 | 0.000 | 0.037 | 0.074 | 0.037 |
| Gemma diverse top20 rank11-20 | 40 | 0.000 | 0.000 | 0.025 | 0.000 |

The diverse sets remain hard for shallow selectors. This matters: adding diversity did not turn the benchmark into an easy top-score or mean-score problem.

## Updated Experimental Target

The next external/local verifier run should prioritize the diverse prompt files, not the repeated pilot files:

```text
outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse.jsonl
outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse.jsonl
```

The older repeated rank11-20 files are still useful for stress-testing repeated-family consistency and comparing against v23, but the diverse files are the cleaner benchmark assets.
