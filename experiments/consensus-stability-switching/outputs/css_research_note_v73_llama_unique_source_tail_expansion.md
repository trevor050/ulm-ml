# v73 Llama Unique-Source Tail Expansion

**Date:** June 1, 2026  
**Question:** Can the sparse Llama unique-source top20-only deployed-mix bucket be enlarged with the existing trace?

## Run

I reran the deployed-mix packet builder for MATH/Llama with one packet per source problem, a larger target, and more trials per problem:

```bash
python3 work/build_deployed_mix_packet_dataset.py \
  --data work/MATH_Llama-3-8B-Instruct.json \
  --dataset-label MATH_Llama-deployed-mix-top20-unique32 \
  --output-prefix cluster_packets_math_llama_n128_deployed_mix_top20_unique32 \
  --target-per-category 32 \
  --trials-per-problem 96 \
  --max-packets-per-problem 1 \
  --seed 60601

python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl \
  --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.jsonl \
  --representatives-per-cluster 1 \
  --rationale-chars 420
```

Then I reran the v72 representativeness target sweep with this asset included.

## Result

The expansion produced:

- `74` one-source Llama packets.
- `30` baseline-correct packets.
- `15` recoverable-top5 packets.
- `12` recoverable-top10-only packets.
- `9` recoverable-top20-only packets.
- `2` no-visible-top20 packets.
- `6` no-correct-generated packets.
- `74` compact prompts in [cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.jsonl](cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.jsonl).

The updated v72 sweep reports, under one baseline regression:

| config | recoverable top20 rate | top20-only target | top20-only selected |
|---|---:|---:|---:|
| Llama balanced | `0.389` | `6/12` | `12` |
| Llama unique16 | `0.366` | `5/8` | `8` |
| Llama unique24 | `0.370` | `2/6` | `6` |
| Llama unique32 attempt | `0.370` | `3/9` | `9` |

## Read

The existing trace can improve the Llama unique-source tail bucket slightly, but it does not create a balanced unique-source benchmark. The top20-only bucket rises to `9`, while no-visible-top20 remains only `2`. This means:

1. The balanced deployed-mix set remains the right first smoke benchmark.
2. The unique-source Llama set is useful as a pressure check, not a decisive tail-specific benchmark.
3. A strong Llama top20-only generalization claim needs more traces, a different seed/split search, or relaxed one-source constraints.
4. Gemma unique16 is still the cleaner lower-duplication tail check in the current artifact set.

## Caveat

This is an asset-generation result, not a verifier result. It improves the next-run materials and clarifies the representativeness limit.
