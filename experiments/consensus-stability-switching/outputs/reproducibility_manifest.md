# Reproducibility Manifest

**Date:** June 1, 2026  
**Workspace:** `/Users/trevorrosato/Documents/Codex/2026-06-01/all-right-suck-it-i-believe-2`

## Environment

- Python: `3.14.3`
- Main dependency: `numpy`
- No sklearn, torch, pandas, or transformer stack required for the completed experiments.
- Remote Windows/RTX 4070 PC is usually reachable via `ssh -o User=trevor trevors-pc.local`, but v84 saw mDNS/alias flakiness. Direct `ssh -o User=trevor 192.168.1.151` worked; `ssh pc` / `192.168.1.223` timed out.
- Remote Ollama is reachable through the explicit IPv4 local tunnel `http://127.0.0.1:11435`, with `mathstral:7b`, `llama3.2:1b`, `qwen3.5:9b`, `gemma4:26b`, and `qwen3:14b` listed after the v119 run.
- Use `ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local`; fall back to direct IP only if mDNS is flaky.

## Data Files

Public repeated-sampling traces from the Monkey Business dataset were downloaded into `work/`.

| file | sha256 |
|---|---|
| `work/GSM8K_Llama-3-8B-Instruct.json` | `0e334c7010a2eb39ab0aaf38cdd196da0b6219a95fd69f82d35b8f51e46ed765` |
| `work/MATH_Llama-3-8B-Instruct.json` | `e2ebc4e3ff3fa3ae2c58274f839b63447aafca157c70482352a6ae279bad04b3` |
| `work/MATH_Gemma-2B.json` | `f8ba7786ce781512b279caf50c62f3777812b951a396b0e9ce1ff5c6a6f7bc58` |
| `work/MATH_Pythia-1B.json` | `b5290ddac205f69fe0416ab60a6d56abd264687e50c231aed18506fba3a09852` |

## Core Commands

Current narrative artifacts:

- `outputs/result_ledger.md`
- `outputs/adaptive_depth_method_proposal.md`
- `outputs/paper_draft_adaptive_cluster_depth.md`
- `outputs/css_research_note_v34_measured_verifier_handoff.md`
- `outputs/css_research_note_v35_paper_package.md`
- `outputs/css_research_note_v36_generation_vs_verification.md`
- `outputs/css_research_note_v37_deployed_mix_verifier_assets.md`
- `outputs/css_research_note_v38_deployed_mix_break_even.md`
- `outputs/css_research_note_v39_deployed_mix_threshold_scoring.md`
- `outputs/css_research_note_v40_current_lit_pressure_test.md`
- `outputs/css_research_note_v41_dynamic_sampling_baseline.md`
- `outputs/css_research_note_v42_token_budget_generation_vs_verification.md`
- `outputs/css_research_note_v43_fine_grained_generation_budget.md`
- `outputs/css_research_note_v44_dynamic_generation_seed_sweep.md`
- `outputs/css_research_note_v45_deployed_mix_statistical_decision.md`
- `outputs/css_research_note_v46_deployed_mix_power_plan.md`
- `outputs/css_research_note_v47_deployed_mix_representativeness.md`
- `outputs/css_research_note_v48_unique_source_deployed_mix_assets.md`
- `outputs/css_research_note_v49_canonical_number_lock.md`
- `outputs/css_research_note_v50_live_literature_refresh.md`
- `outputs/css_research_note_v51_short_trace_baseline.md`
- `outputs/css_research_note_v52_cross_model_verifier_transfer.md`
- `outputs/css_research_note_v53_cross_model_transfer_seed_sweep.md`
- `outputs/css_research_note_v54_cross_task_transfer_boundary.md`
- `outputs/css_research_note_v55_transfer_calibration_audit.md`
- `outputs/css_research_note_v56_reviewer_resistant_pitch.md`
- `outputs/css_research_note_v57_canonical_gap_bootstrap_ci.md`
- `outputs/css_research_note_v58_cross_trace_gap_bootstrap.md`
- `outputs/css_research_note_v59_cross_trace_regime_seed_sweep.md`
- `outputs/css_research_note_v60_literature_boundary_addendum.md`
- `outputs/css_research_note_v61_selectability_phase_diagram.md`
- `outputs/css_research_note_v62_phase_seed_sweep.md`
- `outputs/css_research_note_v63_phase_aware_verifier_triage.md`
- `outputs/css_research_note_v64_phase_threshold_sensitivity.md`
- `outputs/css_research_note_v65_verifier_quality_sensitivity.md`
- `outputs/css_research_note_v66_phase_depth_marginal_utility.md`
- `outputs/css_research_note_v67_phase_depth_cost_roi.md`
- `outputs/css_research_note_v68_phase_depth_policy_frontier.md`
- `outputs/css_research_note_v69_phase_depth_policy_quality_sweep.md`
- `outputs/css_research_note_v70_live_literature_positioning_refresh.md`
- `outputs/css_research_note_v71_deployed_mix_verifier_requirement_table.md`
- `outputs/css_research_note_v72_deployed_mix_requirement_representativeness_sweep.md`
- `outputs/css_research_note_v73_llama_unique_source_tail_expansion.md`
- `outputs/css_research_note_v74_deployed_mix_verifier_report_harness.md`
- `outputs/css_research_note_v75_remote_ollama_verifier_smoke.md`
- `outputs/css_research_note_v76_qwen_evidence_budget_probe.md`
- `outputs/css_research_note_v77_answer_only_verifier_interface.md`
- `outputs/css_research_note_v78_deployed_mix_feature_selector.md`
- `outputs/css_research_note_v79_calibrated_override_selector.md`
- `outputs/css_research_note_v80_utility_override_selector.md`
- `outputs/css_research_note_v81_risk_controlled_override_selector.md`
- `outputs/css_research_note_v82_override_calibration_stability.md`
- `outputs/css_research_note_v83_qwen14b_and_literature_stopline.md`
- `outputs/css_research_note_v84_qwen14b_rich_problem_prompt_stopline.md`
- `outputs/css_research_note_v85_rank_bucket_cross_model_transfer.md`
- `outputs/css_research_note_v86_rank_bucket_transfer_quality_sweep.md`
- `outputs/css_research_note_v87_rank_bucket_cross_seed_transfer.md`
- `outputs/css_research_note_v88_rank_bucket_transfer_budget_map.md`
- `outputs/css_research_note_v89_rank_bucket_verifier_quality_targets.md`
- `outputs/css_research_note_v90_rank_bucket_quality_region_map.md`
- `outputs/css_research_note_v91_rank_bucket_pair_bootstrap.md`
- `outputs/css_research_note_v92_mathstral_verifier_boundary.md`
- `outputs/css_research_note_v93_binary_cluster_judge_interface.md`
- `outputs/css_research_note_v94_qwen14b_binary_cluster_judge.md`
- `outputs/css_research_note_v95_text_semantic_cluster_scorer.md`
- `outputs/css_research_note_v96_source_calibrated_semantic_risk.md`
- `outputs/css_research_note_v97_unique_source_semantic_risk.md`
- `outputs/css_research_note_v98_rebuilt_unique_semantic_risk.md`
- `outputs/css_research_note_v99_raw_semantic_threshold_boundary.md`
- `outputs/css_research_note_v100_split_trained_semantic_threshold_audit.md`
- `outputs/css_research_note_v101_semantic_calibration_scaling.md`
- `outputs/css_research_note_v102_target_style_semantic_calibration.md`
- `outputs/css_research_note_v103_expanded_target_semantic_calibration.md`
- `outputs/css_research_note_v104_rich_signal_semantic_calibration.md`
- `outputs/css_research_note_v105_semantic_meta_gate.md`
- `outputs/css_research_note_v106_symbolic_feature_boundary.md`
- `outputs/css_research_note_v107_process_cluster_scorer.md`
- `outputs/css_research_note_v108_cross_generator_agreement.md`
- `outputs/canonical_selectability_depth_table.md`
- `outputs/cross_trace_gap_bootstrap_ci.md`
- `outputs/cross_trace_regime_seed_sweep.md`
- `outputs/cross_trace_phase_diagram.md`
- `outputs/cross_trace_phase_seed_sweep.md`
- `outputs/phase_aware_verifier_triage.md`
- `outputs/phase_threshold_sensitivity.csv`
- `outputs/verifier_quality_sensitivity.md`
- `outputs/phase_depth_marginal_utility.md`
- `outputs/phase_depth_cost_roi.md`
- `outputs/phase_depth_policy_frontier.md`
- `outputs/phase_depth_policy_quality_sweep.md`
- `outputs/deployed_mix_verifier_requirement_table.md`
- `outputs/deployed_mix_requirement_representativeness_sweep.md`
- `outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.md`
- `outputs/deployed_mix_unique32_llama_unique16_gemma_representativeness.md`
- `outputs/synthetic_deployed_mix_verifier_report.md`
- `outputs/qwen35_9b_deployed_mix_real_v75_slim_concise_percat1_report.md`
- `outputs/qwen35_9b_v76_recoverable_failures_rich_concise_report.md`
- `outputs/qwen35_9b_v76_recoverable_failures_rich_evidenceonly_report.md`
- `outputs/qwen35_9b_v77_recoverable_failures_answeronly_evidenceonly_report.md`
- `outputs/gemma4_26b_v77_recoverable_failures_answeronly_evidenceonly_report.md`
- `outputs/measured_local_verifier_stopline.md`
- `outputs/qwen3_14b_v83_recoverable_failures_answeronly_evidenceonly_report.md`
- `outputs/qwen3_14b_think_v83_recoverable_failures_answeronly_evidenceonly_report.md`
- `outputs/qwen3_14b_v83_deployed_mix_real_v75_slim_concise_percat1_report.md`
- `outputs/qwen3_14b_v83_full144_answeronly_evidenceonly_report.md`
- `outputs/qwen3_14b_v84_recoverable_failures_rich_concise_report.md`
- `outputs/qwen3_14b_v84_full144_rich_concise_report.md`
- `outputs/mathstral_7b_v92_deployed_mix_real_v75_slim_concise_percat1_report.md`
- `outputs/mathstral_7b_v92_v77_answeronly_evidenceonly_percat1_report.md`
- `outputs/mathstral_7b_v92_slim_answeronly_evidenceonly_percat1_report.md`
- `outputs/mathstral_7b_v93_binary_cluster_judge_recoverable_report.md`
- `outputs/mathstral_7b_v93_binary_answer_check_recoverable_report.md`
- `outputs/qwen3_14b_v94_binary_cluster_judge_recoverable_report.md`
- `outputs/qwen3_14b_v94_binary_answer_check_recoverable_report.md`
- `outputs/make_binary_cluster_judge_prompts.py`
- `outputs/score_binary_cluster_judge.py`
- `outputs/rank_bucket_cross_model_transfer_v85.md`
- `outputs/rank_bucket_cross_model_transfer_v85.csv`
- `outputs/rank_bucket_cross_model_transfer_v85_raw.csv`
- `outputs/rank_bucket_transfer_quality_sweep_v86.md`
- `outputs/rank_bucket_transfer_quality_sweep_v86.csv`
- `outputs/rank_bucket_transfer_quality_sweep_v86_raw.csv`
- `outputs/rank_bucket_transfer_quality_sweep_v86_summary.csv`
- `outputs/rank_bucket_cross_seed_transfer_v87.md`
- `outputs/rank_bucket_cross_seed_transfer_v87.csv`
- `outputs/rank_bucket_cross_seed_transfer_v87_raw.csv`
- `outputs/rank_bucket_cross_seed_transfer_v87_summary.csv`
- `outputs/rank_bucket_transfer_budget_map_v88.md`
- `outputs/rank_bucket_transfer_budget_map_v88.csv`
- `outputs/rank_bucket_transfer_budget_map_v88_summary.csv`
- `outputs/rank_bucket_verifier_quality_targets_v89.md`
- `outputs/rank_bucket_verifier_quality_targets_v89.csv`
- `outputs/rank_bucket_verifier_quality_targets_v89_summary.csv`
- `outputs/rank_bucket_quality_region_map_v90.md`
- `outputs/rank_bucket_quality_region_map_v90.csv`
- `outputs/rank_bucket_quality_region_map_v90_summary.csv`
- `outputs/rank_bucket_pair_bootstrap_v91.md`
- `outputs/rank_bucket_pair_bootstrap_v91.csv`
- `outputs/rank_bucket_pair_bootstrap_v91_summary.csv`
- `outputs/deployed_mix_feature_selector_v78_cross_model_report.md`
- `outputs/deployed_mix_feature_selector_v78_unique_train_cross_model_report.md`
- `outputs/deployed_mix_feature_selector_v78_hardtrain_cross_model_report.md`
- `outputs/deployed_mix_feature_selector_v78_unique_filtered_same_model_report.md`
- `outputs/calibrated_override_v79_unique_cross_model_report.md`
- `outputs/calibrated_override_v79_balanced_cross_model_report.md`
- `outputs/calibrated_override_v79_oracle_unique_cross_model_report.md`
- `outputs/utility_override_v80_unique_cross_model_report.md`
- `outputs/utility_override_v80_balanced_cross_model_report.md`
- `outputs/utility_override_v80_oracle_unique_cross_model_report.md`
- `outputs/utility_override_v80_oracle_balanced_cross_model_report.md`
- `outputs/risk_controlled_override_v81_unique_cross_model_report.md`
- `outputs/risk_controlled_override_v81_balanced_cross_model_report.md`
- `outputs/risk_controlled_override_v81_target_oracle_unique_cross_model_report.md`
- `outputs/risk_controlled_override_v81_target_oracle_balanced_cross_model_report.md`
- `outputs/override_calibration_stability_v82.md`
- `outputs/override_calibration_stability_v82_summary.csv`
- `outputs/override_calibration_stability_v82_details.csv`
- `outputs/blind_deployed_mix_v66_assignments.md`
- `outputs/adversarial_reviewer_checklist.md`

Multi-config selector summary:

```bash
python3 work/monkey_css_realbench.py --data work/GSM8K_Llama-3-8B-Instruct.json --dataset-label GSM8K_Llama-3-8B-Instruct --output-prefix monkey_css_gsm8k_realbench
python3 work/monkey_css_realbench.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-3-8B-Instruct --output-prefix monkey_css_math_realbench
python3 work/monkey_css_realbench.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-2B --output-prefix monkey_css_math_gemma2b_realbench
python3 work/monkey_css_realbench.py --data work/MATH_Pythia-1B.json --dataset-label MATH_Pythia-1B --output-prefix monkey_css_math_pythia1b_realbench
python3 work/aggregate_monkey_results.py
```

Cluster selectability audits:

```bash
python3 work/cluster_selectability_audit.py --data work/GSM8K_Llama-3-8B-Instruct.json --dataset-label GSM8K_Llama-3-8B-Instruct --output-prefix cluster_selectability_gsm8k_llama --trials-per-problem 6
python3 work/cluster_selectability_audit.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-3-8B-Instruct --output-prefix cluster_selectability_math_llama
python3 work/cluster_selectability_audit.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-2B --output-prefix cluster_selectability_math_gemma2b
python3 work/cluster_selectability_audit.py --data work/MATH_Pythia-1B.json --dataset-label MATH_Pythia-1B --output-prefix cluster_selectability_math_pythia1b --trials-per-problem 6
python3 work/topk_cluster_oracle_bounds.py
```

Consistency-feature ranker:

```bash
python3 work/monkey_cluster_ranker.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-3-8B-Instruct --output-prefix monkey_cluster_ranker_consistency_math_llama --trials-per-problem 12 --max-train-clusters 30000
python3 work/monkey_cluster_ranker.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-2B --output-prefix monkey_cluster_ranker_consistency_math_gemma2b --trials-per-problem 12 --max-train-clusters 30000
```

Hard-packet and rescue-selector experiments:

```bash
python3 work/build_cluster_packet_dataset.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-3-8B-Instruct --output-prefix cluster_packets_math_llama_n128 --max-packets 60 --trials-per-problem 3 --n 128 --top-k 5
python3 work/build_cluster_packet_dataset.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-2B --output-prefix cluster_packets_math_gemma2b_n128 --max-packets 60 --trials-per-problem 3 --n 128 --top-k 5
python3 work/evaluate_cluster_packets.py --packets outputs/cluster_packets_math_llama_n128.jsonl --output outputs/cluster_packets_math_llama_n128_baselines.md
python3 work/evaluate_cluster_packets.py --packets outputs/cluster_packets_math_gemma2b_n128.jsonl --output outputs/cluster_packets_math_gemma2b_n128_baselines.md
python3 work/hard_packet_feature_transfer.py --llama outputs/cluster_packets_math_llama_n128.jsonl --gemma outputs/cluster_packets_math_gemma2b_n128.jsonl --output-prefix hard_packet_feature_transfer
python3 work/evaluate_rescue_selector_full.py --train-packets outputs/cluster_packets_math_llama_n128.jsonl --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-3-8B-Instruct --output-prefix rescue_selector_full_llama_train_llama_eval_llama --trials-per-problem 6
python3 work/evaluate_rescue_selector_full.py --train-packets outputs/cluster_packets_math_gemma2b_n128.jsonl --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-2B --output-prefix rescue_selector_full_gemma_train_gemma_eval_gemma --trials-per-problem 6
python3 work/gated_rescue_selector.py --train-packets outputs/cluster_packets_math_llama_n128.jsonl --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-3-8B-Instruct --output-prefix gated_rescue_math_llama_n128_t12 --trials-per-problem 12
python3 work/gated_rescue_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128.jsonl --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-2B --output-prefix gated_rescue_math_gemma2b_n128_t12 --trials-per-problem 12
```

Failure detector:

```bash
python3 work/failure_detector_diagnostics.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-3-8B-Instruct --output-prefix failure_detector_math_llama_n128 --trials-per-problem 12
python3 work/failure_detector_diagnostics.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-2B --output-prefix failure_detector_math_gemma2b_n128 --trials-per-problem 12
python3 work/failure_detector_feature_ablation.py
python3 work/failure_detector_transfer.py
python3 work/detector_verifier_frontier.py
python3 work/test_failure_detector_zoo.py
python3 work/failure_detector_zoo.py
python3 work/compare_detector_zoo_frontier.py
python3 work/failure_detector_seed_sweep.py
python3 work/compare_seed_sweep_to_frontier.py
```

Deep top-k cluster-depth audit:

```bash
python3 work/test_deep_topk_cluster_audit.py
python3 work/deep_topk_cluster_audit.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-parser-v2 --output-prefix deep_topk_math_llama_n128 --ns 128 --trials-per-problem 12
python3 work/deep_topk_cluster_audit.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-parser-v2 --output-prefix deep_topk_math_gemma2b_n128 --ns 128 --trials-per-problem 12
python3 work/test_make_canonical_selectability_depth_table.py
python3 work/make_canonical_selectability_depth_table.py --output-prefix canonical_selectability_depth_table
python3 work/test_adaptive_depth_frontier.py
python3 work/adaptive_depth_frontier.py
```

Cluster verifier prompts and audits:

```bash
python3 work/test_build_cluster_packet_dataset.py
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_full.jsonl
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_full.jsonl
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_top5_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_top5_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/build_cluster_packet_dataset.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-top20-rank11-20-strict --output-prefix cluster_packets_math_llama_n128_top20_rank11_20_strict --top-k 20 --min-correct-rank 11 --max-correct-rank 20 --max-packets 30 --trials-per-problem 20 --rationale-chars 700 --representatives-per-cluster 2 --no-force-correct-visible --require-correct-visible
python3 work/build_cluster_packet_dataset.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-top20-rank11-20-strict --output-prefix cluster_packets_math_gemma2b_n128_top20_rank11_20_strict --top-k 20 --min-correct-rank 11 --max-correct-rank 20 --max-packets 30 --trials-per-problem 20 --rationale-chars 700 --representatives-per-cluster 2 --no-force-correct-visible --require-correct-visible
python3 work/build_cluster_packet_dataset.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-top20-rank11-20-diverse --output-prefix cluster_packets_math_llama_n128_top20_rank11_20_diverse --top-k 20 --min-correct-rank 11 --max-correct-rank 20 --max-packets 40 --max-packets-per-problem 1 --trials-per-problem 80 --rationale-chars 700 --representatives-per-cluster 2 --no-force-correct-visible --require-correct-visible
python3 work/build_cluster_packet_dataset.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-top20-rank11-20-diverse --output-prefix cluster_packets_math_gemma2b_n128_top20_rank11_20_diverse --top-k 20 --min-correct-rank 11 --max-correct-rank 20 --max-packets 40 --max-packets-per-problem 1 --trials-per-problem 80 --rationale-chars 700 --representatives-per-cluster 2 --no-force-correct-visible --require-correct-visible
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128_top20_rank11_20_strict.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_strict.jsonl
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_top20_rank11_20_strict.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_strict.jsonl
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128_top20_rank11_20_diverse.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse.jsonl
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_top20_rank11_20_diverse.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse.jsonl
python3 work/test_make_cluster_verifier_prompts.py
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128_top10_strict.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_top10_strict_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_top10_strict.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_top10_strict_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128_top20_rank11_20_diverse.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_top20_rank11_20_diverse.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/test_audit_packet_representative_visibility.py
python3 work/audit_packet_representative_visibility.py --packet-set 'Llama diverse' outputs/cluster_packets_math_llama_n128_top20_rank11_20_diverse.jsonl --packet-set 'Gemma diverse' outputs/cluster_packets_math_gemma2b_n128_top20_rank11_20_diverse.jsonl --packet-set 'Llama repeated' outputs/cluster_packets_math_llama_n128_top20_rank11_20_strict.jsonl --packet-set 'Gemma repeated' outputs/cluster_packets_math_gemma2b_n128_top20_rank11_20_strict.jsonl --output-prefix packet_representative_visibility
python3 work/test_evidence_budget_frontier.py
python3 work/evidence_budget_frontier.py --depth 20 --invoke-rate 0.20 --output-prefix evidence_budget_frontier
python3 work/test_cost_aware_verifier_cascade.py
python3 work/cost_aware_verifier_cascade.py --depth 20 --invoke-rate 0.20 --output-prefix cost_aware_verifier_cascade
python3 work/test_score_verifier_cascade.py
python3 work/test_iso_budget_depth_frontier.py
python3 work/iso_budget_depth_frontier.py --output-prefix iso_budget_depth_frontier
python3 work/test_budgeted_depth_policy.py
python3 work/budgeted_depth_policy.py --output-prefix budgeted_depth_policy
python3 work/test_rank_bucket_depth_policy.py
python3 work/rank_bucket_depth_policy.py --output-prefix rank_bucket_depth_policy
python3 work/test_rank_bucket_seed_sweep.py
python3 work/rank_bucket_seed_sweep.py --output-prefix rank_bucket_seed_sweep
python3 work/cluster_selectability_audit.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-generation-scaling --output-prefix generation_scaling_math_llama --ns 4,8,16,32,64,128,256,512,1024 --trials-per-problem 12
python3 work/cluster_selectability_audit.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-generation-scaling --output-prefix generation_scaling_math_gemma2b --ns 4,8,16,32,64,128,256,512,1024 --trials-per-problem 12
python3 work/test_generation_vs_verification_budget.py
python3 work/generation_vs_verification_budget.py --output-prefix generation_vs_verification_budget
python3 work/test_dynamic_sampling_baseline.py
python3 work/dynamic_sampling_baseline.py --output-prefix dynamic_sampling_baseline --avg-extra-samples 32,64,128,192,384,896
python3 work/dynamic_sampling_baseline.py --output-prefix dynamic_sampling_token_matched --avg-extra-samples 4,8,16,32
python3 work/test_token_budget_generation_vs_verification.py
python3 work/token_budget_generation_vs_verification.py --output-prefix token_budget_generation_vs_verification
python3 work/dynamic_sampling_baseline.py --output-prefix dynamic_sampling_fine_token_matched --chunk-size 8 --avg-extra-samples 4,8,16,32
python3 work/token_budget_generation_vs_verification.py --dynamic-csv outputs/dynamic_sampling_fine_token_matched.csv --output-prefix token_budget_generation_vs_verification_fine
python3 work/test_dynamic_generation_seed_sweep.py
python3 work/dynamic_generation_seed_sweep.py --output-prefix dynamic_generation_seed_sweep
python3 work/test_short_trace_baseline.py
python3 work/short_trace_baseline.py --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json MATH/Gemma=work/MATH_Gemma-2B.json --ns 128 --trials-per-problem 12 --output-prefix short_trace_baseline
python3 work/test_cross_model_verifier_transfer.py
python3 work/cross_model_verifier_transfer.py --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json MATH/Gemma=work/MATH_Gemma-2B.json --n 128 --trials-per-problem 12 --seed 60601 --verifier-train-problems 20 --audit-holdout-gap 24 --verifier-samples-per-problem 120 --output-prefix cross_model_verifier_transfer
python3 work/test_cross_model_verifier_transfer_seed_sweep.py
python3 work/cross_model_verifier_transfer_seed_sweep.py --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json MATH/Gemma=work/MATH_Gemma-2B.json --seeds 60601 60602 60603 --n 128 --trials-per-problem 12 --verifier-train-problems 20 --audit-holdout-gap 24 --verifier-samples-per-problem 120 --output-prefix cross_model_verifier_transfer_seed_sweep
python3 work/cross_model_verifier_transfer_seed_sweep.py --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json GSM8K/Llama=work/GSM8K_Llama-3-8B-Instruct.json --seeds 60601 60602 60603 --n 128 --trials-per-problem 12 --verifier-train-problems 20 --audit-holdout-gap 24 --verifier-samples-per-problem 120 --output-prefix cross_task_verifier_transfer_seed_sweep
python3 work/test_transfer_calibration_summary.py
python3 work/transfer_calibration_summary.py --input model=outputs/cross_model_verifier_transfer_seed_sweep.csv task=outputs/cross_task_verifier_transfer_seed_sweep.csv --output-prefix transfer_calibration_summary
python3 work/test_canonical_gap_bootstrap_ci.py
python3 work/canonical_gap_bootstrap_ci.py --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json MATH/Gemma=work/MATH_Gemma-2B.json --n 128 --trials-per-problem 12 --seed 60601 --verifier-train-problems 30 --audit-holdout-gap 24 --verifier-samples-per-problem 800 --bootstrap-rounds 2000 --output-prefix canonical_gap_bootstrap_ci
python3 work/canonical_gap_bootstrap_ci.py --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json MATH/Gemma=work/MATH_Gemma-2B.json GSM8K/Llama=work/GSM8K_Llama-3-8B-Instruct.json MATH/Pythia=work/MATH_Pythia-1B.json --n 128 --trials-per-problem 12 --seed 60601 --verifier-train-problems 30 --audit-holdout-gap 24 --verifier-samples-per-problem 800 --bootstrap-rounds 2000 --output-prefix cross_trace_gap_bootstrap_ci --report-title 'Cross-Trace Gap Bootstrap CI' --report-description 'Problem-bootstrap uncertainty for the same N=128 selector/oracle/depth audit across all local Monkey Business traces.' --read-note 'The selectability gap is largest on hard MATH traces, nearly saturated on GSM8K/Llama, and still present but lower-coverage on MATH/Pythia. This makes the claim sharper: answer-cluster selectability is a stress-condition diagnostic, not a universal promise that every dataset has the same failure mode.'
python3 work/test_cross_trace_regime_seed_sweep.py
python3 work/cross_trace_regime_seed_sweep.py --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json MATH/Gemma=work/MATH_Gemma-2B.json GSM8K/Llama=work/GSM8K_Llama-3-8B-Instruct.json MATH/Pythia=work/MATH_Pythia-1B.json --seeds 60601 60602 60603 --n 128 --trials-per-problem 12 --verifier-train-problems 30 --audit-holdout-gap 24 --verifier-samples-per-problem 800 --output-prefix cross_trace_regime_seed_sweep
python3 work/test_cross_trace_phase_diagram.py
python3 work/cross_trace_phase_diagram.py --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json MATH/Gemma=work/MATH_Gemma-2B.json GSM8K/Llama=work/GSM8K_Llama-3-8B-Instruct.json MATH/Pythia=work/MATH_Pythia-1B.json --ns 4 8 16 32 64 128 --trials-per-problem 12 --seed 60601 --verifier-train-problems 30 --audit-holdout-gap 24 --verifier-samples-per-problem 800 --output-prefix cross_trace_phase_diagram
python3 work/test_cross_trace_phase_seed_sweep.py
python3 work/cross_trace_phase_seed_sweep.py --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json MATH/Gemma=work/MATH_Gemma-2B.json GSM8K/Llama=work/GSM8K_Llama-3-8B-Instruct.json MATH/Pythia=work/MATH_Pythia-1B.json --ns 4 8 16 32 64 128 --seeds 60601 60602 60603 --trials-per-problem 12 --verifier-train-problems 30 --audit-holdout-gap 24 --verifier-samples-per-problem 800 --output-prefix cross_trace_phase_seed_sweep
python3 work/test_phase_aware_verifier_triage.py
python3 work/phase_aware_verifier_triage.py --phase-csv outputs/cross_trace_phase_seed_sweep.csv --output-prefix phase_aware_verifier_triage
python3 work/test_phase_threshold_sensitivity.py
python3 work/phase_threshold_sensitivity.py --input outputs/cross_trace_phase_seed_sweep_raw.csv --output-prefix phase_threshold_sensitivity --note-version v64
python3 work/test_verifier_quality_sensitivity.py
python3 work/verifier_quality_sensitivity.py --phase-csv outputs/cross_trace_phase_seed_sweep.csv --output-prefix verifier_quality_sensitivity
python3 work/test_phase_depth_marginal_utility.py
python3 work/phase_depth_marginal_utility.py --phase-csv outputs/cross_trace_phase_seed_sweep.csv --output-prefix phase_depth_marginal_utility
python3 work/test_phase_depth_cost_roi.py
python3 work/phase_depth_cost_roi.py --marginal-csv outputs/phase_depth_marginal_utility.csv --output-prefix phase_depth_cost_roi
python3 work/test_phase_depth_policy_frontier.py
python3 work/phase_depth_policy_frontier.py --cost-csv outputs/phase_depth_cost_roi.csv --output-prefix phase_depth_policy_frontier --value-grid 4000,8000,16000,32000,64000 --verifier-success 0.80 --false-regress 0.02
python3 work/test_phase_depth_policy_quality_sweep.py
python3 work/phase_depth_policy_quality_sweep.py --cost-csv outputs/phase_depth_cost_roi.csv --output-prefix phase_depth_policy_quality_sweep --value-grid 4000,8000,16000,32000,64000 --success-grid 0.50,0.80,1.00 --regress-grid 0.00,0.02,0.05
python3 work/test_deployed_mix_verifier_requirement_table.py
python3 work/deployed_mix_verifier_requirement_table.py --output-prefix deployed_mix_verifier_requirement_table --max-baseline-regressions 3
python3 work/test_deployed_mix_requirement_representativeness_sweep.py
python3 work/deployed_mix_requirement_representativeness_sweep.py --output-prefix deployed_mix_requirement_representativeness_sweep --baseline-regressions 1
python3 work/build_deployed_mix_packet_dataset.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-deployed-mix-top20-unique32 --output-prefix cluster_packets_math_llama_n128_deployed_mix_top20_unique32 --target-per-category 32 --trials-per-problem 96 --max-packets-per-problem 1 --seed 60601
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/audit_deployed_mix_representativeness.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl --output-prefix deployed_mix_unique32_llama_unique16_gemma_representativeness
python3 work/test_deployed_mix_verifier_report.py
python3 work/deployed_mix_verifier_report.py --predictions outputs/synthetic_deployed_mix_llama_predictions.jsonl outputs/synthetic_deployed_mix_gemma_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 100 --output-prefix synthetic_deployed_mix_verifier_report
python3 work/test_build_blind_deployed_mix_panel.py
python3 work/build_blind_deployed_mix_panel.py --output-prefix blind_deployed_mix_v66 --per-category 2 --chunks 6
python3 work/test_build_deployed_mix_packet_dataset.py
python3 work/build_deployed_mix_packet_dataset.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-deployed-mix-top20 --output-prefix cluster_packets_math_llama_n128_deployed_mix_top20 --target-per-category 12 --trials-per-problem 24 --max-packets-per-problem 2
python3 work/build_deployed_mix_packet_dataset.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-deployed-mix-top20 --output-prefix cluster_packets_math_gemma2b_n128_deployed_mix_top20 --target-per-category 12 --trials-per-problem 24 --max-packets-per-problem 2
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/test_score_deployed_mix_verifier.py
python3 work/score_deployed_mix_verifier.py --predictions outputs/<model>_llama_deployed_mix_predictions.jsonl outputs/<model>_gemma_deployed_mix_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.25,0.5,0.75,0.9 --output-prefix <model>_deployed_mix_verifier
python3 work/test_deployed_mix_policy_ci.py
python3 work/deployed_mix_policy_ci.py --predictions outputs/<model>_llama_deployed_mix_predictions.jsonl outputs/<model>_gemma_deployed_mix_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.25,0.5,0.75,0.9 --bootstrap-rounds 1000 --output-prefix <model>_deployed_mix_policy_ci
python3 work/deployed_mix_policy_ci.py --predictions outputs/synthetic_deployed_mix_llama_predictions.jsonl outputs/synthetic_deployed_mix_gemma_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 300 --output-prefix synthetic_deployed_mix_policy_ci
python3 work/test_deployed_mix_power_plan.py
python3 work/deployed_mix_power_plan.py --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --n-per-category 12,24,48,96 --simulations 120 --bootstrap-rounds 120 --output-prefix deployed_mix_power_plan
python3 work/test_audit_deployed_mix_representativeness.py
python3 work/audit_deployed_mix_representativeness.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --output-prefix deployed_mix_representativeness
python3 work/build_deployed_mix_packet_dataset.py --data work/MATH_Llama-3-8B-Instruct.json --dataset-label MATH_Llama-deployed-mix-top20-unique16 --output-prefix cluster_packets_math_llama_n128_deployed_mix_top20_unique16 --target-per-category 16 --trials-per-problem 64 --max-packets-per-problem 1 --verifier-train-problems 10 --audit-holdout-gap 0
python3 work/build_deployed_mix_packet_dataset.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-deployed-mix-top20-unique16 --output-prefix cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16 --target-per-category 16 --trials-per-problem 64 --max-packets-per-problem 1 --verifier-train-problems 10 --audit-holdout-gap 0
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique16.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique16_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_unique16_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/audit_deployed_mix_representativeness.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique16.jsonl outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl --output-prefix deployed_mix_unique16_representativeness
python3 work/test_deployed_mix_break_even.py
python3 work/deployed_mix_break_even.py --output-prefix deployed_mix_break_even
python3 work/extract_verifier_prompt_families.py
python3 work/make_manual_full_verifier_predictions.py
python3 work/score_llm_judges.py --predictions outputs/llm_manual_full120_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_full.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_full.answer_key.json --output-prefix llm_manual_full120_cluster_verifier
python3 work/full_verifier_panel_audit.py
python3 work/hard_packet_diversity_audit.py
python3 work/evaluate_cluster_packets.py --packets outputs/cluster_packets_math_llama_n128_top20_rank11_20_strict.jsonl --output outputs/cluster_packets_math_llama_n128_top20_rank11_20_strict_baselines.md
python3 work/evaluate_cluster_packets.py --packets outputs/cluster_packets_math_gemma2b_n128_top20_rank11_20_strict.jsonl --output outputs/cluster_packets_math_gemma2b_n128_top20_rank11_20_strict_baselines.md
python3 work/test_score_llm_judges.py
python3 work/score_llm_judges.py --predictions outputs/pilot_depth_judge_top20_rank11_20_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_strict.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_strict.answer_key.json --output-prefix pilot_depth_judge_top20_rank11_20
```

External/local model verifier runner:

```bash
python3 work/test_run_openai_compatible_verifier.py
python3 work/run_openai_compatible_verifier.py --base-url http://localhost:11434/v1 --model <model> --prompts outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.jsonl --output outputs/<model>_llama_top20_diverse_compact_smoke_predictions.jsonl --limit 3 --resume
python3 work/run_openai_compatible_verifier.py --base-url http://localhost:11434/v1 --model <model> --prompts outputs/cluster_verifier_prompts_math_llama_n128_full.jsonl --output outputs/<model>_llama_full_predictions.jsonl --resume
python3 work/score_llm_judges.py --predictions outputs/<model>_llama_full_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_full.answer_key.json --output-prefix <model>_llama_full_cluster_verifier
```

Remote Ollama native v75 smoke:

```bash
ssh -o User=trevor trevors-pc.local 'powershell -NoProfile -Command "nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader"'
curl -sS http://localhost:11435/api/tags
python3 work/test_run_ollama_native_verifier.py
python3 work/test_build_blind_deployed_mix_panel.py
python3 work/test_deployed_mix_verifier_report.py
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v75_slim_concise.jsonl --representatives-per-cluster 1 --rationale-chars 180 --concise-reason-words 20
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v75_slim_concise.jsonl --representatives-per-cluster 1 --rationale-chars 180 --concise-reason-words 20
python3 work/build_blind_deployed_mix_panel.py --output-prefix deployed_mix_real_v75_slim_concise_percat1 --per-category 1 --chunks 1 --llama-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v75_slim_concise.jsonl --gemma-prompts outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v75_slim_concise.jsonl --llama-answer-key outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v75_slim_concise.answer_key.json --gemma-answer-key outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v75_slim_concise.answer_key.json
python3 work/run_ollama_native_verifier.py --base-url http://localhost:11435 --model qwen3.5:9b --prompts outputs/deployed_mix_real_v75_slim_concise_percat1_prompts.jsonl --output outputs/qwen35_9b_deployed_mix_real_v75_slim_concise_percat1_predictions.jsonl --timeout 180 --retries 1 --log-every 1 --include-timing --num-predict 256 --resume
python3 work/deployed_mix_verifier_report.py --predictions outputs/qwen35_9b_deployed_mix_real_v75_slim_concise_percat1_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v75_slim_concise.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v75_slim_concise.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/deployed_mix_real_v75_slim_concise_percat1_prompts.jsonl --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 500 --output-prefix qwen35_9b_deployed_mix_real_v75_slim_concise_percat1_report
```

Remote Ollama native v76 evidence-budget probes:

```bash
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local
python3 work/test_filter_verifier_prompt_panel.py
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_concise.jsonl --representatives-per-cluster 2 --rationale-chars 420 --concise-reason-words 20
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_concise.jsonl --representatives-per-cluster 2 --rationale-chars 420 --concise-reason-words 20
python3 work/filter_verifier_prompt_panel.py --prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_concise.jsonl outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_concise.jsonl --ids outputs/qwen35_9b_v76_recoverable_failures_ids.txt --output outputs/qwen35_9b_v76_recoverable_failures_rich_concise_prompts.jsonl --add-dataset
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3.5:9b --prompts outputs/qwen35_9b_v76_recoverable_failures_rich_concise_prompts.jsonl --output outputs/qwen35_9b_v76_recoverable_failures_rich_concise_predictions.jsonl --timeout 240 --retries 1 --log-every 1 --include-timing --num-predict 256 --resume
python3 work/deployed_mix_verifier_report.py --predictions outputs/qwen35_9b_v76_recoverable_failures_rich_concise_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_concise.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_concise.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/qwen35_9b_v76_recoverable_failures_rich_concise_prompts.jsonl --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 500 --output-prefix qwen35_9b_v76_recoverable_failures_rich_concise_report
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_evidenceonly.jsonl --representatives-per-cluster 2 --rationale-chars 420 --concise-reason-words 20 --omit-problem --allowed-answers
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_evidenceonly.jsonl --representatives-per-cluster 2 --rationale-chars 420 --concise-reason-words 20 --omit-problem --allowed-answers
python3 work/filter_verifier_prompt_panel.py --prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_evidenceonly.jsonl outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_evidenceonly.jsonl --ids outputs/qwen35_9b_v76_recoverable_failures_ids.txt --output outputs/qwen35_9b_v76_recoverable_failures_rich_evidenceonly_prompts.jsonl --add-dataset
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3.5:9b --prompts outputs/qwen35_9b_v76_recoverable_failures_rich_evidenceonly_prompts.jsonl --output outputs/qwen35_9b_v76_recoverable_failures_rich_evidenceonly_predictions.jsonl --timeout 240 --retries 1 --log-every 1 --include-timing --num-predict 256 --resume
python3 work/deployed_mix_verifier_report.py --predictions outputs/qwen35_9b_v76_recoverable_failures_rich_evidenceonly_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/qwen35_9b_v76_recoverable_failures_rich_evidenceonly_prompts.jsonl --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 500 --output-prefix qwen35_9b_v76_recoverable_failures_rich_evidenceonly_report
```

Remote Ollama native v77 answer-only probes:

```bash
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl --representatives-per-cluster 2 --rationale-chars 420 --omit-problem --allowed-answers --answer-only
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl --representatives-per-cluster 2 --rationale-chars 420 --omit-problem --allowed-answers --answer-only
python3 work/filter_verifier_prompt_panel.py --prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl --ids outputs/qwen35_9b_v76_recoverable_failures_ids.txt --output outputs/v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl --add-dataset
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3.5:9b --prompts outputs/v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl --output outputs/qwen35_9b_v77_recoverable_failures_answeronly_evidenceonly_predictions.jsonl --timeout 240 --retries 1 --log-every 1 --include-timing --num-predict 64 --schema-mode answer_only --resume
python3 work/deployed_mix_verifier_report.py --predictions outputs/qwen35_9b_v77_recoverable_failures_answeronly_evidenceonly_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 500 --output-prefix qwen35_9b_v77_recoverable_failures_answeronly_evidenceonly_report
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model gemma4:26b --prompts outputs/v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl --output outputs/gemma4_26b_v77_recoverable_failures_answeronly_evidenceonly_predictions.jsonl --timeout 240 --retries 1 --log-every 1 --include-timing --num-predict 64 --schema-mode answer_only --resume
python3 work/deployed_mix_verifier_report.py --predictions outputs/gemma4_26b_v77_recoverable_failures_answeronly_evidenceonly_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 500 --output-prefix gemma4_26b_v77_recoverable_failures_answeronly_evidenceonly_report
```

v78 deployed-mix feature selector probes:

```bash
python3 work/deployed_mix_feature_selector.py --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --train-label math_llama_deployed_mix --test-label math_gemma_deployed_mix --output-prefix deployed_mix_feature_selector_v78_train_llama_test_gemma
python3 work/deployed_mix_feature_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label math_gemma_deployed_mix --test-label math_llama_deployed_mix --output-prefix deployed_mix_feature_selector_v78_train_gemma_test_llama
python3 work/deployed_mix_verifier_report.py --predictions outputs/deployed_mix_feature_selector_v78_train_llama_test_gemma_predictions.jsonl outputs/deployed_mix_feature_selector_v78_train_gemma_test_llama_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.55,0.6,0.65,0.7 --bootstrap-rounds 500 --output-prefix deployed_mix_feature_selector_v78_cross_model_report
python3 work/deployed_mix_feature_selector.py --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --train-label math_llama_unique32_deployed_mix --test-label math_gemma_deployed_mix --output-prefix deployed_mix_feature_selector_v78_unique_train_llama_test_gemma
python3 work/deployed_mix_feature_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label math_gemma_unique16_deployed_mix --test-label math_llama_deployed_mix --output-prefix deployed_mix_feature_selector_v78_unique_train_gemma_test_llama
python3 work/deployed_mix_verifier_report.py --predictions outputs/deployed_mix_feature_selector_v78_unique_train_llama_test_gemma_predictions.jsonl outputs/deployed_mix_feature_selector_v78_unique_train_gemma_test_llama_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.55,0.6,0.65,0.7 --bootstrap-rounds 500 --output-prefix deployed_mix_feature_selector_v78_unique_train_cross_model_report
python3 work/deployed_mix_feature_selector.py --train-packets outputs/cluster_packets_math_llama_n128.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --train-label math_llama_hard_top5 --test-label math_gemma_deployed_mix --output-prefix deployed_mix_feature_selector_v78_hardtrain_llama_test_gemma
python3 work/deployed_mix_feature_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label math_gemma_hard_top5 --test-label math_llama_deployed_mix --output-prefix deployed_mix_feature_selector_v78_hardtrain_gemma_test_llama
python3 work/deployed_mix_verifier_report.py --predictions outputs/deployed_mix_feature_selector_v78_hardtrain_llama_test_gemma_predictions.jsonl outputs/deployed_mix_feature_selector_v78_hardtrain_gemma_test_llama_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.55,0.6,0.65,0.7 --bootstrap-rounds 500 --output-prefix deployed_mix_feature_selector_v78_hardtrain_cross_model_report
python3 work/deployed_mix_feature_selector.py --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label math_llama_unique32_deployed_mix_overlap_filtered --test-label math_llama_deployed_mix --output-prefix deployed_mix_feature_selector_v78_unique_filtered_train_llama_test_llama --exclude-test-problems-from-train
python3 work/deployed_mix_feature_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --train-label math_gemma_unique16_deployed_mix_overlap_filtered --test-label math_gemma_deployed_mix --output-prefix deployed_mix_feature_selector_v78_unique_filtered_train_gemma_test_gemma --exclude-test-problems-from-train
python3 work/deployed_mix_verifier_report.py --predictions outputs/deployed_mix_feature_selector_v78_unique_filtered_train_llama_test_llama_predictions.jsonl outputs/deployed_mix_feature_selector_v78_unique_filtered_train_gemma_test_gemma_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.55,0.6,0.65,0.7 --bootstrap-rounds 500 --output-prefix deployed_mix_feature_selector_v78_unique_filtered_same_model_report
```

v79 calibrated override selector probes:

```bash
python3 work/calibrated_override_selector.py --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --train-label math_llama_unique32_source_calibrated --test-label math_gemma_balanced --output-prefix calibrated_override_v79_unique_llama_to_gemma
python3 work/calibrated_override_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label math_gemma_unique16_source_calibrated --test-label math_llama_balanced --output-prefix calibrated_override_v79_unique_gemma_to_llama
python3 work/deployed_mix_verifier_report.py --predictions outputs/calibrated_override_v79_unique_llama_to_gemma_predictions.jsonl outputs/calibrated_override_v79_unique_gemma_to_llama_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.55,0.6,0.65,0.7,0.9 --bootstrap-rounds 500 --output-prefix calibrated_override_v79_unique_cross_model_report
python3 work/calibrated_override_selector.py --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --train-label math_llama_balanced_source_calibrated --test-label math_gemma_balanced --output-prefix calibrated_override_v79_balanced_llama_to_gemma
python3 work/calibrated_override_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label math_gemma_balanced_source_calibrated --test-label math_llama_balanced --output-prefix calibrated_override_v79_balanced_gemma_to_llama
python3 work/deployed_mix_verifier_report.py --predictions outputs/calibrated_override_v79_balanced_llama_to_gemma_predictions.jsonl outputs/calibrated_override_v79_balanced_gemma_to_llama_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.55,0.6,0.65,0.7,0.9 --bootstrap-rounds 500 --output-prefix calibrated_override_v79_balanced_cross_model_report
python3 work/calibrated_override_selector.py --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --train-label math_llama_unique32_oracle_threshold --test-label math_gemma_balanced --output-prefix calibrated_override_v79_oracle_unique_llama_to_gemma --force-threshold 0.3
python3 work/calibrated_override_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label math_gemma_unique16_oracle_threshold --test-label math_llama_balanced --output-prefix calibrated_override_v79_oracle_unique_gemma_to_llama --force-threshold -0.025
python3 work/deployed_mix_verifier_report.py --predictions outputs/calibrated_override_v79_oracle_unique_llama_to_gemma_predictions.jsonl outputs/calibrated_override_v79_oracle_unique_gemma_to_llama_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.55,0.6,0.65,0.7,0.9 --bootstrap-rounds 500 --output-prefix calibrated_override_v79_oracle_unique_cross_model_report
```

v80 utility override selector probes:

```bash
python3 work/utility_override_selector.py --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --train-label math_llama_unique32_utility_gate --test-label math_gemma_balanced --output-prefix utility_override_v80_unique_llama_to_gemma
python3 work/utility_override_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label math_gemma_unique16_utility_gate --test-label math_llama_balanced --output-prefix utility_override_v80_unique_gemma_to_llama
python3 work/deployed_mix_verifier_report.py --predictions outputs/utility_override_v80_unique_llama_to_gemma_predictions.jsonl outputs/utility_override_v80_unique_gemma_to_llama_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.55,0.6,0.65,0.7,0.9 --bootstrap-rounds 500 --output-prefix utility_override_v80_unique_cross_model_report
python3 work/utility_override_selector.py --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --train-label math_llama_balanced_utility_gate --test-label math_gemma_balanced --output-prefix utility_override_v80_balanced_llama_to_gemma
python3 work/utility_override_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label math_gemma_balanced_utility_gate --test-label math_llama_balanced --output-prefix utility_override_v80_balanced_gemma_to_llama
python3 work/deployed_mix_verifier_report.py --predictions outputs/utility_override_v80_balanced_llama_to_gemma_predictions.jsonl outputs/utility_override_v80_balanced_gemma_to_llama_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.55,0.6,0.65,0.7,0.9 --bootstrap-rounds 500 --output-prefix utility_override_v80_balanced_cross_model_report
python3 work/utility_override_selector.py --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --train-label math_llama_unique32_utility_gate --test-label math_gemma_balanced --output-prefix utility_override_v80_oracle_unique_llama_to_gemma --force-threshold 2
python3 work/utility_override_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label math_gemma_unique16_utility_gate --test-label math_llama_balanced --output-prefix utility_override_v80_oracle_unique_gemma_to_llama --force-threshold 0.7
python3 work/deployed_mix_verifier_report.py --predictions outputs/utility_override_v80_oracle_unique_llama_to_gemma_predictions.jsonl outputs/utility_override_v80_oracle_unique_gemma_to_llama_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.55,0.6,0.65,0.7,0.9 --bootstrap-rounds 500 --output-prefix utility_override_v80_oracle_unique_cross_model_report
python3 work/utility_override_selector.py --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --train-label math_llama_balanced_utility_gate --test-label math_gemma_balanced --output-prefix utility_override_v80_oracle_balanced_llama_to_gemma --force-threshold 2
python3 work/utility_override_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label math_gemma_balanced_utility_gate --test-label math_llama_balanced --output-prefix utility_override_v80_oracle_balanced_gemma_to_llama --force-threshold 0.05
python3 work/deployed_mix_verifier_report.py --predictions outputs/utility_override_v80_oracle_balanced_llama_to_gemma_predictions.jsonl outputs/utility_override_v80_oracle_balanced_gemma_to_llama_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --thresholds 0,0.5,0.55,0.6,0.65,0.7,0.9 --bootstrap-rounds 500 --output-prefix utility_override_v80_oracle_balanced_cross_model_report
```

v82 override calibration stability audit:

```bash
python3 work/override_calibration_stability_audit.py
```

v83 qwen3:14b local verifier runs:

```bash
ssh -o User=trevor trevors-pc.local 'ollama pull qwen3:14b'
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local

python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl --output outputs/qwen3_14b_v83_recoverable_failures_answeronly_evidenceonly_predictions.jsonl --timeout 360 --retries 1 --log-every 1 --include-timing --num-predict 64 --schema-mode answer_only --resume
python3 work/deployed_mix_verifier_report.py --predictions outputs/qwen3_14b_v83_recoverable_failures_answeronly_evidenceonly_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 1000 --seed 60601 --output-prefix qwen3_14b_v83_recoverable_failures_answeronly_evidenceonly_report

python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl --output outputs/qwen3_14b_v83_gemma_full72_answeronly_evidenceonly_predictions.jsonl --timeout 360 --retries 1 --log-every 12 --include-timing --num-predict 64 --schema-mode answer_only --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl --output outputs/qwen3_14b_v83_llama_full72_answeronly_evidenceonly_predictions.jsonl --timeout 360 --retries 1 --log-every 12 --include-timing --num-predict 64 --schema-mode answer_only --resume
python3 work/deployed_mix_verifier_report.py --predictions outputs/qwen3_14b_v83_llama_full72_answeronly_evidenceonly_predictions.jsonl outputs/qwen3_14b_v83_gemma_full72_answeronly_evidenceonly_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 1000 --seed 60601 --output-prefix qwen3_14b_v83_full144_answeronly_evidenceonly_report
```

v84 qwen3:14b rich problem-inclusive verifier runs:

```bash
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 192.168.1.151

python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/qwen35_9b_v76_recoverable_failures_rich_concise_prompts.jsonl --output outputs/qwen3_14b_v84_recoverable_failures_rich_concise_predictions.jsonl --timeout 480 --retries 1 --log-every 1 --include-timing --num-predict 128 --schema-mode answer_reason --resume
python3 work/deployed_mix_verifier_report.py --predictions outputs/qwen3_14b_v84_recoverable_failures_rich_concise_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_concise.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_concise.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/qwen35_9b_v76_recoverable_failures_rich_concise_prompts.jsonl --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 1000 --seed 60601 --output-prefix qwen3_14b_v84_recoverable_failures_rich_concise_report

python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_concise.jsonl --output outputs/qwen3_14b_v84_gemma_full72_rich_concise_predictions.jsonl --timeout 480 --retries 1 --log-every 12 --include-timing --num-predict 128 --schema-mode answer_reason --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_concise.jsonl --output outputs/qwen3_14b_v84_llama_full72_rich_concise_predictions.jsonl --timeout 480 --retries 1 --log-every 12 --include-timing --num-predict 128 --schema-mode answer_reason --resume
python3 work/deployed_mix_verifier_report.py --predictions outputs/qwen3_14b_v84_llama_full72_rich_concise_predictions.jsonl outputs/qwen3_14b_v84_gemma_full72_rich_concise_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_concise.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_concise.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_concise.jsonl outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_concise.jsonl --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 1000 --seed 60601 --output-prefix qwen3_14b_v84_full144_rich_concise_report
```

v85 rank-bucket cross-model transfer:

```bash
python3 work/test_rank_bucket_cross_model_transfer.py
python3 work/rank_bucket_cross_model_transfer.py --output-prefix rank_bucket_cross_model_transfer_v85
```

v86 rank-bucket transfer quality sweep:

```bash
python3 work/test_rank_bucket_transfer_quality_sweep.py
python3 work/rank_bucket_transfer_quality_sweep.py --output-prefix rank_bucket_transfer_quality_sweep_v86
```

v87 rank-bucket cross-seed transfer:

```bash
python3 work/test_rank_bucket_cross_seed_transfer.py
python3 work/rank_bucket_cross_seed_transfer.py --output-prefix rank_bucket_cross_seed_transfer_v87
```

v88 rank-bucket transfer budget map:

```bash
python3 work/test_rank_bucket_transfer_budget_map.py
python3 work/rank_bucket_transfer_budget_map.py --input outputs/rank_bucket_cross_seed_transfer_v87.csv --output-prefix rank_bucket_transfer_budget_map_v88
```

v89 rank-bucket verifier quality targets:

```bash
python3 work/test_rank_bucket_verifier_quality_targets.py
python3 work/rank_bucket_verifier_quality_targets.py --input outputs/rank_bucket_cross_seed_transfer_v87_raw.csv --output-prefix rank_bucket_verifier_quality_targets_v89
```

v90 rank-bucket quality region map:

```bash
python3 work/test_rank_bucket_quality_region_map.py
python3 work/rank_bucket_quality_region_map.py --input outputs/rank_bucket_verifier_quality_targets_v89.csv --output-prefix rank_bucket_quality_region_map_v90
```

v91 rank-bucket pair-bootstrap transfer audit:

```bash
python3 work/test_rank_bucket_pair_bootstrap.py
python3 work/rank_bucket_pair_bootstrap.py --input outputs/rank_bucket_cross_seed_transfer_v87_raw.csv --output-prefix rank_bucket_pair_bootstrap_v91
```

v92 mathstral local-verifier boundary:

```bash
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model mathstral:7b --prompts outputs/deployed_mix_real_v75_slim_concise_percat1_prompts.jsonl --output outputs/mathstral_7b_v92_deployed_mix_real_v75_slim_concise_percat1_predictions.jsonl --timeout 180 --retries 1 --retry-sleep 2 --log-every 1 --include-timing --num-predict 256 --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model mathstral:7b --prompts outputs/mathstral_v92_v77_answeronly_evidenceonly_percat1_prompts.jsonl --output outputs/mathstral_7b_v92_v77_answeronly_evidenceonly_percat1_predictions.jsonl --timeout 240 --retries 1 --retry-sleep 2 --log-every 1 --include-timing --num-predict 64 --schema-mode answer_only --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model mathstral:7b --prompts outputs/mathstral_v92_slim_answeronly_evidenceonly_percat1_prompts.jsonl --output outputs/mathstral_7b_v92_slim_answeronly_evidenceonly_percat1_predictions.jsonl --timeout 180 --retries 1 --retry-sleep 2 --log-every 1 --include-timing --num-predict 64 --schema-mode answer_only --resume
```

v93 binary cluster-judge interface:

```bash
python3 work/test_binary_cluster_judge.py
python3 work/make_binary_cluster_judge_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --ids outputs/qwen35_9b_v76_recoverable_failures_ids.txt --dataset MATH/Gemma --output outputs/mathstral_v93_binary_cluster_judge_recoverable_gemma_prompts.jsonl --top-k 20 --representatives-per-cluster 1 --rationale-chars 220
python3 work/make_binary_cluster_judge_prompts.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --ids outputs/qwen35_9b_v76_recoverable_failures_ids.txt --dataset MATH/Llama --output outputs/mathstral_v93_binary_cluster_judge_recoverable_llama_prompts.jsonl --top-k 20 --representatives-per-cluster 1 --rationale-chars 220
python3 work/make_binary_cluster_judge_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --ids outputs/qwen35_9b_v76_recoverable_failures_ids.txt --dataset MATH/Gemma --output outputs/mathstral_v93_binary_answer_check_recoverable_gemma_prompts.jsonl --top-k 20 --style answer_check
python3 work/make_binary_cluster_judge_prompts.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --ids outputs/qwen35_9b_v76_recoverable_failures_ids.txt --dataset MATH/Llama --output outputs/mathstral_v93_binary_answer_check_recoverable_llama_prompts.jsonl --top-k 20 --style answer_check
python3 work/score_binary_cluster_judge.py --predictions outputs/mathstral_7b_v93_binary_cluster_judge_recoverable_gemma_predictions.jsonl outputs/mathstral_7b_v93_binary_cluster_judge_recoverable_llama_predictions.jsonl --answer-keys outputs/mathstral_v93_binary_cluster_judge_recoverable_gemma_prompts.answer_key.json outputs/mathstral_v93_binary_cluster_judge_recoverable_llama_prompts.answer_key.json --output-prefix outputs/mathstral_7b_v93_binary_cluster_judge_recoverable
python3 work/score_binary_cluster_judge.py --predictions outputs/mathstral_7b_v93_binary_answer_check_recoverable_gemma_predictions.jsonl outputs/mathstral_7b_v93_binary_answer_check_recoverable_llama_predictions.jsonl --answer-keys outputs/mathstral_v93_binary_answer_check_recoverable_gemma_prompts.answer_key.json outputs/mathstral_v93_binary_answer_check_recoverable_llama_prompts.answer_key.json --output-prefix outputs/mathstral_7b_v93_binary_answer_check_recoverable
```

v94 qwen3:14b binary cluster-judge stopline:

```bash
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/mathstral_v93_binary_answer_check_recoverable_gemma_prompts.jsonl --output outputs/qwen3_14b_v94_binary_answer_check_recoverable_gemma_predictions.jsonl --timeout 180 --retries 1 --retry-sleep 2 --log-every 10 --include-timing --num-predict 48 --schema-mode answer_only --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/mathstral_v93_binary_answer_check_recoverable_llama_prompts.jsonl --output outputs/qwen3_14b_v94_binary_answer_check_recoverable_llama_predictions.jsonl --timeout 180 --retries 1 --retry-sleep 2 --log-every 10 --include-timing --num-predict 48 --schema-mode answer_only --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/mathstral_v93_binary_cluster_judge_recoverable_gemma_prompts.jsonl --output outputs/qwen3_14b_v94_binary_cluster_judge_recoverable_gemma_predictions.jsonl --timeout 180 --retries 1 --retry-sleep 2 --log-every 10 --include-timing --num-predict 48 --schema-mode answer_only --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/mathstral_v93_binary_cluster_judge_recoverable_llama_prompts.jsonl --output outputs/qwen3_14b_v94_binary_cluster_judge_recoverable_llama_predictions.jsonl --timeout 180 --retries 1 --retry-sleep 2 --log-every 10 --include-timing --num-predict 48 --schema-mode answer_only --resume
python3 work/score_binary_cluster_judge.py --predictions outputs/qwen3_14b_v94_binary_answer_check_recoverable_gemma_predictions.jsonl outputs/qwen3_14b_v94_binary_answer_check_recoverable_llama_predictions.jsonl --answer-keys outputs/mathstral_v93_binary_answer_check_recoverable_gemma_prompts.answer_key.json outputs/mathstral_v93_binary_answer_check_recoverable_llama_prompts.answer_key.json --output-prefix outputs/qwen3_14b_v94_binary_answer_check_recoverable
python3 work/score_binary_cluster_judge.py --predictions outputs/qwen3_14b_v94_binary_cluster_judge_recoverable_gemma_predictions.jsonl outputs/qwen3_14b_v94_binary_cluster_judge_recoverable_llama_predictions.jsonl --answer-keys outputs/mathstral_v93_binary_cluster_judge_recoverable_gemma_prompts.answer_key.json outputs/mathstral_v93_binary_cluster_judge_recoverable_llama_prompts.answer_key.json --output-prefix outputs/qwen3_14b_v94_binary_cluster_judge_recoverable
```

v95 hashed semantic cluster scorer:

```bash
python3 work/test_text_cluster_semantic_scorer.py
python3 work/text_cluster_semantic_scorer.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label Gemma --test-label Llama --feature-mode both --include-problem --output-prefix text_cluster_semantic_v95_train_gemma_test_llama_both
python3 work/text_cluster_semantic_scorer.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label Gemma --test-label Llama --feature-mode both --include-problem --exclude-test-problems-from-train --output-prefix text_cluster_semantic_v95_train_gemma_test_llama_both_nooverlap
python3 work/deployed_mix_verifier_report.py --predictions outputs/text_cluster_semantic_v95_train_gemma_test_llama_both_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl --thresholds 0,0.5,0.75,0.9 --bootstrap-rounds 500 --output-prefix text_cluster_semantic_v95_train_gemma_test_llama_both_report
```

v96 source-calibrated semantic risk control:

```bash
python3 work/test_semantic_risk_controlled_selector.py
python3 work/semantic_risk_controlled_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl --train-label Gemma --test-label Llama --feature-mode both --score-field semantic_cluster_probability --include-problem --seed 60601 --output-prefix semantic_risk_v96_train_gemma_test_llama_both_probability_seed60601
python3 work/deployed_mix_verifier_report.py --predictions outputs/semantic_risk_v96_train_gemma_test_llama_both_probability_seed60601_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl --thresholds 0 --bootstrap-rounds 500 --output-prefix semantic_risk_v96_train_gemma_test_llama_both_probability_seed60601_report
```

v97 unique-source semantic risk pressure:

```bash
python3 work/semantic_risk_controlled_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --train-label Gemma --test-label Llama --feature-mode both --score-field semantic_cluster_probability --include-problem --seed 60602 --output-prefix semantic_risk_v97_train_balanced_gemma_test_unique32_llama_both_probability_seed60602
python3 work/deployed_mix_verifier_report.py --predictions outputs/semantic_risk_v97_train_balanced_gemma_test_unique32_llama_both_probability_seed60602_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.answer_key.json outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv --expected-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.jsonl --thresholds 0 --bootstrap-rounds 500 --output-prefix semantic_risk_v97_train_balanced_gemma_test_unique32_llama_both_probability_seed60602_report
```

v98 rebuilt unique-source semantic risk pressure:

```bash
python3 work/build_deployed_mix_packet_dataset.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-deployed-mix-top20-unique16-rebuilt-v98 --output-prefix cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98 --target-per-category 16 --trials-per-problem 64 --max-packets-per-problem 1 --verifier-train-problems 10 --audit-holdout-gap 0
python3 work/make_cluster_verifier_prompts.py --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98_compact.jsonl --representatives-per-cluster 1 --rationale-chars 420
python3 work/audit_deployed_mix_representativeness.py --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl --output-prefix deployed_mix_unique32_llama_unique16_gemma_rebuilt_v98_representativeness
python3 work/semantic_risk_controlled_selector.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --train-label Gemma_unique16_rebuilt_v98 --test-label Llama_unique32 --feature-mode both --score-field semantic_cluster_probability --include-problem --seed 60603 --output-prefix semantic_risk_v98_unique_gemma_rebuilt_to_unique_llama_both_probability_seed60603
python3 work/deployed_mix_verifier_report.py --predictions outputs/semantic_risk_v98_unique_gemma_rebuilt_to_unique_llama_both_probability_seed60603_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32_category_stats.csv --expected-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.jsonl --thresholds 0 --bootstrap-rounds 500 --output-prefix semantic_risk_v98_unique_gemma_rebuilt_to_unique_llama_both_probability_seed60603_report
```

v99 raw semantic target-threshold diagnostic:

```bash
python3 work/text_cluster_semantic_scorer.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --train-label Gemma_unique16_rebuilt_v98 --test-label Llama_unique32 --feature-mode both --include-problem --seed 60601 --output-prefix raw_semantic_v99_unique_gemma_rebuilt_to_unique_llama_both_seed60601
python3 work/semantic_threshold_diagnostic.py --predictions outputs/raw_semantic_v99_unique_gemma_rebuilt_to_unique_llama_both_seed60601_predictions.jsonl --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_unique32_compact.answer_key.json --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32_category_stats.csv --bootstrap-rounds 500 --output-prefix raw_semantic_v99_unique_gemma_rebuilt_to_unique_llama_both_seed60601_threshold_diag
```

v100 split-trained semantic threshold audit:

```bash
python3 work/semantic_split_threshold_audit.py --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --train-label Gemma_unique16_rebuilt_v98 --test-label Llama_unique32 --feature-mode numeric --include-problem --seed 60601 --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32_category_stats.csv --bootstrap-rounds 500 --output-prefix split_threshold_v100_unique_gemma_rebuilt_to_unique_llama_numeric_seed60601
```

v101 semantic calibration scaling boundary:

```bash
python3 work/semantic_calibration_scaling_audit.py --source-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl --train-label Llama_unique32 --test-label Gemma_unique16_rebuilt_v98 --output-prefix semantic_calibration_v101_problem_unique_llama_to_unique_gemma_rebuilt_numeric_seed60601 --feature-mode numeric --category-stats outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98_category_stats.csv --calibration-per-category 1,2,4,8,all --seed 60601 --bootstrap-rounds 250 --dedupe-problems --overlap-key problem --exclude-test-problems-from-source
python3 work/aggregate_semantic_calibration_v101.py
```

v102 target-style semantic calibration boundary:

```bash
python3 work/semantic_target_calibration_audit.py --source-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl --train-label Llama_unique32 --test-label Gemma_unique16_rebuilt_v98 --output-prefix semantic_target_calibration_v102_problem_unique_llama_to_unique_gemma_rebuilt_numeric_seed60601 --feature-mode numeric --category-stats outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98_category_stats.csv --calibration-per-category 1,2,4,8,all --seed 60601 --bootstrap-rounds 250 --dedupe-problems --overlap-key problem --exclude-test-problems-from-source
python3 work/aggregate_semantic_target_calibration_v102.py
```

v103 expanded-target semantic calibration boundary:

```bash
python3 work/build_deployed_mix_packet_dataset.py --data work/MATH_Gemma-2B.json --dataset-label MATH_Gemma-deployed-mix-top20-expanded48-v103 --output-prefix cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103 --target-per-category 48 --trials-per-problem 96 --verifier-train-problems 80 --verifier-samples-per-problem 8000 --n 128 --top-k 20
python3 work/semantic_target_calibration_audit.py --source-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103.jsonl --train-label Llama_unique32 --test-label Gemma_expanded48_v103 --output-prefix semantic_target_calibration_v103_problem_unique_llama_to_expanded_gemma_numeric_seed60601 --feature-mode numeric --category-stats outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103_category_stats.csv --calibration-per-category 1,2,4,8,16,24,all --seed 60601 --bootstrap-rounds 250 --overlap-key problem --exclude-test-problems-from-source
python3 work/aggregate_semantic_target_calibration_v103.py
```

v104 rich-signal semantic calibration pilot:

```bash
python3 work/semantic_target_calibration_audit.py --source-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103.jsonl --train-label Llama_unique_rich --test-label Gemma_expanded48_v103 --output-prefix semantic_target_calibration_v104_problem_unique_llama_to_expanded_gemma_rich_both_seed60601 --feature-mode both --include-problem --representatives-per-cluster 3 --rationale-chars 700 --hash-dim 65536 --epochs 60 --lr 0.05 --l2 1e-6 --category-stats outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103_category_stats.csv --calibration-per-category 1,2,4,8,16,24,all --seed 60601 --bootstrap-rounds 250 --overlap-key problem --exclude-test-problems-from-source
python3 work/aggregate_semantic_target_calibration_v104.py
```

v105 semantic meta-gate boundary:

```bash
python3 work/semantic_meta_gate_audit.py --raw-predictions outputs/semantic_target_calibration_v103_problem_unique_llama_to_expanded_gemma_both_seed60601_raw_target_predictions.jsonl outputs/semantic_target_calibration_v103_problem_unique_llama_to_expanded_gemma_both_seed60602_raw_target_predictions.jsonl outputs/semantic_target_calibration_v103_problem_unique_llama_to_expanded_gemma_both_seed60603_raw_target_predictions.jsonl outputs/semantic_target_calibration_v103_problem_pooled_llama_to_expanded_gemma_both_seed60601_raw_target_predictions.jsonl outputs/semantic_target_calibration_v103_problem_pooled_llama_to_expanded_gemma_both_seed60602_raw_target_predictions.jsonl outputs/semantic_target_calibration_v103_problem_pooled_llama_to_expanded_gemma_both_seed60603_raw_target_predictions.jsonl outputs/semantic_target_calibration_v104_problem_unique_llama_to_expanded_gemma_rich_both_seed60601_raw_target_predictions.jsonl outputs/semantic_target_calibration_v104_problem_unique_llama_to_expanded_gemma_rich_both_seed60602_raw_target_predictions.jsonl outputs/semantic_target_calibration_v104_problem_unique_llama_to_expanded_gemma_rich_both_seed60603_raw_target_predictions.jsonl outputs/semantic_target_calibration_v104_problem_pooled_llama_to_expanded_gemma_rich_both_seed60601_raw_target_predictions.jsonl outputs/semantic_target_calibration_v104_problem_pooled_llama_to_expanded_gemma_rich_both_seed60602_raw_target_predictions.jsonl outputs/semantic_target_calibration_v104_problem_pooled_llama_to_expanded_gemma_rich_both_seed60603_raw_target_predictions.jsonl --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103.jsonl --category-stats outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103_category_stats.csv --calibration-per-category 1,2,4,8,16,24,all --bootstrap-rounds 250 --output-prefix semantic_meta_gate_v105
```

v108 cross-generator agreement boundary:

```bash
python3 work/cross_generator_agreement_audit.py --n 128 --trials-per-problem 8 --seeds 60601,60602,60603 --verifier-train-problems 30 --audit-holdout-gap 24 --verifier-samples-per-problem 800 --bootstrap-rounds 250 --output-prefix cross_generator_agreement_v108
```

v109 cross-generator risk-gate audit:

```bash
python3 -u work/cross_generator_risk_gate_audit.py --n 128 --trials-per-problem 8 --seeds 60601,60602,60603 --policies target_intersection_top10,target_intersection_top20,union_rank_top3 --calibration-problems 12,24,36 --verifier-train-problems 30 --audit-holdout-gap 24 --verifier-samples-per-problem 800 --bootstrap-rounds 250 --output-prefix cross_generator_risk_gate_v109
```

v110 cross-seed generator router:

```bash
python3 work/cross_seed_generator_router.py --rows outputs/cross_generator_risk_gate_v109_details.jsonl --feature-mode base --output-prefix cross_seed_generator_router_v110
```

v111 source-label placebo control:

```bash
python3 work/cross_seed_router_placebo.py --iterations 200 --output-prefix cross_seed_router_placebo_v111
```

v112 cross-seed router heuristic ablation:

```bash
python3 work/cross_seed_router_heuristic_ablation.py --output-prefix cross_seed_router_heuristic_v112
```

v113 cross-seed router regression frontier:

```bash
python3 work/cross_seed_router_regression_frontier.py --output-prefix cross_seed_router_regression_frontier_v113
```

v114 problem-disjoint router frontier:

```bash
python3 work/cross_seed_router_problem_disjoint_frontier.py --output-prefix cross_seed_router_problem_disjoint_frontier_v114
```

v115 problem-disjoint two-head router control:

```bash
python3 work/cross_seed_router_two_head_control.py --output-prefix cross_seed_router_two_head_control_v115
```

v116 problem-disjoint separability audit:

```bash
python3 work/cross_seed_router_separability_audit.py --output-prefix cross_seed_router_separability_v116
```

v117 trace signal availability audit:

```bash
python3 work/trace_signal_availability_audit.py --output-prefix trace_signal_availability_v117
```

v118 answer-symbolic guard audit:

```bash
python3 work/cross_seed_router_symbolic_guard_audit.py --rebuild-cache --output-prefix cross_seed_router_symbolic_guard_v118 --answer-rows-cache outputs/cross_seed_router_symbolic_guard_v118_answer_rows.jsonl
```

v119 pairwise router-judge smoke:

```bash
python3 work/make_pairwise_router_judge_prompts.py --per-category 20 --output outputs/pairwise_router_judge_v119_prompts.jsonl --manifest outputs/pairwise_router_judge_v119_manifest.csv
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model mathstral:7b --prompts outputs/pairwise_router_judge_v119_prompts.jsonl --output outputs/mathstral_pairwise_router_judge_v119_predictions.jsonl --schema-mode answer_only --num-predict 64 --timeout 180 --include-timing --log-every 10 --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/pairwise_router_judge_v119_prompts.jsonl --output outputs/qwen14b_pairwise_router_judge_v119_predictions.jsonl --schema-mode answer_only --num-predict 64 --timeout 240 --include-timing --log-every 10 --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model gemma4:26b --prompts outputs/pairwise_router_judge_v119_prompts.jsonl --output outputs/gemma4_pairwise_router_judge_v119_predictions.jsonl --schema-mode answer_only --num-predict 64 --timeout 300 --include-timing --log-every 10 --resume
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v119_manifest.csv --predictions outputs/mathstral_pairwise_router_judge_v119_predictions.jsonl --output-prefix outputs/mathstral_pairwise_router_judge_v119_score
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v119_manifest.csv --predictions outputs/qwen14b_pairwise_router_judge_v119_predictions.jsonl --output-prefix outputs/qwen14b_pairwise_router_judge_v119_score
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v119_manifest.csv --predictions outputs/gemma4_pairwise_router_judge_v119_predictions.jsonl --output-prefix outputs/gemma4_pairwise_router_judge_v119_score
```

v120 full accepted-row pairwise router-judge panel:

```bash
python3 work/make_pairwise_router_judge_prompts.py --per-category 999 --packet-prefix pairwise_router_v120_budget0_all --output outputs/pairwise_router_judge_v120_budget0_all_prompts.jsonl --manifest outputs/pairwise_router_judge_v120_budget0_all_manifest.csv
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model mathstral:7b --prompts outputs/pairwise_router_judge_v120_budget0_all_prompts.jsonl --output outputs/mathstral_pairwise_router_judge_v120_budget0_all_predictions.jsonl --schema-mode answer_only --num-predict 64 --timeout 180 --include-timing --log-every 50 --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/pairwise_router_judge_v120_budget0_all_prompts.jsonl --output outputs/qwen14b_pairwise_router_judge_v120_budget0_all_predictions.jsonl --schema-mode answer_only --num-predict 64 --timeout 240 --include-timing --log-every 50 --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model gemma4:26b --prompts outputs/pairwise_router_judge_v120_budget0_all_prompts.jsonl --output outputs/gemma4_pairwise_router_judge_v120_budget0_all_predictions.jsonl --schema-mode answer_only --num-predict 64 --timeout 300 --include-timing --log-every 50 --resume
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v120_budget0_all_manifest.csv --predictions outputs/mathstral_pairwise_router_judge_v120_budget0_all_predictions.jsonl --output-prefix outputs/mathstral_pairwise_router_judge_v120_budget0_all_score
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v120_budget0_all_manifest.csv --predictions outputs/qwen14b_pairwise_router_judge_v120_budget0_all_predictions.jsonl --output-prefix outputs/qwen14b_pairwise_router_judge_v120_budget0_all_score
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v120_budget0_all_manifest.csv --predictions outputs/gemma4_pairwise_router_judge_v120_budget0_all_predictions.jsonl --output-prefix outputs/gemma4_pairwise_router_judge_v120_budget0_all_score
```

v121 pairwise router-judge held-out calibration:

```bash
python3 work/pairwise_router_judge_calibration.py --output-prefix pairwise_router_judge_calibration_v121
```

v122 pairwise router-judge natural-rate accounting:

```bash
python3 work/pairwise_router_judge_natural_rate.py --output-prefix pairwise_router_judge_natural_rate_v122
```

v123 Llama-with-Gemma mirror control:

```bash
python3 work/build_cross_seed_answer_rows.py --target-data work/MATH_Llama-3-8B-Instruct.json --other-data work/MATH_Gemma-2B.json --target-label MATH/Llama --other-label MATH/Gemma --output outputs/cross_seed_answer_rows_llama_with_gemma_v123.jsonl
python3 work/make_pairwise_router_judge_prompts.py --answer-rows outputs/cross_seed_answer_rows_llama_with_gemma_v123.jsonl --data work/MATH_Llama-3-8B-Instruct.json --target MATH/Llama --other MATH/Gemma --dataset-label MATH/Llama --output outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_prompts.jsonl --manifest outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_manifest.csv --score-mode base_utility --regression-budget 0 --per-category 999 --packet-prefix pairwise_router_v123_llama_with_gemma_budget0_all
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model mathstral:7b --prompts outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_prompts.jsonl --output outputs/mathstral_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl --schema-mode answer_only --num-predict 96 --timeout 180 --resume --include-timing --log-every 5
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_prompts.jsonl --output outputs/qwen14b_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl --schema-mode answer_only --num-predict 96 --timeout 180 --resume --include-timing --log-every 5
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model gemma4:26b --prompts outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_prompts.jsonl --output outputs/gemma4_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl --schema-mode answer_only --num-predict 96 --timeout 180 --resume --include-timing --log-every 5
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_manifest.csv --predictions outputs/mathstral_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl --output-prefix outputs/mathstral_pairwise_router_judge_v123_llama_with_gemma_budget0_all_score
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_manifest.csv --predictions outputs/qwen14b_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl --output-prefix outputs/qwen14b_pairwise_router_judge_v123_llama_with_gemma_budget0_all_score
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_manifest.csv --predictions outputs/gemma4_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl --output-prefix outputs/gemma4_pairwise_router_judge_v123_llama_with_gemma_budget0_all_score
python3 work/pairwise_router_judge_natural_rate.py --answer-rows outputs/cross_seed_answer_rows_llama_with_gemma_v123.jsonl --manifest outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_manifest.csv --mathstral outputs/mathstral_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl --qwen14b outputs/qwen14b_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl --gemma4 outputs/gemma4_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl --target MATH/Llama --other MATH/Gemma --output-prefix pairwise_router_judge_natural_rate_v123_llama_with_gemma
```

v124 pairwise natural-rate sensitivity:

```bash
python3 work/pairwise_router_judge_sensitivity.py --output-prefix pairwise_router_judge_sensitivity_v124
```

v125-v130 higher-budget pairwise frontier, guards, and rich-prompt probe:

```bash
python3 work/build_cross_seed_answer_rows.py --target-data work/MATH_Gemma-2B.json --other-data work/MATH_Llama-3-8B-Instruct.json --target-label MATH/Gemma --other-label MATH/Llama --output outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl --seeds 60601,60602,60603 --n 128 --trials-per-problem 8 --verifier-train-problems 30 --audit-holdout-gap 24 --verifier-samples-per-problem 800 --policies target_intersection_top10,target_intersection_top20,union_rank_top3
python3 work/pairwise_router_judge_natural_rate.py --answer-rows outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl --manifest outputs/pairwise_router_judge_v125_budget2_all_manifest.csv --mathstral outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl --qwen14b outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl --gemma4 outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl --router-regression-budget 2 --output-prefix pairwise_router_judge_natural_rate_v125_budget2
python3 work/pairwise_router_judge_sensitivity.py --details outputs/pairwise_router_judge_natural_rate_v125_budget2_details.csv --budget 1 --output-prefix pairwise_router_judge_sensitivity_v126_budget1
python3 work/pairwise_router_judge_sensitivity.py --details outputs/pairwise_router_judge_natural_rate_v125_budget2_details.csv --budget 2 --output-prefix pairwise_router_judge_sensitivity_v126_budget2
python3 work/pairwise_router_judge_natural_rate.py --answer-rows outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl --manifest outputs/pairwise_router_judge_v125_budget2_all_manifest.csv --mathstral outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl --qwen14b outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl --gemma4 outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl --router-regression-budget 2 --pairwise-regression-budgets 0,1,2,3,4,5,6,8,10,12,15,20,25,30 --rules never,B,B_or_BOTH --output-prefix pairwise_router_judge_guard_curve_v127
python3 work/pairwise_router_judge_natural_rate.py --answer-rows outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl --manifest outputs/pairwise_router_judge_v125_budget2_all_manifest.csv --mathstral outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl --qwen14b outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl --gemma4 outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl --router-regression-budget 2 --pairwise-regression-budgets 0,1,2,3,4,5,6,8,10,12,15,20,25,30,40,60,100 --rules never,B,B_or_BOTH,always --output-prefix pairwise_router_judge_budget_curve_v127
python3 work/pairwise_router_judge_guard_sweep.py --answer-rows outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl --manifest outputs/pairwise_router_judge_v125_budget2_all_manifest.csv --mathstral outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl --qwen14b outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl --gemma4 outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl --router-regression-budget 2 --pairwise-regression-budgets 1,2 --guard-regression-budgets 0,1,2 --output-prefix pairwise_router_judge_guard_sweep_v128
python3 work/pairwise_router_budget_increment.py --details outputs/pairwise_router_judge_natural_rate_v125_budget2_details.csv --low-budget 1 --high-budget 2 --output-prefix pairwise_router_budget_increment_v129
python3 work/pairwise_router_policy_guard.py --answer-rows outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl --manifest outputs/pairwise_router_judge_v125_budget2_all_manifest.csv --mathstral outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl --qwen14b outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl --gemma4 outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl --router-regression-budget 2 --output-prefix pairwise_router_policy_guard_v129
python3 work/make_pairwise_rich_probe_prompts.py
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/pairwise_router_rich_probe_v130_prompts.jsonl --output outputs/qwen14b_pairwise_router_rich_probe_v130_predictions.jsonl --schema-mode answer_only --num-predict 96 --timeout 180 --resume --include-timing --log-every 5
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model mathstral:7b --prompts outputs/pairwise_router_rich_probe_v130_prompts.jsonl --output outputs/mathstral_pairwise_router_rich_probe_v130_predictions.jsonl --schema-mode answer_only --num-predict 96 --timeout 180 --resume --include-timing --log-every 5
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model gemma4:26b --prompts outputs/pairwise_router_rich_probe_v130_prompts.jsonl --output outputs/gemma4_pairwise_router_rich_probe_v130_predictions.jsonl --schema-mode answer_only --num-predict 96 --timeout 240 --resume --include-timing --log-every 5
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_rich_probe_v130_manifest.csv --predictions outputs/qwen14b_pairwise_router_rich_probe_v130_predictions.jsonl --output-prefix outputs/qwen14b_pairwise_router_rich_probe_v130_score --thresholds 0,0.5,0.7,0.9
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_rich_probe_v130_manifest.csv --predictions outputs/mathstral_pairwise_router_rich_probe_v130_predictions.jsonl --output-prefix outputs/mathstral_pairwise_router_rich_probe_v130_score --thresholds 0,0.5,0.7,0.9
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_rich_probe_v130_manifest.csv --predictions outputs/gemma4_pairwise_router_rich_probe_v130_predictions.jsonl --output-prefix outputs/gemma4_pairwise_router_rich_probe_v130_score --thresholds 0,0.5,0.7,0.9
python3 work/summarize_pairwise_rich_probe.py
```

Plots:

```bash
python3 work/render_multiconfig_svg.py
python3 work/render_selectability_svg.py
python3 work/render_failure_detector_svg.py
python3 work/render_detector_verifier_frontier_svg.py
```

Verification:

```bash
python3 -m py_compile work/*.py outputs/*.py
```

## Known Caveats

- Some experiments use randomized candidate subsets. Seeds are fixed in scripts, but rates can vary with changed trial counts.
- The candidate verifier is cheap and text-feature-based. Stronger verifier baselines may reduce selectability gaps.
- MATH answer extraction is approximate.
- Hard packets are conditioned on selector failure and should not be reported as deployed accuracy.
- Manual/in-thread verifier panels are not a substitute for a reproducible external/local model verifier.
- The evidence-budget frontier is a sensitivity calculation from measured representative visibility and projected verifier assumptions; it is not a measured verifier benchmark.
- The cost-aware cascade fallback is an oracle evidence-gap diagnostic. A real cascade needs measured verifier confidence or disagreement to decide when to spend full-prompt budget.
- The iso-budget depth frontier uses projected verifier-success rows with measured prompt costs. It is a budget sensitivity analysis, not an external verifier benchmark.
- The budgeted depth policy has both learned and oracle rows. The oracle row uses labels and is headroom only, not deployable.
- The rank-bucket depth policy still uses projected verifier success, not measured external verifier accuracy.
- The rank-bucket seed sweep is a robustness check for the allocation model under projected verifier success; it does not replace the missing external verifier run.
- The mathstral v92 result is a local endpoint boundary, not a positive verifier benchmark: it has one fragile Gemma recovery, Llama regression, invalid confidence in one slim row, and CPU-bound tail latency on richer panels.
- The v93 binary cluster-judge harness is reusable, but the mathstral result is still negative: both binary interfaces recover `0/6` on the targeted recoverable failures.
- The v94 qwen3:14b binary rerun is also negative: both binary interfaces recover `0/6` on the targeted recoverable failures.
- The v95 hashed semantic scorer is a partial negative, not a solved verifier: it finds raw recovery signal, including some top10/top20 deployed-mix recoveries, but preservation/calibration fail and no tested policy passes the conservative lower-CI-positive deployed decision rule. Overlap-filtered training keeps only `18/72` or `19/72` source packets, so lower-overlap calibration data is a real bottleneck.
- The v96 source-calibrated semantic risk-control sweep is also negative: source thresholds make the v95 signal safer but mostly remove recovery. Across 54 policies, Gemma->Llama mean deployed delta is `+0.003`, Llama->Gemma is `-0.025`, and no policy passes the CI-positive rule.
- The v97 lower-duplication pressure test is negative on the valid Llama unique32 packet set: best deployed delta is `+0.014`, no policy passes the CI-positive rule. The Gemma unique16 packet JSONL is unusable/empty for packet-level scoring and must be rebuilt before using it.
- The v98 rebuilt Gemma unique-source pressure test is also negative: the new Gemma unique16 packet set has `96` usable one-source packets and balanced categories, but the 81-policy lower-duplication semantic-risk matrix has zero CI-positive policies. The best point estimate is `+0.051` with baseline regressions; the best clean row is only `+0.035` with CI low `+0.000`.
- The v99 raw semantic threshold diagnostic is a target-oracle calibration probe, not deployable evidence. It finds 4/81 lower-CI-positive threshold rows, with best `+0.063` on rebuilt-Gemma-to-Llama unique, but those thresholds are selected on the target packet set. Use v99 to argue raw headroom exists; use v98 for deployable source-calibrated failure.
- The v100 split-trained semantic threshold audit keeps the v99 headroom under the v98 fit/calibration split: 5/81 target-oracle rows are lower-CI-positive, best `+0.065`, but target thresholds are still selected on the target set. Use v100 to localize the problem to threshold transfer/baseline-risk calibration.
- The v101 semantic calibration scaling sweep is also negative as a deployed policy: across 72 scorer runs and 1080 source-threshold rows, zero source-calibrated rows pass the lower-CI-positive deployed rule. Packet-disjoint target-oracle signal is small, problem-disjoint target-oracle signal still exists, but problem-disjoint clean source-calibrated rows are all no-op. Use v101 to rule out the easy "more source calibration packets" rescue.
- The v102 target-style semantic calibration sweep is negative on held-out target packets: across 72 runs and 1080 rows, zero target-calibrated policies pass the lower-CI-positive rule. Packet-disjoint has one tiny clean point-positive row; problem-disjoint clean target-calibrated rows are no-op. Use v102 to show that small target-style labeled calibration panels are not enough either.
- The v103 expanded-target semantic calibration sweep is also negative as a conservative policy: expanded Gemma target calibration has 288 duplicated/balanced packets and 756 Llama-to-Gemma threshold rows, but zero target-calibrated rows pass the held-out lower-CI-positive rule. Best clean calibrated gain is only `+0.007` with zero lower bound; only target-oracle thresholding reaches a positive lower bound (`+0.034`). Packet/problem aggregates are identical here, so do not treat them as independent repeats.
- The v104 rich-signal semantic calibration pilot is also negative for conservative target calibration: adding problem text, more representatives, longer rationale snippets, larger hash space, and longer training keeps zero CI-positive target-calibrated rows and the same best clean `+0.007` movement. Richer text changes oracle behavior but does not make a deployed threshold.
- The v105 semantic meta-gate is also negative: a multifeature target-style accept/fallback gate over v103/v104 raw predictions gets zero CI-positive calibrated rows. Best clean gate is `+0.008` with zero lower bound, and the largest active point estimate regresses baseline and remains CI-negative.
- The v108 cross-generator agreement audit is a boundary/control, not a conservative method. Llama as auxiliary helps Gemma (`target_intersection_top10` mean `+0.042`, 81 recoveries/6 regressions), but Gemma as auxiliary hurts Llama and no positive no-regression policy appears.
- The v109 cross-generator risk-gate audit is a narrow positive auxiliary-trace result, not a verifier replacement. Gemma-with-Llama `union_rank_top3` is robust at 24/36 calibration problems (`+0.102`/`+0.126`, 3/3 CI-positive seeds), but the reverse direction remains unsafe/flat and small-calibration/no-fit rows must no-op.
- The v110 cross-seed generator router is the stronger auxiliary-trace result: model and threshold are learned on two source seeds and deployed on the held-out seed. Gemma-with-Llama `pool_all` remains positive on 3/3 held-out seeds with mean `+0.084`; Llama-with-Gemma remains weak/flat. This is still a two-trace routing result, not a semantic verifier.
- The v111 source-label placebo uses a fast centroid fitter, not the v110 logistic router. It is a control for threshold luck: 0/200 permuted-label runs match the observed Gemma-with-Llama deltas (`pool_all` placebo max `+0.030` vs observed `+0.084`).
- The v112 heuristic ablation is a tie-safe dumb-control: rank/prior heuristics collapse to no-op, and the best support/confidence rows reach only `+0.054` versus v110 `+0.084`.
- The v113 regression frontier makes the budget tradeoff explicit under the overlap-allowed source split. Source-selected learned routing remains the best low-regression frontier there: Gemma-with-Llama reaches `+0.119` with 3 held-out regressions at source budget 2, while the best <=5-regression heuristic reaches `+0.084`.
- The v114 problem-disjoint frontier is stricter and less flattering. Excluding source rows whose problem ids appear in the held-out seed preserves positive learned-router recovery signal (`+0.097` at source budget 0, `+0.118` at budget 2), but held-out regressions rise to `20`/`30`. Use v114 as the calibration boundary: the auxiliary-generator signal survives; the low-regression safety story does not.
- The v115 two-head control is also negative. A candidate-correctness head trained on all changed problem-disjoint source rows does not restore low-regression held-out control; no v115 row has <=5 held-out regressions, and the two-head variants mostly reshuffle the v114 frontier.
- The v116 separability audit explains the v115 failure: same-feature scores have moderate recovery-vs-regression signal (utility/correctness AUC about `0.71`) but not enough calibrated tail separation, especially on the weak `60602` fold.
- The v117 trace signal availability audit confirms the local Monkey Business JSONs have text samples and correctness labels only. They do not contain logprobs, hidden states, embeddings, confidence, finish reasons, or decoder telemetry.
- The v118 answer-symbolic guard audit is a negative cheap-feature result. Answer-shape/numeric features trail the original base utility score (`0.608` vs `0.711` recovery-vs-regression AUC for base+symbolic utility vs base utility) and no score family restores <=5 held-out regressions.
- The v119 pairwise router-judge smoke is a positive live-interface result, not a final benchmark. On 77 accepted Gemma-with-Llama router rows, mathstral:7b and gemma4:26b recover `9/20` and `10/20` recovery cases with `0/20` accepted regressions; qwen3:14b recovers `15/20` with `3/20` accepted regressions. Treat it as evidence that pairwise answer adjudication is promising, unlike prior full-cluster local verifier prompts.
- The v120 full accepted-row pairwise panel strengthens v119. On all 377 accepted budget-0 Gemma-with-Llama router actions, mathstral:7b recovers `105/192` with `0/20` accepted regressions, gemma4:26b recovers `111/192` with `0/20`, and qwen3:14b recovers `137/192` with `3/20`. This is still accepted-row conditioned, but it is the strongest live local-verifier signal so far.
- The v121 held-out calibration audit is the strongest router-judge result: selecting model/rule on source accepted rows while excluding held-out problem ids yields mean accepted-row delta `+0.368` over held-out seeds, `120` recoveries, and `1` regression. Source zero-regression calibration is not perfectly safe, but it transfers strongly.
- The v122 natural-rate audit is the deployment-denominator correction for v121: over all `1776` held-out Gemma trials, the pairwise-gated policy gets natural delta `+0.067` with `120/1` recoveries/regressions, versus raw-router `+0.097` with `192/20`.
- The v123 mirror control is a negative/control direction: Llama-with-Gemma budget-0 raw routing has only `15` accepted actions (`1` recovery, `5` regressions), raw natural delta `-0.002`, and source-calibrated pairwise selection no-ops on every fold.
- The v124 sensitivity audit shows the v122 natural gain is not a single-problem artifact: leave-one-problem-out natural deltas remain positive for `222/222` `(seed,pid)` groups, min `+0.063`; the only pairwise regression is localized to `s60601/p88/t0`.
- The v125 higher-budget pairwise frontier rebuilds Gemma-with-Llama answer rows into `outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl` because the old default answer-row cache in `outputs/` was empty. Use that explicit file for v125 natural-rate scoring. Router source budget `2` gives raw natural `+0.118` with `240/30`; pairwise budget1 gives `+0.083` with `150/2`, and pairwise budget2 gives `+0.099` with `180/4`.
- The v126 higher-budget sensitivity audit shows v125 is not a concentration artifact: budget1 and budget2 natural leave-one-problem-out stay positive for `222/222` held-out `(seed,pid)` groups, with minimum deltas `+0.079` and `+0.095`. All budget2 pairwise regressions are `qwen14b/B` choices on `union_rank_top3`.
- The v127 pairwise budget curve is an anti-cherrypick check: guarded pairwise rules plateau at natural `+0.099` from source budget `2` through `30`; the unsafe `always` control recovers more only by restoring most raw-router regressions.
- The v128 pairwise guard sweep is not a solved deployment policy. It shows a non-oracle safety frontier: fixed qwen/union cross-judge confirmation reduces budget2 regressions from `4` to `1` while preserving a budget1-sized gain (`+0.083`), and source-selected guard budget1 gets `+0.086` with `155/2`.
- The v129 budget-increment and policy-family guard audit separates the budget2-over-budget1 gain from the lower-budget result. The increment is `+28` correct trials (`+0.016`) and LOO-positive for `222/222`, but sparse across `17/222` nonzero groups; simple source-disjoint policy-family guards do not improve the v125 frontier.
- The v130 rich-prompt probe is targeted stress evidence, not a natural-rate result. Qwen `type_check` fixes the repeated `p88` digit-cycle regressions and preserves the two matched `p63` recoveries, but the `p82` weekday regressions persist; mathstral loses recoveries and gemma4 is structurally invalid under this interface.
- Pairwise prompt and natural-rate loaders now fail loudly when the requested answer-row filter returns zero rows; this guards against silent all-zero natural-rate reports when an answer-row cache is empty or the target/other labels mismatch.
- The full 120-prompt verifier panel collapses to 33 unique problem families and should be reported as a hard-failure signal test, not a broad MATH benchmark.
- The synthetic deployed-mix scorer smoke validates threshold/fallback plumbing only. It is not model evidence and should not be reported as verifier performance.
- The synthetic deployed-mix policy CI smoke validates the stratified bootstrap decision machinery only. It is not model evidence and should not be reported as verifier performance.
- The deployed-mix power plan is a simulation over assumed verifier behavior. It is experiment design, not measured verifier evidence.
- The deployed-mix representativeness audit shows the current balanced packet sets cover only 37-38 unique source problems per model. Treat them as smoke assets unless rebuilt larger/lower-duplication.
- The unique-source deployed-mix rebuild removes within-model duplication but is not perfectly balanced for Llama: top20-only and no-visible-top20 are sparse under one-packet-per-source sampling.
- The short-trace baseline is a completed-trace proxy for First Finish Search, not an online decoding reproduction.
- The cross-model verifier transfer benchmark is a cheap text-feature scorer stress test over sampled N=128 candidate unions. It is not an external verifier result and does not replace the deployed-mix LLM judge run.
- The cross-model transfer seed sweep tests split/sampling robustness for that same cheap scorer. It is still not task-transfer or external-verifier evidence.
- The cross-task transfer boundary test uses the same cheap scorer on MATH/GSM8K Llama traces. It shows candidate AUC can shift more than final cluster selection, so confidence calibration should not be assumed portable.
- The transfer calibration audit is a synthesis over v53/v54 CSVs. It introduces no new verifier evidence; it just separates final selection transfer from candidate confidence/ranking transfer.
- The canonical gap bootstrap CI is a problem-bootstrap over the same sampled-trial setup as the canonical N=128 MATH depth audit. It gives uncertainty for the diagnostic gap, not external verifier performance.
- Detector-zoo gains are seed-sensitive. Use the three-seed robustness sweep for conservative claims.
- Deep top-k bounds are optimistic perfect-verifier oracles. They measure cluster visibility/depth, not realized deployed accuracy.
- Adaptive-depth frontier rows are projections. Replace assumed verifier success/regression rates with measured external/local verifier rates before claiming a completed method.
- The v23 buried top-20 pilot is in-thread/subagent evidence over only 13 unique source problems. Treat it as a readability/signal check, not a benchmark.
- The v75 qwen3.5:9b deployed-mix smoke is real local endpoint evidence, but it is tiny and negative. It should be reported as evidence that the slim prompt/small local model is insufficient, not as a positive verifier result.
- The v76 qwen3.5:9b rich/evidence-only probes are also negative on the same six recoverable failures. They reduce the chance that v75 failed only because the prompt was too slim.
- The v77 answer-only probes are also negative. Qwen formatting improves but recovery stays `0/6`; gemma4:26b remains `0/6` and structurally unreliable.
- The v78 feature-selector probes recover some top5 deployed-mix failures, but not top10/top20 tails, and no configuration passes the conservative lower-CI-positive decision. Treat v78 as evidence for calibrated override research, not as a completed verifier.
- The v79 calibrated override probes show simple source-calibrated margin override is not deployable: it chooses no-op or transfers negative. Target-oracle thresholds are diagnostic only; they show shallow signal exists but do not prove a usable policy.
- The v80 utility override probes show the natural two-head gate is still not deployable: source-calibrated policies are flat, target-oracle gains are shallow and Llama-sided, and top10/top20 tail recovery remains absent.
- The v81 risk-controlled override probes make the gate safer but still target-flat under source calibration.
- The v82 calibration-stability audit repeats v80/v81 over eight source split seeds. It is evidence that the cheap feature-gate family is stably shallow, not a positive deployed method.
- The v83 qwen3:14b runs are real local endpoint evidence, but negative: targeted recoverable reruns remain `0/6`, and the full 144-prompt panel has weak recovery (`2/72`) plus heavy baseline regression (`11/24`). Treat as a local-verifier stopline, not a positive method result.
- The v84 qwen3:14b rich problem-inclusive runs are also negative: targeted recoverable rerun remains `0/6`, and the full 144-prompt panel improves only to `4/72` recoverable hits while preserving `12/24` baseline-correct rows and recovering no top20-only failures. Treat as the prompt-starvation stopline for local qwen3:14b.
- The Ollama native runner now retries `http.client.RemoteDisconnected` because the remote tunnel can drop mid-run. That is operational robustness, not a model-quality change.
- The v85 rank-bucket transfer audit is projected allocation evidence only. It shows the bucket-depth policy transfers across MATH/Llama and MATH/Gemma under assumed 80% success / 2% false regression, but it still uses target-trace candidate scores and labels and does not replace measured verifier evidence.
- The v86 rank-bucket quality sweep is also projected allocation evidence only. It stress-tests v85 over success/regression assumptions and shows small cross-vs-within gaps even at 50% success / 5% false regression, but it still does not measure a real verifier.
- The v87 rank-bucket cross-seed transfer audit is projected allocation evidence only. It breaks source/target split-seed coupling and keeps cross-model/cross-seed rows above fixed compact at 1024 tokens/problem, but it still does not measure a real semantic verifier.
- The v88 rank-bucket transfer budget map is a secondary analysis of v87. It is useful for anti-cherrypick wording, but it introduces no new verifier measurements.
- The v89 rank-bucket verifier quality target map is algebra over v87 projected rows. It gives explicit success/regression targets for the portable fixed-frontier claim, but it is not measured verifier evidence.
- The v90 rank-bucket quality region map is a grid analysis over v89/v87 projected rows. It shows the quality envelope for the portable claim, but it is still not measured verifier evidence.
- The v91 rank-bucket pair-bootstrap audit resamples only six seed-pair rows per direction/budget. It is useful for lower-bound fragility and wording, not a broad statistical proof.
