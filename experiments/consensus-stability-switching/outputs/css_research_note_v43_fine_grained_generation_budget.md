# v43 - Fine-Grained Dynamic Generation Budget Check

**Status:** June 1, 2026. Follow-up to v42, giving the extra-sampling baseline smaller allocation chunks.

## Why This Exists

v42 compared dynamic extra sampling against rank-bucket verification at 512/1024 token budgets, but its generation baseline allocated extra samples in 128-sample chunks. That is a realistic batch-rerun regime, but a reviewer could reasonably say:

> A dynamic sampler would not spend 128 extra samples at once. It would add a few samples at a time.

v43 reruns the token-budget check with 8-sample chunks.

## Artifacts

```text
outputs/dynamic_sampling_fine_token_matched.md
outputs/dynamic_sampling_fine_token_matched.csv
outputs/token_budget_generation_vs_verification_fine.md
outputs/token_budget_generation_vs_verification_fine.csv
```

Command:

```bash
python3 work/dynamic_sampling_baseline.py \
  --output-prefix dynamic_sampling_fine_token_matched \
  --chunk-size 8 \
  --avg-extra-samples 4,8,16,32

python3 work/token_budget_generation_vs_verification.py \
  --dynamic-csv outputs/dynamic_sampling_fine_token_matched.csv \
  --output-prefix token_budget_generation_vs_verification_fine
```

## Result

At 512/1024 tokens per problem, best non-oracle fine-grained dynamic generation still does not improve realized `cluster_sum`:

| dataset | budget | best fine-grained dynamic generation | generation delta | any-correct delta | projected rank-bucket delta |
|---|---:|---|---:|---:|---:|
| MATH/Llama | 512 | do nothing | +0.000 | +0.000 | +0.159 |
| MATH/Llama | 1024 | do nothing | +0.000 | +0.000 | +0.228 |
| MATH/Gemma | 512 | do nothing | +0.000 | +0.000 | +0.120 |
| MATH/Gemma | 1024 | learned hidden-gain at 565 tokens | +0.000 | +0.027 | +0.194 |

The fine-grained run improves the fairness of the generation baseline, but not its deployed-selection outcome.

## Interpretation

The selectability claim survives a stronger generation baseline:

- fixed N=1024 sampling mostly increases hidden coverage (v36),
- uncertainty-targeted 128-sample chunks barely move `cluster_sum` (v41/v42),
- 8-sample chunks at 512/1024 token budgets still do not move `cluster_sum` (v43).

This strengthens the paper's narrow budget claim:

```text
At verifier-scale token budgets, extra generation does not buy enough answer-cluster movement to solve deployed selection on these traces.
```

The verifier side remains projected. The decisive missing result is still measured external/local verifier performance on deployed-mix prompts, scored with v39.

## Caveats

- This is still a trace-prefix simulation over fixed Monkey Business samples.
- The dynamic generation policies are simple uncertainty heuristics plus a tiny calibration-trained hidden-gain model, not a fully optimized dynamic-SC system.
- Fine-grained chunks make allocation fairer, but they do not simulate model-runtime distribution shift from fresh sampling.

## Verification

```bash
python3 work/test_dynamic_sampling_baseline.py
python3 work/dynamic_sampling_baseline.py \
  --output-prefix dynamic_sampling_fine_token_matched \
  --chunk-size 8 \
  --avg-extra-samples 4,8,16,32
python3 work/test_token_budget_generation_vs_verification.py
python3 work/token_budget_generation_vs_verification.py \
  --dynamic-csv outputs/dynamic_sampling_fine_token_matched.csv \
  --output-prefix token_budget_generation_vs_verification_fine
```

All commands passed locally.
