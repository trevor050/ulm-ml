# Failure-Activated Adaptive Cluster-Depth Verification

## One-Sentence Pitch

Repeated sampling often contains a correct answer cluster that cheap selectors cannot surface; use a cheap detector to identify unreliable selections, then spend semantic verification compute over a variable-depth frontier of answer clusters.

## Method

For each problem, sample `N` candidate solutions and extract final answers. Group candidates into answer clusters. Let `cluster_sum` be the cheap default selector:

```text
score(a) = sum verifier_score(y_i) for candidates y_i with final answer a
```

Then run:

```text
1. Select default answer with cluster_sum.
2. Compute set-level uncertainty features:
   - top cluster support and margin,
   - score-mass margin,
   - number of answer clusters,
   - answer entropy,
   - score/support dispersion.
3. Predict whether cluster_sum is wrong and a correct cluster is recoverable within depth k.
4. If risk is low, return cluster_sum.
5. If risk is high, allocate semantic verification budget over top-k clusters.
6. Choose the answer cluster best supported by the visible rationales.
```

The depth `k` is not fixed globally. It should be allocated by risk and frontier shape. The current tested depths are `5, 10, 20, 50`, with `10` and `20` looking like the serious regimes for high-N MATH.

## Current Evidence

The original selector-switching idea is weak. On MATH, the useful finding is the gap:

```text
MATH/Llama N=128: cluster_sum about 0.448, oracle about 0.852
MATH/Gemma N=128: cluster_sum about 0.233, oracle about 0.725
```

Correct clusters are often buried:

```text
MATH/Llama selector misses: correct-rank p50/p90 = 6/21
MATH/Gemma selector misses: correct-rank p50/p90 = 8/33
```

These are the script-generated canonical depth numbers from [canonical_selectability_depth_table.md](canonical_selectability_depth_table.md). Use that file, not older nearby top-k/parser artifacts, for headline depth quotes. The companion bootstrap audit keeps the gap statistically robust: problem-bootstrap headroom CIs are Llama `0.404 [0.309, 0.501]` and Gemma `0.492 [0.402, 0.582]`.

The boundary is now clearer across all local traces: GSM8K/Llama is mostly shallow/surfaced (`headroom 0.145`), MATH/Pythia is coverage-limited but still has buried recoverable top20 headroom (`0.257`), and MATH/Llama/Gemma are the large depth-limited regimes. So the method should be sold as adaptive diagnostics and budget allocation, not a universal claim that every task has the same buried-cluster failure mode.

At 20% invoke with an assumed 80% verifier success rate and 2% false-invocation regression, adaptive depth projections are:

```text
MATH/Llama top5 -> top20: 0.508 -> 0.546
MATH/Gemma top5 -> top20: 0.285 -> 0.343
```

That is not enough to claim a finished method, but it is enough to define a real experiment.

## Required Evaluation

A paper-quality evaluation must report all of:

- `cluster_sum` accuracy,
- any-correct coverage,
- top-k/depth oracle accuracy,
- detector AUC and capture at fixed invoke rates,
- semantic verifier accuracy on recoverable invoked misses,
- regression rate on false/unhelpful invocations,
- net deployed accuracy,
- cost in inspected clusters and prompt tokens.

The most important plot is:

```text
x-axis: invocation rate
y-axis: deployed accuracy
curves: depth k = 5, 10, 20, 50
scenarios: measured verifier, not assumed verifier
```

## Pilot Evidence

Strict rank-stratified packet assets now exist for testing the semantic verifier directly. Cheap selectors are effectively dead on these sets: on top-20 rank11-20 packets, support/max/mean/cheap-sanity selectors score `0.000` on Llama and at most `0.033` on Gemma.

A small blind in-thread/subagent pilot on 40 buried top-20 prompts scored `40/40` after simple fraction normalization. This is intentionally weak evidence because it covers only 13 unique source problems and is not an external reproducible model run. It is still useful as a prompt/readability check: buried rank11-20 clusters can contain enough semantic evidence to recover the right answer.

To make the next verifier run less fragile, I also built diverse one-packet-per-source rank11-20 assets. They cover 27 unique Llama source problems and 40 unique Gemma source problems, with cheap selectors still near zero. These are the preferred external-verifier target.

There are now compact variants of those prompts. The compact files preserve all 20 answer clusters while showing one rationale per cluster truncated to 420 characters, cutting average prompt size roughly in half. Use compact prompts first, then rerun full prompts on failures to measure evidence-budget sensitivity.

An evidence-visibility audit supports this compact-first path: in the diverse buried sets, the first representative from a correct cluster is trace-correct in `0.926` of Llama packets and `0.900` of Gemma packets. The two-representative full packet assets reach `1.000` and `0.975`. Compact failures should therefore be followed by full-prompt reruns, but compact prompts are not obviously starved of correct evidence.

An evidence-budget frontier makes that deployment cost tradeoff explicit. At 20% invoke with the conservative 80% verifier-success / 2% false-regression scenario, moving from full to compact top-20 evidence changes projected accuracy only from Llama `0.546 -> 0.539` and Gemma `0.340 -> 0.332`. The compact path is therefore a plausible first-stage verifier budget, with full prompts reserved for failures or borderline cases.

A cost-aware cascade calculation turns that into a deployable target. Compact-only uses about `475` estimated verifier tokens/problem for Llama and `454` for Gemma at 20% invoke, compared with full-only `924` and `853`. An oracle evidence-gap fallback nearly matches full-only projected accuracy at `516` and `496` tokens/problem, so the critical verifier measurement is now not just correctness, but whether verifier uncertainty from the compact run can cheaply predict when full evidence is needed.

The iso-budget depth frontier prevents overclaiming. Under the same projected 80%/2% verifier assumption, compact top-5/top-10 are better low-budget rows, while compact top-20 is the high-budget/high-accuracy row. For example, Llama compact depth-5 at 20% invoke projects `0.508` at about `128` verifier tokens/problem, while depth-20 at 50% invoke projects `0.653` at about `1184` tokens/problem. Gemma shows the same shape: depth-5 at 10% invoke projects `0.264` at `65` tokens/problem, while depth-20 at 50% invoke projects `0.443` at `1133` tokens/problem.

A first budgeted variable-depth policy is not strong enough yet. Greedy allocation using current depth-detector scores improves some low-budget rows, but at higher budgets it mostly buys shallow top-5 verification and loses to fixed compact frontier rows. The oracle version, using true recoverability labels, reaches Llama `0.746` and Gemma `0.556`, so the remaining method target is calibrated depth-value prediction: learn when a problem is worth deeper inspection.

A rank-bucket policy is a better depth-value model. Instead of independent depth detectors, it predicts the minimal recoverability bucket (`top5`, `top10_only`, `top20_only`, or `none`) and prices actions by cumulative bucket probability. At 1024 verifier tokens/problem, this reaches Llama `0.684` versus fixed compact `0.621`, and Gemma `0.465` versus fixed compact `0.395`. It remains below the oracle budgeted policy, but it is the first learned allocation result that makes adaptive depth look like a plausible method rather than only a diagnostic frontier.

A three-seed robustness sweep keeps the rank-bucket result alive. At 1024 verifier tokens/problem, mean projected delta over `cluster_sum` is Llama `+0.228 +/- 0.008` and Gemma `+0.194 +/- 0.024`. The depth mix is stable in shape: mostly top-10, with top-20 reserved for about `0.11-0.12` of all trials at the high budget.

An extended generation-only ablation answers the most obvious budget objection. Moving from N=128 to N=1024 raises any-correct coverage by `+0.088` on Llama and `+0.169` on Gemma, but `cluster_sum` moves only `+0.009` and `+0.029`, despite costing roughly `114k` and `126k` extra sample tokens/problem. More samples create more hidden coverage; they do not make the current deployed selector reliably surface it.

A dynamic extra-sampling proxy makes the objection less straw-manned. It allocates extra trace samples by N=128 uncertainty signals. On MATH/Llama, this still leaves `cluster_sum` flat while any-correct rises. On MATH/Gemma, the best dynamic rows improve `cluster_sum` only `+0.027` to `+0.041`. This does not prove verification, but it shows that adaptive generation alone is not obviously solving the deployed-selection bottleneck in these traces.

A token-budget comparison makes the same point at verifier-scale budgets. At 512/1024 extra tokens per problem, best dynamic generation reaches Llama `+0.000/+0.000` and Gemma `+0.027/+0.027` `cluster_sum` delta. The rank-bucket verifier projection at those budgets is Llama `+0.159/+0.228` and Gemma `+0.120/+0.194`. The verifier side remains projected, but the generation baseline is now budget-fair.

The fine-grained rerun uses 8-sample chunks instead of 128-sample chunks. At 512/1024 tokens, it still gives Llama `+0.000/+0.000` and Gemma `+0.000/+0.000` on realized `cluster_sum`, so the budget-fair generation baseline is not being kneecapped only by coarse allocation.

The fine-grained generation baseline also survives a three-seed split sweep. Mean best dynamic-generation deltas at 512/1024 tokens are Llama `+0.000/+0.000` and Gemma `+0.000/+0.005`; oracle generation deltas are still only Llama `+0.000/+0.000`, Gemma `+0.005/+0.005`.

A short-trace baseline addresses First Finish Search pressure from the live literature refresh. On completed MATH traces at N=128, shortest answer-cluster selection gets only Llama `0.264` and Gemma `0.104`, far below `cluster_sum`; length-weighted clusters tie but do not beat `cluster_sum`.

A cross-model scorer-transfer stress test addresses the judge/trajectory-shift version of the same concern. A cheap sample-level verifier trained on Gemma and evaluated on Llama reaches `cluster_sum 0.445`, `+0.010` vs the Llama-trained scorer; trained on Llama and evaluated on Gemma it reaches `0.238`, `+0.002` vs the Gemma-trained scorer. A three-seed sweep keeps the same story: mean cross-model gaps are Gemma-trained on Llama `+0.005 +/- 0.005` and Llama-trained on Gemma `+0.000 +/- 0.005`. A cross-task MATH/GSM8K sweep is slightly less clean: final `cluster_sum` gaps are only about `-0.010`, but MATH-trained-to-GSM8K candidate AUC drops `-0.120`. The v55 calibration audit separates these levels explicitly: final cluster selection transfers better than candidate ranking/confidence. This does not replace the missing external verifier, but it weakens the claim that the answer-cluster depth result is just scorer overfitting to one trace model and warns that confidence calibration may transfer worse than final selection.

The decisive verifier benchmark now has deployed-mix assets, not only buried recoverable packets. Each model has 72 compact top-20 prompts balanced across already-correct defaults, recoverable top-5/top-10/top-20 misses, no-visible-top20 cases, and no-correct-generated cases. Use these to measure recovery and false regression together.

The v38 break-even analysis converts those categories into deployment math. At `98%` baseline preservation, top-20 recovery success only needs to exceed `0.022` on Llama and `0.017` on Gemma to break even under the natural deployed-mix rates. The real question is therefore not whether hard-packet recovery can be high in isolation; it is whether a verifier can preserve already-correct defaults while recovering a nontrivial fraction of visible misses.

The v39 scorer makes that measurement policy-level. It sweeps confidence thresholds, falls back to the baseline answer below threshold, and emits natural-rate weighted deployed deltas for MATH/Llama and MATH/Gemma. v45 adds the statistical gate for that run: bootstrap within deployed-mix category, recompute natural-rate weighted deployed delta, and only call a threshold policy positive if the lower 95% confidence bound is above zero. This is now the preferred deployed-mix scoring path after any external/local verifier run.

The v46 power plan says how to interpret that run. The current `72` prompts per model are a useful smoke benchmark: weak-or-better effects pass the v45 gate often at `12` packets/category. Near-break-even marginal effects do not: even `96` packets/category remains under `0.65` simulated pass rate. So the practical protocol is two-stage: run the current deployed-mix set, accept only a comfortably positive result, and scale the packet set before claiming a tiny positive delta.

The v47 representativeness audit adds the scope caveat: the deployed-mix sets cover `38` Llama and `37` Gemma unique source problems, with `27` shared across models. That is acceptable for a smoke benchmark, but a paper claim should either call it that or rebuild a larger lower-duplication set.

The lower-duplication target now has a clean v98 rebuild for Gemma. The original v48/v97 Gemma unique16 packet JSONL was an artifact hazard, but `cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98` has `96` one-source compact prompts with `16` per category. Llama has `79` one-source prompts in the earlier unique-source rebuild; rare top20-only and no-visible categories remain underfilled. Use both prompt families if compute allows: balanced duplicated prompts for category-rate accounting, unique-source prompts for representativeness pressure.

## Immediate Experiment

Run an external/local LLM verifier on the rank-stratified buried prompt sets:

```text
outputs/cluster_verifier_prompts_math_llama_n128_top10_rank6_10_strict.jsonl
outputs/cluster_verifier_prompts_math_gemma2b_n128_top10_rank6_10_strict.jsonl
outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_strict.jsonl
outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_strict.jsonl
outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse.jsonl
outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse.jsonl
outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.jsonl
outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse_compact.jsonl
```

Score with the existing answer keys. Then plug the measured success and regression rates into `outputs/adaptive_depth_frontier.csv` in place of the assumed `80%/2%` and `70%/5%` scenarios.

## What Would Make This Real

The proposal becomes genuinely interesting if:

1. a reproducible verifier beats shallow packet baselines on rank-stratified packets,
2. top-20 rank11-20 packets remain recoverable often enough to justify deeper context,
3. detector-triggered deployment improves accuracy after regression accounting,
4. the gain survives at least a small seed/split robustness sweep.

## What Would Falsify It

The proposal should be downgraded if:

1. real verifier accuracy collapses on rank11-20 packets,
2. false-invocation regressions eat most of the projected gain,
3. top-20 prompt cost is too high relative to the accuracy delta,
4. better detectors cannot capture recoverable misses at useful invoke rates,
5. improvements disappear under parser/equivalence audits.

If that happens, the next method should not be "verify deeper." It should be evidence improvement before verification: retrieval over candidate rationales, proof-state features, symbolic equivalence normalization, or a process/verifier model that changes the cluster ranking before the semantic judge sees the packet. v95 tests the first cheap version of this route with hashed problem/answer/rationale features: raw recoverability signal appears, including some top10/top20 deployed-mix hits, but cross-model preservation/calibration fails. v96 adds source-calibrated risk control and still gets no CI-positive policy, with Gemma->Llama barely positive on average and Llama->Gemma negative. v97 pressures the valid lower-duplication Llama unique32 target and stays negative. v98 rebuilds the Gemma unique-source target and runs 81 lower-duplication semantic-risk policies; the best point estimate is not clean, and zero source-calibrated policies pass the CI-positive rule. v99 then target-thresholds raw semantic scores and finds small oracle headroom (`4/81` lower-CI-positive rows). v100 shows that headroom survives source split training (`5/81` target-oracle positives), so the failure is not total absence of signal. v101 then varies calibration size/composition over `72` runs and `1080` source-threshold rows; zero source-calibrated rows pass, and stricter problem-disjoint clean source rows are all no-op. v102 allows labeled target-style calibration and still finds zero held-out CI-positive policies. v103 expands the Gemma target panel to `48/category`; target-calibrated rows still never pass, best clean calibrated gain is only `+0.007` with zero lower bound, and only diagnostic oracle thresholding reaches `+0.034` with positive lower bound. v104 adds problem text, more cluster representatives, longer rationales, larger hash space, and longer training; conservative target calibration remains unchanged. v105 trains a compact multifeature semantic accept/fallback gate and still gets zero lower-CI-positive calibrated policies. v106/v107 test cheap symbolic/answer-shape and representative-level process/proof-hygiene features; both still fail conservative deployed calibration. v108 tests cross-generator answer agreement as a different evidence axis: Llama helps Gemma with small low-regression target-intersection gains, but Gemma hurts Llama and no positive no-regression policy appears. v109 risk-gates that axis and gets a narrow calibrated positive branch for Gemma-with-Llama `union_rank_top3` at 24/36 calibration problems, while Llama-with-Gemma remains unsafe/flat. v110 trains and thresholds on two source seeds, then deploys on the held-out seed; Gemma-with-Llama `pool_all` remains `+0.084` with 3/3 CI-positive held-out seeds. v111 permutes source utility labels and 0/200 placebo runs match the observed Gemma-with-Llama gains. v112 shows tie-safe simple heuristics do not match that raw gain: rank/prior heuristics no-op, and support/confidence tops out at `+0.054`. v113 shows explicit source-regression budgets favor the learned router frontier when problem overlap is allowed: source budget 2 reaches `+0.119` with 3 held-out regressions. v114 removes source rows whose problem ids appear in the held-out seed; learned-router recovery stays positive (`+0.097` at budget 0, `+0.118` at budget 2), but held-out regressions jump to `20`/`30`, so problem-disjoint calibration is not solved. v115 adds a same-feature candidate-correctness head and still gets no <=5-regression held-out row, so the easy two-head rescue is closed. v116 shows current scores have moderate recovery-vs-regression AUC around `0.70`, so there is signal but not enough tail separation for safe threshold transfer. v117 shows the current traces have no logprobs or hidden states, and v118 shows answer-shape/numeric features do not supply the missing guard signal. v119-v123 change the live-verifier route: pairwise baseline-vs-candidate adjudication recovers accepted auxiliary-router rows with much better regression behavior than full-cluster local verifier prompts; v121 source-selected model/rule calibration transfers with large accepted-row gain (`+0.368`) and one held-out regression; v122 maps that to natural held-out `+0.067` over `1776` trials while cutting raw-router regressions from `20` to `1`; and v123 shows the same machinery no-ops on the bad Llama-with-Gemma control direction. The next selector version should add family-aware uncertainty, higher-router-budget natural scoring, or use a genuinely new signal source such as process labels, regenerated telemetry, stronger symbolic equivalence, or more diverse generators.

## Clean Claim

The current contribution is a diagnostic and method target:

> Any-correct coverage can severely overstate usable test-time scaling. The missing object is not just a better final-answer vote, but a calibrated allocation policy over answer-cluster depth.

This claim is already supported by the trace audits. The unproven part is whether a real verifier can cheaply exploit the depth frontier.
