# v35 Paper Package: Failure-Activated Adaptive Cluster-Depth Verification

**Date:** June 1, 2026  
**Status:** aggressive paper-package synthesis after regenerating the rank-bucket seed sweep.

## Reviewer-Resistant Pitch

Repeated sampling creates a hidden answer-cluster frontier. On high-N MATH traces, a correct answer cluster is often present, but cheap deployed selectors fail to surface it. The failure is not only "pick the second cluster instead": on `cluster_sum` misses, the correct-cluster rank has p50/p90 `6/21` for MATH/Llama and `8/33` for MATH/Gemma. That makes shallow reranking too timid.

The proposed method is failure-activated adaptive cluster-depth verification:

```text
sample many candidates
group by extracted final answer
select a cheap default with cluster_sum
predict whether the default is unreliable and how deep recovery is likely to be
spend compact verifier budget on skip/top-5/top-10/top-20
fall back to fuller evidence only when compact verification is uncertain
```

The contribution should be framed as a measurement target plus a budgeted allocation method, not as "CSS routing wins." CSS routing was the failed starting point. The live contribution is answer-cluster selectability and depth-aware verifier allocation.

## Evidence Ladder

| level | what it proves | status |
|---|---|---|
| Selector-switching baseline | CSS/router is not enough | weak/negative, useful only as motivation |
| Selectability gap | any-correct/cluster-oracle coverage far exceeds cheap selector accuracy | strong on MATH/Llama and MATH/Gemma |
| Negative rankers/rescue | shallow rankers and unconditional rescue do not safely deploy | strong enough to shape method |
| Deep top-k audit | correct clusters are often buried beyond top-3 | strong diagnostic |
| Prompt assets | strict/diverse top-10/top-20 compact/full verifier packets exist | strong artifact readiness |
| Evidence-budget audit | compact prompts preserve most correct-cluster evidence and halve prompt size | strong sensitivity evidence |
| Rank-bucket allocation | learned depth buckets beat fixed compact rows at high budget | promising projected method result |
| Seed sweep | rank-bucket projected gains survive three split seeds | modest but useful robustness |
| Generation-vs-verification | more samples increase coverage but barely move `cluster_sum` | strong objection check |
| Dynamic extra sampling | uncertainty-targeted extra samples still barely move realized `cluster_sum` | strong objection check |
| Token-budget generation-vs-verification | at 512/1024 tokens, dynamic generation is far below projected rank-bucket verification | strong objection check |
| Fine-grained generation budget | 8-sample chunks still do not move `cluster_sum` at matched budgets | strong objection check |
| Dynamic generation seed sweep | three-seed fine-grained generation stays near-zero on deployed delta | strong objection check |
| Short-trace baseline | shortest/first-finish proxy is far below `cluster_sum`; length-weighted clusters only tie | strong objection check |
| Deployed-mix verifier assets | balanced prompts for recovery and regression accounting | strong artifact readiness |
| Deployed-mix break-even | exact recovery-vs-regression thresholds from natural category rates | strong sensitivity analysis |
| Deployed-mix policy scorer | confidence-threshold fallback and natural-rate weighted deployed delta | strong harness readiness |
| Deployed-mix statistical gate | stratified bootstrap CI with lower-bound-positive pass rule | strong decision-protocol readiness |
| Deployed-mix power plan | current 72-prompt set is smoke-sized for medium effects, underpowered for marginal effects | strong experiment-design readiness |
| Deployed-mix representativeness | current balanced assets cover only 37-38 unique source problems/model | strong scope caveat |
| Unique-source deployed-mix assets | lower-duplication prompt family, with measured Llama rare-bucket sparsity | strong artifact readiness |
| Canonical number lock | high-N gap/depth table regenerated from source CSVs | strong claim hygiene |
| External verifier | measured compact/full success, false regression, fallback quality | missing decisive benchmark |

## Best Current Numbers

High-N parser/depth evidence:

| dataset | cheap selector | cluster oracle | top-10 oracle | top-20 oracle | miss-rank p50/p90 |
|---|---:|---:|---:|---:|---:|
| MATH/Llama N=128 | `0.448` | `0.852` | `0.748` | `0.809` | `6/21` |
| MATH/Gemma N=128 | `0.233` | `0.725` | `0.536` | `0.635` | `8/33` |

Use `outputs/canonical_selectability_depth_table.md` for these headline values. It also records the nearby multi-N parser-v2 values that produced earlier ranges.

Budget/depth evidence:

| dataset | result |
|---|---|
| MATH/Llama | v32 rank-bucket at 1024 tokens/problem: `0.684` vs fixed compact `0.621` |
| MATH/Gemma | v32 rank-bucket at 1024 tokens/problem: `0.465` vs fixed compact `0.395` |
| MATH/Llama | v33 three-seed delta at 1024 tokens/problem: `+0.228 +/- 0.008` over `cluster_sum` |
| MATH/Gemma | v33 three-seed delta at 1024 tokens/problem: `+0.194 +/- 0.024` over `cluster_sum` |

Generation-only objection check:

| dataset | N=128 -> N=1024 `cluster_sum` delta | any-correct delta | extra sample tokens/problem |
|---|---:|---:|---:|
| MATH/Llama | +0.009 | +0.088 | 114374 |
| MATH/Gemma | +0.029 | +0.169 | 126364 |

The v33 aggregate was freshly regenerated with:

```bash
python3 work/rank_bucket_seed_sweep.py --output-prefix rank_bucket_seed_sweep
```

It reproduced `outputs/rank_bucket_seed_sweep.md`, `outputs/rank_bucket_seed_sweep.csv`, and `outputs/rank_bucket_seed_sweep_raw.csv`.

## Related-Work Positioning

Primary anchors checked in the June 1, 2026 refresh:

- Self-consistency: sampled reasoning paths plus answer aggregation, the classic baseline. <https://arxiv.org/abs/2203.11171>
- Large Language Monkeys: repeated-sampling coverage scales, but majority/reward selectors can plateau without automatic verification. <https://arxiv.org/abs/2407.21787>
- Efficient Test-Time Scaling via Self-Calibration: adaptive sample budgets from confidence. <https://arxiv.org/abs/2503.00031>
- Scaling Test-Time Compute Without Verification or RL is Suboptimal: verification is crucial when reward distributions are heterogeneous/non-sharp. <https://arxiv.org/abs/2502.12118>
- When To Solve, When To Verify: fixed-budget tradeoff between generating more solutions and spending compute on generative verification. <https://arxiv.org/abs/2504.01005>
- Budget-aware Test-time Scaling via Discriminative Verification: cheap discriminative verification plus self-consistency under fixed compute. <https://arxiv.org/abs/2510.14913>
- Scaling Flaws of Verifier-Guided Search: imperfect verifiers can misrank/prune valid paths as sample size grows. <https://arxiv.org/abs/2502.00271>
- Multi-Agent Verification: scale the number/aspect diversity of verifiers. <https://arxiv.org/abs/2502.20379>
- xVerify: answer extraction/equivalence hygiene for reasoning-model evaluations. <https://arxiv.org/abs/2504.10481>

Novelty gap:

```text
Most work allocates number of samples, number/type of verifiers, or candidate-level verification.
This project allocates verifier compute over answer-cluster depth after repeated sampling.
```

That is the cleanest way to avoid claiming more than the current evidence supports.

## Main Reviewer Attacks And Answers

### Attack: The best gains are projected.

Correct. The rank-bucket frontier assumes verifier success/regression rates. The answer is not to hide this; the draft must make it the main remaining benchmark. The projected result only proves the allocation model is worth testing.

### Attack: The packet verifier evidence is conditioned on failure.

Correct. Rank11-20 packets test recoverability when a correct cluster is deeply buried. They do not measure deployed regression. The next deployed-mix run must include already-correct defaults, no-visible-correct cases, shallow recoverable cases, and buried recoverable cases.

The deployed-mix decision rule is now pre-specified: score confidence-threshold fallback policies, bootstrap within each deployment category, and only count the policy as positive if the lower 95% CI on natural-rate weighted deployed delta is above zero.

The power plan adds the sample-size read: `12` packets/category is enough to catch weak-or-better effects in simulation, but not enough to certify marginal near-break-even deltas. Treat the current deployed-mix assets as a smoke benchmark unless the point estimate is comfortably positive.

The representativeness audit adds the scope read: current deployed-mix assets are balanced and capped at `2` packets/problem, but cover only `38` Llama and `37` Gemma unique source problems. Do not sell them as broad MATH generalization.

The unique-source rebuild adds a second verifier target: Gemma fills `96` one-source prompts, while Llama reaches `79` because rare top20-only/no-visible buckets are sparse. This is the right companion to the balanced smoke set.

### Attack: The gap numbers vary.

Fair. Older top-k, parser-v2, and deep-depth scripts use slightly different extraction/trial provenance. The paper should use a single canonical table before submission. Until then, ranges are safer than third-decimal precision.

### Attack: Why not generate more samples instead?

This is the most important baseline. The current answer is only partial: high-N MATH still has a selector gap, and prompt/token budgets make verification plausible. A serious paper needs measured generation-vs-verification iso-budget curves.

### Attack: A stronger verifier might erase the method.

If a cheap universal verifier closes the gap directly, adaptive depth becomes less important. But even then, cluster-depth reporting remains a useful diagnostic: it tells the verifier what part of the frontier it had to inspect and how much budget it spent.

## Decisive Next Benchmark

Run compact diverse top-20 rank11-20 prompts first:

```bash
python3 work/run_openai_compatible_verifier.py \
  --base-url http://localhost:11434/v1 \
  --model <model> \
  --prompts outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.jsonl \
  --output outputs/<model>_llama_top20_diverse_compact_predictions.jsonl \
  --resume

python3 work/score_llm_judges.py \
  --predictions outputs/<model>_llama_top20_diverse_compact_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.answer_key.json \
  --output-prefix <model>_llama_top20_diverse_compact
```

Then repeat for Gemma compact, rerun full prompts on compact failures/low confidence, and use `work/score_verifier_cascade.py` to measure fallback quality. For the deployed-mix prompt sets, use `work/score_deployed_mix_verifier.py` followed by `work/deployed_mix_policy_ci.py` so the final call is made by the v45 lower-CI-positive rule. If the deployed-mix point estimate is only marginal, scale the packet set before claiming the method.

Current compute status:

- `curl http://localhost:11434/api/tags` fails: local Ollama is not running.
- `ollama` is not installed on the Mac path.
- `ssh pc` to `192.168.1.223` times out.
- `ssh trevors-pc.local` resolves but rejects current SSH auth.

So the block is not research design. It is verifier runtime access.

## Current Artifacts To Read In Order

1. `outputs/paper_draft_adaptive_cluster_depth.md`
2. `outputs/canonical_selectability_depth_table.md`
3. `outputs/result_ledger.md`
4. `outputs/adaptive_depth_method_proposal.md`
5. `outputs/rank_bucket_seed_sweep.md`
6. `outputs/adversarial_reviewer_checklist.md`
7. `outputs/css_research_note_v36_generation_vs_verification.md`
8. `outputs/css_research_note_v37_deployed_mix_verifier_assets.md`
9. `outputs/css_research_note_v38_deployed_mix_break_even.md`
10. `outputs/css_research_note_v39_deployed_mix_threshold_scoring.md`
11. `outputs/css_research_note_v40_current_lit_pressure_test.md`
12. `outputs/css_research_note_v41_dynamic_sampling_baseline.md`
13. `outputs/css_research_note_v42_token_budget_generation_vs_verification.md`
14. `outputs/css_research_note_v43_fine_grained_generation_budget.md`
15. `outputs/css_research_note_v44_dynamic_generation_seed_sweep.md`
16. `outputs/css_research_note_v45_deployed_mix_statistical_decision.md`
17. `outputs/css_research_note_v46_deployed_mix_power_plan.md`
18. `outputs/css_research_note_v47_deployed_mix_representativeness.md`
19. `outputs/css_research_note_v48_unique_source_deployed_mix_assets.md`
20. `outputs/css_research_note_v49_canonical_number_lock.md`
21. `outputs/css_research_note_v50_live_literature_refresh.md`
22. `outputs/css_research_note_v51_short_trace_baseline.md`
23. `outputs/css_research_note_v52_cross_model_verifier_transfer.md`
24. `outputs/css_research_note_v53_cross_model_transfer_seed_sweep.md`
25. `outputs/css_research_note_v54_cross_task_transfer_boundary.md`
26. `outputs/css_research_note_v55_transfer_calibration_audit.md`
27. `outputs/css_research_note_v56_reviewer_resistant_pitch.md`
28. `outputs/css_research_note_v57_canonical_gap_bootstrap_ci.md`
29. `outputs/reproducibility_manifest.md`

## Verification Run

Fresh local checks passed:

```text
python3 outputs/make_result_ledger.py
python3 work/test_evidence_budget_frontier.py
python3 work/test_cost_aware_verifier_cascade.py
python3 work/test_score_verifier_cascade.py
python3 work/test_run_openai_compatible_verifier.py
python3 work/test_iso_budget_depth_frontier.py
python3 work/test_budgeted_depth_policy.py
python3 work/test_rank_bucket_depth_policy.py
python3 work/test_rank_bucket_seed_sweep.py
python3 work/test_audit_packet_representative_visibility.py
python3 work/test_make_cluster_verifier_prompts.py
python3 work/test_build_cluster_packet_dataset.py
python3 work/test_score_llm_judges.py
python3 work/test_adaptive_depth_frontier.py
python3 work/test_deep_topk_cluster_audit.py
python3 work/test_failure_detector_zoo.py
python3 work/test_deployed_mix_policy_ci.py
python3 work/test_deployed_mix_power_plan.py
python3 work/test_audit_deployed_mix_representativeness.py
python3 work/test_make_canonical_selectability_depth_table.py
python3 work/test_short_trace_baseline.py
python3 work/test_cross_model_verifier_transfer.py
python3 work/test_cross_model_verifier_transfer_seed_sweep.py
python3 work/test_transfer_calibration_summary.py
python3 work/test_canonical_gap_bootstrap_ci.py
python3 -m py_compile work/*.py outputs/*.py
```

Link/content integrity passed for the new paper draft, README, manifest, and project notes.

## Bottom Line

This is not done, but it is now a real research object:

> Repeated sampling needs deployed selectability metrics, and hard MATH failures need budgeted depth allocation over answer clusters, not just more votes.

The strongest current method is rank-bucket adaptive depth. The decisive missing result is measured compact/full verifier behavior, judged with the deployed-mix lower-CI-positive policy gate rather than a raw point estimate, interpreted with the v46 power plan, scoped by the v47 representativeness caveat, and ideally checked against the v48 unique-source prompt family.
