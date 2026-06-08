# Pairwise Router-Judge Held-Out Calibration

This v121 audit selects a pairwise judge model/rule on source accepted rows and evaluates on the held-out seed's accepted rows. Source rows also exclude held-out problem ids.

| budget | mean delta | min/max | signs | accepts | recoveries | regressions | selected rules |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | +0.000 | +0.000/+0.000 | 0/3 | 0 | 0 | 0 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |
| 1 | +0.000 | +0.000/+0.000 | 0/3 | 0 | 0 | 0 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |
| 2 | +0.000 | +0.000/+0.000 | 0/3 | 0 | 0 | 0 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |
| 5 | +0.000 | +0.000/+0.000 | 0/3 | 0 | 0 | 0 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |
| 10 | +0.000 | +0.000/+0.000 | 0/3 | 0 | 0 | 0 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |
| 20 | +0.000 | +0.000/+0.000 | 0/3 | 0 | 0 | 0 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |
| 40 | +0.000 | +0.000/+0.000 | 0/3 | 0 | 0 | 0 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |
| 80 | +0.000 | +0.000/+0.000 | 0/3 | 0 | 0 | 0 | 60601:mathstral/never; 60602:mathstral/never; 60603:mathstral/never |

Per-fold CSV: [pairwise_router_judge_calibration_v127.csv](pairwise_router_judge_calibration_v127.csv). Aggregate CSV: [pairwise_router_judge_calibration_v127_aggregate.csv](pairwise_router_judge_calibration_v127_aggregate.csv).