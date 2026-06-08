# Pairwise Router Judge Score

Predictions: `outputs/qwen14b_pairwise_router_judge_v119_predictions.jsonl`.

## Category Accuracy

| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| both_correct | 17 | 0.471 | 2 | 3 | 8 | 4 | 0 |
| neither_correct | 20 | 0.450 | 2 | 9 | 0 | 9 | 0 |
| recovery | 20 | 0.700 | 2 | 14 | 1 | 3 | 0 |
| regression | 20 | 0.300 | 6 | 3 | 0 | 11 | 0 |

## Confidence-Gated Candidate Acceptance

| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 77 | 0.481 | 0.481 | 0.636 | +0.156 | 38 | 15 | 3 |
| 0.50 | 77 | 0.481 | 0.481 | 0.636 | +0.156 | 38 | 15 | 3 |
| 0.70 | 77 | 0.481 | 0.481 | 0.636 | +0.156 | 38 | 15 | 3 |
| 0.90 | 77 | 0.481 | 0.481 | 0.636 | +0.156 | 38 | 15 | 3 |

Details: `outputs/qwen14b_pairwise_router_judge_v119_score.csv`. Categories: `outputs/qwen14b_pairwise_router_judge_v119_score_categories.csv`. Thresholds: `outputs/qwen14b_pairwise_router_judge_v119_score_thresholds.csv`.