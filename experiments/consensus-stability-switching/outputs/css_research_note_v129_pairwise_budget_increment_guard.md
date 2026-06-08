# v129 Pairwise Budget-Increment And Policy-Guard Audit

## Question

v125-v128 left a sharper tradeoff:

- pairwise budget 1: natural `+0.083`, `150/2` recoveries/regressions
- pairwise budget 2: natural `+0.099`, `180/4` recoveries/regressions

This v129 audit asks two narrower questions.

1. Is the budget-2 increment over budget 1 itself a one-problem artifact?
2. Can source-disjoint calibration choose a policy-family guard that keeps the extra recovery while reducing the `qwen14b/B` `union_rank_top3` regression risk?

## Setup

Inputs:

- `outputs/pairwise_router_judge_natural_rate_v125_budget2_details.csv`
- `outputs/pairwise_router_judge_v125_budget2_all_manifest.csv`
- `outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl`
- `outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl`
- `outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl`
- `outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl`

Commands:

```bash
python3 work/pairwise_router_budget_increment.py \
  --details outputs/pairwise_router_judge_natural_rate_v125_budget2_details.csv \
  --low-budget 1 \
  --high-budget 2 \
  --output-prefix pairwise_router_budget_increment_v129

python3 work/pairwise_router_policy_guard.py \
  --answer-rows outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl \
  --manifest outputs/pairwise_router_judge_v125_budget2_all_manifest.csv \
  --mathstral outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --qwen14b outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --gemma4 outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --router-regression-budget 2 \
  --output-prefix pairwise_router_policy_guard_v129
```

Outputs:

- `outputs/pairwise_router_budget_increment_v129.md`
- `outputs/pairwise_router_budget_increment_v129_trial_deltas.csv`
- `outputs/pairwise_router_budget_increment_v129_group_deltas.csv`
- `outputs/pairwise_router_budget_increment_v129_loo.csv`
- `outputs/pairwise_router_policy_guard_v129.md`
- `outputs/pairwise_router_policy_guard_v129.csv`
- `outputs/pairwise_router_policy_guard_v129_aggregate.csv`
- `outputs/pairwise_router_policy_guard_v129_details.csv`

## Budget-2 Increment

The budget-2 increment over budget 1 is positive under every single-problem drop, but sparse.

| trials | net increment | delta | positive trials | negative trials | positive groups | negative groups | zero groups | LOO positive | min LOO | max LOO |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `1776` | `+28` | `+0.016` | `41` | `13` | `13` | `4` | `205` | `222/222` | `+0.011` dropping `s60601/p58` | `+0.020` dropping `s60602/p12` |

Signed increment by policy:

| policy | signed increment |
|---|---:|
| `union_rank_top3` | `+23` |
| `target_intersection_top20` | `+4` |
| `target_intersection_top10` | `+1` |

Trial changes by policy/sign:

| policy | improved trials | worsened trials |
|---|---:|---:|
| `union_rank_top3` | `34` | `11` |
| `target_intersection_top20` | `6` | `2` |
| `target_intersection_top10` | `1` | `0` |

The increment is concentrated in seed `60601` and `60602`; seed `60603` is flat:

| seed | signed increment |
|---:|---:|
| `60601` | `+18` |
| `60602` | `+10` |
| `60603` | `0` |

Top positive groups:

| seed | pid | increment |
|---:|---:|---:|
| `60601` | `58` | `+8` |
| `60602` | `100` | `+7` |
| `60601` | `3` | `+4` |
| `60601` | `27` | `+4` |
| `60602` | `39` | `+4` |
| `60602` | `47` | `+3` |

Negative groups:

| seed | pid | increment |
|---:|---:|---:|
| `60602` | `12` | `-8` |
| `60601` | `101` | `-2` |
| `60601` | `29` | `-1` |
| `60601` | `88` | `-1` |

## Policy-Family Guard

The policy guard reruns the v125 natural-rate setup, but source-disjoint calibration can choose both:

- the pairwise judge model/rule, and
- an allowed subset of routed policy families among `target_intersection_top10`, `target_intersection_top20`, and `union_rank_top3`.

Candidate policy sets are all non-empty subsets of the three policies, plus the no-op rule. This is intentionally a modest guard: it tests whether the obvious route-family veto is available without peeking at held-out regressions.

Result:

| guard budget | trials | baseline | raw delta | guarded delta | raw rec/reg | guarded rec/reg | rec kept | reg kept | selected | policy rec/reg |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `0` | `1776` | `0.237` | `+0.118` | `+0.065` | `240/30` | `117/2` | `0.487` | `0.067` | `60601:mathstral/B/target_intersection_top20`; `60602:gemma4/B/all`; `60603:qwen14b/B/all` | `target_intersection_top10:5/0`; `target_intersection_top20:27/0`; `union_rank_top3:85/2` |
| `1` | `1776` | `0.237` | `+0.118` | `+0.082` | `240/30` | `148/2` | `0.617` | `0.067` | `60601:mathstral/B_or_BOTH/top20+union`; `60602:gemma4/B/all`; `60603:qwen14b/B/all` | `target_intersection_top10:5/0`; `target_intersection_top20:27/0`; `union_rank_top3:116/2` |
| `2` | `1776` | `0.237` | `+0.118` | `+0.097` | `240/30` | `177/4` | `0.738` | `0.133` | `60601:qwen14b/B/top20+union`; `60602:qwen14b/B/all`; `60603:qwen14b/B/all` | `target_intersection_top10:5/0`; `target_intersection_top20:31/0`; `union_rank_top3:141/4` |
| `5` | `1776` | `0.237` | `+0.118` | `+0.097` | `240/30` | `177/4` | `0.738` | `0.133` | same as budget `2` | same as budget `2` |

The guard does not improve the v125 frontier:

- v125 budget 1: `+0.083`, `150/2`
- v129 guarded budget 1: `+0.082`, `148/2`
- v125 budget 2: `+0.099`, `180/4`
- v129 guarded budget 2: `+0.097`, `177/4`

The attempted guard slightly improves the old budget-0 row (`+0.065`, `117/2` vs v125 budget-0 `+0.058`, `105/2`), but it does not solve the higher-budget risk tradeoff.

## Read

The budget-2 increment is real but sparse. It survives leave-one-problem-out over all `222` held-out `(seed, pid)` groups, but only `17/222` groups have nonzero signed increment and `205/222` are unchanged. This should be reported as a tail-risk/tail-recovery choice, not as a broad selector improvement.

The obvious policy-family guard is a negative result. Source-disjoint calibration does not find a simple route-family restriction that keeps the budget-2 recovery while reducing regressions. The budget-1 row remains the cleaner conservative operating point, and budget 2 remains the higher-gain/higher-risk row. v128's cross-judge confirmation guard is therefore the more interesting non-oracle guard family, while v129 closes the simpler policy-family-veto objection.

Current wording:

> Increasing the pairwise source budget buys a small additional natural-rate gain (`+0.016` over budget 1) that is positive under leave-one-problem-out but sparse across problem groups. Simple source-calibrated policy-family guards do not improve the frontier, so the honest tradeoff is conservative budget 1 versus higher-gain budget 2 unless a richer guard, such as cross-judge confirmation, is used.

Next useful pressure tests:

1. Inspect the four budget-2 qwen regressions against matched positive `union_rank_top3` recoveries: `p88` is the repeated digit-cycle offender, `p63` has matched same-family recoveries and one regression, and `p82` looks like weekday lexical drift.
2. Rerun those regression and matched-recovery packets with a richer pairwise prompt that includes more original problem context.
3. If richer pairwise prompting remains qwen-regression-prone, treat qwen/B as the high-recovery judge and mathstral/gemma as conservative judges rather than trying to collapse them into one global policy.
