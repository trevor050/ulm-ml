# v56 Reviewer-Resistant Pitch

## Title

**Answer-Cluster Selectability: Test-Time Scaling Fails When Correct Answers Are Generated but Not Surfaced**

## One-Sentence Claim

Repeated sampling often already contains a correct answer cluster, but current selectors fail to surface it; the resulting **answer-cluster selectability gap** is large on hard MATH traces, survives generation-only and short-trace baselines, and points to adaptive cluster-depth verification as a concrete test-time scaling target for depth-limited regimes.

## Abstract Draft

Test-time scaling is often evaluated by asking whether more samples contain a correct answer. We argue that this misses a distinct bottleneck: after sampling, the system must select the correct final answer cluster. On repeated-sampling traces from Monkey Business, high-N MATH runs show a large gap between generated answer coverage and realized selector accuracy. At N=128, the canonical MATH table gives Llama `cluster_sum 0.448` versus oracle `0.852`, and Gemma `0.233` versus oracle `0.725`; problem-bootstrap headroom CIs remain large at Llama `0.404 [0.309, 0.501]` and Gemma `0.492 [0.402, 0.582]`. On selector misses, the correct cluster is often not near the top, with miss-rank p50/p90 `6/21` and `8/33`. Cross-trace audits make the boundary explicit and seed-stable: GSM8K/Llama is mostly surfaced, MATH/Pythia is coverage-limited but still has buried recoverable clusters, and MATH/Llama/Gemma are the large depth-limited regimes. The N-sweep phase diagram shows why this is a test-time scaling diagnostic: hard MATH becomes depth-limited around `N=32+`, while GSM8K surfaces early and Pythia remains coverage-limited. Phase-aware verifier triage then makes the diagnostic operational: MATH/Llama and MATH/Gemma become top20 verifier-spend targets at `N=32`, while GSM8K and Pythia are controls for surfaced and coverage-limited behavior.

Naive fixes do not close the gap. Learned surface rankers trail `cluster_sum`; extended generation from N=128 to N=1024 mostly increases hidden coverage while barely moving realized `cluster_sum`; token-matched dynamic generation remains near zero; and completed-trace short/first-finish proxies are much worse than `cluster_sum`. The method hypothesis is therefore not "verify everything." It is failure-activated adaptive cluster-depth verification: detect unreliable selections, inspect answer clusters to the cheapest useful depth, and account for false regressions on already-correct defaults.

The current evidence supports the diagnostic and a projected method frontier, not yet a completed verifier system. Rank-bucket depth allocation beats fixed compact depth rows under projected verifier success and survives a small seed sweep, while deployed-mix assets and bootstrap decision rules are prepared for the missing external/local LLM verifier run. Recent transfer audits further narrow the claim: cheap scorer transfer is stable across MATH/Llama and MATH/Gemma over three seeds, but task shift can move candidate-level calibration even when final cluster selection remains mostly stable. A serious benchmark should therefore report answer coverage, realized selector accuracy, depth selectability, generation-vs-verification budget, scorer transfer, confidence calibration, false-regression rate, and bootstrap confidence intervals for deployed gain.

## What Is New Here

1. **Selectability as a separate test-time scaling axis.** The core metric is not only whether a correct sample exists, but whether a selector can surface the correct answer cluster.
2. **Depth, not just top-k reranking.** On hard MATH misses, correct clusters are often buried past top-3, making top-10/top-20 inspection a realistic frontier.
3. **Budgeted adaptive verification target.** The strongest current method direction is to allocate verifier depth by predicted recoverability bucket under a token budget.
4. **Regression-aware deployment accounting.** Deployed-mix assets separate already-correct defaults, recoverable misses, no-visible-answer cases, and no-generated-answer cases, making false regression measurable.
5. **Transfer boundary for cheap scorers.** Same-task cross-model scorer transfer is stable; cross-task confidence calibration is less portable than final answer-cluster selection.
6. **Trace-regime boundary.** The same diagnostic separates shallow/surfaced, coverage-limited, and depth-limited traces instead of claiming one universal failure mode.
7. **Phase-aware verifier triage.** The phase map gives a pre-verifier routing rule: spend depth budget first on depth-limited traces, not on already-surfaced or coverage-limited regimes.

## Core Evidence Ladder

| pressure | result | artifact |
|---|---|---|
| Does the gap exist? | Canonical MATH N=128: Llama `0.448` vs oracle `0.852`; Gemma `0.233` vs `0.725`. | [v49](css_research_note_v49_canonical_number_lock.md) |
| Is the gap statistically robust? | Problem-bootstrap headroom CIs stay large: Llama `0.404 [0.309, 0.501]`, Gemma `0.492 [0.402, 0.582]`. | [v57](css_research_note_v57_canonical_gap_bootstrap_ci.md) |
| Is this only a MATH/Llama/Gemma cherry-pick? | Same audit over all local traces: GSM8K is mostly surfaced, Pythia is coverage-limited, hard MATH is depth-limited, and the map survives three seeds. | [v58](css_research_note_v58_cross_trace_gap_bootstrap.md), [v59](css_research_note_v59_cross_trace_regime_seed_sweep.md) |
| How do regimes change with N? | Hard MATH transitions to depth-limited around `N=32+`; GSM8K surfaces early; Pythia remains coverage-limited; high-N labels are seed-stable. | [v61](css_research_note_v61_selectability_phase_diagram.md), [v62](css_research_note_v62_phase_seed_sweep.md) |
| When should verifier budget be spent? | Phase-aware triage marks MATH/Llama and MATH/Gemma as top20 spend targets at `N=32`, GSM8K as mostly surfaced, and Pythia as coverage-limited. | [v63](css_research_note_v63_phase_aware_verifier_triage.md) |
| Are the phase labels threshold-fragile? | Reclassifying v62 rows over 81 threshold settings keeps high-N Gemma/Pythia unanimous, Llama depth-limited at N=128, and GSM8K as the expected surfaced edge case. | [v64](css_research_note_v64_phase_threshold_sensitivity.md) |
| Does verifier-spend depend on one optimistic quality assumption? | No for depth-limited MATH. At N=128, MATH/Llama/Gemma stay positive even at 50% verifier success and 5% false regression. | [v65](css_research_note_v65_verifier_quality_sensitivity.md) |
| Is top20 just a flattering fixed-depth knob? | No. GSM8K is shallow-control, Pythia is coverage-first, while high-N MATH has nontrivial top10->top20 marginal gain. | [v66](css_research_note_v66_phase_depth_marginal_utility.md) |
| Is top20 cost-efficient? | Not usually. Top5/top10 dominate marginal prompt ROI; top20 is a deliberate expensive tail spend for high-value depth-limited cases. | [v67](css_research_note_v67_phase_depth_cost_roi.md) |
| What depth would a policy actually choose? | At 80% success / 2% false regression, top10 is the ordinary high-N MATH operating point; top20 only wins above value thresholds of about `20k` Gemma and `35k` Llama tokens per +1.0 accuracy. | [v68](css_research_note_v68_phase_depth_policy_frontier.md) |
| Does the policy collapse if verifier quality changes? | No. Lower success shifts choices toward no-verifier/top10 and raises top20 thresholds; the policy degrades rather than pretending fixed top20 is always right. | [v69](css_research_note_v69_phase_depth_policy_quality_sweep.md) |
| Does current literature make this too broad? | Yes if pitched as generic adaptive TTS. The surviving claim is answer-cluster phase diagnostics plus costed cluster-depth routing. | [v70](css_research_note_v70_live_literature_positioning_refresh.md) |
| What exactly must the next verifier run score? | v71 gives finite-sample targets: with one baseline regression, top20 smoke needs uniform `2/12` Llama or `1/12` Gemma recoveries/category, but top20-only evidence needs `6/12` Llama or `4/12` Gemma tail recoveries. | [v71](css_research_note_v71_deployed_mix_verifier_requirement_table.md) |
| Do those verifier targets survive source-unique pressure? | Mostly. Recoverable top20 mass stays similar, Gemma unique16 is healthy, but Llama unique-source top20-only buckets are sparse and should not be overclaimed alone. | [v72](css_research_note_v72_deployed_mix_requirement_representativeness_sweep.md) |
| Can Llama unique-source tail be enlarged locally? | Only slightly. A target-32, 96-trial, one-source attempt reaches `9` top20-only packets and `2` no-visible packets; more traces or relaxed constraints are needed. | [v73](css_research_note_v73_llama_unique_source_tail_expansion.md) |
| Is the next verifier run one-command scoreable? | Yes. v74 wraps raw category scoring, v71 targets, confidence fallback, natural-rate deployed delta, and v45 CI into one report command. | [v74](css_research_note_v74_deployed_mix_verifier_report_harness.md) |
| Has a real local verifier endpoint been exercised? | Yes, with a negative smoke. v75 runs qwen3.5:9b on a 12-prompt slim deployed-mix panel; it preserves sampled baselines but recovers `0/6` visible recoverable buckets. | [v75](css_research_note_v75_remote_ollama_verifier_smoke.md) |
| Was qwen's failure just evidence starvation? | No in a targeted rerun. v76 gives the same six recoverable failures richer evidence and evidence-only prompts; both remain `0/6`. | [v76](css_research_note_v76_qwen_evidence_budget_probe.md) |
| Was qwen's failure just long-form JSON/reason instability? | No. v77 answer-only mode makes qwen parse cleanly, but it remains `0/6`; gemma4:26b is also `0/6` and still structurally unreliable. | [v77](css_research_note_v77_answer_only_verifier_interface.md) |
| Can a trained feature selector replace the failed chat verifier? | Partially. v78 recovers `3/12` top5 deployed-mix failures in both cross-model directions, but top10/top20 remain `0/12` and no CI-positive decision passes. | [v78](css_research_note_v78_deployed_mix_feature_selector.md) |
| Does calibrated override make that selector deployable? | Not yet. v79 source-calibrated thresholds choose no-op or transfer negative; target-oracle thresholds show shallow headroom but calibration transfer is unsolved. | [v79](css_research_note_v79_calibrated_override_selector.md) |
| Does a utility-trained override gate fix calibration? | No. v80 is safe under source calibration but flat; target-oracle thresholds recover only shallow Llama top5 cases and no top10/top20 tails. | [v80](css_research_note_v80_utility_override_selector.md) |
| Was the cheap-gate failure just one unlucky split? | No. v82 repeats v80/v81 over eight seeds: active source gates occur in `23/64` deployable runs, but target-oracle top20-only recovery is still `0`. | [v82](css_research_note_v82_override_calibration_stability.md) |
| Does a stronger local qwen verifier close the loop? | No. qwen3:14b completes the full 144-prompt answer-only/evidence-only deployed-mix panel, but recovers only `2/72` recoverable prompts, preserves only `13/24` baseline-correct rows, and no threshold is CI-positive. | [v83](css_research_note_v83_qwen14b_and_literature_stopline.md) |
| Was qwen3:14b just context-starved? | No. With the original problem and richer cluster evidence, qwen3:14b improves only to `4/72` recoverable prompts, preserves only `12/24` baseline-correct rows, recovers no top20-only failures, and remains CI-negative. | [v84](css_research_note_v84_qwen14b_rich_problem_prompt_stopline.md) |
| Is top-3 enough? | No. Miss-rank p50/p90 is Llama `6/21`, Gemma `8/33`. | [v20](css_research_note_v20_buried_cluster_depth.md) |
| Can learned shallow rankers close it? | No. Current learned cluster rankers roughly match or trail `cluster_sum`. | [v6](css_research_note_v6_cluster_ranker.md) |
| Why not just sample more? | N=128->1024 raises coverage but moves `cluster_sum` only Llama `+0.009`, Gemma `+0.029`. | [v36](css_research_note_v36_generation_vs_verification.md) |
| What about token-matched generation? | At 512/1024 tokens, best dynamic generation gives Llama `+0.000/+0.000`, Gemma `+0.027/+0.027`. | [v42](css_research_note_v42_token_budget_generation_vs_verification.md) |
| What about finer generation allocation? | 8-sample chunks still give `+0.000/+0.000` for both models at 512/1024 tokens. | [v43](css_research_note_v43_fine_grained_generation_budget.md) |
| Is the generation baseline seed-stable? | Three-seed fine-grained dynamic generation stays near zero. | [v44](css_research_note_v44_dynamic_generation_seed_sweep.md) |
| What about first-finish/short traces? | Shortest answer-cluster gets only Llama `0.264`, Gemma `0.104`. | [v51](css_research_note_v51_short_trace_baseline.md) |
| Does adaptive depth help in projection? | Rank-bucket policy at 1024 verifier tokens beats fixed compact rows: Llama `0.684` vs `0.621`, Gemma `0.465` vs `0.395`. | [v32](css_research_note_v32_rank_bucket_depth_policy.md) |
| Is projected allocation seed-stable? | Three-seed projected deltas: Llama `+0.228 +/- 0.008`, Gemma `+0.194 +/- 0.024`. | [v33](css_research_note_v33_rank_bucket_seed_sweep.md) |
| Does projected allocation transfer across trace models? | Mostly. At 1024 tokens/problem, Gemma-trained allocation on Llama reaches `0.652` vs within `0.659`; Llama-trained on Gemma reaches `0.432` vs within `0.441`, and both beat fixed compact rows. | [v85](css_research_note_v85_rank_bucket_cross_model_transfer.md) |
| Does allocation transfer survive verifier-quality stress? | Yes in projection. At 1024 tokens/problem under harsh `50%` success / `5%` false regression, cross gaps are only `-0.006` on Llama and `-0.005` on Gemma. | [v86](css_research_note_v86_rank_bucket_transfer_quality_sweep.md) |
| Does allocation transfer survive split-seed decoupling? | Yes in projection. The harsh cross-model/cross-seed v87 rows still beat fixed compact at 1024 tokens by `+0.018` on Llama and `+0.036` on Gemma. | [v87](css_research_note_v87_rank_bucket_cross_seed_transfer.md) |
| Is the transfer claim budget-dependent? | Yes. v88 shows Gemma->Llama only beats fixed compact at `1024`, while Llama->Gemma beats fixed compact at all tested budgets. | [v88](css_research_note_v88_rank_bucket_transfer_budget_map.md) |
| What verifier quality does the portable claim need? | v89 solves the contract. At 2% false regression, the 1024-token fixed-frontier rows need about `73%` recovery success for Gemma->Llama and `65%` for Llama->Gemma; transfer should not be claimed as beating target calibration. | [v89](css_research_note_v89_rank_bucket_verifier_quality_targets.md) |
| Is that quality claim region-stable? | Partly. v90 scans success `0.50-1.00` and false regression `0-0.10`; best fixed-frontier pass fractions are Gemma->Llama 1024 `0.422` and Llama->Gemma 1024 `0.565`, with smaller within-same regions. | [v90](css_research_note_v90_rank_bucket_quality_region_map.md) |
| Is transfer stable across seed pairs? | Asymmetric. v91 gives Llama->Gemma 1024 as `6/6` positive with CI `[+0.027,+0.044]`; Gemma->Llama 1024 is `5/6` with CI `[-0.006,+0.038]`, so it is lower-bound fragile. | [v91](css_research_note_v91_rank_bucket_pair_bootstrap.md) |
| Does a math-specialized local verifier solve the measured gap? | No. v92's `mathstral:7b` run produces one rich answer-only Gemma top20-only recovery, but slim answer-only loses it, Llama remains `0/3` recoverable with baseline regression, confidence can be invalid, and full rich expansion is CPU/tail-latency blocked. | [v92](css_research_note_v92_mathstral_verifier_boundary.md) |
| Does independent binary cluster scoring solve the interface problem? | No for `mathstral:7b`. v93's fast per-cluster yes/no harness recovers `0/6` under both rationale-conditioned and answer-check prompts; the former is over-permissive, the latter over-conservative. | [v93](css_research_note_v93_binary_cluster_judge_interface.md) |
| Does the binary interface work with a stronger local model? | No. v94 reruns the same 109 binary prompts with `qwen3:14b`; answer-check says no to `108/109`, rationale-conditioned says yes to `24/109`, and both recover `0/6`. | [v94](css_research_note_v94_qwen14b_binary_cluster_judge.md) |
| Can deployment be scored honestly? | Deployed-mix packets, break-even math, threshold fallback scoring, and bootstrap CI gate are prepared. | [v37](css_research_note_v37_deployed_mix_verifier_assets.md), [v38](css_research_note_v38_deployed_mix_break_even.md), [v39](css_research_note_v39_deployed_mix_threshold_scoring.md), [v45](css_research_note_v45_deployed_mix_statistical_decision.md) |
| Are current verifier assets representative? | Current balanced deployed-mix assets are smoke-scale; unique-source rebuild improves coverage but has sparse Llama rare buckets. | [v47](css_research_note_v47_deployed_mix_representativeness.md), [v48](css_research_note_v48_unique_source_deployed_mix_assets.md) |
| Is the scorer model-specific? | Same-task MATH Llama/Gemma transfer is stable over three seeds. | [v53](css_research_note_v53_cross_model_transfer_seed_sweep.md) |
| Does task transfer expose a boundary? | MATH/GSM8K final `cluster_sum` gaps are small, but MATH-trained-to-GSM8K candidate AUC drops `-0.120`. | [v54](css_research_note_v54_cross_task_transfer_boundary.md), [v55](css_research_note_v55_transfer_calibration_audit.md) |

## Strongest Version Of The Pitch

The paper should not claim that verification universally beats generation. That is too broad and too easy to attack. The stronger claim is:

> In high-coverage reasoning traces, final-answer selection can become its own bottleneck. Once a correct answer cluster exists, more generation can have poor marginal value unless the selector improves. Cluster-depth selectability measures this bottleneck, distinguishes it from coverage-limited regimes, and makes adaptive cluster-depth verification a concrete way to spend test-time compute on surfacing already-generated correct answers.

This framing is harder to dismiss because the negative results are part of the claim. CSS/router switching is not enough. Shallow learned rankers are not enough. More samples are not enough under the tested budgets. Short traces are not enough. The next method must explicitly model failure detection, answer-cluster depth, evidence cost, and false regression.

## What Still Blocks A Real Paper

The biggest missing result is still a reproducible external/local LLM verifier benchmark. The current adaptive-depth gains are projected from visible-correct clusters and assumed verifier success/regression rates. Before claiming a completed method, run a real verifier on:

1. compact deployed-mix prompts,
2. full prompts for compact failures or low-confidence cases,
3. diverse buried top-20 prompts,
4. already-correct default packets to measure false regression.

Then score with the v39/v45 path: confidence-threshold fallback to the baseline answer, natural-rate weighted deployed delta, and stratified bootstrap confidence intervals. v63 says the first measured verifier run should prioritize the depth-limited MATH prompts, with GSM8K/Llama and MATH/Pythia used as phase controls rather than blended into one aggregate. v65 says that benchmark is not balanced on one optimistic assumption: depth-limited MATH remains positive under a 50% success / 5% false-regression stress point. v66 adds that the verifier should be adaptive over depth, not always top20: top20 is useful in high-N MATH, mostly wasteful for surfaced GSM8K, and secondary to coverage for Pythia. v67 adds the cost discipline: top5/top10 are the efficient prompt-ROI tiers, while top20 is reserved for high-value depth-limited tail cases. v68 turns that into a utility frontier: at 80% success / 2% false regression, top10 is the ordinary high-N MATH choice, and top20 wins only above explicit value thresholds. v69 repeats the frontier over quality settings and shows the policy degrades toward no-verifier/top10 when success is lower. v70 keeps the novelty claim narrow against live literature: this is answer-cluster phase diagnostics plus costed cluster-depth routing, not generic adaptive test-time scaling. v71 turns the next verifier smoke into countable targets and separates point-positive recovery from actual top20-only evidence. v72 adds the representativeness pressure check: run balanced first, unique-source second, and treat Llama unique-source tail evidence as sparse unless expanded. v73 tries that expansion and shows the current trace is still supply-limited. v74 wraps the entire prediction-to-report path so the real verifier output has an immediate pass/fail interpretation. v75 provides the first real local endpoint smoke and it is negative: qwen3.5:9b on a 12-prompt slim deployed-mix panel recovers none of the visible recoverable examples. v76 reruns those same six recoverable failures with richer evidence and evidence-only prompts, and still gets `0/6`. v77 removes the reason field entirely: qwen formats cleanly but remains `0/6`, while gemma4:26b answer-only is also `0/6` and unreliable. v78 tests the trained-selector replacement route: cross-model feature selectors recover `3/12` top5 failures in both directions, but top10/top20 tails remain `0/12`, hard-packet training overcorrects, and no CI-positive decision passes. v79 makes the override problem explicit: source-calibrated margin thresholds choose no-op or transfer negative, while target-oracle thresholds expose shallow headroom (`+0.056` on Llama) that calibration cannot yet harvest safely. v80 tests the obvious utility-gated fix: source-calibrated two-head policies are safe but flat, and target-oracle thresholds recover only shallow Llama top5 cases (`+0.042` unique / `+0.028` balanced) with no top10/top20 tail recovery. v81 makes the gate risk-controlled and still flat. v82 repeats the override family over eight seeds: active source gates appear in `23/64` deployable runs, `12/23` active gates recover zero target failures, and target-oracle top20-only recovery is `0`. v83 tests the stronger-local-verifier escape hatch: qwen3:14b completes the full 144-prompt answer-only/evidence-only deployed-mix panel, but its `2/72` recoverable hits are swamped by `11/24` baseline-correct regressions and all threshold policies remain CI-negative. v84 tests the obvious context-starvation objection: richer problem-inclusive prompts improve raw recovery only to `4/72`, worsen preservation to `12/24`, still recover no top20-only failures, and remain CI-negative. v85 tests whether the projected rank-bucket policy itself is overfit to one generator trace: cross-model allocation stays within `0.007-0.009` projected accuracy of within-model training at 1024 tokens/problem and beats fixed compact rows on both targets. v86 repeats that transfer test over a verifier-quality grid; even at `50%` success / `5%` false regression, cross gaps are only `-0.006` on Llama and `-0.005` on Gemma. v87 breaks same-seed coupling and still keeps the cross-model/cross-seed rows above fixed compact (`+0.018` Llama, `+0.036` Gemma). Treat this as evidence that the positive claim needs a substantially stronger verifier, expanded positive recovery data, or a different semantic scoring interface, not another one-off qwen/gemma prompt or shallow feature gate.

## Decisive Experiment Spec

Run a local or API LLM judge with JSON outputs:

```bash
python3 work/run_openai_compatible_verifier.py \
  --base-url <openai-compatible-url> \
  --model <judge-model> \
  --prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.jsonl \
  --output outputs/<judge>_llama_deployed_mix_predictions.jsonl \
  --resume
```

Repeat for Gemma deployed-mix prompts, then score:

```bash
python3 work/score_deployed_mix_verifier.py \
  --predictions outputs/<judge>_llama_deployed_mix_predictions.jsonl outputs/<judge>_gemma_deployed_mix_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json \
  --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv \
  --thresholds 0,0.25,0.5,0.75,0.9 \
  --output-prefix <judge>_deployed_mix_verifier

python3 work/deployed_mix_policy_ci.py \
  --predictions outputs/<judge>_llama_deployed_mix_predictions.jsonl outputs/<judge>_gemma_deployed_mix_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_compact.answer_key.json \
  --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv \
  --thresholds 0,0.25,0.5,0.75,0.9 \
  --bootstrap-rounds 1000 \
  --output-prefix <judge>_deployed_mix_policy_ci
```

Pass criterion: at least one threshold policy has positive point-estimate deployed delta and lower 95% CI above zero. If the point estimate is marginal, expand the deployed-mix packet set before claiming success.

## Current Bottom Line

This is no longer just a Hail Mary idea. It is a coherent diagnostic with a strong negative-result moat and a concrete missing verifier experiment. The publishable core is not "we invented a better selector." The publishable core is:

> Test-time scaling should measure answer-cluster selectability, because in high-coverage regimes the correct answer may already be generated but hidden below the selector frontier. Adaptive verification should target cluster depth under deployment and regression constraints, not generic best-of-N reranking.
