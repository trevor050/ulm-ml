# Pairwise Router Judge Score

Predictions: `outputs/gemma4_pairwise_router_judge_v120_budget0_all_predictions.jsonl`.

## Category Accuracy

| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| both_correct | 33 | 0.727 | 1 | 6 | 24 | 0 | 2 |
| neither_correct | 132 | 0.303 | 1 | 19 | 0 | 40 | 72 |
| recovery | 192 | 0.578 | 19 | 111 | 0 | 19 | 43 |
| regression | 20 | 0.800 | 16 | 0 | 0 | 1 | 3 |

## Confidence-Gated Candidate Acceptance

| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 377 | 0.507 | 0.141 | 0.435 | +0.294 | 160 | 111 | 0 |
| 0.50 | 377 | 0.507 | 0.141 | 0.435 | +0.294 | 160 | 111 | 0 |
| 0.70 | 377 | 0.507 | 0.141 | 0.435 | +0.294 | 160 | 111 | 0 |
| 0.90 | 377 | 0.507 | 0.141 | 0.435 | +0.294 | 160 | 111 | 0 |

Details: `outputs/gemma4_pairwise_router_judge_v120_budget0_all_score.csv`. Categories: `outputs/gemma4_pairwise_router_judge_v120_budget0_all_score_categories.csv`. Thresholds: `outputs/gemma4_pairwise_router_judge_v120_budget0_all_score_thresholds.csv`.