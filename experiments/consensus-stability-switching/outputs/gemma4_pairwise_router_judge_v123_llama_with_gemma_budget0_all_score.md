# Pairwise Router Judge Score

Predictions: `outputs/gemma4_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl`.

## Category Accuracy

| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| neither_correct | 9 | 0.333 | 0 | 1 | 0 | 3 | 5 |
| recovery | 1 | 0.000 | 0 | 0 | 0 | 0 | 1 |
| regression | 5 | 0.400 | 2 | 0 | 0 | 0 | 3 |

## Confidence-Gated Candidate Acceptance

| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 15 | 0.333 | 0.333 | 0.333 | +0.000 | 1 | 0 | 0 |
| 0.50 | 15 | 0.333 | 0.333 | 0.333 | +0.000 | 1 | 0 | 0 |
| 0.70 | 15 | 0.333 | 0.333 | 0.333 | +0.000 | 1 | 0 | 0 |
| 0.90 | 15 | 0.333 | 0.333 | 0.333 | +0.000 | 1 | 0 | 0 |

Details: `outputs/gemma4_pairwise_router_judge_v123_llama_with_gemma_budget0_all_score.csv`. Categories: `outputs/gemma4_pairwise_router_judge_v123_llama_with_gemma_budget0_all_score_categories.csv`. Thresholds: `outputs/gemma4_pairwise_router_judge_v123_llama_with_gemma_budget0_all_score_thresholds.csv`.