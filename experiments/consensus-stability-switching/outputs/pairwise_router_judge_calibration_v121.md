# Pairwise Router-Judge Held-Out Calibration

This v121 audit selects a pairwise judge model/rule on source accepted rows and evaluates on the held-out seed's accepted rows. Source rows also exclude held-out problem ids.

| budget | mean delta | min/max | signs | accepts | recoveries | regressions | selected rules |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | +0.368 | +0.239/+0.462 | 3/3 | 151 | 120 | 1 | 60601:qwen14b/B; 60602:gemma4/B; 60603:gemma4/B |
| 1 | +0.368 | +0.239/+0.462 | 3/3 | 151 | 120 | 1 | 60601:qwen14b/B; 60602:gemma4/B; 60603:gemma4/B |
| 2 | +0.349 | +0.239/+0.462 | 3/3 | 154 | 117 | 1 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:gemma4/B |
| 5 | +0.349 | +0.239/+0.462 | 3/3 | 154 | 117 | 1 | 60601:qwen14b/B; 60602:qwen14b/B; 60603:gemma4/B |

Per-fold CSV: [pairwise_router_judge_calibration_v121.csv](pairwise_router_judge_calibration_v121.csv). Aggregate CSV: [pairwise_router_judge_calibration_v121_aggregate.csv](pairwise_router_judge_calibration_v121_aggregate.csv).