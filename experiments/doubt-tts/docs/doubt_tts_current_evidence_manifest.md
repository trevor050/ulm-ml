# Doubt-TTS Current Evidence Manifest

Version: 2026-06-02

This is the canonical snapshot after the early route/control/event-verifier arc, the two-axis validity/action repair, the 161-row evidence-pack pilots, the repaired 48-row counterbalanced overlap protocol, SRAG-E diagnostics, the GPU-backed Gemma4-26B counterbalanced pass, the 300-row v3 cue-balanced controller frontier, source-role transfer diagnostics through v4, and remote-PC qwen/Gemma live baselines. The event-route sections below remain useful historical diagnostics, but the current paper path is the reliability-action routing claim in [doubt_tts_paper_draft_v8.md](doubt_tts_paper_draft_v8.md).

The third-wave synthesis is [doubt_tts_third_wave_dossier_v7.md](doubt_tts_third_wave_dossier_v7.md). It reframes the project as evidence-gated selective compute: validity, compute action, source selection, verifier execution, and response policy are separate decisions. The rerun verifier artifacts are `third_wave_verify_table_event_report.md`, `third_wave_verify_heldout_retrieval_auto_report.md`, and `third_wave_verify_messy_local_index_report.md` in `outputs/probe_runs/`.

## Current Frontier Update

The current strongest aggressive pitch packet is [doubt_tts_aggressive_submission_blueprint_v29.md](doubt_tts_aggressive_submission_blueprint_v29.md). The clean qwen-live source-role-v3 packet is [doubt_tts_aggressive_submission_blueprint_v28.md](doubt_tts_aggressive_submission_blueprint_v28.md), the clean source-role-v2 packet is [doubt_tts_aggressive_submission_blueprint_v27.md](doubt_tts_aggressive_submission_blueprint_v27.md), the clean module-general transfer-v2 packet is [doubt_tts_aggressive_submission_blueprint_v26.md](doubt_tts_aggressive_submission_blueprint_v26.md), the clean transfer-v1 failure packet is [doubt_tts_aggressive_submission_blueprint_v25.md](doubt_tts_aggressive_submission_blueprint_v25.md), the clean static/live stress packet is [doubt_tts_aggressive_submission_blueprint_v24.md](doubt_tts_aggressive_submission_blueprint_v24.md), the clean overlay-result packet is [doubt_tts_aggressive_submission_blueprint_v23.md](doubt_tts_aggressive_submission_blueprint_v23.md), the previous operating/lock packet is [doubt_tts_aggressive_submission_blueprint_v21.md](doubt_tts_aggressive_submission_blueprint_v21.md), and the compact older pitch is [doubt_tts_aggressive_submission_blueprint_v20.md](doubt_tts_aggressive_submission_blueprint_v20.md). The strictest bridge from v3 development evidence to paper-grade evidence is [doubt_tts_v3_locked_protocol_and_reviewer_risk.md](doubt_tts_v3_locked_protocol_and_reviewer_risk.md). V29 supersedes v28 for pitch framing by adding a stronger remote-PC Gemma4-26B transfer-v4 baseline: source-role v3 gets 41/42 on transfer-v3 and 50/50 on fresh transfer-v4; qwen3.5:9b gets 20/42 on transfer-v3; qwen3:14b gets 27/42 on transfer-v3 and 34/50 on transfer-v4, with transfer-v4 clarify 8/16 and deterministic_verify 0/8; Gemma4-26B overlap-guard gets 44/50 on transfer-v4, with 47/50 validity, 44/50 compute, ambiguity 16/16, source false-premise 5/8, and deterministic_verify 6/8. The paper framing is now: reliability-action routing exposes a cost frontier where action-discriminating policies preserve cheap controls but miss `retrieve_then_premise_check`, while overlap-guard repairs the hard branch but can damage direct-answer and verifier controls; policy selection recovers most of that prompt frontier; verifier/source components target the remaining both-base-wrong buckets; overlay stress shows the v0 lexical implementation is not freeze-ready; transfer-v1 shows the first module target is still a phrase patch; transfer-v2 shows broader hand-built rules still fail source-role routing; transfer-v3 shows source-role routing is tractable but source ambiguity is hard; and transfer-v4 shows a frozen source-role-v3 diagnostic plus live qwen/Gemma baselines can separate named source answer, named source premise-check, under-named source ambiguity, stable year-token direct facts, and local deterministic verification on fresh generated rows. On the earlier repaired 48-row counterbalanced overlap split, Gemma4-26B overlap-guard remains the first completed model-only run to pass the gates: 41/48 joint, 44/48 validity, 41/48 compute, 22/24 answerable validity, 22/24 false-premise validity, 12/12 retrieve-answer action, 10/12 retrieval-premise joint, 10/12 direct action, and 9/12 premise action.

The strongest evidence-assisted diagnostic remains noisy SRAG-E wiki-search retrieval at threshold 12: 39/48 joint, 41/48 validity, 39/48 compute, 9/12 retrieve-answer, and 10/12 retrieval-premise joint. It selects acceptable source families for 20/24 source-backed rows, declines 22/24 no-source rows under the audited selected-title definition, makes 25 retrieval attempts, has mean diagnostic cost 2.83, and is mechanically labeled `evidence_assisted_passes_gates_not_model_only`. The module audit shows raw search expected-family recall is 21/24 at rank 1 and 24/24 by rank 3, while final reranked recall is 20/24 at rank 1 and 24/24 by rank 8. The post-hoc repair ablation is negative: snippet fusion reaches 38/48, entity reranking 36/48, and role-aware verification 34/48. The leave-template-out threshold audit chooses t12 in 11/12 folds and reaches 38/48, one point below fixed t12.

The current 300-row candidate is not the next paper-grade v2 benchmark. [doubt_tts_reliability_action_benchmark_v2_gap_audit.md](doubt_tts_reliability_action_benchmark_v2_gap_audit.md) audits it against the v2 reliability-action preregistration and marks it `development_gap_audit_only`: it has 55 direct, 137 premise, 42 retrieve-answer, 26 retrieve-premise, 20 deterministic, and 20 clarify rows, while the v2 target is 45/45/45/60/45/60. It is also short on source-backed retrieval rows and lacks explicit v2 construction fields such as `validity`, `compute_action`, `source_required`, `template_family`, and `semantic_family`.

A new v2 candidate scaffold now exists: [doubt_tts_reliability_action_candidate_v2_report.md](doubt_tts_reliability_action_candidate_v2_report.md), blind export [doubt_tts_reliability_action_candidate_v2_blind_export.md](doubt_tts_reliability_action_candidate_v2_blind_export.md), and gap audit [doubt_tts_reliability_action_candidate_v2_gap_audit.md](doubt_tts_reliability_action_candidate_v2_gap_audit.md). It validates against [doubt_tts_benchmark_schema_v2.json](doubt_tts_benchmark_schema_v2.json) and meets the primary v2 action/validity/source/no-source targets, but it is not paper-locked: all rows remain manual-audit-required, family balance is still weak, and [doubt_tts_reliability_action_v2_baselines.md](doubt_tts_reliability_action_v2_baselines.md) shows a keyword question-only router reaches 219/300 joint. This is construction infrastructure and a leakage red-team surface, not final benchmark evidence.

The latest hardening update is [doubt_tts_benchmark_hardening_and_pitch_update_v16.md](doubt_tts_benchmark_hardening_and_pitch_update_v16.md). It fixes a real blind-export leak by replacing semantic model-facing IDs with opaque IDs, adds a 90-row schema-valid cue-balanced adversarial slice, and reduces the legacy keyword shortcut baseline from 38/90 to 27/90 after verifier cue hardening. The cue-family-only router is now at constant baseline, 15/90. Completed remote-Ollama live checks on the same opaque slice beat the shortcut baseline but preserve the hard-action diagnosis: Qwen3.5-9B action-discriminating reaches 51/90 joint with only 3/15 retrieve-answer and 3/15 retrieve-premise action, while Gemma4-26B action-discriminating reaches 61/90 joint with 8/15 retrieve-answer and 5/15 retrieve-premise action. The remaining shortcut surface is direct-answer defaults, event-retrieval wording, a few obvious premise strings, and underspecification cues; do not spend more live model compute on the 300-row scaffold until the same counterbalancing is extended.

The current strongest benchmark-construction artifact is the v3 cue-balanced scaffold plus overlap-guard scale test and v29 source-role/Gemma stress ladder, summarized in [doubt_tts_aggressive_submission_blueprint_v29.md](doubt_tts_aggressive_submission_blueprint_v29.md), [doubt_tts_reliability_action_cue_balanced_v3_comparison.md](doubt_tts_reliability_action_cue_balanced_v3_comparison.md), [doubt_tts_reliability_action_cue_balanced_v3_hybrid_controllers.md](doubt_tts_reliability_action_cue_balanced_v3_hybrid_controllers.md), [doubt_tts_reliability_action_cue_balanced_v3_family_heldout_selector.md](doubt_tts_reliability_action_cue_balanced_v3_family_heldout_selector.md), [doubt_tts_reliability_action_cue_balanced_v3_learned_selector.md](doubt_tts_reliability_action_cue_balanced_v3_learned_selector.md), [doubt_tts_reliability_action_cue_balanced_v3_cue_stem_heldout_selector.md](doubt_tts_reliability_action_cue_balanced_v3_cue_stem_heldout_selector.md), [doubt_tts_reliability_action_cue_balanced_v3_controller_error_atlas.md](doubt_tts_reliability_action_cue_balanced_v3_controller_error_atlas.md), [doubt_tts_reliability_action_cue_balanced_v3_verifier_overlay.md](doubt_tts_reliability_action_cue_balanced_v3_verifier_overlay.md), [doubt_tts_reliability_action_v3_overlay_stress_protocol.md](doubt_tts_reliability_action_v3_overlay_stress_protocol.md), [doubt_tts_reliability_action_v3_overlay_stress_qwen35_live.md](doubt_tts_reliability_action_v3_overlay_stress_qwen35_live.md), [doubt_tts_reliability_action_v3_overlay_stress_module_target.md](doubt_tts_reliability_action_v3_overlay_stress_module_target.md), [doubt_tts_reliability_action_v3_overlay_transfer_stress_protocol.md](doubt_tts_reliability_action_v3_overlay_transfer_stress_protocol.md), [doubt_tts_reliability_action_v3_overlay_transfer_stress_module_target.md](doubt_tts_reliability_action_v3_overlay_transfer_stress_module_target.md), [doubt_tts_reliability_action_v3_overlay_stress_module_general_v1.md](doubt_tts_reliability_action_v3_overlay_stress_module_general_v1.md), [doubt_tts_reliability_action_v3_overlay_transfer_stress_module_general_v1.md](doubt_tts_reliability_action_v3_overlay_transfer_stress_module_general_v1.md), [doubt_tts_reliability_action_v3_overlay_transfer_stress_v2_protocol.md](doubt_tts_reliability_action_v3_overlay_transfer_stress_v2_protocol.md), [doubt_tts_reliability_action_v3_overlay_transfer_stress_v2_module_general_v1.md](doubt_tts_reliability_action_v3_overlay_transfer_stress_v2_module_general_v1.md), [doubt_tts_reliability_action_v3_overlay_transfer_stress_v2_module_source_role_v2.md](doubt_tts_reliability_action_v3_overlay_transfer_stress_v2_module_source_role_v2.md), [doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v3_protocol.md](doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v3_protocol.md), [doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v3_module_source_role_v2.md](doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v3_module_source_role_v2.md), [doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v3_module_source_role_v3.md](doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v3_module_source_role_v3.md), [doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_protocol.md](doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_protocol.md), [doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_module_source_role_v3.md](doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_module_source_role_v3.md), [doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v3_qwen3_14b_overlap_guard_report.md](doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v3_qwen3_14b_overlap_guard_report.md), [doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_qwen3_14b_overlap_guard_report.md](doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_qwen3_14b_overlap_guard_report.md), [doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_gemma4_26b_overlap_guard_report.md](doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_gemma4_26b_overlap_guard_report.md), [doubt_tts_reliability_action_cue_balanced_v3_locked_eval_plan.md](doubt_tts_reliability_action_cue_balanced_v3_locked_eval_plan.md), [doubt_tts_reliability_action_cue_balanced_v3_cost_frontier.md](doubt_tts_reliability_action_cue_balanced_v3_cost_frontier.md), [doubt_tts_reliability_action_cue_balanced_v3_manual_audit_queue.md](doubt_tts_reliability_action_cue_balanced_v3_manual_audit_queue.md), [doubt_tts_reliability_action_cue_balanced_v3_source_packs.md](doubt_tts_reliability_action_cue_balanced_v3_source_packs.md), [doubt_tts_reliability_action_cue_balanced_v3_source_pack_coverage.md](doubt_tts_reliability_action_cue_balanced_v3_source_pack_coverage.md), [doubt_tts_reliability_action_cue_balanced_v3_audit_template.md](doubt_tts_reliability_action_cue_balanced_v3_audit_template.md), [doubt_tts_reliability_action_v3_accept_all_dry_run.md](doubt_tts_reliability_action_v3_accept_all_dry_run.md), and [doubt_tts_reliability_action_cue_balanced_v3_response_quality_template.md](doubt_tts_reliability_action_cue_balanced_v3_response_quality_template.md). This is development-only controller evidence because v3 and transfer stress rows are generated/manual-audit-required scaffolding, not a final locked benchmark.

The new hostile source-family-heldout diagnostic is [doubt_tts_reliability_action_cue_balanced_v3_source_family_heldout_selector.md](doubt_tts_reliability_action_cue_balanced_v3_source_family_heldout_selector.md). It evaluates only the 105 source-required rows while holding out one machine-built source/event family per fold. This slice is not a selector win: Gemma overlap-guard gets 81/105 joint, the policy-only controller gets 74/105, and the hybrid gets 73/105. That caveat should be explicit in every serious pitch. The positive controller claim is a mixed-distribution cost frontier that preserves direct/no-source specificity while recovering the hard retrieval-premise branch, not universal dominance on source-required rows.

The companion source/no-source accounting is [doubt_tts_reliability_action_cue_balanced_v3_source_required_slices.md](doubt_tts_reliability_action_cue_balanced_v3_source_required_slices.md). It shows where the aggregate frontier comes from: Gemma overlap-guard is best on source-required rows but falls to 151/195 joint on no-source rows and 27/45 direct compute; the learned policy selector gets 74/105 source-required joint, 172/195 no-source joint, and preserves 45/45 direct compute. This is now the cleanest phrasing: overlap is best when source use is already known to be required, but the benchmark asks the controller to decide that under mixed reliability actions.

The controller error atlas is [doubt_tts_reliability_action_cue_balanced_v3_controller_error_atlas.md](doubt_tts_reliability_action_cue_balanced_v3_controller_error_atlas.md). It is the cleanest diagnostic for what the selector has and has not learned: the action/overlap two-policy oracle reaches 257/300, the learned policy selector has 11 rows of regret to that oracle, and the hybrid has 12. The learned selector recovers 49 rows where overlap fixes action failures, mostly source-required retrieval-premise/retrieve-answer rows, and 21 no-source rows where action fixes overlap failures. It loses 7 source-required retrieve-answer rows against overlap and cannot fix 43 rows where both base policies are wrong. That means the next method should not be pitched as "better prompt selection" alone; the unresolved research target is adding a deterministic verifier/source-confidence component for the both-wrong bucket.

The locked-evaluation planner is [doubt_tts_reliability_action_cue_balanced_v3_locked_eval_plan.md](doubt_tts_reliability_action_cue_balanced_v3_locked_eval_plan.md). From development paired discordance, learned-vs-overlap has 21 learned-only versus 7 overlap-only joint wins, exact p=0.0125; learned-vs-action has 49 versus 4, exact p=7.05e-11. The planner treats 300 rows as the minimum credible locked set, 420-480 rows as the stronger paper path, and 600 rows as the first size that supports reviewer-hostile source/no-source/hard-branch slice reporting.

The verifier/source overlay diagnostic is [doubt_tts_reliability_action_cue_balanced_v3_verifier_overlay.md](doubt_tts_reliability_action_cue_balanced_v3_verifier_overlay.md). It starts from the Gemma learned selector at 246/300 and adds two hand-specified components suggested by the atlas. Deterministic-only reaches 262/300, source-confidence-only reaches 253/300, and the full overlay reaches 269/300, with 45/45 direct compute, 47/60 retrieval-premise joint, 81/105 source-required joint, 188/195 no-source joint, one wasted retrieval, and seven missed retrievals. This is development-only method-target evidence because the rules were written after inspecting generated v3 failures.

The overlay stress protocol is [doubt_tts_reliability_action_v3_overlay_stress_protocol.md](doubt_tts_reliability_action_v3_overlay_stress_protocol.md). It exports 30 fresh stress rows and statically audits the v0 overlay trigger surface. Current result: 17/30 static trigger failures, deterministic trigger TP/FP/FN/TN of 1/1/11/17, source raw trigger TP/FP/FN/TN of 6/5/0/19, 11/12 missed deterministic paraphrase positives, and 5/24 raw source false positives on non-retrieve-answer controls. This is not a model result; it is the strongest evidence that the v0 overlay is a method target, not a frozen method.

The first live overlay-stress diagnostic is [doubt_tts_reliability_action_v3_overlay_stress_qwen35_live.md](doubt_tts_reliability_action_v3_overlay_stress_qwen35_live.md). Qwen3.5-9B overlap-guard gets 13/30 joint, 24/30 validity, 14/30 compute, 1/12 deterministic-verify compute, 6/6 retrieve-answer compute, and 0/2 false-premise validity. This supports the stress diagnosis: clean recent answer retrieval works, but deterministic paraphrases, false-premise recent rows, and ambiguous recent-looking rows still break.

The after-inspection module target is [doubt_tts_reliability_action_v3_overlay_stress_module_target.md](doubt_tts_reliability_action_v3_overlay_stress_module_target.md). It reaches 30/30 on the original stress rows by explicitly separating local operations, stable/trivial direct rows, source-answer rows, source-premise rows, and underspecification. This is a target interface, not evidence.

The transfer stress protocol is [doubt_tts_reliability_action_v3_overlay_transfer_stress_protocol.md](doubt_tts_reliability_action_v3_overlay_transfer_stress_protocol.md), with module-target evaluation in [doubt_tts_reliability_action_v3_overlay_transfer_stress_module_target.md](doubt_tts_reliability_action_v3_overlay_transfer_stress_module_target.md). The same after-inspection target collapses to 8/38, with 0/12 deterministic-positive transfer, 0/4 deterministic ambiguous transfer, 0/6 source-positive transfer, 0/4 source false-premise transfer, and 0/4 source ambiguous transfer. Stable direct transfer rows pass at 8/8 across deterministic and source-stable controls. Source-role v2 repairs transfer-v2 to 38/38 and reaches 38/42 on source-role transfer-v3, but source ambiguous rows remain only 3/6. Source-role v3 reaches 41/42 on transfer-v3 and 50/50 on fresh transfer-v4. Remote-PC qwen3:14b overlap-guard reaches 34/50 on transfer-v4, with named source-answer and source-premise rows correct but deterministic_verify at 0/8 and clarify at 8/16. Remote-PC Gemma4-26B overlap-guard reaches 44/50 on the same transfer-v4 split, with ambiguity 16/16 and retrieve-answer 8/8, but source false-premise only 5/8 and deterministic_verify 6/8. The lightweight transfer-v4 source sanity audit is [doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_source_sanity_audit.md](doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_source_sanity_audit.md); it reduces obvious generated-label risk but does not replace human paper-lock audit. This is the current strongest reason to replace phrase patches with frozen typed local-operation, underspecification, source-role, and source-confidence modules.

The v23 numeric audit is [doubt_tts_aggressive_submission_blueprint_v23_numeric_audit.md](doubt_tts_aggressive_submission_blueprint_v23_numeric_audit.md). It checks 25 headline v23 numbers against the verifier overlay, controller atlas, and locked-eval planner artifacts; current status is 25/25 checks passing.

The v24 numeric audit is [doubt_tts_aggressive_submission_blueprint_v24_numeric_audit.md](doubt_tts_aggressive_submission_blueprint_v24_numeric_audit.md). It checks 36 headline v24 numbers against verifier overlay, controller atlas, locked-eval planner, static overlay-stress, and qwen live-stress artifacts; current status is 36/36 checks passing.

The v25 numeric audit is [doubt_tts_aggressive_submission_blueprint_v25_numeric_audit.md](doubt_tts_aggressive_submission_blueprint_v25_numeric_audit.md). It checks 48 headline v25 numbers against verifier overlay, static stress, qwen live stress, module-target, and transfer-stress artifacts; current status is 48/48 checks passing.

The v26 numeric audit is [doubt_tts_aggressive_submission_blueprint_v26_numeric_audit.md](doubt_tts_aggressive_submission_blueprint_v26_numeric_audit.md). It checks 74 headline v26 numbers against verifier overlay, static stress, qwen live stress, v0 module-target, module-general-v1, transfer-v1, and transfer-v2 artifacts; current status is 74/74 checks passing.

The v27 numeric audit is [doubt_tts_aggressive_submission_blueprint_v27_numeric_audit.md](doubt_tts_aggressive_submission_blueprint_v27_numeric_audit.md). It checks 69 headline v27 numbers against verifier overlay, static stress, qwen live stress, v0 module-target, module-general-v1, source-role-v2, and transfer-v3 artifacts; current status is 69/69 checks passing.

The v29 numeric audit is [doubt_tts_aggressive_submission_blueprint_v29_numeric_audit.md](doubt_tts_aggressive_submission_blueprint_v29_numeric_audit.md). It checks 63 headline v29 numbers against verifier overlay, static stress, qwen live stress, source-role-v3, transfer-v4, remote-PC qwen, and remote-PC Gemma artifacts; current status is 63/63 checks passing. The v28 audit remains the clean qwen-live source-role-v3 audit at [doubt_tts_aggressive_submission_blueprint_v28_numeric_audit.md](doubt_tts_aggressive_submission_blueprint_v28_numeric_audit.md), with 52/52 checks passing.

The previous paper-draft v4 numeric audit is [doubt_tts_paper_draft_v4_numeric_audit.md](doubt_tts_paper_draft_v4_numeric_audit.md). It checks 78 headline draft-v4 numbers against cost-frontier, verifier-overlay, controller-atlas, source-slice, static-stress, qwen live-stress, module-target, and transfer-stress artifacts; current status is 78/78 checks passing.

The previous paper-draft v5 numeric audit is [doubt_tts_paper_draft_v5_numeric_audit.md](doubt_tts_paper_draft_v5_numeric_audit.md). It checks 75 headline draft-v5 numbers against verifier-overlay, controller-atlas, static-stress, qwen live-stress, v0 module-target, module-general-v1, transfer-v1, and transfer-v2 artifacts; current status is 75/75 checks passing.

The previous paper-draft v6 numeric audit is [doubt_tts_paper_draft_v6_numeric_audit.md](doubt_tts_paper_draft_v6_numeric_audit.md). It checks 71 headline draft-v6 numbers against verifier-overlay, controller-atlas, static-stress, qwen live-stress, v0 module-target, module-general-v1, source-role-v2, and transfer-v3 artifacts; current status is 71/71 checks passing.

The current paper-draft v8 numeric audit is [doubt_tts_paper_draft_v8_numeric_audit.md](doubt_tts_paper_draft_v8_numeric_audit.md). It checks 93 headline draft-v8 numbers against verifier-overlay, static-stress, qwen live-stress, source-role-v3, transfer-v4, remote-PC qwen, and remote-PC Gemma artifacts; current status is 93/93 checks passing. The draft-v7 audit remains the clean qwen-live source-role-v3 audit at [doubt_tts_paper_draft_v7_numeric_audit.md](doubt_tts_paper_draft_v7_numeric_audit.md), with 82/82 checks passing.

## Canonical Claims

Supported:

1. Static challenge prompts over-abstain and do not beat random/neutral challenge controls.
2. A route-first architecture is useful: ordinary, verifier, ambiguous, and false-premise-risk questions need different test-time compute.
3. One-label route schemas conflate answer validity with compute action; the decisive schema is now two-axis `validity` plus `compute_action`.
4. The hard reliability action is `retrieve_then_premise_check`: retrieve evidence to verify or correct a source-sensitive asserted premise.
5. On the 161-row evidence-pack split, Gemma4-26B action-discriminating beats the deterministic joint baseline but nearly fails the hard branch at 1/18 retrieval-premise joint.
6. On the repaired 48-row counterbalanced split, Qwen prompts, cheap SRAG selectors, and Gemma action-discriminating can improve scalar joint accuracy while still failing required retrieval-premise gates.
7. Gemma4-26B overlap-guard is the first completed model-only run to pass the repaired counterbalanced gates: 41/48 joint and 10/12 retrieval-premise joint.
8. Gemma retrieval-strict is the key ablation: 38/48 joint and 12/12 retrieval-premise, but only 3/12 premise-check action, so the positive overlap-guard result is not reducible to global retrieval.
9. SRAG-E wiki-search, lexical, local-index, and source-table verifier variants show that source selection plus verification can pass the action gates, but they are evidence-assisted diagnostics, not model-only routing evidence.
10. False-premise answer evaluation still needs response types: `abstained`, `accepted_correction`, and `accepted_false_premise`.
11. The event-gate/verifier arc remains useful: event gates improve event false-premise recall, table/retrieval verifiers show verification-shaped failures, and messy-source probes isolate source selection as a bottleneck.

Not supported:

1. Directed disconfirmation is generally better than neutral reconsideration.
2. The router generalizes beyond small hand-built probes.
3. The method improves raw always-answer accuracy.
4. The Gemma pass proves broad model-family transfer.
5. A learned controller is solved; overlap-guard is still a prompt-level policy and SRAG-Q/P remains protocol-negative.
6. SRAG-E retrieval is model-only evidence.
7. The retrieval verifier solves open-domain retrieval; the strongest diagnostics use cached corpora, Wikipedia search summaries, source tables, or verifier scaffolds.
8. The local cached-source messy probe is a live open-corpus retrieval result; it uses a small cached evidence corpus, not live web search over a large noisy index.

## Event-Route Results From The Earlier Track

Note: the event-contrast v3 rows are post current-date conditioning and route-parser hardening. The earlier response-taxonomy, subtype, and held-out event-gate rows were produced before that prompt update; rerunning them was attempted, but the remote Ollama host dropped offline after the event-contrast runs.
The harness also now includes a local counting-total verifier template for the prior held-out `held_ver_007` miss, but that held-out route set has not been rerun live after the patch.
The table-backed event verifier is an offline engineering upper bound and does not require the remote Ollama host.
The retrieval-backed held-out verifier is also offline after evidence caching. The strongest current run ignores source-title hints and infers the source title from clean event phrasing, but it still does not test messy retrieval/search.

| eval | file | result |
|---|---|---|
| balanced route eval | `qwen_route_eval_cascade_report.md` | confidence-gated cascade: 48/48 |
| false-premise subtype eval | `qwen_false_premise_subtypes_cascade_report.md` | 71/72 overall, 63/64 false-premise recall, 8/8 ordinary specificity |
| held-out route probe | `qwen_heldout_route_cascade_report.md` | 61/64 overall |
| response-taxonomy route check | `qwen_response_taxonomy_route_cascade_report.md` | 47/48 overall |
| response-taxonomy route check + event gate | `qwen_response_taxonomy_route_event_gate_report.md` | 48/48 overall |
| false-premise subtype eval + event gate | `qwen_false_premise_subtypes_event_gate_report.md` | 72/72 overall |
| held-out route probe + event gate | `qwen_heldout_route_event_gate_report.md` | 62/64 overall |
| event-contrast route stress test | `qwen_event_contrast_route_strict_v3_report.md` | strict: 60/72 overall, 26/36 false-premise recall, 34/36 ordinary specificity |
| event-contrast route stress test | `qwen_event_contrast_route_cascade_v3_report.md` | cascade: 63/72 overall, 28/36 false-premise recall, 35/36 ordinary specificity |
| event-contrast route stress test + event gate | `qwen_event_contrast_route_event_gate_v3_report.md` | event-gated cascade: 66/72 overall, 31/36 false-premise recall, 35/36 ordinary specificity |
| event-contrast route stress test + table verifier | `table_event_verifier_route_report.md` | table-backed event verifier: 72/72 overall, 36/36 false-premise recall, 36/36 ordinary specificity |
| held-out event verifier baseline | `heldout_table_event_verifier_route_report.md` | original table verifier: 21/32 overall, 1/12 false-premise recall, 20/20 ordinary specificity |
| held-out event verifier + retrieval | `heldout_retrieval_event_verifier_route_report.md` | source-hinted retrieval verifier: 32/32 overall, 12/12 false-premise recall, 20/20 ordinary specificity |
| held-out event verifier + inferred-source retrieval | `heldout_retrieval_auto_source_event_verifier_route_report.md` | inferred-source retrieval verifier: 32/32 overall, 12/12 false-premise recall, 20/20 ordinary specificity |
| messy event-source probe baseline | `messy_table_event_verifier_route_report.md` | original table verifier: 12/24 overall, 0/12 false-premise recall, 12/12 ordinary specificity |
| messy event-source probe + clean-title inference | `messy_retrieval_infer_source_event_verifier_route_report.md` | clean-title inference verifier: 12/24 overall, 0/12 false-premise recall, 12/12 ordinary specificity |
| messy event-source probe + query fixture | `messy_retrieval_query_fixture_event_verifier_route_report.md` | query-fixture retrieval verifier: 24/24 overall, 12/12 false-premise recall, 12/12 ordinary specificity |
| messy event-source probe + local evidence index | `messy_retrieval_local_index_event_verifier_route_report.md` | local cached-source retrieval verifier: 24/24 overall, 12/12 false-premise recall, 12/12 ordinary specificity |
| messy event-source source selection | `messy_local_source_selection_report.md` | local cached-source selector: 24/24 expected source titles |

## Answer Results From The Earlier Track

| eval | file | method | coverage | accepted_accuracy | decision_success | confident_wrong_rate |
|---|---|---|---:|---:|---:|---:|
| mixed 36 | `qwen_36_adaptive_router_cascade_verifier_report.md` | cascade + verifier | 0.78 | 1.00 | 1.00 | 0.00 |
| hard false-premise 24 | `qwen_hard_false_adaptive_router_cascade_report.md` | cascade | 0.12 | 1.00 | 1.00 | 0.00 |
| mixed 36 control | `qwen_36_adaptive_router_cascade_vs_control_report.md` | directed routed probes | 0.78 | 1.00 | 1.00 | 0.00 |
| mixed 36 control | `qwen_36_adaptive_router_cascade_vs_control_report.md` | routed neutral control | 0.81 | 1.00 | 1.00 | 0.00 |
| hard false-premise 24 control | `qwen_hard_false_adaptive_router_cascade_vs_control_report.md` | directed routed probes | 0.08 | 1.00 | 1.00 | 0.00 |
| hard false-premise 24 control | `qwen_hard_false_adaptive_router_cascade_vs_control_report.md` | routed neutral control | 0.25 | 1.00 | 1.00 | 0.00 |
| response-taxonomy 48 control | `qwen_response_taxonomy_cascade_vs_control_report.md` | directed routed probes | 0.17 | 0.88 | 0.98 | 0.02 |
| response-taxonomy 48 control | `qwen_response_taxonomy_cascade_vs_control_report.md` | routed neutral control | 0.27 | 0.85 | 0.96 | 0.04 |
| response-taxonomy 48 event gate | `qwen_response_taxonomy_event_gate_vs_control_report.md` | directed routed probes | 0.17 | 1.00 | 1.00 | 0.00 |
| response-taxonomy 48 event gate | `qwen_response_taxonomy_event_gate_vs_control_report.md` | routed neutral control | 0.27 | 1.00 | 1.00 | 0.00 |

## False-Premise Response Types

Mixed 36 control:

| method | abstained | accepted_correction | accepted_false_premise |
|---|---:|---:|---:|
| directed routed probes | 8 | 4 | 0 |
| routed neutral control | 7 | 5 | 0 |

Hard false-premise control:

| method | abstained | accepted_correction | accepted_false_premise |
|---|---:|---:|---:|
| directed routed probes | 22 | 2 | 0 |
| routed neutral control | 18 | 6 | 0 |

Response-taxonomy 48 control:

| method | abstained | accepted_correction | accepted_false_premise |
|---|---:|---:|---:|
| directed routed probes | 40 | 7 | 1 |
| routed neutral control | 35 | 11 | 2 |

Response-taxonomy 48 event gate:

| method | abstained | accepted_correction | accepted_false_premise |
|---|---:|---:|---:|
| directed routed probes | 40 | 8 | 0 |
| routed neutral control | 35 | 13 | 0 |

## Current Best Paper Claim

The strongest honest claim is now:

> Naive disconfirmation prompts are not enough. The useful object is validity-aware reliability-action routing: answer, check a premise, retrieve evidence, retrieve to check a premise, verify deterministically, or clarify. The current v3 scale result shows why: Gemma action-discriminating reaches 246/300 validity but only 6/60 joint on retrieval-backed premise checks, while Gemma overlap-guard raises that branch to 47/60 joint and overall joint to 232/300 but damages direct-answer controls. A Gemma policy-output hybrid reaches 245/300 joint while preserving 45/45 direct-answer compute and 47/60 retrieval-premise joint, leave-template-family-out rule selection picks the same rule in all 45 folds, and a learned policy-output selector reaches 246/300 under both leave-template-family-out and leave-cue-stem-out splits. On source-required rows alone, overlap-guard remains the stronger slice baseline, 81/105 versus 74/105 for the source-family-heldout policy selector, so the research problem is a cost-aware controller over the mixed reliability-action distribution, not a claim that the selector beats retrieval everywhere. The next validation is locked held-out data with source-required and no-source-required slices reported separately.

Add the new caveat:

> Specialized gates can trade recall for specificity. The event gate improves event false-premise recall, but event routing should be evaluated with current-date conditioning and retrieval/tool baselines. The hand-built table verifier is only an upper bound. The wiki-search, lexical, local-index, and source-table SRAG-E probes show that source selection plus verification can pass the counterbalanced action gates, but they are evidence-assisted diagnostics. The next critical path is a larger locked benchmark plus a learned or calibrated controller that decides when to use overlap-guard behavior and when to invoke source/verifier-backed retrieval.

The current strongest aggressive pitch packet is [doubt_tts_aggressive_submission_blueprint_v29.md](doubt_tts_aggressive_submission_blueprint_v29.md). The clean qwen-live source-role-v3 packet is [doubt_tts_aggressive_submission_blueprint_v28.md](doubt_tts_aggressive_submission_blueprint_v28.md), the clean source-role-v2 packet is [doubt_tts_aggressive_submission_blueprint_v27.md](doubt_tts_aggressive_submission_blueprint_v27.md), the clean module-general transfer-v2 packet is [doubt_tts_aggressive_submission_blueprint_v26.md](doubt_tts_aggressive_submission_blueprint_v26.md), the clean transfer-v1 failure packet is [doubt_tts_aggressive_submission_blueprint_v25.md](doubt_tts_aggressive_submission_blueprint_v25.md), the clean static/live stress packet is [doubt_tts_aggressive_submission_blueprint_v24.md](doubt_tts_aggressive_submission_blueprint_v24.md), the clean overlay-result packet is [doubt_tts_aggressive_submission_blueprint_v23.md](doubt_tts_aggressive_submission_blueprint_v23.md), the previous operating packet is [doubt_tts_aggressive_submission_blueprint_v21.md](doubt_tts_aggressive_submission_blueprint_v21.md), and the compact older pitch is [doubt_tts_aggressive_submission_blueprint_v20.md](doubt_tts_aggressive_submission_blueprint_v20.md). The current strongest paper-style draft is [doubt_tts_paper_draft_v8.md](doubt_tts_paper_draft_v8.md), and its headline numeric claims are checked by [doubt_tts_paper_draft_v8_numeric_audit.md](doubt_tts_paper_draft_v8_numeric_audit.md). The previous draft-v7 audit remains [doubt_tts_paper_draft_v7_numeric_audit.md](doubt_tts_paper_draft_v7_numeric_audit.md), the previous draft-v6 audit remains [doubt_tts_paper_draft_v6_numeric_audit.md](doubt_tts_paper_draft_v6_numeric_audit.md), the previous draft-v5 audit remains [doubt_tts_paper_draft_v5_numeric_audit.md](doubt_tts_paper_draft_v5_numeric_audit.md), the previous draft-v4 audit remains [doubt_tts_paper_draft_v4_numeric_audit.md](doubt_tts_paper_draft_v4_numeric_audit.md), and the previous draft-v3 audit remains [doubt_tts_paper_draft_v3_numeric_audit.md](doubt_tts_paper_draft_v3_numeric_audit.md). The current claim wording addendum is [doubt_tts_claim_ledger_v3_controller_addendum.md](doubt_tts_claim_ledger_v3_controller_addendum.md). The current literature/method synthesis is [doubt_tts_literature_positioning_and_method_v5.md](doubt_tts_literature_positioning_and_method_v5.md). The current next-experiment preregistration is [doubt_tts_preregistered_experiment_plan_v2.md](doubt_tts_preregistered_experiment_plan_v2.md). The current reviewer-risk map is [doubt_tts_reviewer_risk_audit_v2.md](doubt_tts_reviewer_risk_audit_v2.md).

## v3 Update

The latest consolidated dossier is [doubt_tts_final_research_dossier_v3.md](doubt_tts_final_research_dossier_v3.md).

The most current event-contrast route reports are the `v3` files:

| router | report | overall | ordinary specificity | false-premise recall |
|---|---|---:|---:|---:|
| strict | `qwen_event_contrast_route_strict_v3_report.md` | 60/72 | 34/36 | 26/36 |
| cascade | `qwen_event_contrast_route_cascade_v3_report.md` | 63/72 | 35/36 | 28/36 |
| cascade + event gate | `qwen_event_contrast_route_event_gate_v3_report.md` | 66/72 | 35/36 | 31/36 |
| table event verifier | `table_event_verifier_route_report.md` | 72/72 | 36/36 | 36/36 |
| held-out table verifier | `heldout_table_event_verifier_route_report.md` | 21/32 | 20/20 | 1/12 |
| held-out retrieval verifier | `heldout_retrieval_event_verifier_route_report.md` | 32/32 | 20/20 | 12/12 |
| held-out inferred-source retrieval verifier | `heldout_retrieval_auto_source_event_verifier_route_report.md` | 32/32 | 20/20 | 12/12 |
| messy table verifier | `messy_table_event_verifier_route_report.md` | 12/24 | 12/12 | 0/12 |
| messy clean-title inference verifier | `messy_retrieval_infer_source_event_verifier_route_report.md` | 12/24 | 12/12 | 0/12 |
| messy query-fixture retrieval verifier | `messy_retrieval_query_fixture_event_verifier_route_report.md` | 24/24 | 12/12 | 12/12 |
| messy local cached-source retrieval verifier | `messy_retrieval_local_index_event_verifier_route_report.md` | 24/24 | 12/12 | 12/12 |

## Immediate Next Experiment

The immediate next experiment is now specified in [doubt_tts_preregistered_experiment_plan_v2.md](doubt_tts_preregistered_experiment_plan_v2.md), with item schema [doubt_tts_benchmark_schema_v2.json](doubt_tts_benchmark_schema_v2.json). The v1 plan and v1 schema remain historical route/answerability artifacts and predate the Gemma4-26B model-only counterbalanced pass.

Build a larger 240-300 row locked reliability-action benchmark with two-axis labels:

- `validity`: `answerable`, `false_premise`, `ambiguous`;
- `compute_action`: `direct_answer`, `premise_check`, `retrieve_then_answer`, `retrieve_then_premise_check`, `deterministic_verify`, `clarify`.

Then compare model-only policies, frozen learned SRAG-Q/P, retrieval-strict and neutral controls, text-only/family-held-out baselines, and evidence-assisted SRAG-E variants. The current 48-row counterbalanced overlap split is supportive pilot evidence, not paper-grade generalization; the next benchmark must be locked before further prompt or controller tuning.

The earlier event-contrast line still matters as a benchmark-design warning: temporal and event rows need `as_of_date`, source timestamps, and date-conditioned labels such as historical completed, recent completed, future scheduled, future completed, wrong-year, wrong-winner, and nonexistent-award cases.

The benchmark should be treated as locked once built. If prompts, route labels, or verifier logic are tuned on it, it becomes development data and no paper-grade claim should use it as the final held-out result.
