# Pairwise Router Judge Score

Predictions: `outputs/mathstral_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl`.

## Category Accuracy

| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| neither_correct | 9 | 0.778 | 1 | 1 | 0 | 7 | 0 |
| recovery | 1 | 0.000 | 1 | 0 | 0 | 0 | 0 |
| regression | 5 | 0.800 | 4 | 0 | 0 | 1 | 0 |

## Confidence-Gated Candidate Acceptance

| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 15 | 0.733 | 0.333 | 0.333 | +0.000 | 1 | 0 | 0 |
| 0.50 | 15 | 0.733 | 0.333 | 0.333 | +0.000 | 1 | 0 | 0 |
| 0.70 | 15 | 0.733 | 0.333 | 0.333 | +0.000 | 1 | 0 | 0 |
| 0.90 | 15 | 0.733 | 0.333 | 0.333 | +0.000 | 1 | 0 | 0 |

Details: `outputs/mathstral_pairwise_router_judge_v123_llama_with_gemma_budget0_all_score.csv`. Categories: `outputs/mathstral_pairwise_router_judge_v123_llama_with_gemma_budget0_all_score_categories.csv`. Thresholds: `outputs/mathstral_pairwise_router_judge_v123_llama_with_gemma_budget0_all_score_thresholds.csv`.