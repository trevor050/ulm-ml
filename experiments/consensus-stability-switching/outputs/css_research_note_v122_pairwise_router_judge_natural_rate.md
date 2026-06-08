# v122 Pairwise Router-Judge Natural-Rate Accounting

## Question

v121 showed that pairwise baseline-vs-candidate adjudication can be source-calibrated on accepted auxiliary-router rows. This v122 audit asks the denominator question:

> What does the same source-selected pairwise policy do on the natural held-out trial denominator, where non-invoked trials stay on the baseline?

## Setup

Inputs:

- `outputs/pairwise_router_judge_v120_budget0_all_manifest.csv`
- `outputs/mathstral_pairwise_router_judge_v120_budget0_all_predictions.jsonl`
- `outputs/qwen14b_pairwise_router_judge_v120_budget0_all_predictions.jsonl`
- `outputs/gemma4_pairwise_router_judge_v120_budget0_all_predictions.jsonl`
- `outputs/cross_seed_router_problem_disjoint_frontier_v114.csv`

The policy is identical to v121:

1. For each held-out seed, choose the pairwise judge model/rule on source accepted rows.
2. Exclude source rows whose problem id appears in the held-out seed.
3. Apply the selected model/rule to held-out upstream accepted router actions.
4. Count all held-out trials from the v114 budget-0 problem-disjoint Gemma-with-Llama learned-router row.
5. Leave non-invoked trials on the baseline.

Script and outputs:

- `work/pairwise_router_judge_calibration.py`
- `outputs/pairwise_router_judge_natural_v122.md`
- `outputs/pairwise_router_judge_natural_v122.csv`
- `outputs/pairwise_router_judge_natural_v122_aggregate.csv`

Command:

```bash
python3 work/pairwise_router_judge_calibration.py --output-prefix pairwise_router_judge_calibration_v121 --natural-output-prefix pairwise_router_judge_natural_v122
```

## Result

The source-budget-0 pairwise guard converts the accepted-row v121 result into a natural held-out delta of `+0.067` over `1776` trials.

| source regression budget | natural delta | upstream router delta | signs | judge accepts / upstream accepts | recoveries | regressions | selected rules |
|---:|---:|---:|---:|---:|---:|---:|---|
| `0` | `+0.067` | `+0.097` | `3/3` | `151 / 377` | `120` | `1` | `60601:qwen14b/B`; `60602:gemma4/B`; `60603:gemma4/B` |
| `1` | `+0.067` | `+0.097` | `3/3` | `151 / 377` | `120` | `1` | same |
| `2` | `+0.065` | `+0.097` | `3/3` | `154 / 377` | `117` | `1` | `60601:qwen14b/B`; `60602:qwen14b/B`; `60603:gemma4/B` |
| `5` | `+0.065` | `+0.097` | `3/3` | `154 / 377` | `117` | `1` | same |

The raw upstream problem-disjoint router at budget 0 had `192` recoveries and `20` regressions across the same `1776` natural held-out trials. The pairwise guard discards some recovery, but reduces regressions from `20` to `1`.

## Read

This changes the v121 claim from "large accepted-row gain" to "smaller but much safer natural-rate gain." The right reviewer-facing statement is:

> On the problem-disjoint Gemma-with-Llama budget-0 router, source-calibrated pairwise adjudication keeps a natural held-out gain of `+0.067` while reducing held-out regressions from `20` to `1`.

This is not yet a full deployed verifier result:

- The upstream invocation policy is still the v114 learned router, whose calibration was not low-regression by itself.
- The pairwise guard is only run on already accepted auxiliary-router actions.
- The source accepted-row split has sparse regression examples, so uncertainty should be family-aware.
- The result is for the positive Gemma-with-Llama direction; Llama-with-Gemma remains the needed negative/control direction.

Next step:

1. Run the mirrored Llama-with-Gemma pairwise panel and natural-rate accounting.
2. Add seed/problem-family bootstrap intervals over natural trial deltas.
3. Repeat for higher upstream router budgets to map recovery/regression tradeoff after pairwise filtering.
