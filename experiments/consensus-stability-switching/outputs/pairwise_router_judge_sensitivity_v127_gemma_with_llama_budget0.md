# Pairwise Router-Judge Sensitivity Audit

Input details: `outputs/pairwise_router_judge_natural_rate_v127_gemma_with_llama_details.csv`. Pairwise source budget: `0`.

## Aggregate

| denominator | policy | rows | delta | recoveries | regressions |
|---|---|---:|---:|---:|---:|
| natural | raw router | 1776 | +0.118 | 240 | 30 |
| natural | pairwise gated | 1776 | +0.058 | 105 | 2 |
| accepted actions | raw router | 519 | +0.405 | 240 | 30 |
| accepted actions | pairwise gated | 519 | +0.198 | 105 | 2 |

## Leave-One-Problem-Out

| denominator | groups | positive LOO | min delta | max delta | worst dropped group | best dropped group |
|---|---:|---:|---:|---:|---|---|
| natural | 222 | 222/222 | +0.054 | +0.059 | s60602/p12 contrib 8 -> +0.054 | s60603/p82 contrib -1 -> +0.059 |
| accepted actions | 122 | 122/122 | +0.186 | +0.203 | s60602/p12 contrib 8 -> +0.186 | s60603/p88 contrib -1 -> +0.203 |

## Top Natural Contributors

| seed | pid | trials | contribution | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|
| 60602 | 12 | 8 | 8 | 8 | 0 |
| 60602 | 35 | 8 | 8 | 8 | 0 |
| 60603 | 3 | 8 | 8 | 8 | 0 |
| 60603 | 91 | 8 | 8 | 8 | 0 |
| 60603 | 96 | 8 | 8 | 8 | 0 |
| 60603 | 111 | 8 | 8 | 8 | 0 |
| 60602 | 91 | 8 | 7 | 7 | 0 |
| 60603 | 102 | 8 | 7 | 7 | 0 |
| 60603 | 35 | 8 | 6 | 6 | 0 |
| 60603 | 47 | 8 | 6 | 6 | 0 |
| 60603 | 39 | 8 | 5 | 5 | 0 |
| 60603 | 7 | 8 | 3 | 3 | 0 |

## Pairwise Regressions

| seed | pid | trial | policy | packet | judge | choice |
|---:|---:|---:|---|---|---|---|
| 60603 | 82 | 7 | union_rank_top3 | pairwise_router_v125_budget2_all_0510_regression_s60603_p82_t7 | qwen14b | B |
| 60603 | 88 | 4 | union_rank_top3 | pairwise_router_v125_budget2_all_0511_regression_s60603_p88_t4 | qwen14b | B |

## Read

The natural-rate pairwise result is not carried by a single problem group: every leave-one-problem-out natural resample remains positive. Accepted-action LOO is also positive across all accepted problem groups, though its range is wider because the accepted denominator is intentionally concentrated on routed actions.