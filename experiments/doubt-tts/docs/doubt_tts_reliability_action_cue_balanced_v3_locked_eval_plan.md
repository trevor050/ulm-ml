# Reliability-Action v3 Locked Evaluation Plan

Status: generated planning analysis from development scored rows. This is not locked evidence.

The point of this file is to make the next run harder to fool. It uses paired exact McNemar-style discordance from the v3 development rows, then asks what locked-set sizes would make the same effects statistically visible if the rates repeated. This is an effect-planning tool, not a guarantee.

## Development Summary

| method | joint | validity | compute |
|---|---:|---:|---:|
| `gemma_action` | 201/300 | 246/300 | 214/300 |
| `gemma_overlap` | 232/300 | 254/300 | 237/300 |
| `gemma_hybrid` | 245/300 | 260/300 | 250/300 |
| `gemma_learned` | 246/300 | 260/300 | 251/300 |
| `gemma_cue_heldout` | 246/300 | 260/300 | 251/300 |

## Paired Effects

| comparison | metric | A only | B only | net A-B | dev exact p | min n if rates repeat |
|---|---|---:|---:|---:|---:|---:|
| `learned_vs_action` | `joint_correct` | 49 | 4 | +45 | 7.05e-11 | 60 |
| `learned_vs_action` | `validity_correct` | 18 | 4 | +14 | 0.0043 | 160 |
| `learned_vs_action` | `compute_correct` | 41 | 4 | +37 | 9.33e-09 | 60 |
| `learned_vs_overlap` | `joint_correct` | 21 | 7 | +14 | 0.0125 | 180 |
| `learned_vs_overlap` | `validity_correct` | 6 | 0 | +6 | 0.0312 | 275 |
| `learned_vs_overlap` | `compute_correct` | 21 | 7 | +14 | 0.0125 | 180 |
| `hybrid_vs_action` | `joint_correct` | 48 | 4 | +44 | 1.31e-10 | 60 |
| `hybrid_vs_action` | `validity_correct` | 17 | 3 | +14 | 0.0026 | 135 |
| `hybrid_vs_action` | `compute_correct` | 40 | 4 | +36 | 1.71e-08 | 60 |
| `hybrid_vs_overlap` | `joint_correct` | 21 | 8 | +13 | 0.0241 | 240 |
| `hybrid_vs_overlap` | `validity_correct` | 7 | 1 | +6 | 0.0703 | 325 |
| `hybrid_vs_overlap` | `compute_correct` | 21 | 8 | +13 | 0.0241 | 240 |
| `overlap_vs_action` | `joint_correct` | 56 | 25 | +31 | 0.0008 | 110 |
| `overlap_vs_action` | `validity_correct` | 18 | 10 | +8 | 0.1849 | 545 |
| `overlap_vs_action` | `compute_correct` | 48 | 25 | +23 | 0.0095 | 180 |
| `cue_heldout_vs_learned` | `joint_correct` | 0 | 0 | +0 | 1.0000 | none |
| `cue_heldout_vs_learned` | `validity_correct` | 0 | 0 | +0 | 1.0000 | none |
| `cue_heldout_vs_learned` | `compute_correct` | 0 | 0 | +0 | 1.0000 | none |

## Scaled Joint-Effect Table

The table below focuses on the two reviewer-critical joint comparisons: learned selector versus action-discriminating, and learned selector versus overlap-guard.

| planned n | learned vs action A/B/net/p | learned vs overlap A/B/net/p |
|---:|---:|---:|
| 180 | 29/2/+27/4.63e-07 | 13/4/+9/0.0490 |
| 240 | 39/3/+36/5.63e-09 | 17/6/+11/0.0347 |
| 300 | 49/4/+45/7.05e-11 | 21/7/+14/0.0125 |
| 360 | 59/5/+54/9.00e-13 | 25/8/+17/0.0046 |
| 420 | 69/6/+63/1.16e-14 | 29/10/+19/0.0034 |
| 480 | 78/6/+72/4.54e-17 | 34/11/+23/0.0008 |
| 600 | 98/8/+90/8.08e-21 | 42/14/+28/0.0002 |
| 720 | 118/10/+108/1.45e-24 | 50/17/+33/6.74e-05 |
| 900 | 147/12/+135/1.06e-30 | 63/21/+42/4.97e-06 |

## Locked-Set Size Recommendation

- Minimum credible locked set: 300 rows. This preserves the v3 action mix with about 60 retrieval-premise and 60 clarify rows, enough to report hard-branch gates without hiding behind aggregate accuracy.
- Stronger locked set: 420-480 rows. If the learned-vs-overlap joint effect repeats, this range makes the modest mixed-distribution advantage easier to defend while still staying feasible for manual audit.
- Aggressive locked set: 600 rows. This is the first size I would trust for a reviewer-hostile paper claim that reports source-required, no-source, retrieval-premise, and direct-control slices separately.
- Do not use a source-required-only primary endpoint. The source-family-heldout diagnostic says overlap-guard is the stronger source-slice baseline. The primary claim has to be mixed-distribution cost-aware routing, with source/no-source slices as mandatory secondary endpoints.

## Expected Balanced Counts

| planned n | direct | premise | retrieve-answer | retrieve-premise | verify | clarify |
|---:|---:|---:|---:|---:|---:|---:|
| 180 | 27 | 27 | 27 | 36 | 27 | 36 |
| 240 | 36 | 36 | 36 | 48 | 36 | 48 |
| 300 | 45 | 45 | 45 | 60 | 45 | 60 |
| 360 | 54 | 54 | 54 | 72 | 54 | 72 |
| 420 | 63 | 63 | 63 | 84 | 63 | 84 |
| 480 | 72 | 72 | 72 | 96 | 72 | 96 |
| 600 | 90 | 90 | 90 | 120 | 90 | 120 |
| 720 | 108 | 108 | 108 | 144 | 108 | 144 |
| 900 | 135 | 135 | 135 | 180 | 135 | 180 |

## Required Locked Gates

- Primary endpoint: joint correctness over the full mixed reliability-action distribution, learned selector versus action-discriminating and overlap-guard.
- Cost endpoint: mean predicted cost and wasted retrieval; the learned selector must preserve the no-source/direct specificity advantage rather than buying accuracy by global retrieval.
- Hard-branch endpoint: retrieval-premise joint and compute accuracy must stay near the overlap-guard branch level.
- Slice endpoint: report source-required and no-source-required separately. Current development slice: overlap is 81/105 source-required joint; learned policy is 74/105 source-required and 172/195 no-source joint.
- Kill criterion: if learned/hybrid beats action only by over-retrieving direct/no-source rows, the method is not the paper claim.
- Kill criterion: if source-required rows collapse below overlap without a compensating no-source/direct advantage, pitch the result as a negative controller boundary, not a win.

## Source Slice Snapshot

| method | source-required joint | no-source joint | direct compute | mean cost |
|---|---:|---:|---:|---:|
| `gemma4:26b:action_discriminating` | 28/105 | 173/195 | 45/45 | 1.78 |
| `gemma4:26b:overlap_guard` | 81/105 | 151/195 | 27/45 | 2.38 |
| `gemma4:26b:hybrid_overlap_if_either_rtp` | 73/105 | 172/195 | 45/45 | 2.13 |
| `gemma4:26b:learned_policy_joint_selector` | 74/105 | 172/195 | 45/45 | 2.17 |

## Read This As A Reviewer

A 300-row locked eval can support a cautious workshop claim if it reproduces the current shape. A 420-600 row locked eval is the credible paper path because it gives enough branch mass for hostile slice reporting. The most important failure mode is not losing a p-value; it is discovering that the selector is a generated-cue controller that cannot survive audited source families and no-source controls.
