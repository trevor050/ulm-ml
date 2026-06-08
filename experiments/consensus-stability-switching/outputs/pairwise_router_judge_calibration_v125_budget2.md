# Pairwise Router-Judge Held-Out Calibration

This v121 audit selects a pairwise judge model/rule on source accepted rows and evaluates on the held-out seed's accepted rows. Source rows also exclude held-out problem ids.

| budget | mean delta | min/max | signs | accepts | recoveries | regressions | selected rules |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | +0.094 | +0.000/+0.281 | 1/3 | 137 | 77 | 2 | 60601:mathstral/never; 60602:mathstral/never; 60603:qwen14b/B |
| 1 | +0.242 | +0.155/+0.290 | 3/3 | 241 | 137 | 2 | 60601:mathstral/B_or_BOTH; 60602:mathstral/B; 60603:qwen14b/B |
| 2 | +0.325 | +0.281/+0.406 | 3/3 | 264 | 169 | 3 | 60601:qwen14b/B; 60602:gemma4/B; 60603:qwen14b/B |
| 5 | +0.360 | +0.281/+0.406 | 3/3 | 288 | 180 | 4 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:qwen14b/B |

Per-fold CSV: [pairwise_router_judge_calibration_v125_budget2.csv](pairwise_router_judge_calibration_v125_budget2.csv). Aggregate CSV: [pairwise_router_judge_calibration_v125_budget2_aggregate.csv](pairwise_router_judge_calibration_v125_budget2_aggregate.csv).