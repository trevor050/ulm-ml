# v32 Rank-Bucket Depth Policy

## Question

v31 found that independent depth detectors were too myopic: they mostly bought compact top-5 and failed to use deeper verification well. The next question:

> Does directly predicting the correct-cluster rank bucket improve budgeted depth allocation?

## Setup

New script:

```bash
python3 work/test_rank_bucket_depth_policy.py
python3 work/rank_bucket_depth_policy.py --output-prefix rank_bucket_depth_policy
```

The policy predicts the minimal recoverability bucket:

- `top5`,
- `top10_only`,
- `top20_only`,
- `none`.

It then prices compact top-5/top-10/top-20 actions using cumulative bucket probability and greedily spends the verifier-token budget.

## Result

| dataset | budget | rank-bucket policy | old learned policy | fixed compact frontier |
|---|---:|---:|---:|---:|
| MATH/Llama | 128 | 0.508 | 0.508 | 0.488 |
| MATH/Llama | 256 | 0.558 | 0.558 | 0.537 |
| MATH/Llama | 512 | 0.626 | 0.599 | 0.621 |
| MATH/Llama | 1024 | 0.684 | 0.611 | 0.621 |
| MATH/Gemma | 128 | 0.288 | 0.284 | 0.280 |
| MATH/Gemma | 256 | 0.321 | 0.313 | 0.315 |
| MATH/Gemma | 512 | 0.386 | 0.361 | 0.348 |
| MATH/Gemma | 1024 | 0.465 | 0.371 | 0.395 |

Report: `outputs/rank_bucket_depth_policy.md`.

## Interpretation

This is the first learned budgeted-depth policy that clearly improves the pitch. At high budgets, rank-bucket allocation beats both the old learned utility-density policy and the best fixed compact frontier:

```text
MATH/Llama at 1024 tokens/problem: 0.684 vs fixed 0.621
MATH/Gemma at 1024 tokens/problem: 0.465 vs fixed 0.395
```

It also starts to buy deeper inspection only when budget permits: at 1024 tokens/problem, it chooses top-20 for `0.14` of Llama trials and `0.10` of Gemma trials.

## Remaining Gap

The oracle budgeted policy from v31 is still higher: Llama `0.746`, Gemma `0.556`. Rank buckets help, but there is still substantial depth-value prediction headroom.

## Updated Claim

The method now has a plausible learned allocation component:

```text
Predict the rank bucket of recoverable selector misses, then allocate compact verification depth under a token budget.
```

This is still projected verifier-success evidence, not a measured external verifier run.
