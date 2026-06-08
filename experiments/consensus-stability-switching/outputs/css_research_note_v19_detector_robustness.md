# Cluster Selectability v19: Detector Robustness Sweep

**Status:** v19 research note, June 1, 2026  
**Question:** were the v18 detector-zoo gains robust or seed luck?

## Setup

v18 found that detector search could improve the projected deployed verifier frontier. To test robustness, I ran a selected-variant seed sweep:

- seeds: `11, 17, 23`,
- same held-out problem split protocol per seed,
- target: `visible_miss`,
- N=128,
- test trials: 12 per held-out problem,
- calibration trials: 48 per calibration problem,
- selected variants only, not the whole hyperparameter zoo.

Artifacts:

- [failure_detector_seed_sweep.md](failure_detector_seed_sweep.md)
- [failure_detector_seed_sweep.csv](failure_detector_seed_sweep.csv)
- [failure_detector_seed_sweep_raw.csv](failure_detector_seed_sweep_raw.csv)
- [detector_seed_sweep_vs_frontier.md](detector_seed_sweep_vs_frontier.md)
- [detector_seed_sweep_vs_frontier.csv](detector_seed_sweep_vs_frontier.csv)

## Result

The v18 single-seed result was directionally useful but too optimistic.

| dataset | invoke | original acc | seed-sweep mean | std | delta | best variant |
|---|---:|---:|---:|---:|---:|---|
| MATH/Llama | 0.10 | 0.481 | 0.495 | 0.032 | +0.014 | support_diversity_raw |
| MATH/Llama | 0.20 | 0.518 | 0.534 | 0.032 | +0.016 | support_diversity_raw |
| MATH/Llama | 0.30 | 0.552 | 0.569 | 0.033 | +0.017 | support_diversity_raw |
| MATH/Gemma | 0.10 | 0.269 | 0.279 | 0.023 | +0.010 | support_diversity_quadratic |
| MATH/Gemma | 0.20 | 0.302 | 0.299 | 0.021 | -0.003 | support_diversity_quadratic |
| MATH/Gemma | 0.30 | 0.322 | 0.317 | 0.022 | -0.005 | support_diversity_quadratic |

## Interpretation

The robust claim is narrower than v18:

1. Llama support/diversity detectors show a modest positive gain across seeds.
2. Gemma detector improvements are not robust; the frontier is flat to slightly worse after averaging.
3. The standard deviations are larger than the mean deltas, so detector search should be reported as promising but noisy.
4. The deployed bottleneck remains real. Better detector features help, but cheap observable features are not enough to close the selectability gap.

## Reviewer-Safe Claim

> A selected three-seed sweep preserves a small Llama gain from support/diversity failure detection, but does not support a broad claim that the detector-zoo improvement generalizes across model regimes.

This makes the research story more credible:

- semantic verification can recover visible hard failures,
- detector quality matters,
- but detector gains are model-regime-dependent and noisy.

## Next Experiment

The next detector step should use either richer evidence features or a verifier-generated uncertainty signal. More shallow feature search is unlikely to be the decisive path, especially for Gemma.
