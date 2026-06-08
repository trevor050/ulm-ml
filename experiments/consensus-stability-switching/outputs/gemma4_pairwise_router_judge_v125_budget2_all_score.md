# Pairwise Router Judge Score

Predictions: `outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl`.

## Category Accuracy

| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| both_correct | 36 | 0.667 | 1 | 7 | 24 | 0 | 4 |
| neither_correct | 213 | 0.291 | 6 | 28 | 0 | 62 | 117 |
| recovery | 240 | 0.554 | 22 | 133 | 0 | 23 | 62 |
| regression | 30 | 0.767 | 23 | 2 | 0 | 1 | 4 |

## Confidence-Gated Candidate Acceptance

| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 519 | 0.466 | 0.127 | 0.380 | +0.252 | 194 | 133 | 2 |
| 0.50 | 519 | 0.466 | 0.127 | 0.380 | +0.252 | 194 | 133 | 2 |
| 0.70 | 519 | 0.466 | 0.127 | 0.380 | +0.252 | 194 | 133 | 2 |
| 0.90 | 519 | 0.466 | 0.127 | 0.380 | +0.252 | 194 | 133 | 2 |

Details: `outputs/gemma4_pairwise_router_judge_v125_budget2_all_score.csv`. Categories: `outputs/gemma4_pairwise_router_judge_v125_budget2_all_score_categories.csv`. Thresholds: `outputs/gemma4_pairwise_router_judge_v125_budget2_all_score_thresholds.csv`.