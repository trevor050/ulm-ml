# Pairwise Router-Judge Sensitivity Audit

Input details: `/Users/trevorrosato/Documents/Codex/2026-06-01/all-right-suck-it-i-believe-2/outputs/pairwise_router_judge_natural_rate_v122_details.csv`. Pairwise source budget: `0`.

## Aggregate

| denominator | policy | rows | delta | recoveries | regressions |
|---|---|---:|---:|---:|---:|
| natural | raw router | 1776 | +0.097 | 192 | 20 |
| natural | pairwise gated | 1776 | +0.067 | 120 | 1 |
| accepted actions | raw router | 377 | +0.456 | 192 | 20 |
| accepted actions | pairwise gated | 377 | +0.316 | 120 | 1 |

## Leave-One-Problem-Out

| denominator | groups | positive LOO | min delta | max delta | worst dropped group | best dropped group |
|---|---:|---:|---:|---:|---|---|
| natural | 222 | 222/222 | +0.063 | +0.068 | s60601/p3 contrib 8 -> +0.063 | s60601/p88 contrib -1 -> +0.068 |
| accepted actions | 92 | 92/92 | +0.301 | +0.323 | s60601/p3 contrib 8 -> +0.301 | s60601/p88 contrib -1 -> +0.323 |

## Top Natural Contributors

| seed | pid | trials | contribution | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|
| 60601 | 3 | 8 | 8 | 8 | 0 |
| 60601 | 58 | 8 | 8 | 8 | 0 |
| 60602 | 12 | 8 | 8 | 8 | 0 |
| 60602 | 35 | 8 | 8 | 8 | 0 |
| 60603 | 91 | 8 | 8 | 8 | 0 |
| 60603 | 96 | 8 | 8 | 8 | 0 |
| 60601 | 96 | 8 | 7 | 7 | 0 |
| 60603 | 102 | 8 | 7 | 7 | 0 |
| 60601 | 111 | 8 | 6 | 6 | 0 |
| 60603 | 3 | 8 | 6 | 6 | 0 |
| 60603 | 35 | 8 | 6 | 6 | 0 |
| 60601 | 100 | 8 | 5 | 5 | 0 |

## Pairwise Regressions

| seed | pid | trial | policy | packet | judge | choice |
|---:|---:|---:|---|---|---|---|
| 60601 | 88 | 0 | union_rank_top3 | pairwise_router_v120_budget0_all_0358_regression_s60601_p88_t0 | qwen14b | B |

## Read

The natural v122 result is not carried by a single problem group: every leave-one-problem-out natural resample remains positive. Accepted-action LOO is also positive across all accepted problem groups, though its range is wider because the accepted denominator is intentionally concentrated on routed actions.