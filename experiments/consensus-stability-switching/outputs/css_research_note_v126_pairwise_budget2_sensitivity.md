# v126 Higher-Budget Pairwise Sensitivity Audit

## Question

v125 moves the Gemma-with-Llama pairwise router-judge frontier from the conservative budget-0 result to a higher raw-router budget:

- raw router budget 2: `+0.118`, with `240` recoveries and `30` regressions
- pairwise budget 1: `+0.083`, with `150` recoveries and `2` regressions
- pairwise budget 2: `+0.099`, with `180` recoveries and `4` regressions

This v126 audit asks whether those new natural-rate gains are concentrated in a small number of problem groups.

## Setup

Input:

- `outputs/pairwise_router_judge_natural_rate_v125_budget2_details.csv`

Commands:

```bash
python3 work/pairwise_router_judge_sensitivity.py \
  --details outputs/pairwise_router_judge_natural_rate_v125_budget2_details.csv \
  --budget 1 \
  --output-prefix pairwise_router_judge_sensitivity_v126_budget1

python3 work/pairwise_router_judge_sensitivity.py \
  --details outputs/pairwise_router_judge_natural_rate_v125_budget2_details.csv \
  --budget 2 \
  --output-prefix pairwise_router_judge_sensitivity_v126_budget2
```

Outputs:

- `outputs/pairwise_router_judge_sensitivity_v126_budget1.md`
- `outputs/pairwise_router_judge_sensitivity_v126_budget1_natural_loo.csv`
- `outputs/pairwise_router_judge_sensitivity_v126_budget1_accepted_loo.csv`
- `outputs/pairwise_router_judge_sensitivity_v126_budget1_regressions.csv`
- `outputs/pairwise_router_judge_sensitivity_v126_budget2.md`
- `outputs/pairwise_router_judge_sensitivity_v126_budget2_natural_loo.csv`
- `outputs/pairwise_router_judge_sensitivity_v126_budget2_accepted_loo.csv`
- `outputs/pairwise_router_judge_sensitivity_v126_budget2_regressions.csv`

## Result

Budget 1:

| denominator | policy | rows | delta | recoveries | regressions |
|---|---|---:|---:|---:|---:|
| natural | raw router | `1776` | `+0.118` | `240` | `30` |
| natural | pairwise gated | `1776` | `+0.083` | `150` | `2` |
| accepted actions | raw router | `519` | `+0.405` | `240` | `30` |
| accepted actions | pairwise gated | `519` | `+0.285` | `150` | `2` |

Budget 1 leave-one-problem-out:

| denominator | groups | positive LOO | min delta | max delta | worst dropped group | best dropped group |
|---|---:|---:|---:|---:|---|---|
| natural | `222` | `222/222` | `+0.079` | `+0.084` | `s60601/p111`, contribution `8` | `s60603/p82`, contribution `-1` |
| accepted actions | `122` | `122/122` | `+0.274` | `+0.290` | `s60601/p111`, contribution `8` | `s60603/p88`, contribution `-1` |

Budget 1 pairwise regressions:

| seed | pid | trial | policy | packet | judge | choice |
|---:|---:|---:|---|---|---|---|
| `60603` | `82` | `7` | `union_rank_top3` | `pairwise_router_v125_budget2_all_0510_regression_s60603_p82_t7` | `qwen14b` | `B` |
| `60603` | `88` | `4` | `union_rank_top3` | `pairwise_router_v125_budget2_all_0511_regression_s60603_p88_t4` | `qwen14b` | `B` |

Budget 2:

| denominator | policy | rows | delta | recoveries | regressions |
|---|---|---:|---:|---:|---:|
| natural | raw router | `1776` | `+0.118` | `240` | `30` |
| natural | pairwise gated | `1776` | `+0.099` | `180` | `4` |
| accepted actions | raw router | `519` | `+0.405` | `240` | `30` |
| accepted actions | pairwise gated | `519` | `+0.339` | `180` | `4` |

Budget 2 leave-one-problem-out:

| denominator | groups | positive LOO | min delta | max delta | worst dropped group | best dropped group |
|---|---:|---:|---:|---:|---|---|
| natural | `222` | `222/222` | `+0.095` | `+0.100` | `s60601/p3`, contribution `8` | `s60601/p88`, contribution `-1` |
| accepted actions | `122` | `122/122` | `+0.329` | `+0.345` | `s60601/p3`, contribution `8` | `s60601/p88`, contribution `-1` |

Budget 2 pairwise regressions:

| seed | pid | trial | policy | packet | judge | choice |
|---:|---:|---:|---|---|---|---|
| `60601` | `88` | `0` | `union_rank_top3` | `pairwise_router_v125_budget2_all_0494_regression_s60601_p88_t0` | `qwen14b` | `B` |
| `60602` | `63` | `6` | `union_rank_top3` | `pairwise_router_v125_budget2_all_0499_regression_s60602_p63_t6` | `qwen14b` | `B` |
| `60603` | `82` | `7` | `union_rank_top3` | `pairwise_router_v125_budget2_all_0510_regression_s60603_p82_t7` | `qwen14b` | `B` |
| `60603` | `88` | `4` | `union_rank_top3` | `pairwise_router_v125_budget2_all_0511_regression_s60603_p88_t4` | `qwen14b` | `B` |

## Read

The v125 higher-budget gain is not a one-problem artifact. Both the safer budget-1 policy and the higher-gain budget-2 policy remain positive after dropping every individual `(seed, pid)` group:

- budget 1 natural LOO: `222/222` positive, minimum `+0.079`
- budget 2 natural LOO: `222/222` positive, minimum `+0.095`

This is stronger than v124 in two ways. First, the natural gain is larger. Second, it survives after the router is allowed to expose more risky actions.

The regression story is also sharper now. All budget-2 pairwise regressions are `qwen14b/B` choices on `union_rank_top3` actions. Budget 1 is safer because it avoids two of those four regressions while keeping `150/180` of the budget-2 pairwise recoveries.

Current reviewer-resistant wording:

> Higher-budget auxiliary routing increases both recovery supply and regression risk. A source-selected pairwise answer judge preserves a large fraction of the added recoveries, sharply reduces regressions, and remains positive under leave-one-problem-out over all held-out problem groups.

Next useful pressure tests:

1. Manually inspect the four qwen regressions, especially the repeated `p88` family.
2. Rerun the four regressions and a matched missed-recovery set with richer pairwise prompts.
3. Check whether a fold-specific rule that prefers budget 1 when qwen dominates can keep most of budget-2 recovery with budget-1 regression risk.
