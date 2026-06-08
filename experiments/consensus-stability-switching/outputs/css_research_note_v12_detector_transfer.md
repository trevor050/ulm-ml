# Cluster Selectability v12: Failure Detector Transfer

**Status:** v12 research note, June 1, 2026  
**Question:** do cheap failure detectors transfer across model traces?

## Why This Matters

The v11 feature ablation showed that MATH/Llama and MATH/Gemma use different cheap signals for detecting `cluster_sum` failure. A reviewer would reasonably ask:

> Is the failure detector model-specific, or can one detector transfer?

This note trains detectors on calibration problems from one trace and evaluates them on held-out test problems from another trace.

## Setup

Datasets:

- MATH/Llama-3-8B-Instruct,
- MATH/Gemma-2B.

For each dataset:

- train a cheap candidate verifier on 30 problems,
- reserve 24 calibration problems for failure-detector training,
- evaluate on remaining held-out problems,
- sample `N=128`, 12 trials per problem.

Detector targets:

- `miss`: any correct candidate exists, but `cluster_sum` selects wrong.
- `visible_miss`: a correct cluster is visible in top five, but `cluster_sum` selects wrong.

## Transfer Matrix

| target | train | test | AUC | precision@20 | recall@20 | optimistic oracle acc@20 |
|---|---|---|---:|---:|---:|---:|
| miss | llama | llama | 0.723 | 0.640 | 0.306 | 0.515 |
| miss | llama | gemma | 0.637 | 0.657 | 0.271 | 0.292 |
| miss | gemma | llama | 0.730 | 0.607 | 0.290 | 0.494 |
| miss | gemma | gemma | 0.709 | 0.736 | 0.303 | 0.296 |
| miss | pooled | llama | 0.747 | 0.663 | 0.317 | 0.524 |
| miss | pooled | gemma | 0.691 | 0.713 | 0.294 | 0.293 |
| visible_miss | llama | llama | 0.714 | 0.376 | 0.362 | 0.518 |
| visible_miss | llama | gemma | 0.607 | 0.258 | 0.293 | 0.291 |
| visible_miss | gemma | llama | 0.685 | 0.382 | 0.368 | 0.519 |
| visible_miss | gemma | gemma | 0.661 | 0.315 | 0.357 | 0.302 |
| visible_miss | pooled | llama | 0.740 | 0.404 | 0.389 | 0.524 |
| visible_miss | pooled | gemma | 0.643 | 0.275 | 0.312 | 0.294 |

## Interpretation

The detector signal transfers partially, but not cleanly.

Key observations:

1. Llama-trained visible-miss detection degrades on Gemma: `0.714 -> 0.607` AUC.
2. Gemma-trained visible-miss detection transfers to Llama better than expected: `0.661 -> 0.685` AUC.
3. Pooled training improves Llama detection but does not improve Gemma detection.
4. Even when AUC transfers, the optimistic verifier-bound accuracy remains modest.

This supports a nuanced claim:

> Failure detection is not completely model-specific, but calibration matters. A general detector may need model/task conditioning or pooled calibration across regimes.

## Method Implication

A deployable cluster-verification system should not assume one universal risk score. It should report:

- within-model detector performance,
- cross-model or cross-task transfer,
- pooled detector behavior,
- detector threshold sensitivity,
- net deployed gain after verifier regressions.

The practical method likely looks like:

```text
risk = f(cluster_structure, verifier_mass, model/task metadata)
if risk is high:
    invoke stronger cluster evidence verifier
else:
    keep cluster_sum/self-consistency
```

## Current Verdict

This transfer result strengthens the paper because it avoids a lazy conclusion. The detector is neither useless nor universal. It is a moderately transferable uncertainty signal whose failure modes must be measured.

That fits the broader thesis:

> Test-time scaling needs selectability diagnostics, not just more samples and a fixed selector.

## Artifacts

Scripts:

- [failure_detector_transfer.py](failure_detector_transfer.py)

Reports:

- [failure detector transfer matrix](failure_detector_transfer_math_llama_gemma_n128.md)
