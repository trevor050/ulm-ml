# Pairwise Router-Judge Natural-Rate Scoring

This natural-rate audit takes the full held-out trial denominator. The raw router first chooses an auxiliary-generator action exactly as in v120/v123. The pairwise judge then either accepts that action or falls back to the baseline selector. Source rule selection excludes every problem id in the held-out seed, including problems where the raw router proposes no switch.

Router score: `base_utility`. Router source regression budget: `0`. Pairwise rules: `never,B,B_or_BOTH`.

| pairwise source budget | trials | baseline | raw router delta | pairwise delta | raw rec/reg | pairwise rec/reg | rec kept | reg kept | selected |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | 1776 | 0.237 | +0.097 [+0.061, +0.134] | +0.067 [+0.040, +0.096] | 192/20 | 120/1 | 0.625 | 0.050 | 60601:qwen14b/B; 60602:gemma4/B; 60603:gemma4/B |
| 1 | 1776 | 0.237 | +0.097 [+0.062, +0.136] | +0.067 [+0.041, +0.097] | 192/20 | 120/1 | 0.625 | 0.050 | 60601:qwen14b/B; 60602:gemma4/B; 60603:gemma4/B |
| 2 | 1776 | 0.237 | +0.097 [+0.061, +0.135] | +0.065 [+0.039, +0.094] | 192/20 | 117/1 | 0.609 | 0.050 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:gemma4/B |
| 5 | 1776 | 0.237 | +0.097 [+0.061, +0.133] | +0.065 [+0.039, +0.094] | 192/20 | 117/1 | 0.609 | 0.050 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:gemma4/B |

## Read

The accepted-action v121 table is a stress test of whether local LLM judges can identify good router actions once the router proposes one. This natural-rate table is the deployable interpretation: it charges the judge against every held-out trial, including trials where the router never proposes a switch.

Per-fold CSV: [pairwise_router_judge_natural_rate_v122.csv](pairwise_router_judge_natural_rate_v122.csv). Aggregate CSV: [pairwise_router_judge_natural_rate_v122_aggregate.csv](pairwise_router_judge_natural_rate_v122_aggregate.csv). Trial details: [pairwise_router_judge_natural_rate_v122_details.csv](pairwise_router_judge_natural_rate_v122_details.csv).