# Pairwise Router-Judge Policy-Guard Audit

This reruns the v125 natural-rate setup but lets source-disjoint calibration choose not only the judge model/rule, but also which routed policy families are allowed through. The candidate policy sets are all non-empty subsets of the routed policies, plus the no-op rule. This is a risk-control probe, not a final deployed policy.

Router source regression budget: `2`. Guard budgets: `0,1,2,5`. Policies: `target_intersection_top10,target_intersection_top20,union_rank_top3`.

| guard budget | trials | baseline | raw delta | guarded delta | raw rec/reg | guarded rec/reg | rec kept | reg kept | selected | policy rec/reg |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0 | 1776 | 0.237 | +0.118 [+0.079, +0.161] | +0.065 [+0.039, +0.095] | 240/30 | 117/2 | 0.487 | 0.067 | 60601:mathstral/B/target_intersection_top20; 60602:gemma4/B/target_intersection_top10+target_intersection_top20+union_rank_top3; 60603:qwen14b/B/target_intersection_top10+target_intersection_top20+union_rank_top3 | target_intersection_top10:5/0; target_intersection_top20:27/0; union_rank_top3:85/2 |
| 1 | 1776 | 0.237 | +0.118 [+0.080, +0.159] | +0.082 [+0.053, +0.113] | 240/30 | 148/2 | 0.617 | 0.067 | 60601:mathstral/B_or_BOTH/target_intersection_top20+union_rank_top3; 60602:gemma4/B/target_intersection_top10+target_intersection_top20+union_rank_top3; 60603:qwen14b/B/target_intersection_top10+target_intersection_top20+union_rank_top3 | target_intersection_top10:5/0; target_intersection_top20:27/0; union_rank_top3:116/2 |
| 2 | 1776 | 0.237 | +0.118 [+0.079, +0.159] | +0.097 [+0.067, +0.130] | 240/30 | 177/4 | 0.738 | 0.133 | 60601:qwen14b/B/target_intersection_top20+union_rank_top3; 60602:qwen14b/B/target_intersection_top10+target_intersection_top20+union_rank_top3; 60603:qwen14b/B/target_intersection_top10+target_intersection_top20+union_rank_top3 | target_intersection_top10:5/0; target_intersection_top20:31/0; union_rank_top3:141/4 |
| 5 | 1776 | 0.237 | +0.118 [+0.078, +0.160] | +0.097 [+0.066, +0.131] | 240/30 | 177/4 | 0.738 | 0.133 | 60601:qwen14b/B/target_intersection_top20+union_rank_top3; 60602:qwen14b/B/target_intersection_top10+target_intersection_top20+union_rank_top3; 60603:qwen14b/B/target_intersection_top10+target_intersection_top20+union_rank_top3 | target_intersection_top10:5/0; target_intersection_top20:31/0; union_rank_top3:141/4 |

## Read

The policy-family guard asks whether the extra budget2 recovery can be made less fragile by learning which upstream route families are worth trusting. Because the guard is selected from source problems only, a positive row is stronger than a post-hoc veto over the four observed regressions. A negative or flat row means the v125 budget1/budget2 tradeoff is probably the cleaner story.

Per-fold CSV: [pairwise_router_policy_guard_v129.csv](pairwise_router_policy_guard_v129.csv). Aggregate CSV: [pairwise_router_policy_guard_v129_aggregate.csv](pairwise_router_policy_guard_v129_aggregate.csv). Trial details: [pairwise_router_policy_guard_v129_details.csv](pairwise_router_policy_guard_v129_details.csv).