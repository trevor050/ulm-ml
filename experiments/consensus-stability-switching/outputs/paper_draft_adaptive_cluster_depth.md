# Failure-Activated Adaptive Cluster-Depth Verification

**Draft:** June 1, 2026  
**Status:** current method-facing paper draft from the Cluster Selectability sprint.

## Abstract

Repeated sampling can produce a correct answer without producing a usable final prediction. On high-sample MATH traces from Monkey Business, answer-cluster oracle coverage is far above the accuracy of cheap deployed selectors: at `N=128`, MATH/Llama has `cluster_sum` accuracy around `0.448` while the cluster oracle is around `0.846-0.852`; MATH/Gemma has `cluster_sum` around `0.222-0.240` while the oracle is around `0.723-0.725`. Problem-bootstrap CIs over the canonical depth audit keep the headroom large: Llama `0.404 [0.309, 0.501]`, Gemma `0.492 [0.402, 0.582]`. A cross-trace companion audit keeps the scope honest: GSM8K/Llama is mostly surfaced (`headroom 0.145 [0.075, 0.226]`), while MATH/Pythia is coverage-limited (`oracle 0.303 [0.225, 0.383]`) but still has buried top20-recoverable headroom. The exact third decimal varies across the parser-sensitivity and deep-depth audits, so this draft treats the size and persistence of the gap as the claim, not a single canonical point estimate. We call this the cluster selectability gap.

The script-generated canonical table resolves the quote for depth claims: use MATH/Llama `0.448` vs `0.852` and MATH/Gemma `0.233` vs `0.725`, with selector-miss rank p50/p90 `6/21` and `8/33`. The bootstrap CI companion reports problem-resampling uncertainty: Llama headroom `0.404 [0.309, 0.501]`, Gemma headroom `0.492 [0.402, 0.582]`. The table also reports the small provenance drift relative to the multi-N selectability audit.

The cross-trace bootstrap should be used for scope language, not for replacing the MATH headline. It separates regimes: GSM8K/Llama is shallow/surfaced, MATH/Pythia is coverage-limited, and MATH/Llama/Gemma are the current depth-limited stress cases. A three-seed split/trial sweep keeps the same regime map.

An N-sweep phase diagram adds the dynamic picture. GSM8K/Llama becomes shallow/surfaced by `N=8`. MATH/Pythia remains coverage-limited through `N=128`. MATH/Llama and MATH/Gemma transition into depth-limited regimes around `N=32`, with headroom increasing to `0.414` and `0.508` at `N=128` on the single-seed run. A three-seed phase sweep keeps the high-N labels stable: MATH/Llama and MATH/Gemma are depth-limited at `N=64` and `N=128`, GSM8K/Llama is shallow/surfaced, and MATH/Pythia is coverage-limited. This suggests selectability should be reported as a phase diagnostic, not only as a single high-N endpoint.

The phase diagnostic also determines where verifier budget should be spent. v63's phase-aware triage audit marks MATH/Llama and MATH/Gemma as top-20 verifier-spend targets once they enter the depth-limited phase at `N=32`; GSM8K/Llama is a mostly-surfaced control, and MATH/Pythia remains a coverage-limited control. At `N=128`, projected top20 deltas under an 80% success / 2% false-regression assumption are `+0.261` for MATH/Llama and `+0.285` for MATH/Gemma, while the required verifier success to break even under 2% false regression is only `0.038` and `0.034`. v64's threshold-sensitivity audit over 81 plausible regime cutoffs keeps the high-N conclusion stable: Gemma is unanimously depth-limited at `N=64/128`, Llama is depth-limited under all `N=128` settings, and Pythia is unanimously coverage-limited. v65's verifier-quality sensitivity audit shows the spend call is not balanced on one optimistic assumption: at `N=128`, MATH/Llama and MATH/Gemma remain positive even at 50% verifier success and 5% false regression. v66's marginal-depth audit prevents a fixed-depth overclaim: GSM8K/Llama is shallow-control, MATH/Pythia is coverage-first, and high-N MATH keeps nontrivial top10-to-top20 marginal gain. v67 adds prompt-cost discipline: on MATH/Llama and MATH/Gemma, top5/top10 dominate marginal ROI, while top20 buys a real but expensive tail. v68 turns the tradeoff into a utility frontier: at 80% verifier success and 2% false regression, top10 is the ordinary high-N MATH operating point, and top20 beats top10 only when the value of +1.0 accuracy exceeds about `20k` tokens for Gemma or `35k` tokens for Llama. v69 sweeps verifier quality and keeps the qualitative policy shape: lower success shifts choices toward no-verifier or top10, while top20 remains a high-value tail choice. v70's live literature refresh narrows the paper against current adaptive-TTS, overthinking, dynamic self-consistency, and verifier-scaling work: the claim is answer-cluster phase diagnostics plus costed cluster-depth routing, not generic adaptive test-time scaling. v71 turns the missing verifier benchmark into finite-sample requirements: with one already-correct baseline regression in the current 12-prompt/category smoke set, point-positive top20 needs only uniform `2/12` Llama or `1/12` Gemma recoveries per recoverable bucket, but top20-only evidence needs `6/12` Llama or `4/12` Gemma tail recoveries. v72 checks those targets under source-unique pressure: recoverable top20 mass stays similar and Gemma unique16 remains a healthy tail check, but Llama unique-source top20-only buckets are sparse. v73 tries to enlarge that Llama tail bucket locally with a target-32, 96-trial, one-source run; it reaches `9` top20-only packets and `2` no-visible packets, so the current trace remains supply-limited for strong Llama tail-specific claims. v74 packages the scoring path into a one-command report that joins raw category scoring, v71 target checks, confidence fallback, natural-rate deployed deltas, and v45 CIs. v75 exercises a real local Ollama endpoint on the remote RTX box: qwen3.5:9b completes a 12-prompt slim deployed-mix smoke, preserves both sampled baseline-correct rows, but recovers `0/6` visible recoverable buckets. v76 reruns those six qwen failures with richer cluster evidence and evidence-only prompting, and both remain `0/6`. v77 removes the reason field and constrains output to answer/confidence only; qwen now formats cleanly but is still `0/6`, while gemma4:26b is also `0/6` and remains structurally unreliable. v78 then tests a trained feature-selector replacement path on the full deployed-mix panels: cross-model selectors recover `3/12` top5 failures in both directions, but recover `0/12` top10-only and top20-only tails, and no configuration passes the conservative lower-CI-positive rule. v79 converts that into a calibrated override test: source-calibrated thresholds choose no-op or transfer negative, while target-oracle thresholds expose shallow margin headroom (`+0.056` on Llama with `5/12` top5 recoveries) that calibration cannot yet harvest safely. v80 tests a two-head utility override gate with explicit recovery-vs-regression training. Source-calibrated policies are safe but flat, while target-oracle thresholds recover only shallow Llama top5 cases (`+0.042` unique-source and `+0.028` balanced) and still recover no top10/top20 tails. v81 makes the gate risk-controlled and still recovers no target failures under source calibration. v82 repeats v80/v81 over eight seeds and shows the cheap-gate failure is stable: active source gates occur in `23/64` deployable runs, `12/23` active gates recover zero target failures, and target-oracle top20-only recovery remains `0`. v83 tests the stronger local qwen path: qwen3:14b completes the full 144-prompt answer-only/evidence-only deployed-mix panel, but recovers only `2/72` recoverable prompts, preserves only `13/24` baseline-correct rows, and no confidence threshold passes the CI-positive rule. v84 tests the cleanest context-starvation objection: when the original problem and richer cluster evidence are included, qwen3:14b improves only to `4/72` recoverable prompts, preserves only `12/24` baseline-correct rows, recovers no top20-only tail failures, and remains CI-negative. This is a pre-verifier routing claim with a growing negative local-verifier family and a trained-selector calibration-shift follow-up, not an end-to-end positive result.

Naive selector switching and shallow cluster rankers do not close the gap. The harder failure mode is depth: on selector misses, the correct cluster is often buried beyond the first few answer clusters, with correct-rank p50/p90 of `6/21` for MATH/Llama and `8/33` for MATH/Gemma. We propose failure-activated adaptive cluster-depth verification: use cheap set-level features to detect unreliable default selections, then allocate a verifier budget over answer-cluster depth. A rank-bucket policy that predicts whether the recoverable cluster lies in top-5, top-10-only, top-20-only, or nowhere improves projected deployed accuracy under a token budget. In a three-seed sweep at about 1024 verifier tokens per problem, projected delta over `cluster_sum` is `+0.228 +/- 0.008` for MATH/Llama and `+0.194 +/- 0.024` for MATH/Gemma. v85 adds a cross-model transfer stress test for the allocation rule: at 1024 tokens/problem, Gemma-trained allocation on Llama reaches `0.652` versus Llama-within `0.659`, and Llama-trained allocation on Gemma reaches `0.432` versus Gemma-within `0.441`; both cross rows beat their fixed compact frontiers. v86 repeats that transfer check over verifier-quality assumptions and keeps harsh `50%` success / `5%` false-regression cross gaps small (`-0.006` Llama, `-0.005` Gemma). v87 then decouples train and target split seeds: the harsher cross-model/cross-seed rows still beat fixed compact frontiers at 1024 tokens/problem, with Gemma-trained-on-Llama `0.639` (`-0.019` versus within-same, `+0.018` versus fixed) and Llama-trained-on-Gemma `0.431` (`-0.010` versus within-same, `+0.036` versus fixed). v88 shows this is a budget-frontier result, not all-budget dominance. v89 turns the high-budget projection into an explicit quality contract: at 2% false regression, the 1024-token fixed-frontier rows need about 73% recovery success for Gemma-trained-on-Llama and 65% for Llama-trained-on-Gemma; transfer is mostly below the stricter target-calibrated within-same allocator and should not be claimed as beating target calibration. v90 scans a 2D quality grid and finds the best fixed-frontier pass fractions at 1024 tokens/problem: `0.422` for Gemma-trained-on-Llama and `0.565` for Llama-trained-on-Gemma. v91 bootstraps the six seed-pair rows and makes the transfer evidence asymmetric: Llama-trained-on-Gemma 1024 is `6/6` positive with CI `[+0.027,+0.044]`, while Gemma-trained-on-Llama 1024 is `5/6` positive with CI `[-0.006,+0.038]`. These are still projected verifier-success results. v92 adds a measured local math-specialized verifier boundary: `mathstral:7b` gets one rich answer-only Gemma top20-only recovery, but the signal disappears in the slim prompt, Llama remains negative with baseline regression, confidence can be invalid, and full rich expansion is CPU/tail-latency blocked. v95 adds a first-pass hashed semantic cluster scorer: raw recoveries appear, including Llama `6/36` recoverable rows for text-only and Gemma `5/36` for numeric, but preservation/calibration fail and no policy passes the CI-positive deployed rule. v96 then source-calibrates accept/fallback thresholds over 54 semantic policies; Gemma->Llama averages only `+0.003` deployed delta, Llama->Gemma averages `-0.025`, and no policy passes the CI-positive rule. v97 moves the valid side to lower-duplication Llama unique32 evaluation; best deployed delta is only `+0.014`, no policy passes the CI-positive rule, and the old Gemma unique16 packet JSONL is unusable. v98 rebuilds that Gemma unique-source target cleanly and runs 81 lower-duplication semantic-risk policies; the best point estimate is `+0.051` but regresses `3/30` already-correct Llama rows, while the best clean row is only `+0.035` with CI low `+0.000`. v99 target-thresholds the raw semantic scores and finds `4/81` lower-CI-positive oracle rows. v100 repeats the target-threshold audit under the same split-trained regime as v98 and finds `5/81` positive target-oracle rows, including `+0.065` with `7/36` recoveries. v101 varies source calibration size/composition over `72` scorer runs and `1080` source-threshold rows; zero source-calibrated rows pass the deployed CI rule, and problem-disjoint clean source rows are all no-op despite small target-oracle headroom. v102 allows labeled target-style calibration and still finds zero held-out CI-positive policies; the best clean packet-disjoint row is only `+0.024` with zero lower bound, and problem-disjoint clean rows are no-op. v103 expands the Gemma target panel to `48/category` and runs 756 Llama-to-Gemma rows; target-calibrated policies still never pass, the best clean calibrated row is only `+0.007` with zero lower bound, and only held-out oracle thresholding reaches `+0.034` with positive lower bound. v104 then gives the hashed scorer richer local text, including problem text, more representatives, longer rationales, larger hash space, and longer training; conservative target-calibrated behavior is unchanged. v105 adds a multifeature target-style accept/fallback gate; it also finds zero conservative calibrated passes. v106/v107 add cheap symbolic/answer-shape and representative-level process/proof-hygiene features, and still fail conservative calibration. v108 tests cross-generator agreement: Llama as auxiliary helps Gemma modestly, but Gemma hurts Llama and no positive no-regression policy appears. v109 risk-gates that auxiliary signal and gets the first narrow calibrated positive branch: Gemma-with-Llama `union_rank_top3` is `+0.102`/`+0.126` at 24/36 calibration problems with 3/3 CI-positive seeds, while Llama-with-Gemma remains unsafe or flat. v110 removes same-seed thresholding: fitting and thresholding on two source seeds still gives Gemma-with-Llama `pool_all` `+0.084` mean delta with 3/3 held-out seeds CI-positive, 152 recoveries, and 2 regressions. v111 permutes source utility labels 200 times and none match the observed Gemma-with-Llama deltas; `pool_all` placebo max is `+0.030` versus observed `+0.084`. v112 adds the tie-safe simple-heuristic control: rank/prior heuristics collapse to no-op, and the best support/confidence heuristics reach only `+0.054` versus v110 `+0.084`. v113 adds an overlap-allowed regression-budget frontier: learned source-budget 2 reaches `+0.119` with 3 held-out regressions, while the best <=5-regression heuristic reaches `+0.084`. v114 removes source rows whose problem ids appear in the held-out seed; learned rows stay positive (`+0.097` at budget 0, `+0.118` at budget 2), but held-out regressions rise to `20`/`30`, so the auxiliary-generator result is recovery signal and not yet safe problem-disjoint calibration. v115 adds a same-feature candidate-correctness head and still finds no <=5-regression held-out row. v116 shows the same scores have moderate recovery-vs-regression AUC around `0.70`, but not enough tail separation for safe threshold transfer. This is calibration/policy headroom using an extra generator trace, not deployable verifier evidence. The missing benchmark is therefore a reproducible stronger verifier run on the prepared compact/full prompt assets, materially richer labels/features, stronger risk control, or a more general regression-calibrated generator-choice router with new signals.

## 1. Motivation

The optimistic version of test-time scaling says: sample many candidates, then choose the good one. This hides two separable events:

```text
coverage:  a correct candidate exists
selection: the deployed selector surfaces it
```

Any-correct coverage is not a deployed metric. A method can generate a correct answer cluster and still fail because self-consistency, verifier-mass aggregation, or a shallow ranker chooses a louder wrong cluster.

The initial idea in this sprint was Consensus-Stability Switching: choose between candidate selectors based on set-level stability. That idea did not become a standalone winner. The durable result is sharper:

```text
The missing object is not just a better final-answer vote.
It is a calibrated allocation policy over answer-cluster depth.
```

## 2. Definitions

For each problem, sample `N` candidate solutions. Extract a final answer from each candidate and group candidates into answer clusters.

```text
G_a = { candidate i : final_answer_i = a }
```

The cheap default selector used in most later experiments is `cluster_sum`:

```text
cluster_sum(a) = sum verifier_score(candidate_i) for i in G_a
```

Important quantities:

- `any_correct`: at least one sampled candidate is correct.
- `cluster_sum`: the selected answer cluster by aggregate cheap verifier score.
- `cluster_oracle`: whether any answer cluster contains a correct candidate.
- `top-k cluster oracle`: whether a correct answer cluster appears within the top k clusters ranked by `cluster_sum`.
- `recoverable_depth_k`: `cluster_sum` is wrong and a correct cluster appears within depth `k`.

## 3. Empirical Starting Point

The original selector-switching result is weak:

| dataset | first | self-consistency | CSS/router | any-correct |
|---|---:|---:|---:|---:|
| GSM8K/Llama | 0.777 | 0.846 | 0.849 | 0.973 |
| MATH/Llama | 0.295 | 0.398 | 0.403 | 0.691 |
| MATH/Gemma | 0.102 | 0.181 | 0.177 | 0.481 |
| MATH/Pythia | 0.010 | 0.012 | 0.012 | 0.150 |

The canonical high-N parser-v2 depth table keeps the main gap alive:

| dataset | `cluster_sum` | cluster oracle | top-5 oracle | top-10 oracle | top-20 oracle |
|---|---:|---:|---:|---:|---:|
| MATH/Llama N=128 | 0.448 | 0.852 | 0.648 | 0.748 | 0.809 |
| MATH/Gemma N=128 | 0.233 | 0.725 | 0.411 | 0.536 | 0.635 |

The same bootstrap/depth audit across all local traces shows why the paper should be framed as a diagnostic:

| dataset | `cluster_sum` | oracle | headroom | miss rank p50/p90 |
|---|---:|---:|---:|---:|
| MATH/Llama N=128 | 0.448 | 0.852 | 0.404 | 6 / 21 |
| MATH/Gemma N=128 | 0.233 | 0.725 | 0.492 | 8 / 33 |
| GSM8K/Llama N=128 | 0.854 | 0.999 | 0.145 | 2 / 5 |
| MATH/Pythia N=128 | 0.046 | 0.303 | 0.257 | 8 / 27 |

A separate parser-sensitivity rerun reports slightly different point estimates for the same qualitative result: Llama `0.448` vs `0.846`, Gemma `0.222` vs `0.723`. This is not a contradiction to paper over; it is a warning to quote audit provenance whenever using third-decimal numbers.

See `outputs/canonical_selectability_depth_table.md` for the single citation target and the parser/trial-sensitivity note explaining nearby older values.

Correct clusters are not merely second-place mistakes:

| dataset | miss-rank p50 | miss-rank p75 | miss-rank p90 |
|---|---:|---:|---:|
| MATH/Llama N=128 | 6 | 11 | 21 |
| MATH/Gemma N=128 | 8 | 16 | 33 |

This motivates adaptive depth instead of fixed top-2/top-3 reranking.

## 4. Negative Results That Shape the Method

Several simpler solutions fail.

First, learned cluster rankers over support, score mass, score moments, candidate text features, and shallow rationale signatures roughly match or trail `cluster_sum`.

Second, hard-packet rescue selectors work only under conditioning. On packets where `cluster_sum` is known wrong and a correct cluster is visible, shallow learned selectors can perform well, but always-on deployment regresses many examples where `cluster_sum` was already correct.

Third, detector search is only partly robust. A detector zoo improved a single-seed deployed frontier, but a three-seed sweep left only a modest Llama gain and no reliable Gemma gain.

These failures are useful. They imply that a real method must:

- preserve the cheap selector when it is probably right,
- price verifier invocation under regression risk,
- inspect enough cluster depth for hard MATH cases,
- report token budget, not only accuracy.

## 5. Failure-Activated Adaptive Depth

The proposed method has four stages:

```text
1. Run repeated sampling and group candidates by final answer.
2. Select a default answer with cluster_sum.
3. Use set-level uncertainty features to estimate recoverability depth.
4. Spend verifier budget on a selected depth: skip, top-5, top-10, or top-20.
```

Features are cheap set summaries:

- top support and support margin,
- score-mass margin,
- selected-score mass fraction,
- number of answer clusters,
- answer entropy,
- score/support dispersion.

The important target is not only "is the default wrong?" but:

```text
If the default is wrong, how deep must we inspect before a correct cluster appears?
```

## 6. Verifier Prompt Assets And Evidence Budget

Verifier-ready prompt assets exist for strict top-10/top-20 and buried rank-stratified cases. The most important current sets are diverse one-packet-per-source top-20 rank11-20 prompts:

| dataset | packets | unique source problems | correct rank median | cheap selector accuracy |
|---|---:|---:|---:|---:|
| MATH/Llama top20 diverse | 27 | 27 | 13 | near 0 |
| MATH/Gemma top20 diverse | 40 | 40 | 13.5 | near 0 |

Compact prompts preserve all 20 answer clusters while showing one truncated rationale per cluster. They cut prompt size roughly in half:

| dataset | full avg chars | compact avg chars | ultracompact avg chars |
|---|---:|---:|---:|
| MATH/Llama top20 diverse | 18446 | 9475 | 7580 |
| MATH/Gemma top20 diverse | 17017 | 9064 | 7522 |

Compact evidence is usually not starved. The top representative from a correct cluster is trace-correct in `0.926` of Llama diverse packets and `0.900` of Gemma diverse packets. Full two-representative packets reach `1.000` and `0.975`.

Under a conservative 80% verifier-success / 2% false-regression assumption at 20% invoke, moving from full to compact top-20 evidence only slightly lowers projected accuracy:

```text
MATH/Llama: 0.546 -> 0.539
MATH/Gemma: 0.340 -> 0.332
```

This supports compact-first verification, with full prompts reserved for failures or uncertainty.

This does not by itself measure deployed false-regression. The diverse buried sets are conditioned on hard recoverable misses; the missing verifier benchmark also needs ordinary false/unhelpful invocations where `cluster_sum` was already right or no visible correct cluster exists.

## 7. Cost-Aware Depth Frontier

The method should be evaluated as an accuracy-vs-token frontier.

At 20% invoke, compact-only top-20 verification costs about:

```text
MATH/Llama: 475 estimated verifier tokens/problem
MATH/Gemma: 454 estimated verifier tokens/problem
```

Full-only top-20 costs about:

```text
MATH/Llama: 924 tokens/problem
MATH/Gemma: 853 tokens/problem
```

An oracle evidence-gap cascade nearly matches full-only projected accuracy at much lower cost:

```text
MATH/Llama: 516 tokens/problem
MATH/Gemma: 496 tokens/problem
```

But top-20 is not always the best budget choice. In the iso-budget frontier, shallow compact depths dominate low-budget regions:

| dataset | low-budget compact row | high-accuracy compact row |
|---|---|---|
| MATH/Llama | top-5, 20% invoke: 0.508 at 128 tokens/problem | top-20, 50% invoke: 0.653 at 1184 tokens/problem |
| MATH/Gemma | top-5, 10% invoke: 0.264 at 65 tokens/problem | top-20, 50% invoke: 0.443 at 1133 tokens/problem |

This reframes adaptive depth as budget allocation, not "always inspect top-20."

## 8. Budgeted Depth Policies

### Independent Depth Detectors

A first learned variable-depth policy trained separate detectors for top-5, top-10, and top-20 recoverability, then greedily bought the highest expected utility per token.

This was not good enough. It helped slightly at low budgets but lost to fixed compact frontier rows at higher budgets because it mostly bought top-5 and almost never bought top-20.

The oracle policy showed the idea was not dead:

```text
MATH/Llama oracle variable-depth: 0.746
MATH/Gemma oracle variable-depth: 0.556
```

So the bottleneck was depth-value prediction.

### Rank-Bucket Depth Policy

The improved policy predicts a minimal recoverability bucket:

```text
top5
top10_only
top20_only
none
```

Then it prices each action by cumulative bucket probability:

```text
P(recoverable by top5)  = P(top5)
P(recoverable by top10) = P(top5) + P(top10_only)
P(recoverable by top20) = P(top5) + P(top10_only) + P(top20_only)
```

At 1024 verifier tokens/problem, the rank-bucket policy beats both the old learned policy and the fixed compact frontier:

| dataset | rank-bucket policy | old learned policy | fixed compact frontier |
|---|---:|---:|---:|
| MATH/Llama | 0.684 | 0.611 | 0.621 |
| MATH/Gemma | 0.465 | 0.371 | 0.395 |

Those numbers are the single v32 split. They are useful for method shape, but robustness should be quoted from the v33 seed sweep below. The policy still trails oracle allocation, but it is the first learned allocation result that makes adaptive depth look like a plausible method rather than only a diagnostic.

## 9. Robustness

A three-seed sweep reruns the rank-bucket policy across train/calibration/test splits. At the two most relevant budgets:

| dataset | budget | acc mean | acc std | delta mean over cluster_sum | delta std | depth mix |
|---|---:|---:|---:|---:|---:|---|
| MATH/Llama | 512 | 0.590 | 0.027 | +0.159 | 0.012 | 5:0.20, 10:0.37, 20:0.00 |
| MATH/Llama | 1024 | 0.659 | 0.021 | +0.228 | 0.008 | 5:0.25, 10:0.55, 20:0.12 |
| MATH/Gemma | 512 | 0.368 | 0.013 | +0.120 | 0.020 | 5:0.10, 10:0.40, 20:0.00 |
| MATH/Gemma | 1024 | 0.441 | 0.017 | +0.194 | 0.024 | 5:0.12, 10:0.63, 20:0.11 |

A separate three-seed cross-model stress test trains the bucket predictor on one MATH generator trace and applies it to the other. This isolates transfer of the depth-allocation mapping, because target rows still use the target trace's own candidate scores and labels.

| train | target | budget | projected acc | delta | gap vs within | fixed compact |
|---|---|---:|---:|---:|---:|---:|
| MATH/Gemma | MATH/Llama | 1024 | 0.652 | +0.221 | -0.007 | 0.621 |
| MATH/Llama | MATH/Gemma | 1024 | 0.432 | +0.185 | -0.009 | 0.395 |

This is encouraging but narrow. It says the projected allocation rule is not obviously one-model calibration; it does not supply measured verifier success or false-regression rates.

The cross-model result is also not tied to a single verifier-quality point:

| quality | train | target | projected acc | delta | gap vs within |
|---|---|---:|---:|---:|---:|
| 50% success / 5% false regression | MATH/Gemma | MATH/Llama | 0.548 | +0.117 | -0.006 |
| 50% success / 5% false regression | MATH/Llama | MATH/Gemma | 0.343 | +0.096 | -0.005 |
| 80% success / 2% false regression | MATH/Gemma | MATH/Llama | 0.652 | +0.221 | -0.007 |
| 80% success / 2% false regression | MATH/Llama | MATH/Gemma | 0.432 | +0.185 | -0.009 |
| 100% success / 0% false regression | MATH/Gemma | MATH/Llama | 0.726 | +0.295 | +0.001 |
| 100% success / 0% false regression | MATH/Llama | MATH/Gemma | 0.494 | +0.247 | -0.012 |

v87 breaks the same-seed coupling by training every source model/seed against every target model/seed. At 1024 tokens/problem:

| train | target | split relation | projected acc | delta | gap vs within-same | gap vs fixed |
|---|---|---|---:|---:|---:|---:|
| MATH/Gemma | MATH/Llama | cross-model/cross-seed | 0.639 | +0.209 | -0.019 | +0.018 |
| MATH/Llama | MATH/Gemma | cross-model/cross-seed | 0.431 | +0.184 | -0.010 | +0.036 |

The v88 budget map makes the high-budget qualifier explicit. Gemma-trained allocation on Llama beats fixed compact only at `1024` tokens/problem; at `512` it is still `-0.044` below fixed compact. Llama-trained allocation on Gemma beats fixed compact at all tested budgets, with the largest margin at `1024`.

v89 solves the verifier-quality contract behind those transferred rows. Against fixed compact at `2%` false regression, the 1024-token rows require about `0.734` recovery success for Gemma-trained-on-Llama and `0.651` for Llama-trained-on-Gemma. Lower-budget Gemma-trained-on-Llama rows need roughly `0.977-1.063` recovery success at the same false-regression rate, so they are not credible claim rows. Against the stricter target-calibrated within-model/same-seed allocator, transfer is mostly negative; Gemma-trained-on-Llama loses at every tested budget, and Llama-trained-on-Gemma is positive only at 128 and 256 tokens/problem. This locks the wording: portable allocation is a fixed-frontier budget claim with an explicit success/regression target, not a target-calibrated transfer superiority claim.

v90 expands that point estimate into a quality-region map over success `0.50..1.00` and false regression `0.00..0.10`. The best fixed-frontier region for Gemma-trained-on-Llama is still 1024 tokens/problem, passing `0.422` of grid points; lower budgets are tiny or dead. Llama-trained-on-Gemma is broader, with the 1024-token row passing `0.565` of grid points. The within-same regions are smaller, again warning against target-calibrated transfer claims.

v91 checks the six train-seed/target-seed pairs directly. The Llama-trained-on-Gemma 1024-token fixed-frontier gap is positive on all six pairs, with pair-bootstrap CI `[+0.027,+0.044]`. The Gemma-trained-on-Llama 1024-token row is positive on five of six pairs, but its CI crosses zero (`[-0.006,+0.038]`). The safe transfer claim is therefore asymmetric: Llama-to-Gemma is the stable portable fixed-frontier result; Gemma-to-Llama is promising but lower-bound fragile under the current six-pair audit.

The high-budget improvement survives this small robustness check. The stable shape is also informative: most invoked examples use top-10, while top-20 is reserved for about `0.11-0.12` of all trials at the high budget.

The mean accuracies are lower than the flattering single-split v32 row (`0.684` Llama, `0.465` Gemma), but the deltas over each split's own `cluster_sum` baseline remain positive. That is the right robustness claim.

## 10. What Is Still Unproven

The central limitation is that most deployed-policy rows assume verifier behavior:

```text
80% success on recoverable invocations
2% false regression on false/unhelpful invocations
```

That is a sensitivity model, not a measured result.

The project already has:

- compact and full verifier prompt assets,
- rank-stratified buried prompt sets,
- balanced deployed-mix top-20 prompt assets with already-correct defaults, recoverable depths, and unhelpful invocations,
- answer keys,
- external/OpenAI-compatible verifier runner,
- compact/full cascade scorer.

The missing benchmark is to run a reproducible external/local verifier on the depth-limited MATH compact top-20 sets first, rerun full prompts on failures or uncertain cases, and feed measured success/regression/fallback rates back into the frontier. GSM8K/Llama and MATH/Pythia should be included as phase controls rather than blended into one aggregate.

For this benchmark to answer the reviewer objection, it cannot score only rank11-20 buried packets. It also needs a deployed mix that includes false invocations and already-correct defaults, because the method lives or dies on regression accounting under a fixed token budget.

Those deployed-mix assets now exist: 72 compact top-20 prompts each for MATH/Llama and MATH/Gemma, balanced across `baseline_correct`, `recoverable_top5`, `recoverable_top10_only`, `recoverable_top20_only`, `no_visible_top20`, and `no_correct_generated`. They are described in `outputs/css_research_note_v37_deployed_mix_verifier_assets.md`.

The deployed-mix rates also give a break-even equation:

```text
delta = recoverable_rate(depth k) * recovery_success
        - baseline_correct_rate * false_regression
```

At `98%` preservation of already-correct defaults, the recovery success needed to break even is low: Llama needs only `0.040/0.027/0.022` for top-5/top-10/top-20; Gemma needs `0.038/0.023/0.017`. These thresholds are not verifier results, but they specify what the external verifier run must measure.

The deployed-mix scorer now evaluates that external run as a policy, not only as raw accuracy. It sweeps confidence thresholds where low-confidence predictions fall back to the baseline answer, then reports natural-rate weighted `deployed_delta` rows for MATH/Llama and MATH/Gemma. A synthetic smoke run validates the scorer plumbing, but it is not benchmark evidence.

The deployed-mix statistical decision rule is also pre-specified: bootstrap within each dataset/category stratum, recompute natural-rate weighted `deployed_delta`, and call the policy positive only if the lower 95% bootstrap confidence bound is above zero. This prevents the external verifier result from becoming a threshold-cherry-picking exercise after the fact.

A power simulation clarifies how to use the current deployed-mix assets. The existing `72` prompts per model are sufficient as a smoke benchmark for weak-or-better verifier effects: with `12` packets/category, the v45 pass rate is `0.842` for Llama and `0.925` for Gemma under the weak scenario. They are not enough to certify tiny marginal effects near break-even: at expected deltas of only `+0.016` to `+0.018`, even `96` packets/category stays below `0.65` pass rate. The benchmark should therefore be two-stage: run the current set first, then scale the packet set only if the measured point estimate is marginal.

A representativeness audit gives the matching scope caveat. The current deployed-mix assets are category-balanced and cap duplication at `2` packets/problem, but cover only `38` unique Llama source problems and `37` unique Gemma source problems, with `27` shared across both models. They are smoke assets, not broad generalization evidence.

A lower-duplication alternative now exists, with a v98 clean rebuild for Gemma after the old unique16 packet JSONL proved unusable for packet-level scoring. Rebuilding with one packet per source yields `79` Llama prompts and `96` rebuilt Gemma prompts. The rebuilt Gemma set fills all `16` packets/category; Llama fills the common categories but only reaches `8` `recoverable_top20_only` and `7` `no_visible_top20` prompts. This exposes a real tradeoff in the 128-problem trace: category balance and source uniqueness cannot both be perfect for Llama rare categories.

## 11. More Samples Baseline

A reviewer will reasonably ask why the verifier budget should not be spent on additional samples. The extended generation-only audit answers the narrow version of that objection: on these traces, more samples mostly increase latent coverage while barely improving the deployed `cluster_sum` selector.

| dataset | N=128 `cluster_sum` | N=1024 `cluster_sum` | deployed delta | N=128 any-correct | N=1024 any-correct | extra sample tokens/problem |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.457 | 0.466 | +0.009 | 0.858 | 0.946 | 114374 |
| MATH/Gemma | 0.242 | 0.271 | +0.029 | 0.725 | 0.894 | 126364 |

At the first doubling after the base point, N=128 to N=256 costs roughly `16031` extra sample tokens/problem for Llama and `17220` for Gemma, while `cluster_sum` changes by only `-0.002` and `+0.002`. By contrast, the rank-bucket policy at `1024` verifier tokens/problem projects `+0.228 +/- 0.008` and `+0.194 +/- 0.024` over `cluster_sum`.

This is not an end-to-end measured verifier comparison. It is evidence for the narrower claim that generation-only scaling does not remove the selectability bottleneck under the current selector.

A dynamic extra-sampling proxy strengthens that objection check. Starting at N=128, it allocates extra 128-sample chunks by early answer entropy, low cluster-score margin, or low top-cluster score share. On MATH/Llama, uncertainty-targeted extra generation raises any-correct by up to `+0.095` but leaves `cluster_sum` at `+0.000` even at roughly `114k` extra sample tokens/problem. On MATH/Gemma, the best dynamic rows improve `cluster_sum` only `+0.027` to `+0.041`, while any-correct rises as much as `+0.149`. This is still a trace-prefix proxy, but it is a harder generation-only baseline than fixed N.

At the verifier-scale budgets used by the rank-bucket frontier, the comparison is sharper. With only `512-1024` extra tokens/problem, dynamic generation cannot buy many additional traces. The best non-oracle dynamic generation row has Llama `+0.000` `cluster_sum` delta at both 512 and 1024 tokens, and Gemma `+0.027`; the projected rank-bucket verifier deltas at the same budgets are Llama `+0.159/+0.228` and Gemma `+0.120/+0.194`. These verifier numbers are still projected, but the generation baseline is now token-matched.

The small-chunk version of this check gives dynamic generation a fairer allocation granularity. With 8-sample chunks, best non-oracle dynamic generation still has `+0.000` `cluster_sum` delta for both Llama and Gemma at 512/1024 token budgets. This removes one easy objection to the coarse 128-sample chunk baseline.

A three-seed sweep of the fine-grained dynamic baseline keeps the conclusion. Mean best non-oracle generation delta at 512/1024 tokens is Llama `+0.000/+0.000` and Gemma `+0.000/+0.005`, while the v33 rank-bucket verifier projection is Llama `+0.159/+0.228` and Gemma `+0.120/+0.194`. The verifier result still needs measurement; the generation-side objection is now much less hand-wavy.

First-finish style heuristics are another simple test-time scaling objection. On the completed MATH traces, choosing the shortest completion or the answer cluster with the shortest member is much worse than `cluster_sum`: at `N=128`, shortest-cluster reaches only Llama `0.264` and Gemma `0.104`. A length-weighted cluster score approximately ties `cluster_sum` (`0.452` vs `0.454` on Llama, `0.244` vs `0.243` on Gemma), but does not improve it. This is only a completed-trace proxy for online First Finish Search, but it shows that short traces do not explain away the selectability gap here.

A cheap cross-model verifier-transfer stress test addresses a narrower scorer-shift objection. Training the sample-level text-feature scorer on Gemma and evaluating Llama gives `cluster_sum 0.445`, `+0.010` versus the Llama-trained scorer; training on Llama and evaluating Gemma gives `0.238`, `+0.002` versus the Gemma-trained scorer. A three-seed sweep keeps the cross gaps near zero: Gemma-trained on Llama averages `+0.005 +/- 0.005`, and Llama-trained on Gemma averages `+0.000 +/- 0.005`. A cross-task MATH/GSM8K sweep is slightly less portable at the candidate level: MATH-trained scorer on GSM8K drops candidate AUC by `-0.120`, though final `cluster_sum` drops only `-0.009`. The resulting calibration audit makes the boundary explicit: selection transfer is more stable than confidence transfer. This is not an external verifier result, but it suggests the measured depth gap is not merely a scorer memorizing one model's trace style, and it says confidence calibration should be remeasured under task shift.

## 12. Evaluation Checklist

A serious paper should report:

- `cluster_sum` accuracy,
- any-correct / cluster-oracle coverage,
- top-k depth oracle curves,
- answer extraction and equivalence audit,
- detector AUC and capture at fixed invoke rates,
- compact/full prompt token cost,
- measured verifier accuracy on rank-stratified packets,
- generation-only scaling under the same budget/accounting convention,
- short-trace / early-finish selection baselines when trace lengths are available,
- scorer transfer across trace models/tasks,
- scorer calibration transfer across trace models/tasks,
- false-invocation regression rate,
- baseline-preservation rate on already-correct deployed-mix packets,
- recovery accuracy by deployed-mix depth category,
- confidence-triggered full-prompt fallback rate,
- stratified confidence interval for natural-rate weighted deployed delta,
- power or sample-size analysis for the deployed-mix decision rule,
- source-problem coverage and duplication for verifier packet sets,
- deployed accuracy under a fixed verifier-token budget,
- seed/split robustness for learned allocation.

## 13. Related Work Positioning

This work is adjacent to self-consistency, repeated-sampling scaling, self-calibrated adaptive sampling, discriminative verification, verifier-guided search, and multi-verifier scaling. The difference is the allocation unit.

Most related work asks:

```text
How many samples should we generate?
Which candidate should a verifier score?
How should multiple verifiers vote?
```

This draft asks:

```text
Given a set of sampled answers, how deep into the answer-cluster frontier should we spend verifier compute?
```

That framing makes the cluster selectability gap visible and forces deployed evaluation to account for both selection depth and token budget.

More specifically:

- Self-consistency and repeated-sampling scaling establish the coverage side of the story, but majority/reward-model selectors can plateau even when any-sample coverage keeps growing.
- Self-calibration and confidence-aware sampling allocate more or fewer generations by problem difficulty; adaptive cluster-depth verification allocates semantic inspection depth after the sample set exists.
- Budget-aware discriminative verification and GenRM budget studies ask how much compute should go to solution generation versus verification; this method asks how verification compute should be spent over the answer-cluster frontier.
- Multi-verifier scaling treats verifier diversity as the scaling axis; this method is compatible with that, but first asks which answer clusters the verifier ensemble should see.
- Verifier-guided search failure analyses are a warning: if an imperfect verifier prunes or misranks early, more search can amplify mistakes. The cluster-depth framing preserves the sampled frontier and measures the depth needed to recover from cheap selector failures.

## 14. Limitations

- The strongest learned-policy results are still projected verifier-success results.
- The generation-vs-verification budget ablation uses sample-character token estimates and projected verifier gains; a paper-quality comparison needs one measured tokenizer/endpoint.
- A reproducible local verifier family has now been completed, but the full-cluster version is negative: qwen3.5:9b on the v75 slim deployed-mix panel preserves sampled baselines and recovers none of the visible recoverable buckets; v76 rich/evidence-only reruns remain `0/6`; v77 answer-only qwen fixes formatting but remains `0/6`, and gemma4:26b is also `0/6`. v83 adds qwen3:14b: targeted recoverable reruns remain `0/6`, and the full 144-prompt deployed-mix panel recovers only `2/72` recoverable prompts while regressing `11/24` baseline-correct rows. v78 shows a trained feature selector can recover some top5 failures, but it still misses top10/top20 tails and does not pass the conservative CI gate. v79 shows simple source-calibrated margin override is not enough: target-oracle thresholds reveal shallow signal, but deployable threshold selection remains unsolved. v80/v81 show utility-gated and risk-controlled overrides are still insufficient. v82 repeats those policies over eight source split seeds and finds stable shallow failure: active source gates often fail to recover target examples, target-oracle gains are shallow, and top20 tail recovery is absent. v95 shows a richer hashed semantic scorer has raw recovery signal, including some top10/top20 deployed-mix hits, but still fails preservation/calibration and the lower-CI-positive deployed rule. v96 tests source-calibrated thresholds for that semantic scorer and still finds no CI-positive policy. v97 keeps the valid lower-duplication Llama side negative and exposes a Gemma unique16 packet artifact hazard. v98 rebuilds Gemma unique16 cleanly and still finds zero CI-positive source-calibrated policies over 81 lower-duplication semantic-risk rows. v99/v100 show target-side oracle thresholds can make raw and split-trained semantic rows CI-positive, so the remaining semantic-scorer problem is calibration/data, not total lack of signal. v101 tests the obvious calibration-size/composition rescue and still finds zero source-calibrated CI-positive policies. v102 tests small labeled target-style calibration splits and still finds zero held-out CI-positive policies. v103 expands target-style calibration and still finds zero conservative held-out threshold policies; best calibrated movement is tiny, while oracle headroom remains diagnostic only. v104 adds richer local hashed problem/rationale evidence and still fails conservative target calibration. v105 adds a multifeature target-style gate and still fails the conservative held-out rule. v106/v107 add cheap symbolic and representative-level process features and still fail conservative calibration. v108 shows cross-generator agreement is asymmetric; v109 calibrates it into a narrow positive Gemma-with-Llama routing branch; v110 shows that branch transfers across held-out seeds; v111 rules out an easy source-label placebo explanation; v112 shows tie-safe simple heuristics trail the learned router; v113 keeps learned routing ahead under overlap-allowed source-regression budgets; v114 shows problem-disjoint calibration keeps recovery signal but loses low-regression control; v115 shows a same-feature correctness head does not fix that control problem; v116 localizes the reason to moderate but insufficient recovery/regression separability; v117 rules out hidden local decoder telemetry; and v118 shows answer-shape features do not supply the missing guard. v119-v123 are the live exceptions worth scaling: pairwise baseline-vs-candidate adjudication on accepted router rows gives positive recovery/regression tradeoffs, v121 source-selected model/rule calibration transfers with `+0.368` accepted-row delta, v122 converts that to natural held-out `+0.067` with regressions reduced from `20` to `1`, and v123 no-ops on the bad reverse direction. A positive end-to-end claim still needs source/family-aware uncertainty, higher-router-budget stress, and ideally a stronger verifier endpoint.
- Phase-aware verifier triage is still computed from trace labels and assumed verifier success/regression rates; it chooses where to run the real verifier, but does not replace that run.
- Verifier-quality sensitivity sweeps the assumption space, but still uses projected trace-label recoverability rather than measured semantic-verifier behavior.
- The cheap verifier and set-level features are intentionally lightweight; stronger process/verifier features could change the frontier.
- MATH answer extraction and symbolic equivalence remain imperfect.
- Trace correctness labels can create visibility hazards; verifier failures must be separated from missing/equivalent answer labels.
- The manual/in-thread verifier panels are useful prompt-readability tests, not independent benchmarks.
- Seed sweeps are small and should be expanded if this becomes a real submission.

## 15. Falsification Conditions

The method should be downgraded if:

1. external verifier accuracy collapses on compact rank-stratified buried packets,
2. full-prompt reruns do not rescue compact failures,
3. verifier confidence cannot trigger full-prompt fallback efficiently,
4. false-invocation regressions erase the projected gains,
5. rank-bucket allocation loses its advantage with measured verifier rates,
6. parser/equivalence improvements remove much of the cluster selectability gap.
7. generation-only scaling with a stronger deployed selector dominates measured adaptive-depth verification at matched cost.

## 16. Conclusion

The original CSS/router idea is not the contribution. The contribution is a measurement and method target:

> Any-correct coverage can severely overstate usable test-time scaling. The missing object is a budgeted allocation policy over answer-cluster depth.

The current best method hypothesis is rank-bucket adaptive depth:

```text
Predict where a recoverable correct cluster is likely buried,
then spend compact verifier budget at the cheapest useful depth.
```

The evidence is now stronger than a single flattering projection: the rank-bucket policy beats fixed compact rows at high budgets and survives seed, cross-model, verifier-quality, and decoupled split-seed stress. The decisive next result is a measured external verifier run.
