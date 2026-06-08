# v25 Compact Diverse Verifier Prompts

## Motivation

The v24 diverse rank11-20 prompt sets are cleaner benchmark assets, but the full top-20 prompts are large: roughly 17k-18k characters on average and up to 31k. That is workable for some long-context models but annoying for cheap local verifier runs.

I added prompt-time compaction controls to `work/make_cluster_verifier_prompts.py`:

```bash
--representatives-per-cluster
--rationale-chars
```

This preserves the same packets, packet IDs, cluster set, and answer keys while reducing the amount of rationale text shown per cluster.

## New Prompt Files

Compact, one representative per cluster, 420 chars per rationale:

- `outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.jsonl`
- `outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse_compact.jsonl`

Ultracompact, one representative per cluster, 240 chars per rationale:

- `outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_ultracompact.jsonl`
- `outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse_ultracompact.jsonl`

Audit: `outputs/compact_diverse_prompt_audit.md`.

## Size Reduction

| set | prompts | avg chars | p90 chars | max chars |
|---|---:|---:|---:|---:|
| Llama full | 27 | 18446 | 23836 | 31231 |
| Llama compact | 27 | 9475 | 11032 | 11778 |
| Llama ultracompact | 27 | 7580 | 7960 | 8181 |
| Gemma full | 40 | 17017 | 21804 | 23930 |
| Gemma compact | 40 | 9064 | 10571 | 11217 |
| Gemma ultracompact | 40 | 7522 | 7941 | 8284 |

## Recommended Verifier Run Order

1. Run compact prompts first. They are much cheaper while still preserving one rationale for every top-20 cluster.
2. If compact accuracy is poor, run the full prompts on the same packet IDs to measure whether failures are caused by truncation or genuine verifier weakness.
3. Use ultracompact prompts only for cheap broad sweeps or small-context models.

This turns the next external/local verifier experiment into an ablation:

```text
same packets, same answer keys, same cluster depth,
different evidence budget per cluster
```

That is reviewer-useful because it separates "semantic verifier cannot solve buried clusters" from "we starved the verifier of evidence."
