# v48 - Unique-Source Deployed-Mix Assets

## Why this exists

v47 showed that the original deployed-mix assets are category-balanced but source-light: `72` packets per model collapse to `38` Llama and `37` Gemma unique source problems.

v48 rebuilds a lower-duplication alternative with one packet per source problem, then measures the tradeoff.

## New assets

MATH/Llama:

- [cluster_packets_math_llama_n128_deployed_mix_top20_unique16.md](cluster_packets_math_llama_n128_deployed_mix_top20_unique16.md)
- [cluster_packets_math_llama_n128_deployed_mix_top20_unique16.jsonl](cluster_packets_math_llama_n128_deployed_mix_top20_unique16.jsonl)
- [cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique16_compact.jsonl](cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique16_compact.jsonl)
- [cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique16_compact.answer_key.json](cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique16_compact.answer_key.json)

MATH/Gemma:

- [cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.md](cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.md)
- [cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl](cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl)
- [cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_unique16_compact.jsonl](cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_unique16_compact.jsonl)
- [cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_unique16_compact.answer_key.json](cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_unique16_compact.answer_key.json)

Audit:

- [deployed_mix_unique16_representativeness.md](deployed_mix_unique16_representativeness.md)
- [deployed_mix_unique16_representativeness.csv](deployed_mix_unique16_representativeness.csv)

## Result

The one-packet-per-source rebuild improves source coverage:

- MATH/Llama: `79` packets, `79` unique source problems.
- MATH/Gemma: `96` packets, `96` unique source problems.

Gemma fills the full `16` packets/category target. Llama fills most categories, but rare buckets remain sparse:

- `recoverable_top20_only`: `8/16`
- `no_visible_top20`: `7/16`

This is a real constraint of the 128-problem trace under one-source sampling, not just a script hiccup.

## Recommended use

Use the original balanced `72`-prompt/model deployed-mix set when the priority is category-balanced recovery/regression accounting.

Use the unique-source set when the priority is source coverage and lower duplication.

If a real verifier result is strong on both, the claim is much healthier. If it is strong only on the duplicated balanced set, report it as a smoke result and rebuild a larger trace before claiming broad deployment gains.
