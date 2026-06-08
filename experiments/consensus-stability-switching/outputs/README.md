# Cluster Selectability Research Sprint

**Status:** June 3, 2026. This folder contains the current research artifacts for the original Consensus-Stability Switching sprint.

## Best Current Pitch

The original CSS/router idea has been sharpened into:

> Repeated sampling creates large answer-cluster coverage, but current selectors often cannot surface the correct cluster. The resulting **cluster selectability gap** should be measured directly and attacked with calibrated failure detection plus stronger cluster-level evidence.

The latest method-facing version is adaptive depth: predict whether a missed correct cluster is likely within top-5, top-10, top-20, or nowhere, then spend compact verifier budget at the cheapest useful depth. Treat v32 as the single-split method result, v33 as the robustness result, v85-v91 as the projected transfer/quality-bound stack, v92-v94 as the measured local full-cluster verifier/interface boundary, v95-v118 as the selector/calibration/local-feature stopline stack, and v119-v130 as the new pairwise router-judge path showing that a narrower two-answer adjudication interface can recover accepted auxiliary-router candidates with much better regression behavior than full-cluster local verification. v122 is the natural-rate denominator correction: the v121 `+0.368` is accepted-row only, while the natural held-out gain is `+0.067` with regressions reduced from `20` to `1`. v123 is the mirrored Llama-with-Gemma control: the raw router is `-0.002` natural-rate and source-calibrated pairwise selection no-ops. v124 shows the v122 natural gain is not one-problem concentration: leave-one-problem-out stays positive on `222/222` groups, min `+0.063`. v125 raises the raw-router source regression budget to `2`: raw natural delta is `+0.118` with `240/30` rec/reg, while pairwise budget 1 gets `+0.083` with `150/2` and pairwise budget 2 gets `+0.099` with `180/4`. v126 shows those higher-budget gains are also not concentration artifacts: budget1 and budget2 natural leave-one-problem-out stay positive on `222/222` groups, min `+0.079` and `+0.095`. v127 turns the pairwise source budget into an anti-cherrypick curve: the guarded rule set plateaus at `+0.099` from source budget `2` through `30`, while an unsafe `always` control approaches raw-router gain only by restoring most regressions. v128 adds deployable guard pressure: fixed qwen/union cross-judge confirmation keeps a budget-1-sized natural gain (`+0.083`) while reducing budget-2 regressions from `4` to `1`, and source-selected guard budget 1 gets `+0.086` with `155/2`. v129 separates the budget2 increment from budget1: the increment is `+0.016` and LOO-positive for `222/222` groups, but sparse (`17/222` nonzero groups), and simple source-disjoint policy-family guards do not improve the frontier. v130 tests richer prompts on the localized qwen regression tail: type-check prompting fixes the repeated `p88` digit-cycle regressions while preserving matched `p63` recoveries, but `p82` weekday regressions remain and other local judges become unstable or invalid. Exact N=128 gap numbers vary slightly by audit provenance, so quote the source next to the number.

Start here:

- [v10 failure-detector note](css_research_note_v10_failure_detector.md)
- [v11 detector-ablation note](css_research_note_v11_detector_ablation.md)
- [v12 detector-transfer note](css_research_note_v12_detector_transfer.md)
- [v13 answer-extraction audit](css_research_note_v13_extraction_audit.md)
- [v14 LLM cluster-verifier smoke test](css_research_note_v14_llm_cluster_verifier_smoke.md)
- [v15 40-packet blind verifier panel](css_research_note_v15_panel40_cluster_verifier.md)
- [v16 full 120-packet verifier audit](css_research_note_v16_full120_verifier_audit.md)
- [v17 detector-triggered verifier frontier](css_research_note_v17_deployed_verifier_frontier.md)
- [v18 failure-detector zoo](css_research_note_v18_detector_zoo.md)
- [v19 detector robustness sweep](css_research_note_v19_detector_robustness.md)
- [v20 buried-cluster depth audit](css_research_note_v20_buried_cluster_depth.md)
- [v21 adaptive cluster-depth frontier](css_research_note_v21_adaptive_depth_frontier.md)
- [v22 depth-verifier prompt assets](css_research_note_v22_depth_verifier_assets.md)
- [v23 buried top-20 verifier pilot](css_research_note_v23_buried_verifier_pilot.md)
- [v24 diverse buried top-20 assets](css_research_note_v24_diverse_buried_assets.md)
- [v25 compact verifier prompts](css_research_note_v25_compact_verifier_prompts.md)
- [v26 compact evidence visibility](css_research_note_v26_compact_evidence_visibility.md)
- [v27 evidence-budget frontier](css_research_note_v27_evidence_budget_frontier.md)
- [v28 cost-aware verifier cascade](css_research_note_v28_cost_aware_cascade.md)
- [v29 cascade scoring harness](css_research_note_v29_cascade_scoring_harness.md)
- [v30 iso-budget depth frontier](css_research_note_v30_iso_budget_depth_frontier.md)
- [v31 budgeted depth policy](css_research_note_v31_budgeted_depth_policy.md)
- [v32 rank-bucket depth policy](css_research_note_v32_rank_bucket_depth_policy.md)
- [v33 rank-bucket seed sweep](css_research_note_v33_rank_bucket_seed_sweep.md)
- [v34 measured-verifier handoff](css_research_note_v34_measured_verifier_handoff.md)
- [v35 paper package](css_research_note_v35_paper_package.md)
- [v36 generation-vs-verification ablation](css_research_note_v36_generation_vs_verification.md)
- [v37 deployed-mix verifier assets](css_research_note_v37_deployed_mix_verifier_assets.md)
- [v38 deployed-mix break-even analysis](css_research_note_v38_deployed_mix_break_even.md)
- [v39 deployed-mix threshold/fallback scoring](css_research_note_v39_deployed_mix_threshold_scoring.md)
- [v40 current literature pressure test](css_research_note_v40_current_lit_pressure_test.md)
- [v41 dynamic extra-sampling baseline](css_research_note_v41_dynamic_sampling_baseline.md)
- [v42 token-budget generation-vs-verification comparison](css_research_note_v42_token_budget_generation_vs_verification.md)
- [v43 fine-grained dynamic generation budget check](css_research_note_v43_fine_grained_generation_budget.md)
- [v44 dynamic generation seed sweep](css_research_note_v44_dynamic_generation_seed_sweep.md)
- [v45 deployed-mix statistical decision protocol](css_research_note_v45_deployed_mix_statistical_decision.md)
- [v46 deployed-mix power plan](css_research_note_v46_deployed_mix_power_plan.md)
- [v47 deployed-mix representativeness audit](css_research_note_v47_deployed_mix_representativeness.md)
- [v48 unique-source deployed-mix assets](css_research_note_v48_unique_source_deployed_mix_assets.md)
- [v49 canonical number lock](css_research_note_v49_canonical_number_lock.md)
- [v50 live literature refresh](css_research_note_v50_live_literature_refresh.md)
- [v51 short-trace baseline](css_research_note_v51_short_trace_baseline.md)
- [v52 cross-model verifier transfer](css_research_note_v52_cross_model_verifier_transfer.md)
- [v53 cross-model transfer seed sweep](css_research_note_v53_cross_model_transfer_seed_sweep.md)
- [v54 cross-task transfer boundary](css_research_note_v54_cross_task_transfer_boundary.md)
- [v55 transfer calibration audit](css_research_note_v55_transfer_calibration_audit.md)
- [v56 reviewer-resistant pitch](css_research_note_v56_reviewer_resistant_pitch.md)
- [v57 canonical gap bootstrap CI](css_research_note_v57_canonical_gap_bootstrap_ci.md)
- [v58 cross-trace gap bootstrap](css_research_note_v58_cross_trace_gap_bootstrap.md)
- [v59 cross-trace regime seed sweep](css_research_note_v59_cross_trace_regime_seed_sweep.md)
- [v60 literature boundary addendum](css_research_note_v60_literature_boundary_addendum.md)
- [v61 selectability phase diagram](css_research_note_v61_selectability_phase_diagram.md)
- [v62 phase seed sweep](css_research_note_v62_phase_seed_sweep.md)
- [v63 phase-aware verifier triage](css_research_note_v63_phase_aware_verifier_triage.md)
- [v64 phase threshold sensitivity](css_research_note_v64_phase_threshold_sensitivity.md)
- [v65 verifier quality sensitivity](css_research_note_v65_verifier_quality_sensitivity.md)
- [v66 phase depth marginal utility](css_research_note_v66_phase_depth_marginal_utility.md)
- [v67 phase depth cost ROI](css_research_note_v67_phase_depth_cost_roi.md)
- [v68 phase depth policy frontier](css_research_note_v68_phase_depth_policy_frontier.md)
- [v69 phase depth policy quality sweep](css_research_note_v69_phase_depth_policy_quality_sweep.md)
- [v70 live literature positioning refresh](css_research_note_v70_live_literature_positioning_refresh.md)
- [v71 deployed-mix verifier requirement table](css_research_note_v71_deployed_mix_verifier_requirement_table.md)
- [v72 deployed-mix requirement representativeness sweep](css_research_note_v72_deployed_mix_requirement_representativeness_sweep.md)
- [v73 Llama unique-source tail expansion](css_research_note_v73_llama_unique_source_tail_expansion.md)
- [v74 deployed-mix verifier report harness](css_research_note_v74_deployed_mix_verifier_report_harness.md)
- [v75 remote Ollama verifier smoke](css_research_note_v75_remote_ollama_verifier_smoke.md)
- [v76 qwen evidence-budget probe](css_research_note_v76_qwen_evidence_budget_probe.md)
- [v77 answer-only verifier interface](css_research_note_v77_answer_only_verifier_interface.md)
- [v78 deployed-mix feature selector](css_research_note_v78_deployed_mix_feature_selector.md)
- [v79 calibrated override selector](css_research_note_v79_calibrated_override_selector.md)
- [v80 utility override selector](css_research_note_v80_utility_override_selector.md)
- [v81 risk-controlled override selector](css_research_note_v81_risk_controlled_override_selector.md)
- [v82 override calibration stability audit](css_research_note_v82_override_calibration_stability.md)
- [v83 qwen3:14b verifier smoke and literature stopline](css_research_note_v83_qwen14b_and_literature_stopline.md)
- [v84 qwen3:14b rich problem-prompt stopline](css_research_note_v84_qwen14b_rich_problem_prompt_stopline.md)
- [v85 rank-bucket cross-model transfer](css_research_note_v85_rank_bucket_cross_model_transfer.md)
- [v86 rank-bucket transfer quality sweep](css_research_note_v86_rank_bucket_transfer_quality_sweep.md)
- [v87 rank-bucket cross-seed transfer](css_research_note_v87_rank_bucket_cross_seed_transfer.md)
- [v88 rank-bucket transfer budget map](css_research_note_v88_rank_bucket_transfer_budget_map.md)
- [v89 rank-bucket verifier quality targets](css_research_note_v89_rank_bucket_verifier_quality_targets.md)
- [v90 rank-bucket quality region map](css_research_note_v90_rank_bucket_quality_region_map.md)
- [v91 rank-bucket pair-bootstrap transfer audit](css_research_note_v91_rank_bucket_pair_bootstrap.md)
- [v92 mathstral verifier boundary](css_research_note_v92_mathstral_verifier_boundary.md)
- [v93 binary cluster-judge interface](css_research_note_v93_binary_cluster_judge_interface.md)
- [v94 qwen3:14b binary cluster-judge stopline](css_research_note_v94_qwen14b_binary_cluster_judge.md)
- [v95 hashed semantic cluster-scorer boundary](css_research_note_v95_text_semantic_cluster_scorer.md)
- [v96 source-calibrated semantic risk-control boundary](css_research_note_v96_source_calibrated_semantic_risk.md)
- [v97 unique-source semantic risk-control pressure](css_research_note_v97_unique_source_semantic_risk.md)
- [v98 rebuilt unique-source semantic risk-control boundary](css_research_note_v98_rebuilt_unique_semantic_risk.md)
- [v99 raw semantic threshold boundary](css_research_note_v99_raw_semantic_threshold_boundary.md)
- [v100 split-trained semantic threshold audit](css_research_note_v100_split_trained_semantic_threshold_audit.md)
- [v101 semantic calibration scaling boundary](css_research_note_v101_semantic_calibration_scaling.md)
- [v102 target-style semantic calibration boundary](css_research_note_v102_target_style_semantic_calibration.md)
- [v103 expanded-target semantic calibration boundary](css_research_note_v103_expanded_target_semantic_calibration.md)
- [v104 rich-signal semantic calibration pilot](css_research_note_v104_rich_signal_semantic_calibration.md)
- [v105 semantic meta-gate boundary](css_research_note_v105_semantic_meta_gate.md)
- [v106 symbolic feature boundary](css_research_note_v106_symbolic_feature_boundary.md)
- [v107 process-feature cluster scorer boundary](css_research_note_v107_process_cluster_scorer.md)
- [v108 cross-generator agreement boundary](css_research_note_v108_cross_generator_agreement.md)
- [v109 cross-generator risk-gate audit](css_research_note_v109_cross_generator_risk_gate.md)
- [v110 cross-seed generator router](css_research_note_v110_cross_seed_generator_router.md)
- [v111 cross-seed router placebo](css_research_note_v111_cross_seed_router_placebo.md)
- [v112 cross-seed router heuristic ablation](css_research_note_v112_cross_seed_router_heuristic_ablation.md)
- [v113 cross-seed router regression frontier](css_research_note_v113_cross_seed_router_regression_frontier.md)
- [v114 problem-disjoint router frontier](css_research_note_v114_problem_disjoint_router_frontier.md)
- [v115 problem-disjoint two-head router control](css_research_note_v115_problem_disjoint_two_head_router.md)
- [v116 problem-disjoint separability audit](css_research_note_v116_problem_disjoint_separability.md)
- [v117 trace signal availability audit](css_research_note_v117_trace_signal_availability.md)
- [v118 answer-symbolic guard audit](css_research_note_v118_answer_symbolic_guard.md)
- [v119 pairwise router-judge smoke](css_research_note_v119_pairwise_router_judge.md)
- [v120 full pairwise router-judge panel](css_research_note_v120_full_pairwise_router_judge.md)
- [v121 pairwise router-judge held-out calibration](css_research_note_v121_pairwise_router_judge_calibration.md)
- [v122 pairwise router-judge natural-rate accounting](css_research_note_v122_pairwise_natural_rate.md)
- [v123 Llama-with-Gemma pairwise control](css_research_note_v123_pairwise_mirror_control.md)
- [v124 pairwise natural-rate sensitivity](css_research_note_v124_pairwise_sensitivity.md)
- [v125 higher-budget pairwise router-judge frontier](css_research_note_v125_pairwise_budget2_frontier.md)
- [v126 higher-budget pairwise sensitivity](css_research_note_v126_pairwise_budget2_sensitivity.md)
- [v127 pairwise budget curve](css_research_note_v127_pairwise_budget_curve.md)
- [v128 pairwise guard sweep](css_research_note_v128_pairwise_guard_sweep.md)
- [v129 pairwise budget-increment and policy-guard audit](css_research_note_v129_pairwise_budget_increment_guard.md)
- [v130 pairwise rich-prompt regression probe](css_research_note_v130_pairwise_rich_prompt_probe.md)
- [measured local verifier stopline](measured_local_verifier_stopline.md)
- [adaptive-depth method proposal](adaptive_depth_method_proposal.md)
- [current adaptive-depth paper draft](paper_draft_adaptive_cluster_depth.md)
- [canonical selectability/depth table](canonical_selectability_depth_table.md)
- [paper-style draft](paper_draft_cluster_selectability.md)
- [recent test-time scaling context](related_work_recent_test_time_scaling.md)
- [v9 rescue-selector ablation](css_research_note_v9_rescue_selector.md)
- [v8 cluster-selectability proposal](css_research_note_v8_cluster_selectability_proposal.md)
- [reproducibility manifest](reproducibility_manifest.md)
- [adversarial reviewer checklist](adversarial_reviewer_checklist.md)
- [result ledger](result_ledger.md)

## Source-Of-Truth Order

For the current adaptive-depth paper, use:

1. [v56 reviewer-resistant pitch](css_research_note_v56_reviewer_resistant_pitch.md) for the current front-door claim.
2. [current adaptive-depth paper draft](paper_draft_adaptive_cluster_depth.md) for the narrative.
3. [canonical selectability/depth table](canonical_selectability_depth_table.md) for high-N parser-v2 MATH gap/depth numbers.
4. [v57 canonical gap bootstrap CI](css_research_note_v57_canonical_gap_bootstrap_ci.md) for uncertainty on the headline gap/depth numbers.
5. [v58 cross-trace gap bootstrap](css_research_note_v58_cross_trace_gap_bootstrap.md) for the boundary claim across MATH, GSM8K, and Pythia.
6. [v59 cross-trace regime seed sweep](css_research_note_v59_cross_trace_regime_seed_sweep.md) for split/trial stability of that boundary.
7. [v60 literature boundary addendum](css_research_note_v60_literature_boundary_addendum.md) for current positioning against TTS/verifier/judge-shift work.
8. [v61 selectability phase diagram](css_research_note_v61_selectability_phase_diagram.md) for how regimes change with sample count.
9. [v62 phase seed sweep](css_research_note_v62_phase_seed_sweep.md) for seed stability of the N-sweep phase diagram.
10. [v63 phase-aware verifier triage](css_research_note_v63_phase_aware_verifier_triage.md) for spend/no-spend guidance by regime.
11. [v64 phase threshold sensitivity](css_research_note_v64_phase_threshold_sensitivity.md) for threshold robustness of the regime labels.
12. [v65 verifier quality sensitivity](css_research_note_v65_verifier_quality_sensitivity.md) for robustness to verifier success/false-regression assumptions.
13. [v66 phase depth marginal utility](css_research_note_v66_phase_depth_marginal_utility.md) for whether top20 is necessary versus top5/top10 by phase.
14. [v67 phase depth cost ROI](css_research_note_v67_phase_depth_cost_roi.md) for prompt-cost-normalized depth utility.
15. [v68 phase depth policy frontier](css_research_note_v68_phase_depth_policy_frontier.md) for the explicit token-value decision rule.
16. [v69 phase depth policy quality sweep](css_research_note_v69_phase_depth_policy_quality_sweep.md) for robustness of the utility frontier to verifier quality.
17. [v70 live literature positioning refresh](css_research_note_v70_live_literature_positioning_refresh.md) for current novelty boundaries.
18. [v71 deployed-mix verifier requirement table](css_research_note_v71_deployed_mix_verifier_requirement_table.md) for finite-sample smoke targets for the next real verifier run.
19. [v72 deployed-mix requirement representativeness sweep](css_research_note_v72_deployed_mix_requirement_representativeness_sweep.md) for balanced vs source-unique verifier target caveats.
20. [v73 Llama unique-source tail expansion](css_research_note_v73_llama_unique_source_tail_expansion.md) for the best-effort Llama tail asset expansion.
21. [v74 deployed-mix verifier report harness](css_research_note_v74_deployed_mix_verifier_report_harness.md) for the one-command report once predictions exist.
22. [v75 remote Ollama verifier smoke](css_research_note_v75_remote_ollama_verifier_smoke.md) for the first real local endpoint smoke and negative qwen result.
23. [v76 qwen evidence-budget probe](css_research_note_v76_qwen_evidence_budget_probe.md) for rich/evidence-only qwen fallback failures.
24. [v77 answer-only verifier interface](css_research_note_v77_answer_only_verifier_interface.md) for answer-only qwen/gemma probes.
25. [v78 deployed-mix feature selector](css_research_note_v78_deployed_mix_feature_selector.md) for the trained selector route after local LLM verifier failure.
26. [v79 calibrated override selector](css_research_note_v79_calibrated_override_selector.md) for source-calibrated override and oracle-threshold calibration-shift evidence.
27. [v80 utility override selector](css_research_note_v80_utility_override_selector.md) for the two-head utility gate and calibration-data failure evidence.
28. [v81 risk-controlled override selector](css_research_note_v81_risk_controlled_override_selector.md) for conservative abstention-gate failure evidence.
29. [v82 override calibration stability audit](css_research_note_v82_override_calibration_stability.md) for multi-seed cheap-selector calibration failure evidence.
30. [v83 qwen3:14b verifier smoke and literature stopline](css_research_note_v83_qwen14b_and_literature_stopline.md) for qwen3:14b answer-only/evidence-only measured evidence and novelty boundary.
31. [v84 qwen3:14b rich problem-prompt stopline](css_research_note_v84_qwen14b_rich_problem_prompt_stopline.md) for the richer problem-inclusive qwen3:14b failure that closes the prompt-starvation objection.
32. [v85 rank-bucket cross-model transfer](css_research_note_v85_rank_bucket_cross_model_transfer.md) for projected adaptive-depth allocation transfer across Llama/Gemma.
33. [v86 rank-bucket transfer quality sweep](css_research_note_v86_rank_bucket_transfer_quality_sweep.md) for quality-stress of the v85 allocation-transfer result.
34. [v87 rank-bucket cross-seed transfer](css_research_note_v87_rank_bucket_cross_seed_transfer.md) for decoupled split-seed stress of the allocation-transfer result.
35. [v88 rank-bucket transfer budget map](css_research_note_v88_rank_bucket_transfer_budget_map.md) for the budget-dependence caveat on the v87 high-budget headline.
36. [v89 rank-bucket verifier quality targets](css_research_note_v89_rank_bucket_verifier_quality_targets.md) for the success/regression contract behind the v87/v88 transfer claim.
37. [v90 rank-bucket quality region map](css_research_note_v90_rank_bucket_quality_region_map.md) for the 2D verifier-quality robustness envelope behind the transfer claim.
38. [v91 rank-bucket pair-bootstrap transfer audit](css_research_note_v91_rank_bucket_pair_bootstrap.md) for seed-pair lower-bound fragility of the transfer claim.
39. [v95 hashed semantic cluster-scorer boundary](css_research_note_v95_text_semantic_cluster_scorer.md) for the trained semantic-selector follow-up after local verifier/binary-judge failures.
40. [v96 source-calibrated semantic risk-control boundary](css_research_note_v96_source_calibrated_semantic_risk.md) for the stricter source-calibrated semantic-selector stopline.
41. [v97 unique-source semantic risk-control pressure](css_research_note_v97_unique_source_semantic_risk.md) for lower-duplication Llama pressure and the Gemma unique16 packet artifact hazard.
42. [v98 rebuilt unique-source semantic risk-control boundary](css_research_note_v98_rebuilt_unique_semantic_risk.md) for the rebuilt Gemma unique-source target and symmetric lower-duplication semantic-risk stopline.
43. [v99 raw semantic threshold boundary](css_research_note_v99_raw_semantic_threshold_boundary.md) for target-threshold headroom versus deployable calibration failure.
44. [v100 split-trained semantic threshold audit](css_research_note_v100_split_trained_semantic_threshold_audit.md) for split-trained raw headroom and threshold-transfer failure.
45. [v101 semantic calibration scaling boundary](css_research_note_v101_semantic_calibration_scaling.md) for packet-vs-problem-disjoint calibration-size/composition failure.
46. [v102 target-style semantic calibration boundary](css_research_note_v102_target_style_semantic_calibration.md) for same-distribution calibration failure on held-out target packets.
47. [v103 expanded-target semantic calibration boundary](css_research_note_v103_expanded_target_semantic_calibration.md) for larger duplicated target-style calibration still failing conservative held-out threshold selection.
48. [v104 rich-signal semantic calibration pilot](css_research_note_v104_rich_signal_semantic_calibration.md) for problem text / longer-rationale hashed features still failing conservative target calibration.
49. [v105 semantic meta-gate boundary](css_research_note_v105_semantic_meta_gate.md) for multifeature target-style accept/fallback gates still failing conservative deployed calibration.
50. [v106 symbolic feature boundary](css_research_note_v106_symbolic_feature_boundary.md) for dependency-light answer-shape/arithmetic-consistency features still failing conservative deployed calibration.
51. [v107 process-feature cluster scorer boundary](css_research_note_v107_process_cluster_scorer.md) for representative-level proof-hygiene/process features still failing conservative deployed calibration.
52. [v108 cross-generator agreement boundary](css_research_note_v108_cross_generator_agreement.md) for asymmetric auxiliary-generator agreement signal that helps Gemma with Llama but is not bidirectionally conservative.
53. [v109 cross-generator risk-gate audit](css_research_note_v109_cross_generator_risk_gate.md) for calibrated auxiliary-generator routing: Llama helps Gemma under `union_rank_top3` with 24/36 calibration problems, but the reverse direction remains unsafe/flat.
54. [v110 cross-seed generator router](css_research_note_v110_cross_seed_generator_router.md) for source-seed threshold transfer: Gemma-with-Llama `pool_all` stays `+0.084` with 3/3 held-out seeds CI-positive and only two regressions.
55. [v111 cross-seed router placebo](css_research_note_v111_cross_seed_router_placebo.md) for the source-label permutation control: 0/200 placebo runs match the v110 Gemma-with-Llama deltas.
56. [v112 cross-seed router heuristic ablation](css_research_note_v112_cross_seed_router_heuristic_ablation.md) for the dumb-control boundary: tie-safe rank/prior heuristics collapse to no-op and the best support/confidence heuristics reach `+0.054`, below v110.
57. [v113 cross-seed router regression frontier](css_research_note_v113_cross_seed_router_regression_frontier.md) for explicit source-regression budgets under the overlap-allowed source split: learned Gemma-with-Llama routing reaches `+0.119` with 3 held-out regressions at source budget 2.
58. [v114 problem-disjoint router frontier](css_research_note_v114_problem_disjoint_router_frontier.md) for the stricter calibration boundary: excluding source rows whose problem ids appear in the held-out seed preserves positive recovery signal but raises held-out regressions.
59. [v115 problem-disjoint two-head router control](css_research_note_v115_problem_disjoint_two_head_router.md) for the same-feature regression-control failure: a candidate-correctness head does not restore low-regression held-out calibration.
60. [v116 problem-disjoint separability audit](css_research_note_v116_problem_disjoint_separability.md) for the diagnostic: same-feature scores rank recoveries above regressions at about AUC `0.70`, but not sharply enough for safe source-threshold transfer.
61. [v117 trace signal availability audit](css_research_note_v117_trace_signal_availability.md) for the local-data boundary: existing traces have text samples and correctness labels, but no logprobs, hidden states, embeddings, or decoder telemetry.
62. [v118 answer-symbolic guard audit](css_research_note_v118_answer_symbolic_guard.md) for the cheap local-feature stopline: answer shape/numeric features trail the original router score and do not restore low-regression calibration.
63. [v119 pairwise router-judge smoke](css_research_note_v119_pairwise_router_judge.md) for the new live-verifier direction: local models can adjudicate baseline-vs-candidate answer pairs with positive recovery/regression tradeoffs on accepted router rows.
64. [v120 full pairwise router-judge panel](css_research_note_v120_full_pairwise_router_judge.md) for the scaled accepted-row result: mathstral/gemma4 recover more than half of accepted recovery rows with zero accepted regressions on the full budget-0 panel.
65. [v121 pairwise router-judge held-out calibration](css_research_note_v121_pairwise_router_judge_calibration.md) for source-selected model/rule transfer over accepted rows: budget-0 calibration gets `+0.368`, `120` recoveries, and `1` held-out regression.
66. [v122 pairwise router-judge natural-rate accounting](css_research_note_v122_pairwise_natural_rate.md) for the deployment denominator correction: the same source-selected budget-0 policy gets natural held-out `+0.067` over `1776` trials while reducing upstream router regressions from `20` to `1`.
67. [v123 Llama-with-Gemma pairwise mirror control](css_research_note_v123_pairwise_mirror_control.md) for the negative/control direction: the reverse raw router is slightly harmful (`-0.002`) and source-calibrated pairwise selection no-ops over the full `1776`-trial denominator.
68. [v124 pairwise natural-rate sensitivity](css_research_note_v124_pairwise_sensitivity.md) for concentration risk: leave-one-problem-out natural deltas stay positive for `222/222` held-out problem groups, with min `+0.063`.
69. [v125 higher-budget pairwise router-judge frontier](css_research_note_v125_pairwise_budget2_frontier.md) for scaling the Gemma-with-Llama router to source regression budget `2`: raw natural delta reaches `+0.118` with `240/30` rec/reg, while pairwise-gated rows get `+0.083` with `150/2` at budget 1 and `+0.099` with `180/4` at budget 2.
70. [v126 higher-budget pairwise sensitivity](css_research_note_v126_pairwise_budget2_sensitivity.md) for the concentration/regression check on v125: budget1 and budget2 natural leave-one-problem-out remain positive for `222/222` held-out groups, with min `+0.079` and `+0.095`; all budget2 regressions are `qwen14b/B` choices on `union_rank_top3`.
71. [v127 pairwise budget curve](css_research_note_v127_pairwise_budget_curve.md) for the anti-cherrypick curve over pairwise source budgets: guarded rules plateau at `+0.099` from budget `2` through `30`, while allowing `always` approaches raw-router gain only by restoring most regressions.
72. [v128 pairwise guard sweep](css_research_note_v128_pairwise_guard_sweep.md) for non-oracle guard pressure: fixed qwen/union cross-judge confirmation keeps `+0.083` with `149/1`, and source-selected guard budget 1 gets `+0.086` with `155/2`.
73. [v129 pairwise budget-increment and policy-guard audit](css_research_note_v129_pairwise_budget_increment_guard.md) for the budget1-to-budget2 tradeoff: the increment is `+28` correct trials (`+0.016`) and LOO-positive for `222/222` groups, but sparse across `17/222` nonzero groups; source-disjoint policy-family guards do not improve the v125 frontier.
74. [v130 pairwise rich-prompt regression probe](css_research_note_v130_pairwise_rich_prompt_probe.md) for localized qwen regression-tail pressure: `type_check` fixes repeated `p88` digit regressions and keeps matched `p63` recoveries, but `p82` weekday regressions remain and mathstral/gemma4 do not become better guards under richer prompts.
47. [measured local verifier stopline](measured_local_verifier_stopline.md) for the compact v75-v77/v83-v84 local-verifier verdict table.
47. [result ledger](result_ledger.md) for the compact claim ledger.
48. [v33 rank-bucket seed sweep](css_research_note_v33_rank_bucket_seed_sweep.md) for robust learned-policy numbers.
49. [v34 measured-verifier handoff](css_research_note_v34_measured_verifier_handoff.md) for exact smoke/full/cascade commands once a model endpoint is available.
50. [v35 paper package](css_research_note_v35_paper_package.md) for the broad package checklist.
51. [v36 generation-vs-verification ablation](css_research_note_v36_generation_vs_verification.md) for the "why not just sample more?" objection.
52. [v37 deployed-mix verifier assets](css_research_note_v37_deployed_mix_verifier_assets.md) for regression-aware external-verifier evaluation.
53. [v38 deployed-mix break-even analysis](css_research_note_v38_deployed_mix_break_even.md) for the recovery-vs-regression thresholds.
54. [v39 deployed-mix threshold/fallback scoring](css_research_note_v39_deployed_mix_threshold_scoring.md) for the policy-level scorer and confidence-threshold runbook.
55. [v40 current literature pressure test](css_research_note_v40_current_lit_pressure_test.md) for the live 2025/2026 objection map.
56. [v41 dynamic extra-sampling baseline](css_research_note_v41_dynamic_sampling_baseline.md) for the adaptive generation-only objection.
57. [v42 token-budget generation-vs-verification comparison](css_research_note_v42_token_budget_generation_vs_verification.md) for the 512/1024-token budget objection.
58. [v43 fine-grained dynamic generation budget check](css_research_note_v43_fine_grained_generation_budget.md) for the small-chunk generation objection.
59. [v44 dynamic generation seed sweep](css_research_note_v44_dynamic_generation_seed_sweep.md) for robustness of the token-matched generation baseline.
60. [v45 deployed-mix statistical decision protocol](css_research_note_v45_deployed_mix_statistical_decision.md) for the pre-specified CI gate on the next real verifier run.
60. [v46 deployed-mix power plan](css_research_note_v46_deployed_mix_power_plan.md) for interpreting whether the current 72-prompt/model smoke is enough.
61. [v47 deployed-mix representativeness audit](css_research_note_v47_deployed_mix_representativeness.md) for source-problem duplication and cross-model overlap caveats.
62. [v48 unique-source deployed-mix assets](css_research_note_v48_unique_source_deployed_mix_assets.md) for the lower-duplication verifier target.
63. [v49 canonical number lock](css_research_note_v49_canonical_number_lock.md) for the script-generated high-N diagnostic table.
64. [v50 live literature refresh](css_research_note_v50_live_literature_refresh.md) for current 2026 positioning pressure.
65. [v51 short-trace baseline](css_research_note_v51_short_trace_baseline.md) for the First Finish Search objection.
66. [v52 cross-model verifier transfer](css_research_note_v52_cross_model_verifier_transfer.md) for the scorer trajectory-shift objection.
67. [v53 cross-model transfer seed sweep](css_research_note_v53_cross_model_transfer_seed_sweep.md) for seed robustness of the scorer-transfer result.
68. [v54 cross-task transfer boundary](css_research_note_v54_cross_task_transfer_boundary.md) for MATH/GSM8K scorer-transfer limits.
69. [v55 transfer calibration audit](css_research_note_v55_transfer_calibration_audit.md) for selection-vs-confidence transfer.
70. [v32 rank-bucket depth policy](css_research_note_v32_rank_bucket_depth_policy.md) for the single-split method table.
71. [MATH/Llama deep top-k audit](deep_topk_math_llama_n128.md) and [MATH/Gemma deep top-k audit](deep_topk_math_gemma2b_n128.md) for detailed depth/oracle provenance.
72. [v13 answer-extraction audit](css_research_note_v13_extraction_audit.md) when discussing parser sensitivity.

## Core Evidence

- [multi-config selector summary](monkey_css_multiconfig_summary.md)
- [top-k cluster oracle bounds](topk_cluster_oracle_bounds.md)
- [cluster selectability gap plot](cluster_selectability_gap_plot.svg)
- [MATH/Llama selectability audit](cluster_selectability_math_llama.md)
- [MATH/Gemma selectability audit](cluster_selectability_math_gemma2b.md)
- [GSM8K/Llama selectability audit](cluster_selectability_gsm8k_llama.md)
- [MATH/Pythia selectability audit](cluster_selectability_math_pythia1b.md)

## Negative / Sharpening Results

- [learned cluster-ranker revision](css_research_note_v6_cluster_ranker.md)
- [MATH/Llama consistency ranker](monkey_cluster_ranker_consistency_math_llama.md)
- [MATH/Gemma consistency ranker](monkey_cluster_ranker_consistency_math_gemma2b.md)
- [hard-packet feature transfer](hard_packet_feature_transfer.md)
- [MATH/Llama gated rescue](gated_rescue_math_llama_n128_t12.md)
- [MATH/Gemma gated rescue](gated_rescue_math_gemma2b_n128_t12.md)
- [MATH/Llama failure detector](failure_detector_math_llama_n128.md)
- [MATH/Gemma failure detector](failure_detector_math_gemma2b_n128.md)
- [MATH/Llama detector feature ablation](failure_detector_ablation_math_llama_n128.md)
- [MATH/Gemma detector feature ablation](failure_detector_ablation_math_gemma2b_n128.md)
- [failure detector transfer matrix](failure_detector_transfer_math_llama_gemma_n128.md)
- [answer extraction audit v2](answer_extraction_audit_v2.md)
- [MATH/Llama parser-v2 selectability audit](cluster_selectability_math_llama_parser_v2.md)
- [MATH/Gemma parser-v2 selectability audit](cluster_selectability_math_gemma2b_parser_v2.md)
- [MATH/Llama deep top-k audit](deep_topk_math_llama_n128.md)
- [MATH/Gemma deep top-k audit](deep_topk_math_gemma2b_n128.md)
- [adaptive cluster-depth frontier](adaptive_depth_frontier.md)
- [failure detector bound plot](failure_detector_bound_plot.svg)

## Verifier Protocol

- [cluster-packet verifier protocol](cluster_packet_verifier_protocol.md)
- [MATH/Llama hard packet dataset](cluster_packets_math_llama_n128.md)
- [MATH/Gemma hard packet dataset](cluster_packets_math_gemma2b_n128.md)
- [MATH/Llama verifier prompts](cluster_verifier_prompts_math_llama_n128.jsonl)
- [MATH/Gemma verifier prompts](cluster_verifier_prompts_math_gemma2b_n128.jsonl)
- [blind LLM-judge smoke-test report](llm_manual_smoke_cluster_verifier.md)
- [40-packet blind LLM-judge panel report](llm_manual_panel40_cluster_verifier.md)
- [full 120-packet manual verifier report](llm_manual_full120_cluster_verifier.md)
- [full 120-packet verifier audit](llm_manual_full120_panel_audit.md)
- [full verifier prompt family digest](full_verifier_prompt_family_digest.md)
- [hard-packet diversity audit](hard_packet_diversity_audit.md)
- [depth packet asset audit](depth_packet_asset_audit.md)
- [diverse depth packet audit](diverse_depth_packet_audit.md)
- [compact diverse prompt audit](compact_diverse_prompt_audit.md)
- [packet representative visibility audit](packet_representative_visibility.md)
- [evidence-budget adjusted frontier](evidence_budget_frontier.md)
- [cost-aware verifier cascade](cost_aware_verifier_cascade.md)
- [iso-budget adaptive-depth frontier](iso_budget_depth_frontier.md)
- [budgeted variable-depth policy](budgeted_depth_policy.md)
- [rank-bucket depth policy](rank_bucket_depth_policy.md)
- [rank-bucket seed sweep](rank_bucket_seed_sweep.md)
- [generation-vs-verification budget ablation](generation_vs_verification_budget.md)
- [dynamic extra-sampling baseline](dynamic_sampling_baseline.md)
- [token-budget generation-vs-verification comparison](token_budget_generation_vs_verification.md)
- [fine-grained token-budget generation-vs-verification comparison](token_budget_generation_vs_verification_fine.md)
- [dynamic generation seed sweep](dynamic_generation_seed_sweep.md)
- [short-trace baseline](short_trace_baseline.md)
- [cross-model verifier transfer](cross_model_verifier_transfer.md)
- [cross-model verifier transfer seed sweep](cross_model_verifier_transfer_seed_sweep.md)
- [cross-task verifier transfer seed sweep](cross_task_verifier_transfer_seed_sweep.md)
- [transfer calibration summary](transfer_calibration_summary.md)
- [canonical gap bootstrap CI](canonical_gap_bootstrap_ci.md)
- [cross-trace gap bootstrap CI](cross_trace_gap_bootstrap_ci.md)
- [cross-trace regime seed sweep](cross_trace_regime_seed_sweep.md)
- [cross-trace selectability phase diagram](cross_trace_phase_diagram.md)
- [cross-trace phase seed sweep](cross_trace_phase_seed_sweep.md)
- [phase-aware verifier triage](phase_aware_verifier_triage.md)
- [phase threshold sensitivity](phase_threshold_sensitivity.csv)
- [MATH/Llama extended generation scaling](generation_scaling_math_llama.md)
- [MATH/Gemma extended generation scaling](generation_scaling_math_gemma2b.md)
- [detector-triggered verifier frontier](detector_verifier_frontier.md)
- [detector-triggered verifier frontier plot](detector_verifier_frontier.svg)
- [failure detector zoo](failure_detector_zoo.md)
- [detector zoo frontier comparison](detector_zoo_frontier_comparison.md)
- [failure detector seed sweep](failure_detector_seed_sweep.md)
- [seed sweep vs original frontier](detector_seed_sweep_vs_frontier.md)
- [MATH/Llama full verifier prompts](cluster_verifier_prompts_math_llama_n128_full.jsonl)
- [MATH/Gemma full verifier prompts](cluster_verifier_prompts_math_gemma2b_n128_full.jsonl)
- [MATH/Llama top20 buried verifier prompts](cluster_verifier_prompts_math_llama_n128_top20_rank11_20_strict.jsonl)
- [MATH/Gemma top20 buried verifier prompts](cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_strict.jsonl)
- [MATH/Llama diverse top20 buried verifier prompts](cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse.jsonl)
- [MATH/Gemma diverse top20 buried verifier prompts](cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse.jsonl)
- [MATH/Llama compact diverse top20 prompts](cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.jsonl)
- [MATH/Gemma compact diverse top20 prompts](cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse_compact.jsonl)
- [MATH/Llama deployed-mix top20 packets](cluster_packets_math_llama_n128_deployed_mix_top20.md)
- [MATH/Gemma deployed-mix top20 packets](cluster_packets_math_gemma2b_n128_deployed_mix_top20.md)
- [MATH/Llama deployed-mix compact prompts](cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.jsonl)
- [MATH/Gemma deployed-mix compact prompts](cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.jsonl)
- [deployed-mix break-even analysis](deployed_mix_break_even.md)
- [synthetic deployed-mix scorer smoke](synthetic_deployed_mix_verifier_eval.md)
- [synthetic deployed-mix policy CI smoke](synthetic_deployed_mix_policy_ci.md)
- [deployed-mix power plan](deployed_mix_power_plan.md)
- [deployed-mix representativeness audit](deployed_mix_representativeness.md)
- [unique-source deployed-mix representativeness audit](deployed_mix_unique16_representativeness.md)
- [MATH/Llama unique-source deployed-mix compact prompts](cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique16_compact.jsonl)
- [MATH/Gemma unique-source deployed-mix compact prompts](cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_unique16_compact.jsonl)
- [buried top20 pilot verifier report](pilot_depth_judge_top20_rank11_20.md)

## Main Scripts

- [monkey_css_realbench.py](monkey_css_realbench.py)
- [cluster_selectability_audit.py](cluster_selectability_audit.py)
- [topk_cluster_oracle_bounds.py](topk_cluster_oracle_bounds.py)
- [build_cluster_packet_dataset.py](build_cluster_packet_dataset.py)
- [hard_packet_feature_transfer.py](hard_packet_feature_transfer.py)
- [gated_rescue_selector.py](gated_rescue_selector.py)
- [failure_detector_diagnostics.py](failure_detector_diagnostics.py)
- [failure_detector_feature_ablation.py](failure_detector_feature_ablation.py)
- [failure_detector_transfer.py](failure_detector_transfer.py)
- [answer_extraction_audit.py](answer_extraction_audit.py)
- [score_llm_judges.py](score_llm_judges.py)
- [score_verifier_cascade.py](score_verifier_cascade.py)
- [iso_budget_depth_frontier.py](iso_budget_depth_frontier.py)
- [budgeted_depth_policy.py](budgeted_depth_policy.py)
- [rank_bucket_depth_policy.py](rank_bucket_depth_policy.py)
- [rank_bucket_seed_sweep.py](rank_bucket_seed_sweep.py)
- [make_canonical_selectability_depth_table.py](make_canonical_selectability_depth_table.py)
- [test_make_canonical_selectability_depth_table.py](test_make_canonical_selectability_depth_table.py)
- [generation_vs_verification_budget.py](generation_vs_verification_budget.py)
- [test_generation_vs_verification_budget.py](test_generation_vs_verification_budget.py)
- [dynamic_sampling_baseline.py](dynamic_sampling_baseline.py)
- [test_dynamic_sampling_baseline.py](test_dynamic_sampling_baseline.py)
- [token_budget_generation_vs_verification.py](token_budget_generation_vs_verification.py)
- [test_token_budget_generation_vs_verification.py](test_token_budget_generation_vs_verification.py)
- [dynamic_generation_seed_sweep.py](dynamic_generation_seed_sweep.py)
- [test_dynamic_generation_seed_sweep.py](test_dynamic_generation_seed_sweep.py)
- [short_trace_baseline.py](short_trace_baseline.py)
- [test_short_trace_baseline.py](test_short_trace_baseline.py)
- [cross_model_verifier_transfer.py](cross_model_verifier_transfer.py)
- [test_cross_model_verifier_transfer.py](test_cross_model_verifier_transfer.py)
- [cross_model_verifier_transfer_seed_sweep.py](cross_model_verifier_transfer_seed_sweep.py)
- [test_cross_model_verifier_transfer_seed_sweep.py](test_cross_model_verifier_transfer_seed_sweep.py)
- [transfer_calibration_summary.py](transfer_calibration_summary.py)
- [test_transfer_calibration_summary.py](test_transfer_calibration_summary.py)
- [canonical_gap_bootstrap_ci.py](canonical_gap_bootstrap_ci.py)
- [test_canonical_gap_bootstrap_ci.py](test_canonical_gap_bootstrap_ci.py)
- [cross_trace_regime_seed_sweep.py](cross_trace_regime_seed_sweep.py)
- [test_cross_trace_regime_seed_sweep.py](test_cross_trace_regime_seed_sweep.py)
- [cross_trace_phase_diagram.py](cross_trace_phase_diagram.py)
- [test_cross_trace_phase_diagram.py](test_cross_trace_phase_diagram.py)
- [cross_trace_phase_seed_sweep.py](cross_trace_phase_seed_sweep.py)
- [test_cross_trace_phase_seed_sweep.py](test_cross_trace_phase_seed_sweep.py)
- [phase_aware_verifier_triage.py](phase_aware_verifier_triage.py)
- [test_phase_aware_verifier_triage.py](test_phase_aware_verifier_triage.py)
- [phase_threshold_sensitivity.py](phase_threshold_sensitivity.py)
- [test_phase_threshold_sensitivity.py](test_phase_threshold_sensitivity.py)
- [verifier_quality_sensitivity.py](verifier_quality_sensitivity.py)
- [test_verifier_quality_sensitivity.py](test_verifier_quality_sensitivity.py)
- [phase_depth_marginal_utility.py](phase_depth_marginal_utility.py)
- [test_phase_depth_marginal_utility.py](test_phase_depth_marginal_utility.py)
- [phase_depth_cost_roi.py](phase_depth_cost_roi.py)
- [test_phase_depth_cost_roi.py](test_phase_depth_cost_roi.py)
- [phase_depth_policy_frontier.py](phase_depth_policy_frontier.py)
- [test_phase_depth_policy_frontier.py](test_phase_depth_policy_frontier.py)
- [phase_depth_policy_quality_sweep.py](phase_depth_policy_quality_sweep.py)
- [test_phase_depth_policy_quality_sweep.py](test_phase_depth_policy_quality_sweep.py)
- [build_blind_deployed_mix_panel.py](build_blind_deployed_mix_panel.py)
- [test_build_blind_deployed_mix_panel.py](test_build_blind_deployed_mix_panel.py)
- [build_deployed_mix_packet_dataset.py](build_deployed_mix_packet_dataset.py)
- [test_build_deployed_mix_packet_dataset.py](test_build_deployed_mix_packet_dataset.py)
- [score_deployed_mix_verifier.py](score_deployed_mix_verifier.py)
- [test_score_deployed_mix_verifier.py](test_score_deployed_mix_verifier.py)
- [deployed_mix_verifier_report.py](deployed_mix_verifier_report.py)
- [test_deployed_mix_verifier_report.py](test_deployed_mix_verifier_report.py)
- [deployed_mix_feature_selector.py](deployed_mix_feature_selector.py)
- [test_deployed_mix_feature_selector.py](test_deployed_mix_feature_selector.py)
- [calibrated_override_selector.py](calibrated_override_selector.py)
- [test_calibrated_override_selector.py](test_calibrated_override_selector.py)
- [utility_override_selector.py](utility_override_selector.py)
- [test_utility_override_selector.py](test_utility_override_selector.py)
- [risk_controlled_override_selector.py](risk_controlled_override_selector.py)
- [test_risk_controlled_override_selector.py](test_risk_controlled_override_selector.py)
- [override_calibration_stability_audit.py](override_calibration_stability_audit.py)
- [test_override_calibration_stability_audit.py](test_override_calibration_stability_audit.py)
- [deployed_mix_policy_ci.py](deployed_mix_policy_ci.py)
- [test_deployed_mix_policy_ci.py](test_deployed_mix_policy_ci.py)
- [deployed_mix_power_plan.py](deployed_mix_power_plan.py)
- [test_deployed_mix_power_plan.py](test_deployed_mix_power_plan.py)
- [deployed_mix_verifier_requirement_table.py](deployed_mix_verifier_requirement_table.py)
- [test_deployed_mix_verifier_requirement_table.py](test_deployed_mix_verifier_requirement_table.py)
- [deployed_mix_requirement_representativeness_sweep.py](deployed_mix_requirement_representativeness_sweep.py)
- [test_deployed_mix_requirement_representativeness_sweep.py](test_deployed_mix_requirement_representativeness_sweep.py)
- [audit_deployed_mix_representativeness.py](audit_deployed_mix_representativeness.py)
- [test_audit_deployed_mix_representativeness.py](test_audit_deployed_mix_representativeness.py)
- [deployed_mix_break_even.py](deployed_mix_break_even.py)
- [test_deployed_mix_break_even.py](test_deployed_mix_break_even.py)
- [hard_packet_diversity_audit.py](hard_packet_diversity_audit.py)
- [extract_verifier_prompt_families.py](extract_verifier_prompt_families.py)
- [make_manual_full_verifier_predictions.py](make_manual_full_verifier_predictions.py)
- [full_verifier_panel_audit.py](full_verifier_panel_audit.py)
- [detector_verifier_frontier.py](detector_verifier_frontier.py)
- [render_detector_verifier_frontier_svg.py](render_detector_verifier_frontier_svg.py)
- [run_openai_compatible_verifier.py](run_openai_compatible_verifier.py)
- [failure_detector_zoo.py](failure_detector_zoo.py)
- [compare_detector_zoo_frontier.py](compare_detector_zoo_frontier.py)
- [test_failure_detector_zoo.py](test_failure_detector_zoo.py)
- [failure_detector_seed_sweep.py](failure_detector_seed_sweep.py)
- [compare_seed_sweep_to_frontier.py](compare_seed_sweep_to_frontier.py)
- [deep_topk_cluster_audit.py](deep_topk_cluster_audit.py)
- [adaptive_depth_frontier.py](adaptive_depth_frontier.py)
- [test_adaptive_depth_frontier.py](test_adaptive_depth_frontier.py)

## Current Bottom Line

The strongest safe claim is diagnostic:

> Any-correct coverage can dramatically overstate usable test-time performance. Papers should report realized selector accuracy, cluster coverage, top-k cluster selectability, and failure-detector quality.

The strongest method hypothesis is:

> Use cheap selectors by default, then invoke stronger cluster-level verification only when a calibrated failure detector predicts that the default selector is likely wrong. The verifier must improve cluster evidence, not merely rerank the existing top few clusters.

The full manual/in-thread verifier audit scored `111/120` against trace keys, with `111/111` on cases where the manual mathematical answer was visible after normalization. The deployed frontier then shows the next bottleneck: invocation. A detector zoo looked strong on one seed, but a three-seed robustness sweep narrows the claim: Llama keeps a small positive gain at 20% invoke (`0.518` to `0.534` mean), while Gemma is flat/slightly worse (`0.302` to `0.299` mean). The latest depth audits make the pitch more concrete: high-N MATH misses are not usually top-3 mistakes. On selector misses, MATH/Llama has correct-cluster rank p50/p90 `6/21`; MATH/Gemma has `8/33`. A serious method likely needs adaptive cluster-depth inspection plus better evidence ranking. The cost-aware version is now a frontier: compact top-5/top-10 are often better low-budget rows, while compact top-20 becomes useful when the budget supports higher invocation and the goal is maximum projected accuracy. The first independent-depth learned policy was weak, but rank-bucket depth prediction now beats fixed compact rows at high budgets, a three-seed sweep keeps positive projected deltas for both Llama and Gemma, v85 shows the projected allocation rule transfers across Llama/Gemma within about `0.007-0.009` accuracy at 1024 tokens/problem, v86 keeps the cross-vs-within gaps small under `50%/5%`, `80%/2%`, and `100%/0%` verifier-quality settings, and v87 breaks same-seed coupling: harsh cross-model/cross-seed transfer still beats fixed compact rows by `+0.018` on Llama and `+0.036` on Gemma at 1024 tokens/problem. v88 adds the budget map: Gemma->Llama transfer only beats fixed compact at `1024`, while Llama->Gemma beats fixed compact at all tested budgets. v89 makes this claim quality-testable: the high-budget fixed-frontier row needs about `73%` recovery success for Gemma->Llama and `65%` for Llama->Gemma at `2%` false regression, while the stricter target-calibrated within-same comparison is mostly negative and should not be overclaimed. v90 turns that into a 2D region map over `50-100%` success and `0-10%` false regression: Gemma->Llama's best fixed-frontier region is at 1024 with pass fraction `0.422`, while Llama->Gemma's best fixed-frontier region is also 1024 with pass fraction `0.565`. v91 adds seed-pair bootstrap pressure: Llama->Gemma 1024 is the clean row (`6/6` positive pairs, CI `[+0.027,+0.044]`), while Gemma->Llama 1024 is directionally positive but lower-bound fragile (`5/6`, CI `[-0.006,+0.038]`).

The measured-verifier path is now live but negative for local qwen/gemma endpoints. v75-v77 show qwen3.5:9b and gemma4:26b fail under slim, richer, evidence-only, and answer-only interfaces; v83 adds qwen3:14b and scales from 12-prompt smoke to the full 144-prompt answer-only/evidence-only panel. The full qwen3:14b panel recovers only `2/72` recoverable prompts, preserves only `13/24` baseline-correct rows, and has no CI-positive threshold. v84 includes the original problem and richer cluster evidence; recovery rises only to `4/72`, preservation worsens to `12/24`, top20-only recovery remains `0`, and the run is still CI-negative. v92-v94 test mathstral and binary cluster-judge interfaces and remain negative. v95 tests a first-pass hashed semantic scorer; raw recovery signal appears, but preservation/calibration fail and no policy passes the CI-positive deployed rule. v96 adds source-calibrated risk control over 54 semantic policies; Gemma->Llama averages only `+0.003` deployed delta, Llama->Gemma averages `-0.025`, and no policy passes the CI rule. v97 moves the valid side of that test to Llama unique32; best delta is only `+0.014` with no CI-positive policy, and Gemma unique16 packet JSONL is an artifact hazard. v98 rebuilds that Gemma unique-source target cleanly, runs 81 lower-duplication semantic-risk policies, and still finds no CI-positive source-calibrated policy. v99 target-thresholds raw semantic scores and finds `4/81` lower-CI-positive oracle rows. v100 repeats target-thresholding under the same split-trained scorer regime as v98 and still finds `5/81` positive target-oracle rows, including `+0.065` on rebuilt-Gemma-to-Llama unique with `7/36` recoveries. v101 then sweeps calibration size/composition over 72 runs and 1080 source-threshold rows: zero source-calibrated rows pass the CI-positive deployed rule, problem-disjoint clean source rows are all no-op, and target-oracle rows still show small signal. v102 allows labeled target-style calibration and still gets zero held-out CI-positive policies; packet-disjoint has one tiny clean point-positive row, while problem-disjoint clean rows are no-op. v103 expands the Gemma target panel to `48/category` and repeats Llama-to-Gemma thresholding over 756 rows: zero target-calibrated rows pass, best clean calibrated gain is only `+0.007` with zero lower bound, and only held-out oracle thresholding reaches a positive lower bound (`+0.034`). v104 gives the hashed scorer problem text, more representatives, longer rationale snippets, larger hash space, and longer training; conservative target-calibrated behavior is unchanged, while oracle behavior is still diagnostic and can trade off baseline preservation. v105 trains multifeature target-style accept/fallback gates over v103/v104 predictions; zero calibrated gates pass, best clean gate is only `+0.008`, and the most active point estimate regresses baseline and remains CI-negative. v106 replaces hashed text with dependency-light symbolic/answer-shape features and still fails conservative target calibration. v107 uses representative-level process/proof-hygiene features; Llama->Gemma has tiny point-positive rows, but every seed/direction/overlap regime has lower CI at zero or below, so zero policies pass. This shifts the selector boundary: raw split-trained headroom exists, but the current cheap family is not rescued by source calibration, small/expanded target calibration, richer local hashed text, a compact multifeature gate, cheap symbolic features, or representative-level process features. v108 then tests a different axis, cross-generator answer agreement: Llama as an auxiliary trace gives Gemma target-intersection gains around `+0.034` to `+0.042` with few regressions, but Gemma as auxiliary hurts Llama and no positive no-regression policy appears. v109 calibrates that auxiliary-trace axis and finds a narrow positive branch: Gemma-with-Llama `union_rank_top3` is robustly positive with 24/36 calibration problems (`+0.102`/`+0.126`, 3/3 CI-positive seeds), while the reverse direction remains unsafe or flat and small-calibration rows are mostly no-op. v110 removes same-seed threshold comfort: train and threshold on two source seeds, deploy on the held-out seed, and Gemma-with-Llama `pool_all` still gets `+0.084` mean delta with 3/3 CI-positive seeds and only two regressions. v111 permutes source utility labels and finds 0/200 placebo runs match the observed Gemma-with-Llama deltas; `pool_all` placebo max is only `+0.030`. v112 adds the tie-safe dumb heuristic control: rank/prior heuristics collapse to no-op, and the best support/confidence heuristics reach `+0.054`, below v110 `+0.084`. v113 adds an overlap-allowed regression-budget frontier: source-budget 2 learned routing reaches `+0.119` with 3 held-out regressions, while the best <=5-regression heuristic reaches `+0.084`. v114 then removes source rows whose problem ids appear in the held-out seed; learned rows remain positive (`+0.097` at source budget 0, `+0.118` at budget 2) but regressions jump to `20`/`30`, so this is recovery signal rather than safe problem-disjoint calibration. v115 adds a same-feature candidate-correctness head; it does not restore low-regression control, with no row at <=5 held-out regressions and only small frontier reshuffling. v116 shows why: recovery-vs-regression AUC is moderate around `0.70`, with a weak held-out seed, so the scores have real ranking signal but not enough calibrated tail separation. v117 confirms existing local traces do not contain logprobs, hidden states, embeddings, or decoder telemetry, only text samples and correctness labels. The next positive route needs a substantially stronger verifier endpoint, real symbolic/problem-semantic equivalence, regenerated richer traces, full-cluster process/proof features, additional generator traces, or a genuinely different policy class.

v39 upgrades the deployed-mix scorer so verifier runs report confidence-threshold fallback to the baseline answer and natural-rate weighted `deployed_delta` rows, not just raw packet accuracy. v41 adds a harder generation-only baseline: uncertainty-targeted and tiny learned extra-sampling policies raise coverage but barely move realized `cluster_sum`, especially on MATH/Llama. v42 makes the budget comparison sharper: at 512/1024 tokens per problem, dynamic generation is much weaker than the projected rank-bucket verifier rows on realized selection. v43 reruns the same objection with 8-sample chunks and still gets no positive `cluster_sum` delta at the matched budgets. v44 sweeps that fine-grained generation baseline over three seeds; mean deployed-selector delta remains near zero. v45 adds the pre-specified decision rule for deployed verifier runs: stratified bootstrap CIs over deployment categories, with a pass only when the lower 95% CI on natural-rate weighted `deployed_delta` is positive. v46 adds a power plan: the current 72-prompt/model deployed-mix set is enough for a useful medium-effect smoke, but marginal break-even effects need a larger packet set before being claimed. v47 audits representativeness: the current deployed-mix assets have only 37-38 unique source problems per model and should be framed as smoke assets, not broad generalization evidence. v48 builds a lower-duplication alternative: 79 Llama and 96 Gemma one-packet-per-source prompts, with Llama rare-category sparsity now explicitly measured. v49 locks the core diagnostic numbers behind a script-generated canonical table with explicit provenance drift. v50 refreshes the live literature pressure map through 2026, v51 tests the First Finish Search/short-trace objection, v53 seed-sweeps scorer model transfer, v54 bounds task transfer, v55 separates selection from calibration transfer, v56 distills the current publishable pitch, v57 adds problem-bootstrap CIs for the canonical MATH gap, v58 extends the same bootstrap/depth audit across all local traces, v59 seed-sweeps that regime map, v60 updates the literature boundary, v61 adds the N-sweep phase diagram, v62 seed-sweeps that diagram, v63 turns it into verifier-spend triage, and v64 stress-tests the regime thresholds. v78-v82 then test the local-verifier fallback family: trained feature selection finds shallow top5 signal, margin/utility/risk override gates cannot safely transfer calibration, and the eight-seed audit shows target-oracle top20-only recovery remains `0`. v83/v84 add the qwen3:14b stopline, including the richer problem-inclusive prompt failure. v85-v91 add projected allocation transfer, quality robustness, cross-seed robustness, budget-dependence, explicit verifier-quality targets, a 2D quality-region map, and seed-pair bootstrap: the rank-bucket depth policy is not obviously one-model calibration, one-quality-point luck, or same-split-seed coupling, but the cleanest portable result is asymmetric. Llama->Gemma is stable at 1024; Gemma->Llama is promising but lower-bound fragile. High-N MATH remains the depth-limited verifier target; GSM8K surfaces early, Pythia remains coverage-limited, and local qwen/gemma prompt variants are now negative evidence rather than the path forward.
