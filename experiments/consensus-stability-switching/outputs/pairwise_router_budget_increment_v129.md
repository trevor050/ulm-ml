# Pairwise Router-Judge Budget Increment Audit

Input details: `pairwise_router_judge_natural_rate_v125_budget2_details.csv`. This compares pairwise source budget `2` against budget `1` trial-by-trial.

## Aggregate

| trials | net increment | delta | positive trials | negative trials | positive groups | negative groups | zero groups | LOO positive | min LOO | max LOO |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1776 | +28 | +0.016 | 41 | 13 | 13 | 4 | 205 | 222/222 | +0.011 dropping s60601/p58 | +0.020 dropping s60602/p12 |

## Breakdowns

- Signed policy increment: `union_rank_top3:23; target_intersection_top20:4; target_intersection_top10:1`
- Trial changes by policy/sign: `('union_rank_top3', 1):34; ('union_rank_top3', -1):11; ('target_intersection_top20', 1):6; ('target_intersection_top20', -1):2; ('target_intersection_top10', 1):1`
- Signed seed increment: `60601:18; 60602:10`

## Top Positive Groups

| seed | pid | trials | increment | positive trials | negative trials |
|---:|---:|---:|---:|---:|---:|
| 60601 | 58 | 8 | +8 | 8 | 0 |
| 60602 | 100 | 8 | +7 | 7 | 0 |
| 60601 | 3 | 8 | +4 | 4 | 0 |
| 60601 | 27 | 8 | +4 | 4 | 0 |
| 60602 | 39 | 8 | +4 | 4 | 0 |
| 60602 | 47 | 8 | +3 | 3 | 0 |
| 60601 | 43 | 8 | +2 | 2 | 0 |
| 60601 | 98 | 8 | +2 | 2 | 0 |
| 60602 | 43 | 8 | +2 | 2 | 0 |
| 60601 | 7 | 8 | +1 | 1 | 0 |
| 60601 | 10 | 8 | +1 | 1 | 0 |
| 60602 | 63 | 8 | +1 | 2 | 1 |

## Negative Groups

| seed | pid | trials | increment | positive trials | negative trials |
|---:|---:|---:|---:|---:|---:|
| 60602 | 12 | 8 | -8 | 0 | 8 |
| 60601 | 101 | 8 | -2 | 0 | 2 |
| 60601 | 29 | 8 | -1 | 0 | 1 |
| 60601 | 88 | 8 | -1 | 0 | 1 |

## Read

The increment audit separates the high-budget gain from the already-positive lower-budget result. If the increment is positive under every leave-one-problem-out drop, the extra budget is not a single-problem artifact. If most groups are zero, the increment is still sparse and should be reported as a risk/reward tail choice rather than a broad selector improvement.

Trial deltas: [pairwise_router_budget_increment_v129_trial_deltas.csv](pairwise_router_budget_increment_v129_trial_deltas.csv). Group deltas: [pairwise_router_budget_increment_v129_group_deltas.csv](pairwise_router_budget_increment_v129_group_deltas.csv). LOO: [pairwise_router_budget_increment_v129_loo.csv](pairwise_router_budget_increment_v129_loo.csv).