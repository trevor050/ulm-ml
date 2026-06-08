# Pairwise Router-Judge Sensitivity Audit

Input details: `outputs/pairwise_router_judge_natural_rate_v127_gemma_with_llama_details.csv`. Pairwise source budget: `80`.

## Aggregate

| denominator | policy | rows | delta | recoveries | regressions |
|---|---|---:|---:|---:|---:|
| natural | raw router | 1776 | +0.118 | 240 | 30 |
| natural | pairwise gated | 1776 | +0.099 | 180 | 4 |
| accepted actions | raw router | 519 | +0.405 | 240 | 30 |
| accepted actions | pairwise gated | 519 | +0.339 | 180 | 4 |

## Leave-One-Problem-Out

| denominator | groups | positive LOO | min delta | max delta | worst dropped group | best dropped group |
|---|---:|---:|---:|---:|---|---|
| natural | 222 | 222/222 | +0.095 | +0.100 | s60601/p3 contrib 8 -> +0.095 | s60601/p88 contrib -1 -> +0.100 |
| accepted actions | 122 | 122/122 | +0.329 | +0.345 | s60601/p3 contrib 8 -> +0.329 | s60601/p88 contrib -1 -> +0.345 |

## Top Natural Contributors

| seed | pid | trials | contribution | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|
| 60601 | 3 | 8 | 8 | 8 | 0 |
| 60601 | 58 | 8 | 8 | 8 | 0 |
| 60601 | 111 | 8 | 8 | 8 | 0 |
| 60602 | 35 | 8 | 8 | 8 | 0 |
| 60603 | 3 | 8 | 8 | 8 | 0 |
| 60603 | 91 | 8 | 8 | 8 | 0 |
| 60603 | 96 | 8 | 8 | 8 | 0 |
| 60603 | 111 | 8 | 8 | 8 | 0 |
| 60601 | 96 | 8 | 7 | 7 | 0 |
| 60602 | 91 | 8 | 7 | 7 | 0 |
| 60602 | 100 | 8 | 7 | 7 | 0 |
| 60603 | 102 | 8 | 7 | 7 | 0 |

## Pairwise Regressions

| seed | pid | trial | policy | packet | judge | choice |
|---:|---:|---:|---|---|---|---|
| 60601 | 88 | 0 | union_rank_top3 | pairwise_router_v125_budget2_all_0494_regression_s60601_p88_t0 | qwen14b | B |
| 60602 | 63 | 6 | union_rank_top3 | pairwise_router_v125_budget2_all_0499_regression_s60602_p63_t6 | qwen14b | B |
| 60603 | 82 | 7 | union_rank_top3 | pairwise_router_v125_budget2_all_0510_regression_s60603_p82_t7 | qwen14b | B |
| 60603 | 88 | 4 | union_rank_top3 | pairwise_router_v125_budget2_all_0511_regression_s60603_p88_t4 | qwen14b | B |

## Read

The natural-rate pairwise result is not carried by a single problem group: every leave-one-problem-out natural resample remains positive. Accepted-action LOO is also positive across all accepted problem groups, though its range is wider because the accepted denominator is intentionally concentrated on routed actions.