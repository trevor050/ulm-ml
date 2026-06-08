# Pairwise Router Judge Score

Predictions: `outputs/mathstral_pairwise_router_rich_probe_v130_predictions.jsonl`.

## Category Accuracy

| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| neither_correct | 10 | 1.000 | 0 | 0 | 0 | 10 | 0 |
| recovery | 4 | 0.000 | 0 | 0 | 0 | 4 | 0 |
| regression | 10 | 0.000 | 0 | 2 | 2 | 6 | 0 |

## Confidence-Gated Candidate Acceptance

| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 24 | 0.417 | 0.417 | 0.250 | -0.167 | 4 | 0 | 4 |
| 0.50 | 24 | 0.417 | 0.417 | 0.250 | -0.167 | 4 | 0 | 4 |
| 0.70 | 24 | 0.417 | 0.417 | 0.250 | -0.167 | 4 | 0 | 4 |
| 0.90 | 24 | 0.417 | 0.417 | 0.250 | -0.167 | 4 | 0 | 4 |

Details: `outputs/mathstral_pairwise_router_rich_probe_v130_score.csv`. Categories: `outputs/mathstral_pairwise_router_rich_probe_v130_score_categories.csv`. Thresholds: `outputs/mathstral_pairwise_router_rich_probe_v130_score_thresholds.csv`.