# Pairwise Router-Judge Natural-Rate Scoring

This natural-rate audit takes the full held-out trial denominator. The raw router first chooses an auxiliary-generator action exactly as in v120/v123. The pairwise judge then either accepts that action or falls back to the baseline selector. Source rule selection excludes every problem id in the held-out seed, including problems where the raw router proposes no switch.

Router score: `base_utility`. Router source regression budget: `0`. Pairwise rules: `never,B,B_or_BOTH`.

| pairwise source budget | trials | baseline | raw router delta | pairwise delta | raw rec/reg | pairwise rec/reg | rec kept | reg kept | selected |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | 1776 | 0.445 | -0.002 [-0.006, +0.001] | +0.000 [+0.000, +0.000] | 1/5 | 0/0 | 0.000 | 0.000 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |
| 1 | 1776 | 0.445 | -0.002 [-0.006, +0.001] | +0.000 [+0.000, +0.000] | 1/5 | 0/0 | 0.000 | 0.000 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |
| 2 | 1776 | 0.445 | -0.002 [-0.006, +0.001] | +0.000 [+0.000, +0.000] | 1/5 | 0/0 | 0.000 | 0.000 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |
| 5 | 1776 | 0.445 | -0.002 [-0.006, +0.001] | +0.000 [+0.000, +0.000] | 1/5 | 0/0 | 0.000 | 0.000 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |

## Read

The accepted-action v121 table is a stress test of whether local LLM judges can identify good router actions once the router proposes one. This natural-rate table is the deployable interpretation: it charges the judge against every held-out trial, including trials where the router never proposes a switch.

Per-fold CSV: [pairwise_router_judge_natural_rate_v123_llama_with_gemma.csv](pairwise_router_judge_natural_rate_v123_llama_with_gemma.csv). Aggregate CSV: [pairwise_router_judge_natural_rate_v123_llama_with_gemma_aggregate.csv](pairwise_router_judge_natural_rate_v123_llama_with_gemma_aggregate.csv). Trial details: [pairwise_router_judge_natural_rate_v123_llama_with_gemma_details.csv](pairwise_router_judge_natural_rate_v123_llama_with_gemma_details.csv).