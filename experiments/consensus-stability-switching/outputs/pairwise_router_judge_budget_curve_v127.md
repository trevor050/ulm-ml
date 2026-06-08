# Pairwise Router-Judge Natural-Rate Scoring

This natural-rate audit takes the full held-out trial denominator. The raw router first chooses an auxiliary-generator action exactly as in v120/v123. The pairwise judge then either accepts that action or falls back to the baseline selector. Source rule selection excludes every problem id in the held-out seed, including problems where the raw router proposes no switch.

Router score: `base_utility`. Router source regression budget: `2`. Pairwise rules: `never,B,B_or_BOTH,always`.

| pairwise source budget | trials | baseline | raw router delta | pairwise delta | raw rec/reg | pairwise rec/reg | rec kept | reg kept | selected |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | 1776 | 0.237 | +0.118 [+0.078, +0.159] | +0.061 [+0.031, +0.093] | 240/30 | 128/20 | 0.533 | 0.667 | 60601:mathstral/never; 60602:gemma4/B; 60603:mathstral/always |
| 1 | 1776 | 0.237 | +0.118 [+0.080, +0.159] | +0.086 [+0.053, +0.121] | 240/30 | 173/20 | 0.721 | 0.667 | 60601:mathstral/B_or_BOTH; 60602:gemma4/B; 60603:mathstral/always |
| 2 | 1776 | 0.237 | +0.118 [+0.079, +0.159] | +0.102 [+0.066, +0.139] | 240/30 | 203/22 | 0.846 | 0.733 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:mathstral/always |
| 3 | 1776 | 0.237 | +0.118 [+0.078, +0.160] | +0.102 [+0.067, +0.139] | 240/30 | 203/22 | 0.846 | 0.733 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:mathstral/always |
| 4 | 1776 | 0.237 | +0.118 [+0.079, +0.159] | +0.102 [+0.067, +0.140] | 240/30 | 203/22 | 0.846 | 0.733 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:mathstral/always |
| 5 | 1776 | 0.237 | +0.118 [+0.079, +0.158] | +0.102 [+0.065, +0.139] | 240/30 | 203/22 | 0.846 | 0.733 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:mathstral/always |
| 6 | 1776 | 0.237 | +0.118 [+0.079, +0.159] | +0.102 [+0.068, +0.139] | 240/30 | 203/22 | 0.846 | 0.733 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:mathstral/always |
| 8 | 1776 | 0.237 | +0.118 [+0.079, +0.160] | +0.114 [+0.076, +0.155] | 240/30 | 229/26 | 0.954 | 0.867 | 60601:mathstral/always; 60602:qwen14b/B; 60603:mathstral/always |
| 10 | 1776 | 0.237 | +0.118 [+0.079, +0.160] | +0.114 [+0.075, +0.155] | 240/30 | 229/26 | 0.954 | 0.867 | 60601:mathstral/always; 60602:qwen14b/B; 60603:mathstral/always |
| 12 | 1776 | 0.237 | +0.118 [+0.079, +0.160] | +0.114 [+0.075, +0.155] | 240/30 | 229/26 | 0.954 | 0.867 | 60601:mathstral/always; 60602:qwen14b/B; 60603:mathstral/always |
| 15 | 1776 | 0.237 | +0.118 [+0.079, +0.160] | +0.118 [+0.078, +0.159] | 240/30 | 240/30 | 1.000 | 1.000 | 60601:mathstral/always; 60602:mathstral/always; 60603:mathstral/always |
| 20 | 1776 | 0.237 | +0.118 [+0.079, +0.160] | +0.118 [+0.078, +0.159] | 240/30 | 240/30 | 1.000 | 1.000 | 60601:mathstral/always; 60602:mathstral/always; 60603:mathstral/always |
| 25 | 1776 | 0.237 | +0.118 [+0.078, +0.159] | +0.118 [+0.078, +0.160] | 240/30 | 240/30 | 1.000 | 1.000 | 60601:mathstral/always; 60602:mathstral/always; 60603:mathstral/always |
| 30 | 1776 | 0.237 | +0.118 [+0.080, +0.159] | +0.118 [+0.079, +0.160] | 240/30 | 240/30 | 1.000 | 1.000 | 60601:mathstral/always; 60602:mathstral/always; 60603:mathstral/always |
| 40 | 1776 | 0.237 | +0.118 [+0.079, +0.160] | +0.118 [+0.078, +0.160] | 240/30 | 240/30 | 1.000 | 1.000 | 60601:mathstral/always; 60602:mathstral/always; 60603:mathstral/always |
| 60 | 1776 | 0.237 | +0.118 [+0.079, +0.158] | +0.118 [+0.077, +0.160] | 240/30 | 240/30 | 1.000 | 1.000 | 60601:mathstral/always; 60602:mathstral/always; 60603:mathstral/always |
| 100 | 1776 | 0.237 | +0.118 [+0.079, +0.158] | +0.118 [+0.078, +0.159] | 240/30 | 240/30 | 1.000 | 1.000 | 60601:mathstral/always; 60602:mathstral/always; 60603:mathstral/always |

## Read

The accepted-action v121 table is a stress test of whether local LLM judges can identify good router actions once the router proposes one. This natural-rate table is the deployable interpretation: it charges the judge against every held-out trial, including trials where the router never proposes a switch.

Per-fold CSV: [pairwise_router_judge_budget_curve_v127.csv](pairwise_router_judge_budget_curve_v127.csv). Aggregate CSV: [pairwise_router_judge_budget_curve_v127_aggregate.csv](pairwise_router_judge_budget_curve_v127_aggregate.csv). Trial details: [pairwise_router_judge_budget_curve_v127_details.csv](pairwise_router_judge_budget_curve_v127_details.csv).