# Pairwise Router Judge Score

Predictions: `outputs/mathstral_pairwise_router_judge_v120_budget0_all_predictions.jsonl`.

## Category Accuracy

| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| both_correct | 33 | 0.000 | 4 | 28 | 0 | 1 | 0 |
| neither_correct | 132 | 0.530 | 24 | 38 | 0 | 70 | 0 |
| recovery | 192 | 0.474 | 53 | 91 | 14 | 34 | 0 |
| regression | 20 | 0.450 | 9 | 0 | 0 | 11 | 0 |

## Confidence-Gated Candidate Acceptance

| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 377 | 0.451 | 0.141 | 0.419 | +0.279 | 171 | 105 | 0 |
| 0.50 | 377 | 0.451 | 0.141 | 0.419 | +0.279 | 171 | 105 | 0 |
| 0.70 | 377 | 0.451 | 0.141 | 0.419 | +0.279 | 171 | 105 | 0 |
| 0.90 | 377 | 0.451 | 0.141 | 0.419 | +0.279 | 171 | 105 | 0 |

Details: `outputs/mathstral_pairwise_router_judge_v120_budget0_all_score.csv`. Categories: `outputs/mathstral_pairwise_router_judge_v120_budget0_all_score_categories.csv`. Thresholds: `outputs/mathstral_pairwise_router_judge_v120_budget0_all_score_thresholds.csv`.