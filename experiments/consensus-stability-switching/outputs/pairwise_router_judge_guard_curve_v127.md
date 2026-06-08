# Pairwise Router-Judge Natural-Rate Scoring

This natural-rate audit takes the full held-out trial denominator. The raw router first chooses an auxiliary-generator action exactly as in v120/v123. The pairwise judge then either accepts that action or falls back to the baseline selector. Source rule selection excludes every problem id in the held-out seed, including problems where the raw router proposes no switch.

Router score: `base_utility`. Router source regression budget: `2`. Pairwise rules: `never,B,B_or_BOTH`.

| pairwise source budget | trials | baseline | raw router delta | pairwise delta | raw rec/reg | pairwise rec/reg | rec kept | reg kept | selected |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | 1776 | 0.237 | +0.118 [+0.078, +0.159] | +0.058 [+0.033, +0.087] | 240/30 | 105/2 | 0.438 | 0.067 | 60601:mathstral/never; 60602:gemma4/B; 60603:qwen14b/B |
| 1 | 1776 | 0.237 | +0.118 [+0.080, +0.159] | +0.083 [+0.055, +0.115] | 240/30 | 150/2 | 0.625 | 0.067 | 60601:mathstral/B_or_BOTH; 60602:gemma4/B; 60603:qwen14b/B |
| 2 | 1776 | 0.237 | +0.118 [+0.079, +0.159] | +0.099 [+0.067, +0.133] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |
| 3 | 1776 | 0.237 | +0.118 [+0.078, +0.160] | +0.099 [+0.068, +0.134] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |
| 4 | 1776 | 0.237 | +0.118 [+0.079, +0.159] | +0.099 [+0.068, +0.134] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |
| 5 | 1776 | 0.237 | +0.118 [+0.079, +0.158] | +0.099 [+0.068, +0.133] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |
| 6 | 1776 | 0.237 | +0.118 [+0.079, +0.159] | +0.099 [+0.068, +0.133] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |
| 8 | 1776 | 0.237 | +0.118 [+0.079, +0.160] | +0.099 [+0.067, +0.134] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |
| 10 | 1776 | 0.237 | +0.118 [+0.079, +0.160] | +0.099 [+0.068, +0.133] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |
| 12 | 1776 | 0.237 | +0.118 [+0.079, +0.160] | +0.099 [+0.068, +0.133] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |
| 15 | 1776 | 0.237 | +0.118 [+0.079, +0.160] | +0.099 [+0.067, +0.134] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |
| 20 | 1776 | 0.237 | +0.118 [+0.079, +0.160] | +0.099 [+0.069, +0.134] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |
| 25 | 1776 | 0.237 | +0.118 [+0.078, +0.159] | +0.099 [+0.068, +0.135] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |
| 30 | 1776 | 0.237 | +0.118 [+0.080, +0.159] | +0.099 [+0.068, +0.135] | 240/30 | 180/4 | 0.750 | 0.133 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |

## Read

The accepted-action v121 table is a stress test of whether local LLM judges can identify good router actions once the router proposes one. This natural-rate table is the deployable interpretation: it charges the judge against every held-out trial, including trials where the router never proposes a switch.

Per-fold CSV: [pairwise_router_judge_guard_curve_v127.csv](pairwise_router_judge_guard_curve_v127.csv). Aggregate CSV: [pairwise_router_judge_guard_curve_v127_aggregate.csv](pairwise_router_judge_guard_curve_v127_aggregate.csv). Trial details: [pairwise_router_judge_guard_curve_v127_details.csv](pairwise_router_judge_guard_curve_v127_details.csv).