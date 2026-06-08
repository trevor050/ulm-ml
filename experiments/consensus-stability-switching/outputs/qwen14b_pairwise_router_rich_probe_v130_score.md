# Pairwise Router Judge Score

Predictions: `outputs/qwen14b_pairwise_router_rich_probe_v130_predictions.jsonl`.

## Category Accuracy

| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| neither_correct | 10 | 0.000 | 10 | 0 | 0 | 0 | 0 |
| recovery | 4 | 1.000 | 0 | 4 | 0 | 0 | 0 |
| regression | 10 | 0.400 | 4 | 5 | 1 | 0 | 0 |

## Confidence-Gated Candidate Acceptance

| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 24 | 0.333 | 0.417 | 0.333 | -0.083 | 10 | 4 | 6 |
| 0.50 | 24 | 0.333 | 0.417 | 0.333 | -0.083 | 10 | 4 | 6 |
| 0.70 | 24 | 0.333 | 0.417 | 0.333 | -0.083 | 10 | 4 | 6 |
| 0.90 | 24 | 0.333 | 0.417 | 0.333 | -0.083 | 10 | 4 | 6 |

Details: `outputs/qwen14b_pairwise_router_rich_probe_v130_score.csv`. Categories: `outputs/qwen14b_pairwise_router_rich_probe_v130_score_categories.csv`. Thresholds: `outputs/qwen14b_pairwise_router_rich_probe_v130_score_thresholds.csv`.