# Reliability-Action Cue-Balanced Candidate v3 Report

Status: generated 300-row v3 benchmark-construction scaffold. It is schema-aligned and cue-balanced, but all rows remain manual-audit-required.

- rows: 300
- output: `work/probe/reliability_action_cue_balanced_candidate_v3_locked.jsonl`
- template families: 45
- oracle template-family majority ceiling: 60/300

## Compute-Action Counts

| compute action | count | target |
|---|---:|---:|
| `direct_answer` | 45 | 45 |
| `premise_check` | 45 | 45 |
| `retrieve_then_answer` | 45 | 45 |
| `retrieve_then_premise_check` | 60 | 60 |
| `deterministic_verify` | 45 | 45 |
| `clarify` | 60 | 60 |

## Validity Counts

| validity | count |
|---|---:|
| `ambiguous` | 60 |
| `answerable` | 135 |
| `false_premise` | 105 |

## Subtype Counts

| subtype | count |
|---|---:|
| `ambiguous_underspecified` | 60 |
| `category_error` | 12 |
| `false_event_year` | 6 |
| `false_relation_real_entity` | 3 |
| `math_calendar_logic` | 45 |
| `multi_hop_false_premise` | 3 |
| `nonexistent_award_category_office` | 3 |
| `nonexistent_entity` | 3 |
| `ordinary_event_control` | 45 |
| `physical_impossibility` | 9 |
| `recent_completed_event` | 45 |
| `sport_mismatch` | 6 |
| `wrong_winner_opponent_host` | 60 |

## Caveats

- This is still generated scaffolding, not a locked benchmark.
- Many rows are controlled rephrasings of the 90-row slice and require manual source/label audit.
- The crucial pre-model test is whether opaque blind export plus text-only baselines keep shortcut accuracy well below live-model accuracy.
