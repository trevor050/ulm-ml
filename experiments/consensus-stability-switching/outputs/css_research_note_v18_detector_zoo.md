# Cluster Selectability v18: Failure-Detector Zoo

**Status:** v18 research note, June 1, 2026  
**Question:** can better cheap detectors move the deployed verifier frontier?

## Why This Matters

v17 showed that semantic cluster verification is not enough by itself. Deployed gains are limited by the detector that decides when to invoke the verifier.

This note tests whether the old detector was merely underpowered.

## Setup

I ran a dependency-free detector zoo over the same held-out problem split:

- target: `visible_miss`,
- N=128,
- test trial count unchanged at 12 per held-out problem,
- calibration rows increased by sampling more candidate-set trials per calibration problem,
- variants: raw logistic, feature subsets, quadratic feature expansions, and a hand risk score.

Artifacts:

- [failure_detector_zoo.md](failure_detector_zoo.md)
- [failure_detector_zoo.csv](failure_detector_zoo.csv)
- [detector_zoo_frontier_comparison.md](detector_zoo_frontier_comparison.md)
- [detector_zoo_frontier_comparison.csv](detector_zoo_frontier_comparison.csv)

## Result

The detector frontier improves.

| dataset | invoke | original perfect-visible acc | zoo best acc | delta | best variant |
|---|---:|---:|---:|---:|---|
| MATH/Llama | 0.10 | 0.481 | 0.536 | +0.055 | support_diversity_raw |
| MATH/Llama | 0.20 | 0.518 | 0.575 | +0.057 | support_diversity_raw |
| MATH/Llama | 0.30 | 0.552 | 0.611 | +0.060 | support_diversity_raw |
| MATH/Gemma | 0.10 | 0.269 | 0.307 | +0.038 | support_diversity_quadratic |
| MATH/Gemma | 0.20 | 0.302 | 0.333 | +0.032 | all_quadratic |
| MATH/Gemma | 0.30 | 0.322 | 0.351 | +0.029 | all_raw |

The best Llama detector reaches AUC `0.778`, up from the old visible-miss AUC `0.714`. Gemma remains harder: best AUC is only `0.639`, close to the old `0.661`, but fixed-invoke projected accuracy still improves modestly.

## Interpretation

This is good news with caveats:

1. Detector quality is not fixed. Better calibration sampling and feature maps can move the deployed frontier.
2. Llama failures are especially detectable from support/diversity features.
3. Gemma failures remain less clean; quadratic features help at fixed invoke rates but do not produce a strong AUC.
4. Even the improved detector does not close the selectability gap. At 20% invoke, Llama reaches `0.575` under perfect visible verification, still far below any-correct coverage around `0.861`.

## Reviewer-Safe Claim

> The deployed method is detector-limited, but the detector is improvable. A lightweight support/diversity detector raises the projected perfect-verifier frontier on MATH/Llama from `0.518` to `0.575` at 20% invocation.

This should be treated as a local detector-search result, not as a final benchmark, because the calibration set is resampled more heavily and no external verifier has run yet.

## Next Experiment

The next step is to rerun the improved detector under multiple seeds and connect it to a reproducible external/local cluster verifier.
