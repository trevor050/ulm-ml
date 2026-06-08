# Pairwise Router Judge Score

Predictions: `outputs/gemma4_pairwise_router_rich_probe_v130_predictions.jsonl`.

## Category Accuracy

| category | rows | choice acc | A | B | BOTH | NEITHER | invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| neither_correct | 10 | 0.000 | 0 | 0 | 0 | 0 | 10 |
| recovery | 4 | 0.000 | 0 | 0 | 0 | 0 | 4 |
| regression | 10 | 0.000 | 0 | 0 | 0 | 0 | 10 |

## Confidence-Gated Candidate Acceptance

| threshold | rows | choice acc | baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 24 | 0.000 | 0.417 | 0.417 | +0.000 | 0 | 0 | 0 |
| 0.50 | 24 | 0.000 | 0.417 | 0.417 | +0.000 | 0 | 0 | 0 |
| 0.70 | 24 | 0.000 | 0.417 | 0.417 | +0.000 | 0 | 0 | 0 |
| 0.90 | 24 | 0.000 | 0.417 | 0.417 | +0.000 | 0 | 0 | 0 |

Details: `outputs/gemma4_pairwise_router_rich_probe_v130_score.csv`. Categories: `outputs/gemma4_pairwise_router_rich_probe_v130_score_categories.csv`. Thresholds: `outputs/gemma4_pairwise_router_rich_probe_v130_score_thresholds.csv`.