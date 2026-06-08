# Pairwise Router Judge Score

Predictions: `outputs/gemma4_pairwise_router_judge_v119_predictions.jsonl`.

## Category Accuracy

| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| both_correct | 17 | 0.471 | 1 | 6 | 8 | 0 | 2 |
| neither_correct | 20 | 0.300 | 0 | 4 | 0 | 6 | 10 |
| recovery | 20 | 0.500 | 2 | 10 | 0 | 2 | 6 |
| regression | 20 | 0.750 | 15 | 0 | 0 | 3 | 2 |

## Confidence-Gated Candidate Acceptance

| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 77 | 0.506 | 0.481 | 0.610 | +0.130 | 28 | 10 | 0 |
| 0.50 | 77 | 0.506 | 0.481 | 0.610 | +0.130 | 28 | 10 | 0 |
| 0.70 | 77 | 0.506 | 0.481 | 0.610 | +0.130 | 28 | 10 | 0 |
| 0.90 | 77 | 0.506 | 0.481 | 0.610 | +0.130 | 28 | 10 | 0 |

Details: `outputs/gemma4_pairwise_router_judge_v119_score.csv`. Categories: `outputs/gemma4_pairwise_router_judge_v119_score_categories.csv`. Thresholds: `outputs/gemma4_pairwise_router_judge_v119_score_thresholds.csv`.