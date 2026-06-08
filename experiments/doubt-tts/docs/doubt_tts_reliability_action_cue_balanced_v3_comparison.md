# Reliability-Action Cue-Balanced v3 Comparison

Status: comparison of cheap shortcut baselines and completed remote-Ollama model runs on the 300-row opaque-ID v3 candidate.

- baseline scored rows: `work/probe/runs/reliability_action_cue_balanced_candidate_v3_baseline_scored_results.jsonl`
- Qwen scored rows: `work/probe/runs/reliability_action_cue_balanced_v3_qwen_action_discriminating_scored_results.jsonl`
- Qwen overlap scored rows: `work/probe/runs/reliability_action_cue_balanced_v3_qwen_overlap_guard_scored_results.jsonl`
- Gemma scored rows: `work/probe/runs/reliability_action_cue_balanced_v3_gemma4_26b_action_discriminating_scored_results.jsonl`
- Gemma overlap scored rows: `work/probe/runs/reliability_action_cue_balanced_v3_gemma4_26b_overlap_guard_scored_results.jsonl`
- machine-readable comparison: `work/probe/runs/reliability_action_cue_balanced_v3_comparison.json`

## Overall

| method | joint | validity | compute |
|---|---:|---:|---:|
| `oracle_template_family_majority` | 60/300 (0.200) | 60/300 (0.200) | 60/300 (0.200) |
| `legacy_keyword_question_only_router` | 87/300 (0.290) | 150/300 (0.500) | 87/300 (0.290) |
| `qwen3.5:9b:action_discriminating` | 167/300 (0.557) | 226/300 (0.753) | 178/300 (0.593) |
| `qwen3.5:9b:overlap_guard` | 192/300 (0.640) | 236/300 (0.787) | 206/300 (0.687) |
| `gemma4:26b:action_discriminating` | 201/300 (0.670) | 246/300 (0.820) | 214/300 (0.713) |
| `gemma4:26b:overlap_guard` | 232/300 (0.773) | 254/300 (0.847) | 237/300 (0.790) |

## Joint Accuracy By Expected Compute Action

| method | direct | premise | retrieve-answer | retrieve-premise | verify | clarify |
|---|---:|---:|---:|---:|---:|---:|
| `legacy_keyword_question_only_router` | 30/45 (0.667) | 6/45 (0.133) | 27/45 (0.600) | 12/60 (0.200) | 0/45 (0.000) | 12/60 (0.200) |
| `qwen3.5:9b:action_discriminating` | 45/45 (1.000) | 41/45 (0.911) | 10/45 (0.222) | 0/60 (0.000) | 11/45 (0.244) | 60/60 (1.000) |
| `qwen3.5:9b:overlap_guard` | 41/45 (0.911) | 36/45 (0.800) | 22/45 (0.489) | 11/60 (0.183) | 23/45 (0.511) | 59/60 (0.983) |
| `gemma4:26b:action_discriminating` | 45/45 (1.000) | 45/45 (1.000) | 22/45 (0.489) | 6/60 (0.100) | 23/45 (0.511) | 60/60 (1.000) |
| `gemma4:26b:overlap_guard` | 27/45 (0.600) | 44/45 (0.978) | 34/45 (0.756) | 47/60 (0.783) | 20/45 (0.444) | 60/60 (1.000) |

## Compute-Action Accuracy By Expected Compute Action

| method | direct | premise | retrieve-answer | retrieve-premise | verify | clarify |
|---|---:|---:|---:|---:|---:|---:|
| `legacy_keyword_question_only_router` | 30/45 (0.667) | 6/45 (0.133) | 27/45 (0.600) | 12/60 (0.200) | 0/45 (0.000) | 12/60 (0.200) |
| `qwen3.5:9b:action_discriminating` | 45/45 (1.000) | 41/45 (0.911) | 10/45 (0.222) | 11/60 (0.183) | 11/45 (0.244) | 60/60 (1.000) |
| `qwen3.5:9b:overlap_guard` | 41/45 (0.911) | 36/45 (0.800) | 22/45 (0.489) | 25/60 (0.417) | 23/45 (0.511) | 59/60 (0.983) |
| `gemma4:26b:action_discriminating` | 45/45 (1.000) | 45/45 (1.000) | 22/45 (0.489) | 19/60 (0.317) | 23/45 (0.511) | 60/60 (1.000) |
| `gemma4:26b:overlap_guard` | 27/45 (0.600) | 44/45 (0.978) | 34/45 (0.756) | 52/60 (0.867) | 20/45 (0.444) | 60/60 (1.000) |

## Qwen Overlap-Guard Minus Qwen Action-Discriminating

| branch | joint delta | compute delta |
|---|---:|---:|
| direct | -4/45 | -4/45 |
| premise | -5/45 | -5/45 |
| retrieve-answer | +12/45 | +12/45 |
| retrieve-premise | +11/60 | +14/60 |
| verify | +12/45 | +12/45 |
| clarify | -1/60 | -1/60 |

## Gemma Overlap-Guard Minus Gemma Action-Discriminating

| branch | joint delta | compute delta |
|---|---:|---:|
| direct | -18/45 | -18/45 |
| premise | -1/45 | -1/45 |
| retrieve-answer | +12/45 | +12/45 |
| retrieve-premise | +41/60 | +33/60 |
| verify | -3/45 | -3/45 |
| clarify | +0/60 | +0/60 |

## Paired Exact Tests

| comparison | metric | A only | B only | net A-B | exact p |
|---|---|---:|---:|---:|---:|
| Qwen vs keyword | joint | 118 | 38 | 80 | 9.739e-11 |
| Qwen overlap vs keyword | joint | 135 | 30 | 105 | 4.157e-17 |
| Qwen overlap vs Qwen action | joint | 40 | 15 | 25 | 0.001016 |
| Qwen overlap vs Qwen action | compute | 46 | 18 | 28 | 0.0006174 |
| Qwen overlap vs Qwen action | validity | 13 | 3 | 10 | 0.02127 |
| Gemma vs keyword | joint | 137 | 23 | 114 | 5.963e-21 |
| Gemma overlap vs keyword | joint | 163 | 18 | 145 | 2.075e-30 |
| Gemma overlap vs Gemma action | joint | 56 | 25 | 31 | 0.0007521 |
| Gemma overlap vs Gemma action | compute | 48 | 25 | 23 | 0.009542 |
| Gemma overlap vs Gemma action | validity | 18 | 10 | 8 | 0.1849 |
| Gemma vs Qwen | joint | 38 | 4 | 34 | 5.653e-08 |
| Gemma vs Qwen | compute | 42 | 6 | 36 | 1.009e-07 |
| Gemma vs Qwen | validity | 40 | 20 | 20 | 0.01349 |
| Gemma overlap vs Qwen overlap | joint | 60 | 20 | 40 | 8.581e-06 |
| Gemma overlap vs Qwen overlap | compute | 53 | 22 | 31 | 0.0004496 |
| Gemma overlap vs Qwen overlap | validity | 34 | 16 | 18 | 0.01535 |

## Interpretation

The v3 scaffold now clears the cheap shortcut gate: the legacy keyword baseline is far below all completed model runs. The overlap-guard prompt improves the retrieval-premise branch for both models, with the largest gain on Gemma, but it also exposes a real control tradeoff: Gemma overlap-guard routes many direct-answer and deterministic-verify examples into retrieval or clarification. This is useful evidence for the proposal, because the research object is no longer just scalar refusal accuracy; it is the Pareto problem of preserving fast-path answerability while catching false-premise retrieval cases.
