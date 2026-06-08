# v36 Generation-vs-Verification Budget Ablation

**Date:** June 1, 2026  
**Question:** why not spend the budget on more samples instead of adaptive cluster-depth verification?

## Result

Extended generation-only audits now run MATH/Llama and MATH/Gemma beyond the previous `N=128` focus:

```text
N = 4, 8, 16, 32, 64, 128, 256, 512, 1024
```

The answer is sharp: more samples mostly increase hidden coverage, not deployed selection.

| dataset | N=128 `cluster_sum` | N=1024 `cluster_sum` | delta | N=128 any-correct | N=1024 any-correct | extra sample tokens/problem |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.457 | 0.466 | +0.009 | 0.858 | 0.946 | 114374 |
| MATH/Gemma | 0.242 | 0.271 | +0.029 | 0.725 | 0.894 | 126364 |

For comparison, the v33 rank-bucket adaptive-depth policy projects much larger deployed gains at `1024` verifier tokens/problem:

| dataset | projected rank-bucket delta at 1024 verifier tokens/problem |
|---|---:|
| MATH/Llama | +0.228 +/- 0.008 |
| MATH/Gemma | +0.194 +/- 0.024 |

This is not a measured verifier-vs-generation victory because the rank-bucket result still uses projected verifier-success assumptions. It is a strong objection check: generation-only scaling does not make the selectability bottleneck disappear under the current selector.

## Important Detail

At the first doubling after the base point, the result is already visible:

| dataset | N=128 -> N=256 extra sample tokens/problem | `cluster_sum` delta | any-correct delta |
|---|---:|---:|---:|
| MATH/Llama | 16031 | -0.002 | +0.036 |
| MATH/Gemma | 17220 | +0.002 | +0.084 |

So even tens of thousands of extra generation tokens mostly buy additional latent coverage rather than a better final deployed answer.

## How It Was Measured

Generation scaling:

```bash
python3 work/cluster_selectability_audit.py \
  --data work/MATH_Llama-3-8B-Instruct.json \
  --dataset-label MATH_Llama-generation-scaling \
  --output-prefix generation_scaling_math_llama \
  --ns 4,8,16,32,64,128,256,512,1024 \
  --trials-per-problem 12

python3 work/cluster_selectability_audit.py \
  --data work/MATH_Gemma-2B.json \
  --dataset-label MATH_Gemma-generation-scaling \
  --output-prefix generation_scaling_math_gemma2b \
  --ns 4,8,16,32,64,128,256,512,1024 \
  --trials-per-problem 12
```

Budget comparison:

```bash
python3 work/test_generation_vs_verification_budget.py
python3 work/generation_vs_verification_budget.py --output-prefix generation_vs_verification_budget
```

Generation token estimates are measured from actual held-out trace sample lengths as `characters / 4`. This is approximate, but the orders of magnitude are not close enough for the conclusion to depend on tokenizer details.

## Read

The reviewer attack "why not just generate more?" now has a measured local answer:

> More samples substantially raise any-correct coverage while barely improving `cluster_sum`.

That means the method should not be framed as competing with sampling coverage. It should be framed as exploiting the extra coverage that sampling creates but cheap selectors fail to surface.

## Caveats

- The comparison uses sample-character token estimates, not model-tokenized generation bills.
- The generation-only curves are measured, but the rank-bucket verifier gains remain projected.
- A true paper-quality version should compare measured external verifier runs against generation-only curves under one tokenizer and one model endpoint.
- The current conclusion is narrower but useful: more sampling alone does not solve deployed selection on high-N MATH in these traces.

Artifacts:

- [generation-vs-verification report](generation_vs_verification_budget.md)
- [generation-vs-verification CSV](generation_vs_verification_budget.csv)
- [generation-vs-verification comparison CSV](generation_vs_verification_budget_comparison.csv)
- [MATH/Llama generation scaling](generation_scaling_math_llama.md)
- [MATH/Gemma generation scaling](generation_scaling_math_gemma2b.md)
