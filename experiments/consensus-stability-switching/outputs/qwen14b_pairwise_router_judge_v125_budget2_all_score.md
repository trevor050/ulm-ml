# Pairwise Router Judge Score

Predictions: `outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl`.

## Category Accuracy

| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| both_correct | 36 | 0.667 | 2 | 5 | 24 | 5 | 0 |
| neither_correct | 213 | 0.385 | 30 | 99 | 2 | 82 | 0 |
| recovery | 240 | 0.750 | 32 | 180 | 0 | 28 | 0 |
| regression | 30 | 0.433 | 13 | 4 | 1 | 12 | 0 |

## Confidence-Gated Candidate Acceptance

| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 519 | 0.576 | 0.127 | 0.464 | +0.337 | 315 | 180 | 5 |
| 0.50 | 519 | 0.576 | 0.127 | 0.464 | +0.337 | 315 | 180 | 5 |
| 0.70 | 519 | 0.576 | 0.127 | 0.464 | +0.337 | 315 | 180 | 5 |
| 0.90 | 519 | 0.576 | 0.127 | 0.464 | +0.337 | 315 | 180 | 5 |

Details: `outputs/qwen14b_pairwise_router_judge_v125_budget2_all_score.csv`. Categories: `outputs/qwen14b_pairwise_router_judge_v125_budget2_all_score_categories.csv`. Thresholds: `outputs/qwen14b_pairwise_router_judge_v125_budget2_all_score_thresholds.csv`.