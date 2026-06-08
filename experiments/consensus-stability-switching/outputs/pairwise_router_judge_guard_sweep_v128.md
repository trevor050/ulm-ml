# Pairwise Router-Judge Guard Sweep

This audit stress-tests the v125/v126 higher-budget pairwise result with simple deployable guards. The guard sees only pairwise judge choices and the router policy name; it does not see correctness labels on the held-out fold.

Answer rows: `outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl`. Manifest: `outputs/pairwise_router_judge_v125_budget2_all_manifest.csv`.

## Source-Selected Guard

| pairwise budget | guard budget | delta | CI | rec/reg | accepts | selected |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 0 | +0.066 | [+0.040, +0.095] | 119/2 | 183 | 60601:mathstral/B_or_BOTH/no_union; 60602:gemma4/B/none; 60603:qwen14b/B/none |
| 1 | 1 | +0.083 | [+0.054, +0.115] | 150/2 | 237 | 60601:mathstral/B_or_BOTH/none; 60602:gemma4/B/none; 60603:qwen14b/B/none |
| 1 | 2 | +0.083 | [+0.054, +0.115] | 150/2 | 237 | 60601:mathstral/B_or_BOTH/none; 60602:gemma4/B/none; 60603:qwen14b/B/none |
| 2 | 0 | +0.068 | [+0.042, +0.097] | 123/2 | 203 | 60601:qwen14b/B/no_qwen_union; 60602:qwen14b/B/other_candidate; 60603:qwen14b/B/none |
| 2 | 1 | +0.086 | [+0.057, +0.119] | 155/2 | 248 | 60601:qwen14b/B/other_candidate; 60602:qwen14b/B/other_candidate; 60603:qwen14b/B/none |
| 2 | 2 | +0.099 | [+0.067, +0.133] | 180/4 | 288 | 60601:qwen14b/B/none; 60602:qwen14b/B/none; 60603:qwen14b/B/none |

## Fixed Guards

| pairwise budget | guard | delta | CI | rec/reg | accepts | selected |
|---:|---|---:|---:|---:|---:|---|
| 1 | `no_qwen_union` | +0.050 | [+0.028, +0.075] | 88/0 | 136 | 60601:mathstral/B_or_BOTH/no_qwen_union; 60602:gemma4/B/no_qwen_union; 60603:qwen14b/B/no_qwen_union |
| 1 | `no_union` | +0.019 | [+0.008, +0.034] | 34/0 | 58 | 60601:mathstral/B_or_BOTH/no_union; 60602:gemma4/B/no_union; 60603:qwen14b/B/no_union |
| 1 | `none` | +0.083 | [+0.055, +0.115] | 150/2 | 237 | 60601:mathstral/B_or_BOTH/none; 60602:gemma4/B/none; 60603:qwen14b/B/none |
| 1 | `qwen_union_other_candidate` | +0.079 | [+0.051, +0.110] | 142/1 | 208 | 60601:mathstral/B_or_BOTH/qwen_union_other_candidate; 60602:gemma4/B/qwen_union_other_candidate; 60603:qwen14b/B/qwen_union_other_candidate |
| 1 | `two_b` | +0.074 | [+0.047, +0.104] | 133/1 | 184 | 60601:mathstral/B_or_BOTH/two_b; 60602:gemma4/B/two_b; 60603:qwen14b/B/two_b |
| 2 | `no_qwen_union` | +0.022 | [+0.010, +0.037] | 39/0 | 77 | 60601:qwen14b/B/no_qwen_union; 60602:qwen14b/B/no_qwen_union; 60603:qwen14b/B/no_qwen_union |
| 2 | `no_union` | +0.022 | [+0.009, +0.038] | 39/0 | 77 | 60601:qwen14b/B/no_union; 60602:qwen14b/B/no_union; 60603:qwen14b/B/no_union |
| 2 | `none` | +0.099 | [+0.068, +0.133] | 180/4 | 288 | 60601:qwen14b/B/none; 60602:qwen14b/B/none; 60603:qwen14b/B/none |
| 2 | `qwen_union_other_candidate` | +0.083 | [+0.055, +0.115] | 149/1 | 223 | 60601:qwen14b/B/qwen_union_other_candidate; 60602:qwen14b/B/qwen_union_other_candidate; 60603:qwen14b/B/qwen_union_other_candidate |
| 2 | `two_b` | +0.082 | [+0.053, +0.115] | 147/1 | 213 | 60601:qwen14b/B/two_b; 60602:qwen14b/B/two_b; 60603:qwen14b/B/two_b |

## Read

`none` is the original v125 pairwise gate. `qwen_union_other_candidate` keeps qwen decisions except it requires another judge to also accept the candidate when the action is the riskier `union_rank_top3` policy. This is the cleanest non-oracle guard because v126 localized every budget-2 regression to qwen `B` on `union_rank_top3`.

Aggregate CSV: `pairwise_router_judge_guard_sweep_v128_aggregate.csv`. Per-fold CSV: `pairwise_router_judge_guard_sweep_v128.csv`. Trial details: `pairwise_router_judge_guard_sweep_v128_details.csv`.