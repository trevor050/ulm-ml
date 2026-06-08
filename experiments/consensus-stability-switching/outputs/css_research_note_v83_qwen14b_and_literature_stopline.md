# v83 Qwen3:14B Verifier Smoke And Literature Stopline

**Date:** June 2, 2026

## Question

After v82 showed that cheap feature-gate overrides are stable but shallow, does a stronger local Ollama verifier change the story, and does current test-time-scaling literature leave a defensible novelty slice?

## New Measured Verifier Evidence

v83 adds qwen3:14b runs on the existing deployed-mix harness. The initial 12-packet smoke is still tiny, but the follow-up full-panel run is the real stopline: `72` deployed-mix prompts per dataset, `144` scored predictions total, using the v74 report path and the v45 CI decision rule.

Main reports:

- [qwen3:14b deployed-mix 12-packet smoke](qwen3_14b_deployed_mix_real_v83_slim_concise_percat1_report.md)
- [qwen3:14b answer-only recoverable-failure rerun](qwen3_14b_v83_recoverable_failures_answeronly_evidenceonly_report.md)
- [qwen3:14b thinking-mode recoverable-failure rerun](qwen3_14b_think_v83_recoverable_failures_answeronly_evidenceonly_report.md)
- [qwen3:14b full 144-prompt answer-only evidence-only report](qwen3_14b_v83_full144_answeronly_evidenceonly_report.md)

The deployed-mix smoke completed `12/12` packets: `6` MATH/Gemma and `6` MATH/Llama. It preserved both sampled `baseline_correct` rows, but recovered no visible recoverable cases:

| dataset | baseline-correct preserved | recoverable_top5 | recoverable_top10_only | recoverable_top20_only | v71 top20 tail positive |
|---|---:|---:|---:|---:|---|
| MATH/Gemma | `1/1` | `0/1` | `0/1` | `0/1` | False |
| MATH/Llama | `1/1` | `0/1` | `0/1` | `0/1` | False |

The confidence-threshold policy table is flat: every threshold has natural-rate deployed delta `+0.000` with lower-CI-positive decision false. This is not evidence of improvement; it is a preservation-only smoke.

The full 144-prompt answer-only evidence-only run is stronger and more damning. It completes both full deployed-mix panels, but raw recovery is tiny and baseline regressions dominate:

| dataset | coverage | baseline_correct | recoverable_top5 | recoverable_top10_only | recoverable_top20_only | best threshold read |
|---|---:|---:|---:|---:|---:|---|
| MATH/Gemma | `72/72` | `5/12` preserved | `0/12` | `0/12` | `1/12` | all CI decisions negative; best delta `-0.075` at threshold `0.90` |
| MATH/Llama | `72/72` | `8/12` preserved | `1/12` | `0/12` | `0/12` | no positive CI decision; best delta `+0.000` by abstaining at threshold `0.90` |

The v71 target check fails everywhere. With these baseline regressions, the full-panel target requires far more recoveries than qwen3:14b supplies: Llama observes `0/5` needed at top20 and `0/>12` top20-only; Gemma observes `0/7` uniform top20 and `1/>12` top20-only. Confidence fallback can reduce harm by abstaining, but it cannot turn the model into a positive deployed policy.

The answer-only evidence-only rerun isolates the six recoverable failures. It also recovers `0/6`:

| dataset | recoverable packets | correct | deployed delta at threshold 0 |
|---|---:|---:|---:|
| MATH/Gemma | `3` | `0` | `-0.299` |
| MATH/Llama | `3` | `0` | `-0.428` |

The thinking-mode rerun is worse operationally: several outputs are null/garbled, and it still recovers `0/6`. Treat this as interface-fit negative evidence, not as a useful verifier configuration.

## Interpretation

v75-v77 already showed that installed qwen3.5:9b and gemma4:26b were not enough under slim, rich, evidence-only, and answer-only prompting. v83 extends that negative result to qwen3:14b and then scales it from targeted smoke to full deployed-mix panel:

- bigger local qwen preserves trivial already-correct rows,
- it does not recover the targeted top5/top10/top20 visible failures,
- on the full panel it finds only `2/72` recoverable cases while regressing `11/24` already-correct baselines,
- answer-only and thinking variants do not rescue the failure,
- confidence fallback cannot create deployed gain when recovery is this weak and regression this high.

This matters because it kills the tempting "just pull a slightly stronger local model" story. The missing positive method result now needs either a substantially stronger measured verifier, more recovery calibration data, or a genuinely richer semantic scoring interface. Another shallow prompt tweak or feature gate is probably academic procrastination wearing a lab coat.

## Literature Pressure

Primary sources checked or rechecked:

- [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171): establishes majority/answer-consistency over sampled reasoning paths as a core repeated-sampling baseline.
- [Training Verifiers to Solve Math Word Problems](https://arxiv.org/abs/2110.14168): classic verifier-over-many-candidates setup; useful historical anchor, but not enough novelty by itself.
- [Scaling Test-Time Compute Without Verification or RL is Suboptimal](https://arxiv.org/abs/2502.12118): supports verification as important when traces are heterogeneous.
- [Scaling Flaws of Verifier-Guided Search in Mathematical Reasoning](https://arxiv.org/abs/2502.00271): warns that imperfect verifiers can misrank/prune valid reasoning as search scales.
- [When To Solve, When To Verify](https://arxiv.org/abs/2504.01005): makes solve-vs-verify budget a direct competing frame; practical budgets can favor more solution sampling over generative verification.
- [First Finish Search](https://arxiv.org/abs/2505.18149): pressures the pitch with a simple short-trace heuristic; v51 is the local answer.
- [Putting the Value Back in RL](https://arxiv.org/abs/2505.04842): co-training reasoners and verifiers is an adjacent stronger-verifier path, not something this lab has measured.
- [Reasoning on a Budget](https://arxiv.org/abs/2507.02076): makes adaptive/controllable test-time compute crowded; generic adaptive TTS is not novel.
- [Budget-aware Test-time Scaling via Discriminative Verification](https://arxiv.org/abs/2510.14913): budget-aware verifier hybrids are a live competitor; our claim must be cluster-depth-specific.
- [Seer Self-Consistency](https://arxiv.org/abs/2511.09345): dynamic self-consistency is the serious "sample smarter" baseline; v41-v44 must stay foregrounded.
- [DAJ](https://arxiv.org/abs/2601.22230): judge training has distribution-shift hazards, reinforcing deployed-mix, confidence fallback, and transfer/calibration reporting.
- [When More Thinking Hurts](https://arxiv.org/abs/2604.10739): supports the nonuniform-compute premise and warns against "more compute always helps" framing.

## Surviving Novelty Slice

The safe pitch is not:

> We introduce verifier-based test-time scaling.

That claim is cooked. The field is already full of verifier, dynamic sampling, budget, judge, and overthinking work.

The safe pitch is:

> Answer-cluster selectability is a missing diagnostic axis for repeated-sampling traces. It separates coverage-limited, surfaced, and depth-limited regimes. In depth-limited traces, the correct answer is already generated but buried below the selector frontier, so the right method target is costed cluster-depth routing with false-regression accounting.

This survives because the local package has evidence on all three pieces:

- **diagnostic:** canonical MATH N=128 gap and bootstrap CIs show large headroom.
- **regime map:** cross-trace and N-sweep audits distinguish hard MATH, GSM8K, and Pythia.
- **method target:** phase/cost/utility studies say when top5/top10/top20 verification is worth buying.

The negative results are now part of the moat:

- CSS/router switching is weak.
- learned cluster rankers and shallow consistency features do not close the gap.
- extra generation and short-trace proxies do not explain high-N MATH.
- qwen3.5:9b, gemma4:26b, and qwen3:14b local verifier smokes are negative.
- v78-v82 cheap-selector override families find shallow top5 signal but no deployable top10/top20 tail recovery.

## Claims To Soften In The Draft

Use "projected adaptive-depth frontier" unless a measured stronger verifier replaces the assumed success/regression rates.

Do not imply that local LLM verifier evidence supports recovery. Current local endpoint evidence is negative across qwen3.5:9b, gemma4:26b, and qwen3:14b.

Do not call top20 the default policy. v66-v69 say top20 is expensive tail spend; top10 is the ordinary high-N MATH choice under the current 80% success / 2% false-regression utility point.

Do not claim broad domain generalization. v58-v64 support a regime diagnostic over local traces, not a universal law.

Do not claim confidence calibration transfers. v55 and v78-v82 say final selection can be stable while calibration and override gates shift.

## Best Next Artifact

The next useful artifact is a reviewer-facing "measured verifier stopline" table that joins v75-v77 and v83:

| model/interface | prompt family | recoverable correct | baseline preservation | read |
|---|---|---:|---:|---|
| qwen3.5:9b | slim/rich/evidence-only/answer-only | `0/6` targeted failures | preserves sampled baselines in slim smoke | insufficient local verifier |
| gemma4:26b | answer-only evidence-only | `0/6` targeted failures | structurally unreliable | insufficient local verifier |
| qwen3:14b | deployed-mix slim concise | `0/6` visible recoverable buckets | `2/2` sampled baseline-correct rows | preservation-only, no gain |
| qwen3:14b | answer-only evidence-only targeted | `0/6` targeted failures | not applicable | no recovery |
| qwen3:14b | answer-only evidence-only full144 | `2/72` recoverable prompts | `13/24` baseline-correct preserved | weak raw signal, regression-heavy, CI-negative |

After that table, stop spending cycles on local qwen/gemma prompt variants unless the model class changes materially. The decisive route is a stronger measured verifier or richer semantic cluster scoring.
