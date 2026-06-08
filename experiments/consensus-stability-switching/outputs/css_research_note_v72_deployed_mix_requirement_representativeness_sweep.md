# v72 Deployed-Mix Requirement Representativeness Sweep

**Date:** June 1, 2026  
**Question:** Do the v71 verifier smoke targets survive lower-duplication deployed-mix assets?

## Run

I compared the finite-sample top20 verifier targets across the balanced deployed-mix smoke set and source-unique variants.

```bash
python3 work/deployed_mix_requirement_representativeness_sweep.py \
  --output-prefix deployed_mix_requirement_representativeness_sweep \
  --baseline-regressions 1
```

Primary artifact: [deployed_mix_requirement_representativeness_sweep.md](deployed_mix_requirement_representativeness_sweep.md).

## Result

Assuming one already-correct baseline regression:

| config | dataset | baseline preservation | recoverable top20 rate | uniform successes/category | top20-only target | top20-only selected |
|---|---|---:|---:|---:|---:|---:|
| balanced | MATH/Llama | `0.917` | `0.389` | `2` | `6` | `12` |
| balanced | MATH/Gemma | `0.917` | `0.342` | `1` | `4` | `12` |
| unique16 | MATH/Llama | `0.938` | `0.366` | `1` | `5` | `8` |
| unique16 | MATH/Gemma | `0.938` | `0.370` | `1` | `3` | `16` |
| unique24 | MATH/Llama | `0.958` | `0.370` | `1` | `2` | `6` |

## Read

The target does not disappear when duplicate pressure is reduced. Recoverable top20 mass stays around `0.36-0.39`, and uniform successes/category remain low.

The caveat is Llama tail sparsity. The unique-source Llama sets have only `8` or `6` top20-only packets, so a failed top20-only result there would be ambiguous. Gemma unique16 is healthier: it has `16` top20-only packets and a low `3/16` tail-only target under one baseline regression.

## Benchmark Recommendation

Run the balanced deployed-mix set first because it is category-balanced and gives the cleanest regression-aware smoke. Then run the unique-source set as a representativeness pressure check:

- Treat Gemma unique16 as a meaningful lower-duplication top20-tail check.
- Treat Llama unique-source as a caveat unless the top20-only bucket is enlarged.
- Report balanced and unique-source results separately, not pooled.

## Caveat

This is still a target-table audit, not a verifier result. It tells us how to interpret a real verifier run once predictions exist.
