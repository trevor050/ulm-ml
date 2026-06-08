# v42 - Token-Budget Generation-vs-Verification Comparison

**Status:** June 1, 2026. Budget-fair objection check using trace-only dynamic extra sampling and the v33 rank-bucket verification projection.

## Question

v41 showed that uncertainty-targeted extra samples barely improve realized `cluster_sum`, but many of those rows spend thousands of generation tokens/problem.

The sharper objection is:

> At the same 512-1024 token budgets used by the adaptive-depth verifier projection, how much dynamic extra sampling can we actually buy, and how much does it improve deployed selection?

## Artifacts

Scripts:

```text
work/dynamic_sampling_baseline.py
work/token_budget_generation_vs_verification.py
```

Outputs:

```text
outputs/dynamic_sampling_token_matched.md
outputs/dynamic_sampling_token_matched.csv
outputs/token_budget_generation_vs_verification.md
outputs/token_budget_generation_vs_verification.csv
```

## Method

The dynamic generation side starts from N=128 and allocates extra 128-sample chunks using:

- fixed arbitrary/uniform allocation,
- answer entropy,
- low cluster-score margin,
- low top-cluster score share,
- a tiny calibration-trained hidden-gain predictor,
- an oracle hidden-gain allocation for headroom only.

For the budget comparison, the scorer selects the best **non-oracle** dynamic generation row whose extra sample tokens/problem fit within the token budget. It also allows a `do_nothing` baseline with zero cost and zero delta, because a rational generation policy should not be forced to spend tokens on a harmful row.

The verifier side uses the v33 rank-bucket rows at the same nominal budgets. These remain projected verifier-success rows, not measured external-verifier evidence.

## Result

| dataset | token budget | best dynamic generation within budget | generation `cluster_sum` delta | oracle generation delta | rank-bucket verifier projected delta |
|---|---:|---|---:|---:|---:|
| MATH/Llama | 512 | do nothing | +0.000 | +0.000 | +0.159 |
| MATH/Llama | 1024 | do nothing | +0.000 | +0.000 | +0.228 |
| MATH/Gemma | 512 | low margin at 435 tokens/problem | +0.027 | +0.000 | +0.120 |
| MATH/Gemma | 1024 | low margin at 435 tokens/problem | +0.027 | +0.014 | +0.194 |

The `1024`-token comparison is the cleanest:

- Llama: best dynamic generation `+0.000`, rank-bucket projection `+0.228`.
- Gemma: best dynamic generation `+0.027`, rank-bucket projection `+0.194`.

Even oracle extra-sampling allocation has no Llama gain and only `+0.014` Gemma gain at 1024 generation tokens/problem in this coarse chunk setup.

## Interpretation

This does not prove the verifier method end-to-end. The verifier rows are still projections that must be replaced by measured external/local verifier behavior.

It does make the budget objection much sharper. At the token budgets where adaptive-depth verification is projected to help, extra generation cannot buy enough additional traces to reliably change the selected answer cluster. The fair generation baseline is not "N=1024 costs 100k+ tokens"; it is:

```text
with 512-1024 extra tokens/problem, dynamic generation gets at most a few 128-sample chunks on a small subset of problems
```

Under that constraint, realized `cluster_sum` barely moves.

## What This Adds

The paper can now separate three claims:

1. Fixed extra sampling to N=1024 increases hidden coverage but barely moves `cluster_sum` (v36).
2. Uncertainty-targeted extra sampling also barely moves `cluster_sum` (v41).
3. At verifier-scale token budgets, dynamic extra sampling is even weaker because it cannot buy many samples (v42).

The decisive remaining test is unchanged: run the external/local verifier on deployed-mix prompts and score it with v39.

## Verification

```bash
python3 work/test_dynamic_sampling_baseline.py
python3 work/dynamic_sampling_baseline.py \
  --output-prefix dynamic_sampling_token_matched \
  --avg-extra-samples 4,8,16,32
python3 work/test_token_budget_generation_vs_verification.py
python3 work/token_budget_generation_vs_verification.py \
  --output-prefix token_budget_generation_vs_verification
```

All commands passed locally.
