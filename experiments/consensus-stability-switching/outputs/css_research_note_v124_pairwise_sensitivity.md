# v124 Pairwise Natural-Rate Sensitivity Audit

## Question

v122 gives the strongest current natural-rate positive result:

- raw Gemma-with-Llama router: `+0.097`, with `192` recoveries and `20` regressions
- source-calibrated pairwise-gated router: `+0.067`, with `120` recoveries and `1` regression

This v124 audit asks the obvious reviewer question:

> Is that natural `+0.067` carried by one or two lucky problem groups?

## Setup

Input:

- `outputs/pairwise_router_judge_natural_rate_v122_details.csv`
- pairwise source budget `0`

Command:

```bash
python3 work/pairwise_router_judge_sensitivity.py --output-prefix pairwise_router_judge_sensitivity_v124
```

Outputs:

- `outputs/pairwise_router_judge_sensitivity_v124.md`
- `outputs/pairwise_router_judge_sensitivity_v124_natural_loo.csv`
- `outputs/pairwise_router_judge_sensitivity_v124_accepted_loo.csv`
- `outputs/pairwise_router_judge_sensitivity_v124_top_contributors.csv`
- `outputs/pairwise_router_judge_sensitivity_v124_regressions.csv`

## Result

Aggregate check:

| denominator | policy | rows | delta | recoveries | regressions |
|---|---|---:|---:|---:|---:|
| natural | raw router | `1776` | `+0.097` | `192` | `20` |
| natural | pairwise gated | `1776` | `+0.067` | `120` | `1` |
| accepted actions | raw router | `377` | `+0.456` | `192` | `20` |
| accepted actions | pairwise gated | `377` | `+0.316` | `120` | `1` |

Leave-one-problem-out:

| denominator | groups | positive LOO | min delta | max delta | worst dropped group | best dropped group |
|---|---:|---:|---:|---:|---|---|
| natural | `222` | `222/222` | `+0.063` | `+0.068` | `s60601/p3`, contribution `8` | `s60601/p88`, contribution `-1` |
| accepted actions | `92` | `92/92` | `+0.301` | `+0.323` | `s60601/p3`, contribution `8` | `s60601/p88`, contribution `-1` |

The lone pairwise-gated regression is fully localized:

| seed | pid | trial | policy | packet | judge | choice |
|---:|---:|---:|---|---|---|---|
| `60601` | `88` | `0` | `union_rank_top3` | `pairwise_router_v120_budget0_all_0358_regression_s60601_p88_t0` | `qwen14b` | `B` |

## Read

The v122 result is not a one-problem artifact. Dropping any single `(seed, pid)` group leaves the natural pairwise-gated delta positive, with a tight range from `+0.063` to `+0.068`.

This does not prove broad generalization; it is still one trace family with three split seeds. But it strengthens the current claim in exactly the right way:

> The pairwise-gated auxiliary-router gain is distributed over many held-out problem groups, while its regression risk is concentrated in one identifiable packet.

The next useful work is now precise:

1. Audit `s60601/p88/t0` manually and with richer pairwise prompts.
2. Run rationale-inclusive pairwise prompts on the border set: the single regression, top missed recoveries, and top accepted recoveries.
3. Repeat v122/v124 at higher raw-router budgets to see whether pairwise gating scales the risk frontier or only cleans the budget-0 branch.
