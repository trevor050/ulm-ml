# v80 Utility Override Selector

## Question

Can the v78 trained feature selector be made deployable by separating two decisions?

1. Rank the best non-baseline answer cluster.
2. Override `cluster_sum` only when a utility-trained gate predicts that the override is worth the false-regression risk.

This is the direct follow-up to v79, where one-dimensional margin calibration exposed shallow target-oracle signal but failed under source calibration.

## Implementation

`work/utility_override_selector.py` trains:

- a selector head from visible cluster features, reused from v78,
- a gate head over baseline/alternative probabilities, margin, rank, support, and score-difference features,
- weighted utility labels:
  - recovery: positive label, weight `1.0`,
  - baseline false regression: negative label, default weight `3.0`,
  - unhelpful override: negative label, default weight `0.5`.

The policy chooses a gate threshold on a source calibration split, includes an explicit no-op threshold, starts probability thresholds at `0.05` rather than `0.0`, and now forces no-op when the gate split contains too few recovery labels. That guardrail matters: an earlier balanced Gemma->Llama split had zero positive gate examples and a calibration set with no baseline-correct examples, which made threshold `0.0` look good in-source while overriding everything out-of-source.

## Source-Calibrated Cross-Model Result

Main reports:

- [unique-source cross-model report](utility_override_v80_unique_cross_model_report.md)
- [balanced-source cross-model report](utility_override_v80_balanced_cross_model_report.md)
- [unique Llama->Gemma policy](utility_override_v80_unique_llama_to_gemma.md)
- [unique Gemma->Llama policy](utility_override_v80_unique_gemma_to_llama.md)
- [balanced Llama->Gemma policy](utility_override_v80_balanced_llama_to_gemma.md)
- [balanced Gemma->Llama policy](utility_override_v80_balanced_gemma_to_llama.md)

Source-calibrated v80 is safe but not useful:

| train -> test | chosen threshold | threshold reason | test delta | recoveries | baseline regressions |
|---|---:|---|---:|---:|---:|
| Llama unique32 -> Gemma balanced | `0.250` | source calibration | `+0.000` | `0` | `0` |
| Gemma unique16 -> Llama balanced | `2.000` | source calibration no-op | `+0.000` | `0` | `0` |
| Llama balanced -> Gemma balanced | `0.500` | source calibration | `+0.000` | `0` | `0` |
| Gemma balanced -> Llama balanced | `2.000` | forced no-op, zero recovery labels | `+0.000` | `0` | `0` |

The deployed-mix reports are complete for both 72-packet balanced panels, preserve baselines, and pass no positive target or CI decision. This improves safety relative to the broken threshold-0 prototype, but it does not recover visible failures.

## Target-Oracle Diagnostic

Target-threshold sweeps show limited shallow headroom on Llama only:

| train -> test | oracle threshold | test delta | recoveries | baseline regressions | note |
|---|---:|---:|---:|---:|---|
| Gemma unique16 -> Llama balanced | `0.700` | `+0.042` | `4` | `1` | all recoveries are top5; no tail recovery |
| Gemma balanced -> Llama balanced | `0.050` | `+0.028` | `2` | `0` | top5 only |
| Llama unique32 -> Gemma balanced | `2.000` | `+0.000` | `0` | `0` | no positive target threshold |
| Llama balanced -> Gemma balanced | `2.000` | `+0.000` | `0` | `0` | no positive target threshold |

Diagnostic reports:

- [unique-source oracle report](utility_override_v80_oracle_unique_cross_model_report.md)
- [balanced-source oracle report](utility_override_v80_oracle_balanced_cross_model_report.md)

Even with target thresholds, the gains are shallow and statistically weak. The unique-source oracle Llama result has natural-rate deployed delta about `+0.037`, but the 95% CI still includes zero and the v71 tail targets fail. The balanced oracle result has point delta about `+0.036` at threshold `0.0`, also not a conservative pass.

## Interpretation

v80 adds value as a falsification and calibration result, not as a successful deployed method.

The feature-selector family can find some top5 alternatives, but the hard part is now clearer:

- top10/top20 tail recovery remains `0/12`,
- source threshold calibration is too data-starved and shift-sensitive,
- utility gates need enough positive recovery labels to be allowed to act,
- target-oracle headroom is small and Llama-sided, not a general cross-model win,
- no v80 configuration passes the lower-CI-positive deployed decision rule.

## Paper Consequence

Do not pitch a learned override selector as the current contribution.

Use v80 to say:

> After a negative local LLM verifier and a shallow trained-selector result, even a utility-trained two-head override policy cannot safely harvest the deployed-mix headroom under source calibration. The remaining bottleneck is transferable, regression-aware calibration under rare positive recovery labels, especially for deeper top10/top20 tails.

This strengthens the main paper framing: the research contribution is the diagnostic/regression-aware evaluation target plus adaptive depth, not a solved cheap selector.

## Next Experiment

Build a larger calibration-stability experiment over repeated source splits and pooled calibration:

- train the same selector/gate family over many problem-level splits,
- report active-vs-no-op threshold frequency,
- estimate calibration confidence intervals for recovery and false-regression rates,
- require a lower confidence bound on source utility before allowing active override,
- compare against target-oracle sweeps to separate absent signal from threshold-selection failure.

The goal is not a bigger model. The goal is to make calibration uncertainty explicit enough that an active override policy is only selected when it has enough recovery evidence to justify the regression risk.
