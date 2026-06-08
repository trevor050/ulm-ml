# Doubt-TTS Probe Harness

Cheap executable protocol for testing collapse scoring before spending real compute.

Run the deterministic fixture smoke test:

```bash
python3 work/probe/doubt_probe.py
```

Outputs:

- `work/probe/runs/mock_results.jsonl`
- `work/probe/runs/mock_report.md`

Regenerate the reviewer-facing evidence matrix:

```bash
python3 work/probe/summarize_evidence.py
```

Output:

- `outputs/doubt_tts_evidence_matrix.md`

## Reliability-Action v3 Audit And Lock Pipeline

The current operating/submission packet is:

- `outputs/doubt_tts_aggressive_submission_blueprint_v29.md`

The current paper-style draft is:

- `outputs/doubt_tts_paper_draft_v8.md`

The clean module-general stress/transfer packet is:

- `outputs/doubt_tts_aggressive_submission_blueprint_v26.md`

The clean overlay-result packet is:

- `outputs/doubt_tts_aggressive_submission_blueprint_v23.md`

The older lock-pipeline inventory packet is:

- `outputs/doubt_tts_aggressive_submission_blueprint_v21.md`

The compact older pitch is:

- `outputs/doubt_tts_aggressive_submission_blueprint_v20.md`

Generate the prioritized human-audit queue:

```bash
python3 work/probe/build_reliability_action_v3_manual_audit_queue.py
```

Generate the blank JSONL/CSV audit worksheet:

```bash
python3 work/probe/build_reliability_action_v3_audit_template.py
```

Outputs:

- `work/probe/reliability_action_cue_balanced_v3_audit_template.jsonl`
- `work/probe/reliability_action_cue_balanced_v3_audit_template.csv`
- `outputs/doubt_tts_reliability_action_cue_balanced_v3_audit_template.md`

Build machine source-pack candidates for all source-required rows:

```bash
python3 work/probe/build_reliability_action_v3_source_packs.py
python3 work/probe/analyze_reliability_action_v3_source_pack_coverage.py
python3 work/probe/build_reliability_action_v3_audit_template.py
```

Outputs:

- `work/probe/source_packs/v3/rows/*.json`
- `work/probe/source_packs/v3/source_fetches.jsonl`
- `work/probe/reliability_action_cue_balanced_v3_source_pack_overlay.jsonl`
- `work/probe/reliability_action_cue_balanced_v3_source_pack_overlay.csv`
- `outputs/doubt_tts_reliability_action_cue_balanced_v3_source_packs.md`
- `work/probe/runs/reliability_action_cue_balanced_v3_source_pack_coverage_rows.jsonl`
- `outputs/doubt_tts_reliability_action_cue_balanced_v3_source_pack_coverage.md`

Current status: 105/105 source-required rows have machine
`complete_candidate` source packs and 105/105 pass lexical support. This does
not satisfy the lock gate until a human auditor marks
`source_pack_status=complete`.

Validate lock-candidate plumbing without claiming evidence:

```bash
python3 work/probe/build_reliability_action_v3_lock_candidate.py --mode accept_all_dry_run
```

Outputs:

- `work/probe/locked_candidates/v3_accept_all_dry_run_locked.jsonl`
- `work/probe/locked_candidates/v3_accept_all_dry_run_blind_inputs.jsonl`
- `work/probe/locked_candidates/v3_accept_all_dry_run_label_key.jsonl`
- `outputs/doubt_tts_reliability_action_v3_accept_all_dry_run.md`

The accept-all dry run is not paper evidence. It exists to test ID mapping,
hashing, blind/key export, leakage checks, and distribution accounting. In
audited mode, source-required rows must have `source_pack_status=complete`:

```bash
python3 work/probe/build_reliability_action_v3_lock_candidate.py \
  --mode audited \
  --audit work/probe/reliability_action_cue_balanced_v3_audit_template.csv
```

Generate the high-risk final-response quality worksheet:

```bash
python3 work/probe/build_reliability_action_v3_response_quality_template.py
```

Outputs:

- `work/probe/reliability_action_cue_balanced_v3_response_quality_template.jsonl`
- `work/probe/reliability_action_cue_balanced_v3_response_quality_template.csv`
- `outputs/doubt_tts_reliability_action_cue_balanced_v3_response_quality_template.md`

Default sample is top 120 audit rows, including all 60 retrieval-premise rows.
Use this before broad safety claims because route correctness does not prove the
final answer/correction/clarification is acceptable.

## Counterbalanced Overlap Live Experiment

The repaired overlap-gate experiment is documented in:

- `outputs/doubt_tts_counterbalanced_overlap_protocol_v1.md`

The key target split is:

- `work/probe/overlap_gate_holdout_counterbalanced_blind_inputs.jsonl`
- `work/probe/overlap_gate_holdout_counterbalanced_label_key.jsonl`

Current baselines on this split:

- deterministic two-axis router: 21/48 joint;
- paired cue-transfer baselines: 12/48 or worse;
- leave-one-out cue signatures: 0/48.

Completed local-model evidence:

- Qwen action-discriminating: 22/48 joint, 39/48 validity, 23/48 compute, 0/12 retrieval-premise joint.
- Qwen overlap-guard: 25/48 joint, 38/48 validity, 29/48 compute.
- Gemma4-26B action-discriminating: 27/48 joint, 44/48 validity, 28/48 compute, 1/12 retrieval-premise joint.
- Gemma4-26B retrieval-strict: 38/48 joint, 46/48 validity, 38/48 compute, 12/12 retrieve-answer, 12/12 retrieval-premise, but 3/12 premise-check action. Over-retrieval ablation, not supportive.
- Gemma4-26B overlap-guard: 41/48 joint, 44/48 validity, 41/48 compute, 12/12 retrieve-answer action, 10/12 retrieval-premise joint, 10/12 direct action, 9/12 premise action. First completed model-only counterbalanced run marked `supportive`.
- Cheap SRAG selector pilot: best variant 27/48 joint, 39/48 validity, 30/48 compute, 2/12 retrieval-premise joint.
- SRAG-E noisy wiki-search retrieval verifier: best threshold 39/48 joint, 41/48 validity, 39/48 compute, 9/12 retrieve-answer, 10/12 retrieval-premise joint; source selection 20/24 and audited selected-title no-source decline 22/24 with 25 retrieval attempts. Evidence-assisted Wikipedia-search diagnostic only, not model-only or open-web-general evidence.
- SRAG-E wiki-search post-hoc repair ablation: `python3 work/probe/run_counterbalanced_srag_e_wiki_search_posthoc_repair.py`. Snippet fusion reaches 38/48, entity rerank 36/48, role verifier 34/48; negative diagnostic, not method evidence.
- SRAG-E threshold-selection audit: `python3 work/probe/analyze_srag_e_threshold_selection.py`. Leave-template-out wiki-search threshold-only selection chooses t12 in 11/12 template folds and reaches 38/48, one point below fixed t12. Post-hoc robustness audit, not preregistered evidence.
- SRAG-E lexical retrieval verifier: best threshold 38/48 joint, 42/48 validity, 38/48 compute, 11/12 retrieve-answer, 8/12 retrieval-premise joint; source selection 23/24 and audited selected-title no-source decline 21/24. Evidence-assisted diagnostic only, not model-only or open-web retrieval evidence.
- SRAG-E pattern-based local-index verifier: 42/48 joint, 42/48 validity, 42/48 compute, 12/12 retrieve-answer, 8/12 retrieval-premise joint. Evidence-assisted diagnostic only, not model-only or open-web retrieval evidence.
- SRAG-E source-table verifier override: 46/48 joint, 46/48 validity, 46/48 compute, 12/12 retrieval-premise joint. Evidence-assisted diagnostic only, not model-only evidence.
- Protocol verdict: both Qwen policies and cheap SRAG selectors are `mixed_fails_required_gates`; wiki-search/lexical/local-index/source-table SRAG-E verifier overrides are `evidence_assisted_passes_gates_not_model_only`.
- CPU-only Llama3.2-1B overlap-guard: 6/48 joint, a negative smoke that routes every row to retrieval-premise.

Run a live model when the Ollama endpoint is stable:

```bash
MODEL=qwen3.5:9b POLICY=overlap_guard \
  work/probe/run_counterbalanced_overlap_live.sh
```

Gemma overlap-guard condition:

```bash
MODEL=gemma4:26b POLICY=overlap_guard \
  RUN_NAME=overlap_gate_holdout_counterbalanced_gemma4_26b_overlap_guard \
  work/probe/run_counterbalanced_overlap_live.sh
```

Partial runs are not model evidence. The live runner checkpoints and resumes,
but a valid result needs 48/48 predictions and zero missing predictions in the
scored report. Use `--only-id <row_id>` on `run_two_axis_live_route.py` only for
debugging flaky rows.

Evaluate the protocol gates mechanically:

```bash
python3 work/probe/evaluate_counterbalanced_overlap_protocol.py
```

Run cheap non-oracle SRAG selector pilots over the completed Qwen action/overlap predictions:

```bash
python3 work/probe/run_counterbalanced_srag_selectors.py
python3 work/probe/evaluate_counterbalanced_overlap_protocol.py
python3 work/probe/analyze_overlap_holdout_cost_frontier.py
```

Run SRAG-E source-table diagnostics:

```bash
python3 work/probe/run_counterbalanced_srag_e_wiki_search_retrieval.py
python3 work/probe/audit_wiki_search_retrieval_modules.py
python3 work/probe/run_counterbalanced_srag_e_lexical_retrieval.py
python3 work/probe/run_counterbalanced_srag_e_local_index.py
python3 work/probe/run_counterbalanced_srag_e_source_table.py
python3 work/probe/evaluate_counterbalanced_overlap_protocol.py
python3 work/probe/analyze_overlap_holdout_cost_frontier.py
```

Outputs:

- `work/probe/runs/counterbalanced_overlap_protocol_eval.json`
- `outputs/doubt_tts_counterbalanced_overlap_protocol_eval.md`

Run the diagnostic source-table upper bound:

```bash
python3 work/probe/run_counterbalanced_overlap_source_table_router.py
python3 work/probe/evaluate_counterbalanced_overlap_protocol.py
```

This produces `outputs/doubt_tts_overlap_gate_holdout_counterbalanced_source_table_report.md`.
It is useful only as verifier-target evidence: it shows the repaired split is
solvable with the right source/event table, not that a model has learned the
routing gate.

Next paper-grade benchmark spec:

- `outputs/doubt_tts_preregistered_experiment_plan_v2.md`
- `outputs/doubt_tts_benchmark_schema_v2.json`

Audit the current 300-row candidate against the v2 reliability-action target before any expensive live run:

```bash
python3 work/probe/audit_reliability_action_benchmark_v2.py
```

Outputs:

- `work/probe/runs/reliability_action_benchmark_v2_audit.json`
- `outputs/doubt_tts_reliability_action_benchmark_v2_gap_audit.md`

Current v2 status: the existing candidate is development data only. It is short on retrieval-premise, deterministic-verify, clarify, source-backed retrieval, and explicit v2 construction metadata.

Build the separate v2 candidate scaffold:

```bash
python3 work/probe/build_reliability_action_candidate_v2.py
python3 work/probe/audit_reliability_action_benchmark_v2.py \
  --candidate work/probe/reliability_action_benchmark_v2_candidate_locked.jsonl \
  --out-json work/probe/runs/reliability_action_benchmark_v2_candidate_audit.json \
  --out-report outputs/doubt_tts_reliability_action_candidate_v2_gap_audit.md
python3 work/probe/validate_benchmark_schema.py \
  --schema outputs/doubt_tts_benchmark_schema_v2.json \
  --input work/probe/reliability_action_benchmark_v2_candidate_locked.jsonl
python3 work/probe/export_reliability_action_candidate_v2.py
python3 work/probe/run_reliability_action_v2_baselines.py
```

Current scaffold status: exact primary action/validity targets pass and the blind/key export is clean, but keyword question-only routing reaches 219/300 joint. Do not treat the scaffold as a final semantic benchmark until cue counterbalancing and manual evidence audit are done.

Current v3 controller diagnostics:

```bash
python3 work/probe/analyze_reliability_action_v3_results.py
python3 work/probe/analyze_reliability_action_v3_hybrids.py
python3 work/probe/analyze_reliability_action_v3_family_heldout_selector.py
python3 work/probe/analyze_reliability_action_v3_learned_selector.py
python3 work/probe/analyze_reliability_action_v3_cue_stem_heldout_selector.py
python3 work/probe/analyze_reliability_action_v3_source_family_heldout_selector.py
python3 work/probe/analyze_reliability_action_v3_source_required_slices.py
python3 work/probe/analyze_reliability_action_v3_controller_error_atlas.py
python3 work/probe/analyze_reliability_action_v3_verifier_overlay.py
python3 work/probe/build_reliability_action_v3_overlay_stress_protocol.py
python3 work/probe/analyze_reliability_action_v3_overlay_stress_module_target.py
python3 work/probe/build_reliability_action_v3_overlay_transfer_stress.py
python3 work/probe/analyze_reliability_action_v3_overlay_stress_module_target.py \
  --input work/probe/reliability_action_v3_overlay_transfer_stress_blind_inputs.jsonl \
  --key work/probe/reliability_action_v3_overlay_transfer_stress_label_key.jsonl \
  --run-name reliability_action_v3_overlay_transfer_stress_module_target \
  --report outputs/doubt_tts_reliability_action_v3_overlay_transfer_stress_module_target.md \
  --qwen-scored work/probe/runs/nonexistent_qwen_transfer.jsonl
python3 work/probe/analyze_reliability_action_v3_overlay_stress_module_general_v1.py
python3 work/probe/analyze_reliability_action_v3_overlay_stress_module_general_v1.py \
  --input work/probe/reliability_action_v3_overlay_transfer_stress_blind_inputs.jsonl \
  --key work/probe/reliability_action_v3_overlay_transfer_stress_label_key.jsonl \
  --run-name reliability_action_v3_overlay_transfer_stress_module_general_v1 \
  --report outputs/doubt_tts_reliability_action_v3_overlay_transfer_stress_module_general_v1.md
python3 work/probe/build_reliability_action_v3_overlay_transfer_stress_v2.py
python3 work/probe/analyze_reliability_action_v3_overlay_stress_module_general_v1.py \
  --input work/probe/reliability_action_v3_overlay_transfer_stress_v2_blind_inputs.jsonl \
  --key work/probe/reliability_action_v3_overlay_transfer_stress_v2_label_key.jsonl \
  --run-name reliability_action_v3_overlay_transfer_stress_v2_module_general_v1 \
  --report outputs/doubt_tts_reliability_action_v3_overlay_transfer_stress_v2_module_general_v1.md
python3 work/probe/analyze_reliability_action_v3_overlay_stress_module_source_role_v2.py
python3 work/probe/analyze_reliability_action_v3_overlay_stress_module_source_role_v2.py \
  --input work/probe/reliability_action_v3_overlay_transfer_stress_blind_inputs.jsonl \
  --key work/probe/reliability_action_v3_overlay_transfer_stress_label_key.jsonl \
  --run-name reliability_action_v3_overlay_transfer_stress_module_source_role_v2 \
  --report outputs/doubt_tts_reliability_action_v3_overlay_transfer_stress_module_source_role_v2.md
python3 work/probe/analyze_reliability_action_v3_overlay_stress_module_source_role_v2.py \
  --input work/probe/reliability_action_v3_overlay_transfer_stress_v2_blind_inputs.jsonl \
  --key work/probe/reliability_action_v3_overlay_transfer_stress_v2_label_key.jsonl \
  --run-name reliability_action_v3_overlay_transfer_stress_v2_module_source_role_v2 \
  --report outputs/doubt_tts_reliability_action_v3_overlay_transfer_stress_v2_module_source_role_v2.md
python3 work/probe/build_reliability_action_v3_overlay_source_role_transfer_stress_v3.py
python3 work/probe/analyze_reliability_action_v3_overlay_stress_module_source_role_v2.py \
  --input work/probe/reliability_action_v3_overlay_source_role_transfer_stress_v3_blind_inputs.jsonl \
  --key work/probe/reliability_action_v3_overlay_source_role_transfer_stress_v3_label_key.jsonl \
  --run-name reliability_action_v3_overlay_source_role_transfer_stress_v3_module_source_role_v2 \
  --report outputs/doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v3_module_source_role_v2.md
python3 work/probe/analyze_reliability_action_v3_overlay_stress_module_source_role_v3.py
python3 work/probe/build_reliability_action_v3_overlay_source_role_transfer_stress_v4.py
python3 work/probe/analyze_reliability_action_v3_overlay_stress_module_source_role_v3.py \
  --input work/probe/reliability_action_v3_overlay_source_role_transfer_stress_v4_blind_inputs.jsonl \
  --key work/probe/reliability_action_v3_overlay_source_role_transfer_stress_v4_label_key.jsonl \
  --run-name reliability_action_v3_overlay_source_role_transfer_stress_v4_module_source_role_v3 \
  --report outputs/doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_module_source_role_v3.md
python3 work/probe/run_two_axis_live_route.py \
  --input work/probe/reliability_action_v3_overlay_source_role_transfer_stress_v4_blind_inputs.jsonl \
  --key work/probe/reliability_action_v3_overlay_source_role_transfer_stress_v4_label_key.jsonl \
  --model qwen3:14b \
  --url http://127.0.0.1:11436/api/generate \
  --run-name reliability_action_v3_overlay_source_role_transfer_stress_v4_qwen3_14b_overlap_guard \
  --policy overlap_guard \
  --sleep 0.02
python3 work/probe/run_two_axis_live_route.py \
  --input work/probe/reliability_action_v3_overlay_source_role_transfer_stress_v4_blind_inputs.jsonl \
  --key work/probe/reliability_action_v3_overlay_source_role_transfer_stress_v4_label_key.jsonl \
  --model gemma4:26b \
  --url http://127.0.0.1:11437/api/generate \
  --run-name reliability_action_v3_overlay_source_role_transfer_stress_v4_gemma4_26b_overlap_guard \
  --policy overlap_guard \
  --sleep 0.02
python3 work/probe/analyze_reliability_action_v3_cost_frontier.py
python3 work/probe/plan_reliability_action_v3_locked_eval.py
python3 work/probe/build_reliability_action_v3_manual_audit_queue.py
python3 work/probe/audit_doubt_tts_paper_draft_v3_numeric_claims.py
python3 work/probe/audit_doubt_tts_paper_draft_v4_numeric_claims.py
python3 work/probe/audit_doubt_tts_paper_draft_v5_numeric_claims.py
python3 work/probe/audit_doubt_tts_paper_draft_v6_numeric_claims.py
python3 work/probe/audit_doubt_tts_paper_draft_v7_numeric_claims.py
python3 work/probe/audit_doubt_tts_paper_draft_v8_numeric_claims.py
python3 work/probe/audit_doubt_tts_blueprint_v23_numeric_claims.py
python3 work/probe/audit_doubt_tts_blueprint_v24_numeric_claims.py
python3 work/probe/audit_doubt_tts_blueprint_v25_numeric_claims.py
python3 work/probe/audit_doubt_tts_blueprint_v26_numeric_claims.py
python3 work/probe/audit_doubt_tts_blueprint_v27_numeric_claims.py
python3 work/probe/audit_doubt_tts_blueprint_v28_numeric_claims.py
python3 work/probe/audit_doubt_tts_blueprint_v29_numeric_claims.py
```

For the Gemma transfer-v4 run, tunnel the Windows Ollama endpoint first:

```bash
ssh -N -L 11437:127.0.0.1:11434 trevor@192.168.1.151
```

If the tunnel drops mid-run, reopen it and rerun the same command; `run_two_axis_live_route.py` resumes from existing predictions for that run name.

Run the 30-row overlay stress live diagnostic through the remote/local Ollama
endpoint:

```bash
python3 work/probe/run_two_axis_live_route.py \
  --input work/probe/reliability_action_v3_overlay_stress_blind_inputs.jsonl \
  --key work/probe/reliability_action_v3_overlay_stress_label_key.jsonl \
  --model qwen3.5:9b \
  --url http://127.0.0.1:11436/api/generate \
  --run-name reliability_action_v3_overlay_stress_qwen35_9b_overlap_guard \
  --policy overlap_guard \
  --sleep 0.02
```

Key v3 results: keyword baseline 87/300, template-family majority 60/300, Gemma action-discriminating 201/300, Gemma overlap-guard 232/300, Gemma `overlap_if_either_rtp` hybrid 245/300, leave-template-family-out rule selector 245/300, learned policy-only selector 246/300, and cue-stem-heldout learned policy-only selector 246/300. The cue-stem split holds out all 20 variants of one question form per fold, so it is the stricter development check against simple cue-form memorization. The hostile source-family-heldout source-only slice is not a controller win: on the 105 source-required rows, Gemma overlap-guard gets 81/105 joint, while the policy-only controller gets 74/105 and the hybrid gets 73/105. Verifier/source overlay is method-shaped but not freeze-ready: v23 reaches 269/300, while v24 stress shows 17/30 static trigger failures, including 11/12 missed deterministic paraphrase positives and 5/24 raw source false positives. The first qwen3.5:9b overlap-guard live stress run gets 13/30 joint, 1/12 deterministic-verify compute, 6/6 retrieve-answer compute, and 0/2 false-premise validity. The after-inspection phrase module reaches 30/30 on original stress but collapses to 8/38 on transfer-v1. Broader module-general-v1 reaches 28/30 original stress and 38/38 transfer-v1, then drops to 23/38 on fresh transfer-v2 with source false-premise and source ambiguous still 0/4. Source-role v2 repairs transfer-v2 to 38/38 and gets 38/42 on source-heavy transfer-v3, with source false-premise 8/8, source answerable 8/8, and source ambiguous 3/6. Source-role v3 reaches 41/42 on transfer-v3 and 50/50 on fresh transfer-v4; qwen3:14b overlap-guard gets 34/50 on transfer-v4, with clarify 8/16 and deterministic_verify 0/8; Gemma4-26B overlap-guard gets 44/50 on transfer-v4, with validity 47/50, compute 44/50, ambiguity 16/16, source false-premise 5/8, and deterministic_verify 6/8. This is still generated/manual-audit-required development evidence, not locked paper data. Use this as an explicit caveat: the main claim is a mixed-distribution cost frontier and a falsifiable controller target, not a solved overlay.

Cost frontier: Gemma overlap-guard has mean diagnostic cost 2.38 with 17 wasted retrievals and 9 missed retrievals. Gemma `overlap_if_either_rtp` has mean cost 2.13 with 1 wasted retrieval and 19 missed retrievals. Gemma learned policy-only selector has mean cost 2.17 with 1 wasted retrieval and 15 missed retrievals. Cue-stem-heldout learned policy-only has mean cost 2.15 with 1 wasted retrieval and 17 missed retrievals. This is now the clearest controller-frontier framing.

Source/no-source slice accounting: Gemma overlap-guard wins source-required rows at 81/105 joint but falls to 151/195 on no-source rows and 27/45 direct compute. The Gemma learned policy selector gets 74/105 source-required joint, 172/195 no-source joint, and 45/45 direct compute. This is the cleanest explanation of the mixed-distribution frontier.

Current paper draft: `outputs/doubt_tts_paper_draft_v8.md`. Numeric audit:
`python3 work/probe/audit_doubt_tts_paper_draft_v8_numeric_claims.py`, which
writes `outputs/doubt_tts_paper_draft_v8_numeric_audit.md`. Draft v7 remains
the clean qwen-live source-role-v3 draft before the Gemma transfer-v4 baseline.

The manual-audit queue ranks all 300 rows by scientific risk. Its top 80 rows include all 60 retrieval-premise rows, 11 retrieve-answer rows, 8 direct controls, and 1 premise-check row. Audit those before treating any v3 controller result as more than development evidence.

Build the current schema-conformant seed benchmark from existing probe files:

```bash
python3 work/probe/prepare_preregistered_seed.py
```

Outputs:

- `work/probe/preregistered_benchmark_seed.jsonl`
- `outputs/doubt_tts_preregistered_seed_report.md`

Audit the seed against the planned locked benchmark distribution:

```bash
python3 work/probe/audit_preregistered_benchmark.py
```

Output:

- `outputs/doubt_tts_preregistered_gap_audit.md`

Build the 300-item locked-candidate benchmark:

```bash
python3 work/probe/build_preregistered_candidate.py
```

Outputs:

- `work/probe/preregistered_benchmark_candidate_locked.jsonl`
- `work/probe/preregistered_benchmark_extension.jsonl`
- `outputs/doubt_tts_preregistered_candidate_report.md`

Audit and schema-validate the candidate:

```bash
python3 work/probe/audit_preregistered_benchmark.py \
  --input work/probe/preregistered_benchmark_candidate_locked.jsonl \
  --report outputs/doubt_tts_preregistered_candidate_gap_audit.md

python3 work/probe/validate_benchmark_schema.py \
  --input work/probe/preregistered_benchmark_candidate_locked.jsonl
```

The candidate is suitable for harness development, but it is not paper-locked
until the manual evidence/source audit is complete.

Export blinded model-facing inputs and a separate label key:

```bash
python3 work/probe/export_blinded_candidate.py
```

Outputs:

- `work/probe/preregistered_benchmark_candidate_blind_inputs.jsonl`
- `work/probe/preregistered_benchmark_candidate_label_key.jsonl`
- `outputs/doubt_tts_preregistered_candidate_blind_export.md`

For route-only model evaluations, the model should see the blind input file
only. The label key is for scoring after predictions are written.

Score blinded route predictions:

```bash
python3 work/probe/score_blinded_route_predictions.py \
  --predictions work/probe/runs/candidate_model_predictions.jsonl
```

Prediction rows need at least `id` and `predicted_route`.

Run blinded question-only route baselines:

```bash
python3 work/probe/run_blinded_route_baselines.py
```

Outputs:

- `work/probe/runs/candidate_blinded_route_baseline_predictions.jsonl`
- `work/probe/runs/candidate_blinded_route_baseline_scored_results.jsonl`
- `outputs/doubt_tts_candidate_blinded_route_baselines.md`

These baselines see only the blinded input rows, not labels, evidence, source
metadata, or subtype labels.

Analyze blinded route baselines with Wilson intervals and exact paired tests:

```bash
python3 work/probe/analyze_blinded_route_stats.py
```

Outputs:

- `work/probe/runs/candidate_blinded_route_stats.json`
- `outputs/doubt_tts_candidate_blinded_route_stats.md`

This is the reviewer-facing sanity check for whether the candidate is solved by
constant route policies or brittle question-only heuristics.

Audit the validity/action axis split:

```bash
python3 work/probe/audit_route_taxonomy_axes.py
```

Outputs:

- `work/probe/route_taxonomy_axis_audit.json`
- `outputs/doubt_tts_route_taxonomy_axis_audit.md`

This is the current benchmark-design guardrail: some rows are both
false-premise and retrieval-backed, so final routing claims should use the
two-axis validity/action protocol.

Run and key-score two-axis deterministic baselines:

```bash
python3 work/probe/run_two_axis_baselines.py

python3 work/probe/score_two_axis_predictions.py \
  --predictions work/probe/runs/candidate_two_axis_baseline_predictions.jsonl \
  --out work/probe/runs/candidate_two_axis_baseline_key_scored_results.jsonl \
  --stats work/probe/runs/candidate_two_axis_baseline_key_score_stats.json \
  --report outputs/doubt_tts_candidate_two_axis_key_score_report.md \
  --compare two_axis_question_only_router single_route_question_only_projection \
  --compare two_axis_question_only_router always_false_premise_check
```

Outputs:

- `outputs/doubt_tts_candidate_two_axis_baselines.md`
- `outputs/doubt_tts_candidate_two_axis_key_score_report.md`
- `work/probe/runs/candidate_two_axis_baseline_key_score_stats.json`

The key-scored report is the preferred citation because it uses the same
separate label key as a live model run.

The scorer also accepts multiple prediction files, so a live run can be paired
against baselines on the same rows:

```bash
python3 work/probe/score_two_axis_predictions.py \
  --predictions work/probe/runs/candidate_two_axis_baseline_predictions.jsonl \
                work/probe/runs/<live_run>_predictions.jsonl \
  --compare <live_method_name> two_axis_question_only_router
```

Audit blind exports for hard label/source leakage:

```bash
python3 work/probe/audit_blind_exports.py
```

Outputs:

- `work/probe/blind_export_leakage_audit.json`
- `outputs/doubt_tts_blind_export_leakage_audit.md`

This checks field allowlists, input hashes, duplicate ids, and blind/key
alignment for the full 300-row export and the staged 62/161-row exports. It
does not prove the question text lacks lexical shortcuts; that is what the
question-only baselines measure.

Run the label/evidence quality audit:

```bash
python3 work/probe/audit_candidate_quality.py
```

Output:

- `outputs/doubt_tts_preregistered_candidate_quality_audit.md`

Run the deterministic verifier derivation audit:

```bash
python3 work/probe/audit_verifier_derivations.py
```

Outputs:

- `work/probe/preregistered_candidate_verifier_audit.jsonl`
- `outputs/doubt_tts_preregistered_candidate_verifier_audit.md`

Verified verifier rows are removed from the manual paper-lock queue.

Run the automated source/evidence audit:

```bash
python3 work/probe/audit_candidate_sources.py
```

Outputs:

- `work/probe/preregistered_candidate_source_audit.jsonl`
- `outputs/doubt_tts_preregistered_candidate_source_audit.md`

This fetches and caches Wikipedia summaries for rows with `source.expected_title`.
It is a weak source-hook check, not a substitute for final manual evidence audit.

Build the prioritized manual paper-lock audit queue:

```bash
python3 work/probe/build_manual_audit_queue.py
```

Outputs:

- `work/probe/preregistered_candidate_manual_audit_queue.jsonl`
- `outputs/doubt_tts_preregistered_candidate_manual_audit_queue.md`

This ranks the remaining manual audit work into source blockers, sourced
false-premise contradiction checks, retrieval/source trace checks, unsourced
answer/verifier checks, unsourced false-premise checks, and ambiguity checks.

Build automated source suggestions for unsourced queued rows:

```bash
python3 work/probe/suggest_candidate_sources.py
```

Outputs:

- `work/probe/preregistered_candidate_source_suggestions.jsonl`
- `outputs/doubt_tts_preregistered_candidate_source_suggestions.md`

This prepares likely evidence pages and weak support signals. It is not final
source validation and can be affected by Wikipedia rate limits.

Build a full-extract evidence pack for priority-1 audit rows:

```bash
python3 work/probe/build_p1_audit_pack.py
```

Outputs:

- `work/probe/preregistered_candidate_p1_audit_pack.jsonl`
- `outputs/doubt_tts_preregistered_candidate_p1_audit_pack.md`

This does not paper-lock rows. It separates summary-only alias misses from rows
that still need human contradiction/nonexistence judgment.

Audit temporal freshness for recent/future event wording:

```bash
python3 work/probe/audit_temporal_freshness.py
```

Outputs:

- `work/probe/preregistered_candidate_temporal_freshness_audit.jsonl`
- `outputs/doubt_tts_preregistered_candidate_temporal_freshness_audit.md`

Rows marked `manual_review` are demoted from automation-supported subsets by
the evidence-readiness builder until their wording is repaired or manually
justified.

Build the evidence-readiness map and subset exports:

```bash
python3 work/probe/build_candidate_evidence_readiness.py
```

Outputs:

- `work/probe/preregistered_candidate_evidence_readiness.jsonl`
- `outputs/doubt_tts_preregistered_candidate_evidence_readiness.md`
- `work/probe/preregistered_candidate_automation_supported_blind_inputs.jsonl`
- `work/probe/preregistered_candidate_automation_supported_label_key.jsonl`
- `work/probe/preregistered_candidate_evidence_pack_blind_inputs.jsonl`
- `work/probe/preregistered_candidate_evidence_pack_label_key.jsonl`

Run blinded baselines on the automation-supported subset:

```bash
python3 work/probe/run_blinded_route_baselines.py \
  --input work/probe/preregistered_candidate_automation_supported_blind_inputs.jsonl \
  --key work/probe/preregistered_candidate_automation_supported_label_key.jsonl \
  --out work/probe/runs/candidate_automation_supported_blinded_route_baseline_predictions.jsonl \
  --scored-out work/probe/runs/candidate_automation_supported_blinded_route_baseline_scored_results.jsonl \
  --report outputs/doubt_tts_candidate_automation_supported_blinded_route_baselines.md

python3 work/probe/analyze_blinded_route_stats.py \
  --scored work/probe/runs/candidate_automation_supported_blinded_route_baseline_scored_results.jsonl \
  --out work/probe/runs/candidate_automation_supported_blinded_route_stats.json \
  --report outputs/doubt_tts_candidate_automation_supported_blinded_route_stats.md
```

Run local offline baselines on the candidate:

```bash
python3 work/probe/run_candidate_baselines.py
```

Outputs:

- `work/probe/runs/candidate_offline_baselines_results.jsonl`
- `outputs/doubt_tts_candidate_offline_baselines.md`

These are benchmark sanity checks, not model results.

Run the adversarial question-text leakage baseline:

```bash
python3 work/probe/run_text_leakage_baseline.py
```

Outputs:

- `work/probe/runs/text_leakage_baseline_stats.json`
- `outputs/doubt_tts_text_leakage_baseline.md`

This trains pure Naive Bayes classifiers over blinded question text only,
including cue-masked and subtype-held-out variants. High random-CV scores are
evidence of template leakage, not model reasoning. Treat family-held-out,
subtype-held-out, and adversarial paraphrase splits as required before making
semantic route-understanding claims.

Export seed/candidate family blind splits:

```bash
python3 work/probe/export_family_split_blinds.py
python3 work/probe/audit_blind_exports.py
```

Outputs:

- `work/probe/preregistered_candidate_seed_family_blind_inputs.jsonl`
- `work/probe/preregistered_candidate_seed_family_label_key.jsonl`
- `work/probe/preregistered_candidate_candidate_family_blind_inputs.jsonl`
- `work/probe/preregistered_candidate_candidate_family_label_key.jsonl`
- `outputs/doubt_tts_candidate_family_split_exports.md`

Use these to report template-family transfer separately from random folds.

Build deterministic cue-ablation paraphrases:

```bash
python3 work/probe/build_paraphrase_stress_set.py
python3 work/probe/audit_blind_exports.py
python3 work/probe/run_text_leakage_baseline.py
```

Outputs:

- `work/probe/preregistered_candidate_paraphrase_stress_locked.jsonl`
- `work/probe/preregistered_candidate_paraphrase_stress_blind_inputs.jsonl`
- `work/probe/preregistered_candidate_paraphrase_stress_label_key.jsonl`
- `outputs/doubt_tts_candidate_paraphrase_stress_export.md`

This is a cheap stress surface, not a human-validated paraphrase benchmark. The
current text-only baseline transfers strongly from original to deterministic
paraphrases, so human/adversarial paraphrases are still required for semantic
claims.

Build the counterbalanced cue stress split:

```bash
python3 work/probe/build_counterbalanced_cue_stress_set.py
python3 work/probe/audit_blind_exports.py
python3 work/probe/run_text_leakage_baseline.py
```

Outputs:

- `work/probe/preregistered_candidate_counterbalanced_cue_stress_locked.jsonl`
- `work/probe/preregistered_candidate_counterbalanced_cue_stress_blind_inputs.jsonl`
- `work/probe/preregistered_candidate_counterbalanced_cue_stress_label_key.jsonl`
- `outputs/doubt_tts_candidate_counterbalanced_cue_stress_export.md`

This is a 26-row synthetic repair scaffold that reuses `did`, scheduled-host,
winner/award, modal, and `if` cue families across route/validity/action labels.
It is useful because text-only shortcut performance drops sharply on it, but it
still needs manual evidence review before paper-lock.

Audit lexical/template confounds:

```bash
python3 work/probe/audit_template_confounds.py
python3 work/probe/summarize_evidence.py
```

Outputs:

- `work/probe/runs/template_confound_audit.json`
- `outputs/doubt_tts_template_confound_audit.md`

Use this to identify high-purity cue families that need counterexamples before
paper-locking the benchmark.

Run the mock-backend route plumbing check on the candidate:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/preregistered_benchmark_candidate_locked.jsonl \
  --route-only \
  --backend mock \
  --out work/probe/runs/candidate_mock_route_results.jsonl \
  --report outputs/doubt_tts_candidate_mock_route_report.md
```

Outputs:

- `work/probe/runs/candidate_mock_route_results.jsonl`
- `outputs/doubt_tts_candidate_mock_route_report.md`

This checks that the main probe harness understands the candidate schema and all
five route labels, including `retrieval_needed`. It is not model evidence.

Run the live Ollama route-only candidate evaluation when the GPU box or local
Ollama endpoint is available:

```bash
OLLAMA_URL=http://127.0.0.1:11435/api/generate \
OLLAMA_MODEL=qwen3.5:9b \
work/probe/run_candidate_live_route.sh
```

Optional smoke subset:

```bash
LIMIT=30 work/probe/run_candidate_live_route.sh
```

Automation-supported staged subset:

```bash
RUN_NAME=candidate_automation_supported_qwen_strict \
DATA=work/probe/preregistered_candidate_automation_supported_blind_inputs.jsonl \
KEY=work/probe/preregistered_candidate_automation_supported_label_key.jsonl \
work/probe/run_candidate_live_route.sh
```

Evidence-pack staged subset:

```bash
RUN_NAME=candidate_evidence_pack_qwen_strict \
DATA=work/probe/preregistered_candidate_evidence_pack_blind_inputs.jsonl \
KEY=work/probe/preregistered_candidate_evidence_pack_label_key.jsonl \
work/probe/run_candidate_live_route.sh
```

Outputs:

- `work/probe/runs/${RUN_NAME}_route_results.jsonl`
- `outputs/doubt_tts_${RUN_NAME}_route_report.md`
- `work/probe/runs/${RUN_NAME}_blinded_predictions.jsonl`
- `work/probe/runs/${RUN_NAME}_blinded_scored_results.jsonl`
- `outputs/doubt_tts_${RUN_NAME}_blinded_score_report.md`
- `outputs/doubt_tts_${RUN_NAME}_blinded_route_stats.md`

Preferred live two-axis candidate evaluation:

```bash
OLLAMA_URL=http://127.0.0.1:11435/api/generate \
OLLAMA_MODEL=qwen3.5:9b \
python3 work/probe/run_two_axis_live_route.py
```

The default prompt is intentionally neutral about retrieval cost. It may classify
validity well while routing event facts to `direct_answer`. To test a
retrieval-favoring cost policy, set:

```bash
ROUTE_POLICY=retrieval_strict
```

That policy reserves `deterministic_verify` for math/calendar/logic and pushes
specific event, award, sport, host, winner, recent, future, and scheduled facts
toward retrieval. It is an ablation, not the final controller; it can over-retrieve
stable direct-answer rows.

There is also an action-discriminating policy:

```bash
ROUTE_POLICY=action_discriminating
```

It explicitly distinguishes direct answers, plain premise checks,
retrieval-backed answers, and retrieval-backed premise checks. On the current
161-row evidence-pack split it is the strongest live prompt so far, but still
misses the deterministic question-only baseline because it under-routes
retrieval rows.

Automation-supported staged subset:

```bash
RUN_NAME=candidate_automation_supported_two_axis_qwen_strict \
DATA=work/probe/preregistered_candidate_automation_supported_blind_inputs.jsonl \
KEY=work/probe/preregistered_candidate_automation_supported_label_key.jsonl \
python3 work/probe/run_two_axis_live_route.py
```

Retrieval-strict staged subset:

```bash
RUN_NAME=candidate_automation_supported_two_axis_qwen_retrieval_strict \
DATA=work/probe/preregistered_candidate_automation_supported_blind_inputs.jsonl \
KEY=work/probe/preregistered_candidate_automation_supported_label_key.jsonl \
ROUTE_POLICY=retrieval_strict \
python3 work/probe/run_two_axis_live_route.py
```

Evidence-pack staged subset:

```bash
RUN_NAME=candidate_evidence_pack_two_axis_qwen_strict \
DATA=work/probe/preregistered_candidate_evidence_pack_blind_inputs.jsonl \
KEY=work/probe/preregistered_candidate_evidence_pack_label_key.jsonl \
python3 work/probe/run_two_axis_live_route.py
```

Live prediction rows are scored against the separate label key. Positive
evidence must beat the two-axis question-only baseline on joint accuracy and
improve false-premise validity recall without collapsing answerable specificity.

Run the offline two-stage policy recombination diagnostic after base and
retrieval-strict evidence-pack live runs exist:

```bash
python3 work/probe/run_two_stage_policy_ablation.py
```

Outputs:

- `work/probe/runs/candidate_evidence_pack_two_stage_policy_ablation_predictions.jsonl`
- `work/probe/runs/candidate_evidence_pack_two_stage_policy_ablation_scored_results.jsonl`
- `work/probe/runs/candidate_evidence_pack_two_stage_policy_ablation_stats.json`
- `outputs/doubt_tts_candidate_evidence_pack_two_stage_policy_ablation.md`

This is not a new model run. It diagnoses whether the 161-row failures come
from validity prediction, action prediction, or their coupling.

Analyze prompt-policy complementarity and family transfer:

```bash
python3 work/probe/analyze_policy_selector_diagnostics.py
```

Outputs:

- `work/probe/runs/candidate_evidence_pack_policy_selector_diagnostics.json`
- `outputs/doubt_tts_candidate_evidence_pack_policy_selector_diagnostics.md`

This is also diagnostic. It measures oracle selection across the live prompt
policies and checks whether selecting the best seed-family prompt transfers to
candidate-family rows, and vice versa.

Optional Ollama smoke test:

```bash
python3 work/probe/doubt_probe.py \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://localhost:11435/api/generate \
  --per-family 2 \
  --methods greedy doubt_tts \
  --out work/probe/runs/ollama_results.jsonl \
  --report work/probe/runs/ollama_report.md
```

Full live Qwen mixed-set run:

```bash
python3 work/probe/doubt_probe.py \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --methods greedy self_consistency random_control doubt_tts \
  --out work/probe/runs/qwen_36_results.jsonl \
  --report work/probe/runs/qwen_36_report.md
```

Hard false-premise run:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/hard_false_premise_questions.jsonl \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --methods greedy self_consistency random_control doubt_tts \
  --out work/probe/runs/qwen_hard_false_results.jsonl \
  --report work/probe/runs/qwen_hard_false_report.md
```

Adaptive-oracle upper-bound run:

```bash
python3 work/probe/doubt_probe.py \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --methods adaptive_oracle \
  --out work/probe/runs/qwen_36_adaptive_oracle_results.jsonl \
  --report work/probe/runs/qwen_36_adaptive_oracle_report.md
```

Real adaptive-router run:

```bash
python3 work/probe/doubt_probe.py \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --methods adaptive_router \
  --out work/probe/runs/qwen_36_adaptive_router_results.jsonl \
  --report work/probe/runs/qwen_36_adaptive_router_report.md
```

Route-only strict prompt evaluation:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/router_eval_questions.jsonl \
  --route-only \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --strict-route \
  --out work/probe/runs/qwen_route_eval_strict_results.jsonl \
  --report work/probe/runs/qwen_route_eval_strict_report.md
```

False-premise subtype route evaluation:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/false_premise_subtype_questions.jsonl \
  --route-only \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --strict-route \
  --out work/probe/runs/qwen_false_premise_subtypes_strict_results.jsonl \
  --report work/probe/runs/qwen_false_premise_subtypes_strict_report.md
```

Presupposition-decomposition route evaluation:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/false_premise_subtype_questions.jsonl \
  --route-only \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --decompose-route \
  --out work/probe/runs/qwen_false_premise_subtypes_decompose_results.jsonl \
  --report work/probe/runs/qwen_false_premise_subtypes_decompose_report.md
```

Cascaded route evaluation:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/router_eval_questions.jsonl \
  --route-only \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --cascade-route \
  --out work/probe/runs/qwen_route_eval_cascade_results.jsonl \
  --report work/probe/runs/qwen_route_eval_cascade_report.md
```

Cascade plus verifier answer run:

```bash
python3 work/probe/doubt_probe.py \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --cascade-route \
  --use-verifier \
  --methods adaptive_router \
  --out work/probe/runs/qwen_36_adaptive_router_cascade_verifier_results.jsonl \
  --report work/probe/runs/qwen_36_adaptive_router_cascade_verifier_report.md
```

Routed challenge-control ablation:

```bash
python3 work/probe/doubt_probe.py \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --cascade-route \
  --use-verifier \
  --methods adaptive_router adaptive_router_random_control \
  --out work/probe/runs/qwen_36_adaptive_router_cascade_vs_control_results.jsonl \
  --report work/probe/runs/qwen_36_adaptive_router_cascade_vs_control_report.md
```

Response-taxonomy benchmark:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/response_taxonomy_questions.jsonl \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --cascade-route \
  --methods adaptive_router adaptive_router_random_control \
  --out work/probe/runs/qwen_response_taxonomy_cascade_vs_control_results.jsonl \
  --report work/probe/runs/qwen_response_taxonomy_cascade_vs_control_report.md
```

Event-gated response-taxonomy benchmark:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/response_taxonomy_questions.jsonl \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --cascade-route \
  --event-gate \
  --methods adaptive_router adaptive_router_random_control \
  --out work/probe/runs/qwen_response_taxonomy_event_gate_vs_control_results.jsonl \
  --report work/probe/runs/qwen_response_taxonomy_event_gate_vs_control_report.md
```

Event-contrast route stress test:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/event_contrast_route_questions.jsonl \
  --route-only \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --cascade-route \
  --event-gate \
  --out work/probe/runs/qwen_event_contrast_route_event_gate_v3_results.jsonl \
  --report work/probe/runs/qwen_event_contrast_route_event_gate_v3_report.md
```

Table-backed event-verifier upper-bound:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/event_contrast_route_questions.jsonl \
  --route-only \
  --event-verifier-only \
  --out work/probe/runs/table_event_verifier_route_results.jsonl \
  --report work/probe/runs/table_event_verifier_route_report.md
```

Held-out source-hinted retrieval event-verifier:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/heldout_event_retrieval_questions.jsonl \
  --route-only \
  --retrieval-event-verifier-only \
  --out work/probe/runs/heldout_retrieval_event_verifier_route_results.jsonl \
  --report work/probe/runs/heldout_retrieval_event_verifier_route_report.md
```

Held-out inferred-source retrieval event-verifier:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/heldout_event_retrieval_questions.jsonl \
  --route-only \
  --retrieval-event-verifier-only \
  --ignore-event-source-title \
  --out work/probe/runs/heldout_retrieval_auto_source_event_verifier_route_results.jsonl \
  --report work/probe/runs/heldout_retrieval_auto_source_event_verifier_route_report.md
```

Held-out table baseline:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/heldout_event_retrieval_questions.jsonl \
  --route-only \
  --event-verifier-only \
  --out work/probe/runs/heldout_table_event_verifier_route_results.jsonl \
  --report work/probe/runs/heldout_table_event_verifier_route_report.md
```

Messy source-selection probe with query fixture:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/messy_event_search_questions.jsonl \
  --route-only \
  --retrieval-event-verifier-only \
  --search-event-source \
  --use-event-search-query \
  --out work/probe/runs/messy_retrieval_query_fixture_event_verifier_route_results.jsonl \
  --report work/probe/runs/messy_retrieval_query_fixture_event_verifier_route_report.md
```

Messy source-selection probe with local cached evidence index:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/messy_event_search_questions.jsonl \
  --route-only \
  --retrieval-event-verifier-only \
  --local-event-source-index \
  --out work/probe/runs/messy_retrieval_local_index_event_verifier_route_results.jsonl \
  --report work/probe/runs/messy_retrieval_local_index_event_verifier_route_report.md
```

Strict router plus lightweight verifier:

```bash
python3 work/probe/doubt_probe.py \
  --backend ollama \
  --ollama-model qwen3.5:9b \
  --ollama-url http://127.0.0.1:11435/api/generate \
  --strict-route \
  --use-verifier \
  --methods adaptive_router \
  --out work/probe/runs/qwen_36_adaptive_router_strict_verifier_results.jsonl \
  --report work/probe/runs/qwen_36_adaptive_router_strict_verifier_report.md
```

For `qwen3.5:9b`, the harness prepends `/no_think`, sends `think:false`,
and caps `num_ctx` at 512. Without those, Ollama may return only thinking
text or fail under context pressure.

`adaptive_oracle` uses dataset family labels and is only an upper-bound
diagnostic. It is useful for deciding whether routing is worth pursuing; it is
not evidence for a deployable router.

`adaptive_router` is non-oracle: it asks the model to classify the route first
and probes only false-premise/ambiguous routes.

`--strict-route` uses a priority-rule router prompt. In the 48-item route eval,
it fixes ambiguity/verifier routing for Qwen but still misses subtle
false-premise relation/date cases.

`--use-verifier` enables a narrow deterministic verifier for the pilot's simple
arithmetic, counting-total, calendar, and syllogism templates. It is
intentionally not a general verifier.

`--cascade-route` runs the strict router first. It preserves `verifier` and
`ambiguous` routes, then runs presupposition decomposition only for the
ordinary/false-premise branch. This avoids the decompose-only regression where a
calendar-offset question was routed as ordinary and skipped the verifier.
`--cascade-fp-threshold` defaults to `0.75`; when strict says `ordinary`, a
decomposition false-premise override below that confidence is vetoed.

`--event-gate` adds a specialized event-existence check after cascade routing
would otherwise return `ordinary` for an event-like question. It targets
non-existent Olympics/World Cup/award/event-year failures.

On the 72-item event-contrast route stress test, `--event-gate` improves
false-premise recall while preserving most ordinary specificity. The final v3
run uses current-date-conditioned route prompts and route-parser hardening; its
remaining misses are event-calendar and winner/host-relation facts, which should
be retrieval-backed or verifier-backed rather than handled by more prompt text.

`--event-verifier-only` runs a narrow table-backed event verifier without
Ollama. It reaches 72/72 on the current event-contrast route set, so treat it as
an upper bound showing that event facts should be verified. It is not evidence
that the hand-built table generalizes.

`--retrieval-event-verifier-only` runs a retrieval verifier for the fresh
held-out event set. By default, each item names a Wikipedia source page; with
`--ignore-event-source-title`, the harness infers clean event titles from the
question before fetching/caching summaries. The verifier applies small
finite-state checks for opponent, location, award category, and sport/action
vocabulary. On `heldout_event_retrieval_questions.jsonl`, the original table
gets 21/32 while both retrieval modes get 32/32. This still leaves messy
search/source selection untested.

`--search-event-source --use-event-search-query` is a query-fixture condition
for `messy_event_search_questions.jsonl`. It deliberately assumes query/source
selection has been solved and tests only whether the verifier still handles
messy phrasing. The result is 24/24; table and clean-title inference baselines
are 12/24. Do not treat this as live open-domain search evidence.

`--local-event-source-index` selects a source from cached Wikipedia summaries
instead of using source-title hints. On `messy_event_search_questions.jsonl`, it
gets 24/24 source-selection accuracy and 24/24 route accuracy. This is still a
small local corpus, not open-web search.

The mock backend is not evidence about a real model. It is a fixture that verifies
the protocol path: question schema, answer normalization, challenge sampling,
answer survival, entropy, doubt yield, overconfidence gap, and report generation.

## Reliability-action v2 benchmark hardening

The v2 benchmark path uses `outputs/doubt_tts_benchmark_schema_v2.json` and the
two-axis labels `validity` plus `compute_action`.

The current 300-row v2 scaffold is structurally useful but not paper evidence:

```bash
python3 work/probe/build_reliability_action_candidate_v2.py
python3 work/probe/validate_benchmark_schema.py \
  --schema outputs/doubt_tts_benchmark_schema_v2.json \
  --input work/probe/reliability_action_benchmark_v2_candidate_locked.jsonl
python3 work/probe/export_reliability_action_candidate_v2.py
python3 work/probe/run_reliability_action_v2_baselines.py
```

`export_reliability_action_candidate_v2.py` must keep opaque model-facing IDs.
The original semantic row ID is only in the private label key as `source_id`.
Semantic IDs in blind files are a leakage bug.

The current hardening scaffold is the cue-balanced 90-row slice:

```bash
python3 work/probe/build_reliability_action_cue_balanced_slice_v2.py
python3 work/probe/validate_benchmark_schema.py \
  --schema outputs/doubt_tts_benchmark_schema_v2.json \
  --input work/probe/reliability_action_cue_balanced_slice_v2_locked.jsonl
python3 work/probe/export_reliability_action_candidate_v2.py \
  --input work/probe/reliability_action_cue_balanced_slice_v2_locked.jsonl \
  --blind-out work/probe/reliability_action_cue_balanced_slice_v2_blind_inputs.jsonl \
  --key-out work/probe/reliability_action_cue_balanced_slice_v2_label_key.jsonl \
  --manifest outputs/doubt_tts_reliability_action_cue_balanced_slice_v2_blind_export.md \
  --id-prefix racue
python3 work/probe/run_reliability_action_cue_balanced_baselines.py
```

Current cue-balanced result: constants and cue-family-only are 15/90; legacy
keyword question-only routing is 27/90 after verifier-cue hardening. This is the
template for a 300-row cue-balanced v3 candidate. Do not spend GPU/live model
compute on the current 300-row scaffold until cue/family leakage is reduced.

Completed live model checks on the cue-balanced slice:

```bash
OLLAMA_NUM_CTX=2048 python3 work/probe/run_two_axis_live_route.py \
  --input work/probe/reliability_action_cue_balanced_slice_v2_blind_inputs.jsonl \
  --key work/probe/reliability_action_cue_balanced_slice_v2_label_key.jsonl \
  --model qwen3.5:9b \
  --url http://127.0.0.1:11435/api/generate \
  --policy action_discriminating \
  --run-name reliability_action_cue_balanced_qwen_action_discriminating

OLLAMA_NUM_CTX=2048 python3 work/probe/run_two_axis_live_route.py \
  --input work/probe/reliability_action_cue_balanced_slice_v2_blind_inputs.jsonl \
  --key work/probe/reliability_action_cue_balanced_slice_v2_label_key.jsonl \
  --model gemma4:26b \
  --url http://127.0.0.1:11435/api/generate \
  --policy action_discriminating \
  --run-name reliability_action_cue_balanced_gemma4_26b_action_discriminating
```

Qwen3.5-9B action-discriminating gets 51/90 joint; Gemma4-26B
action-discriminating gets 61/90. Both beat the 27/90 keyword shortcut baseline,
but retrieval actions remain weak, especially retrieve-then-premise-check.

The 300-row v3 scaffold extends this construction to the preregistered counts:

```bash
python3 work/probe/build_reliability_action_cue_balanced_candidate_v3.py
python3 work/probe/validate_benchmark_schema.py \
  --schema outputs/doubt_tts_benchmark_schema_v2.json \
  --input work/probe/reliability_action_cue_balanced_candidate_v3_locked.jsonl
python3 work/probe/export_reliability_action_candidate_v2.py \
  --input work/probe/reliability_action_cue_balanced_candidate_v3_locked.jsonl \
  --blind-out work/probe/reliability_action_cue_balanced_candidate_v3_blind_inputs.jsonl \
  --key-out work/probe/reliability_action_cue_balanced_candidate_v3_label_key.jsonl \
  --manifest outputs/doubt_tts_reliability_action_cue_balanced_candidate_v3_blind_export.md \
  --id-prefix rav3
python3 work/probe/run_reliability_action_cue_balanced_baselines.py \
  --blind work/probe/reliability_action_cue_balanced_candidate_v3_blind_inputs.jsonl \
  --key work/probe/reliability_action_cue_balanced_candidate_v3_label_key.jsonl \
  --predictions work/probe/runs/reliability_action_cue_balanced_candidate_v3_baseline_predictions.jsonl \
  --scored work/probe/runs/reliability_action_cue_balanced_candidate_v3_baseline_scored_results.jsonl \
  --stats work/probe/runs/reliability_action_cue_balanced_candidate_v3_baseline_stats.json \
  --report outputs/doubt_tts_reliability_action_cue_balanced_candidate_v3_baselines.md \
  --title "Reliability-Action Cue-Balanced Candidate v3 Baselines"
```

Completed v3 live runs:

```bash
OLLAMA_NUM_CTX=2048 python3 work/probe/run_two_axis_live_route.py \
  --input work/probe/reliability_action_cue_balanced_candidate_v3_blind_inputs.jsonl \
  --key work/probe/reliability_action_cue_balanced_candidate_v3_label_key.jsonl \
  --model qwen3.5:9b \
  --url http://127.0.0.1:11435/api/generate \
  --policy action_discriminating \
  --run-name reliability_action_cue_balanced_v3_qwen_action_discriminating

OLLAMA_NUM_CTX=2048 python3 work/probe/run_two_axis_live_route.py \
  --input work/probe/reliability_action_cue_balanced_candidate_v3_blind_inputs.jsonl \
  --key work/probe/reliability_action_cue_balanced_candidate_v3_label_key.jsonl \
  --model gemma4:26b \
  --url http://127.0.0.1:11435/api/generate \
  --policy action_discriminating \
  --run-name reliability_action_cue_balanced_v3_gemma4_26b_action_discriminating

OLLAMA_NUM_CTX=2048 python3 work/probe/run_two_axis_live_route.py \
  --input work/probe/reliability_action_cue_balanced_candidate_v3_blind_inputs.jsonl \
  --key work/probe/reliability_action_cue_balanced_candidate_v3_label_key.jsonl \
  --model qwen3.5:9b \
  --url http://127.0.0.1:11435/api/generate \
  --policy overlap_guard \
  --run-name reliability_action_cue_balanced_v3_qwen_overlap_guard

OLLAMA_NUM_CTX=2048 python3 work/probe/run_two_axis_live_route.py \
  --input work/probe/reliability_action_cue_balanced_candidate_v3_blind_inputs.jsonl \
  --key work/probe/reliability_action_cue_balanced_candidate_v3_label_key.jsonl \
  --model gemma4:26b \
  --url http://127.0.0.1:11435/api/generate \
  --policy overlap_guard \
  --run-name reliability_action_cue_balanced_v3_gemma4_26b_overlap_guard

python3 work/probe/analyze_reliability_action_v3_results.py
python3 work/probe/analyze_reliability_action_v3_hybrids.py
python3 work/probe/analyze_reliability_action_v3_family_heldout_selector.py
python3 work/probe/analyze_reliability_action_v3_learned_selector.py
```

Current v3 results: keyword baseline 87/300, oracle template-family majority
60/300, Qwen action-discriminating 167/300, Qwen overlap-guard 192/300,
Gemma action-discriminating 201/300, and Gemma overlap-guard 232/300.
Overlap-guard improves Qwen over Qwen action by +25 joint items and Gemma over
Gemma action by +31 joint items. The key frontier is Gemma overlap-guard:
retrieve-then-premise-check improves from 19/60 compute and 6/60 joint to 52/60
compute and 47/60 joint, but direct-answer compute drops from 45/45 to 27/45.
Treat this as a controller target, not a solved global prompt.

Current hybrid diagnostic: `gemma4:26b:hybrid_overlap_if_either_rtp`
selects overlap-guard on 69/300 rows when either Gemma policy predicts
`retrieve_then_premise_check`. It reaches 245/300 joint, 260/300 validity,
250/300 compute, preserves 45/45 direct-answer compute, and keeps 47/60
retrieval-premise joint. Leave-template-family-out rule selection over 45
template families picks the same rule in all folds. This is development-only
because v3 is generated and unaudited; the next paper-grade step is a frozen
held-out controller over audited rows.

Current learned selector diagnostic: the pure policy-output Naive Bayes selector
trained on the other 44 template families reaches 246/300 joint, 260/300
validity, and 251/300 compute with the same 45/45 direct-answer compute and
47/60 retrieval-premise joint profile. Question/reason feature variants reach up
to 252/300 but are cue-riskier on generated v3. The cue-stem-heldout variant
holds out all 20 variants of one question form per fold; the policy-only
selector still reaches 246/300 joint, 260/300 validity, and 251/300 compute,
while the policy+reason+question variant reaches 250/300.

Current source-family-heldout diagnostic: `analyze_reliability_action_v3_source_family_heldout_selector.py`
holds out one machine-built source/event family at a time and evaluates only the
105 source-required rows. Gemma overlap-guard gets 81/105 joint, the
policy-only controller gets 74/105, and the hybrid gets 73/105. This is the
strongest caveat against overselling the selector: on rows where sources are
always required, always-overlap is the right slice baseline.

Current source-required slice diagnostic: `analyze_reliability_action_v3_source_required_slices.py`
summarizes source-required vs no-source-required rows for the main controllers.
It is the companion to the hostile source-family result: overlap wins
source-required rows, while policy controllers recover no-source specificity.
