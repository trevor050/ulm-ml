# Cluster Selectability v10: Failure Detector Diagnostics

**Status:** v10 research note, June 1, 2026  
**Question:** can cheap candidate-set features detect when `cluster_sum` is wrong?

## Why This Matters

The v9 rescue-selector ablation showed:

- hard packets are learnable when we condition on `cluster_sum` being wrong,
- but an unconditional rescue selector catastrophically regresses ordinary examples,
- and a simple calibrated gate does not produce robust held-out gains.

That makes the next bottleneck explicit:

> A deployable cluster verifier needs a failure detector. It must know when to distrust the default cluster selector.

This note tests whether cheap candidate-set features can detect `cluster_sum` failures.

## Setup

For each held-out `N=128` candidate set, I form answer clusters and compute cheap diagnostics:

- top and second cluster support,
- support gap,
- top and second verifier-mass score,
- verifier-mass margin and share,
- top cluster max/mean/std verifier score,
- cluster count,
- answer entropy,
- score distribution statistics,
- support distribution statistics.

Two labels are evaluated:

- `miss`: any correct candidate exists, but `cluster_sum` selects a wrong cluster.
- `visible_miss`: a correct cluster is visible in the top five clusters, but `cluster_sum` selects a wrong cluster.

A logistic detector is trained on reserved calibration problems and evaluated on held-out test problems.

## Base Rates

| dataset | split | any-correct | visible-correct top5 | cluster_sum | miss | visible miss |
|---|---|---:|---:|---:|---:|---:|
| MATH/Llama | calibration | 0.792 | 0.642 | 0.316 | 0.476 | 0.326 |
| MATH/Llama | test | 0.861 | 0.651 | 0.443 | 0.419 | 0.208 |
| MATH/Gemma | calibration | 0.597 | 0.337 | 0.188 | 0.410 | 0.149 |
| MATH/Gemma | test | 0.725 | 0.416 | 0.239 | 0.486 | 0.177 |

Notice the distribution shift between calibration and test. Llama's calibration split is harder than its test split; Gemma's test split has substantially higher any-correct coverage. This is one reason the simple gate in v9 was brittle.

## Detector AUC

| dataset | target | AUC |
|---|---|---:|
| MATH/Llama | miss | 0.723 |
| MATH/Llama | visible_miss | 0.714 |
| MATH/Gemma | miss | 0.709 |
| MATH/Gemma | visible_miss | 0.661 |

Cheap features contain signal, but not enough to cleanly isolate useful verifier calls.

## Precision / Recall Tradeoff

### MATH/Llama

| target | invoke rate | precision | recall | optimistic perfect-visible-verifier accuracy |
|---|---:|---:|---:|---:|
| miss | 0.10 | 0.573 | 0.137 | 0.481 |
| miss | 0.20 | 0.640 | 0.306 | 0.515 |
| miss | 0.30 | 0.632 | 0.452 | 0.547 |
| visible_miss | 0.10 | 0.382 | 0.184 | 0.481 |
| visible_miss | 0.20 | 0.376 | 0.362 | 0.518 |
| visible_miss | 0.30 | 0.365 | 0.524 | 0.552 |

Baseline `cluster_sum` on the same test trials is `0.443`.

### MATH/Gemma-2B

| target | invoke rate | precision | recall | optimistic perfect-visible-verifier accuracy |
|---|---:|---:|---:|---:|
| miss | 0.10 | 0.719 | 0.148 | 0.275 |
| miss | 0.20 | 0.736 | 0.303 | 0.296 |
| miss | 0.30 | 0.680 | 0.419 | 0.312 |
| visible_miss | 0.10 | 0.303 | 0.172 | 0.269 |
| visible_miss | 0.20 | 0.315 | 0.357 | 0.302 |
| visible_miss | 0.30 | 0.278 | 0.471 | 0.322 |

Baseline `cluster_sum` on the same test trials is `0.239`.

## Interpretation

This is the cleanest diagnostic result so far.

Cheap failure detection is possible but weak. It can rank risky candidate sets above chance, but the useful visible misses are not concentrated enough to make a simple gate reliable.

Even under an optimistic assumption, a perfect top-five verifier invoked on the top 20% detector-ranked examples would reach only:

- MATH/Llama: `0.515`, from `0.443`.
- MATH/Gemma: `0.296`, from `0.239`.

Those are real possible gains, but still far below full oracle coverage:

- MATH/Llama full oracle at N=128: about `0.846`.
- MATH/Gemma full oracle at N=128: about `0.725`.

So the bottleneck is now decomposed:

```text
full oracle gap
  = failure detection problem
  + visible-cluster verification problem
  + buried-cluster evidence problem
```

The buried-cluster part is especially important on high-N MATH, where correct clusters are often not in the top few under current verifier mass.

## Method Implication

The next real method should not be "replace `cluster_sum` with a learned cluster scorer."

It should be:

```text
1. Detect likely selector failure using calibrated set-level uncertainty.
2. When failure risk is high, spend extra compute on cluster evidence.
3. Let the extra evidence change the cluster ranking, not merely choose among the current top few.
4. Penalize regressions explicitly.
```

A useful deployed metric is:

```text
net_gain =
  P(invoked, cluster_sum wrong, verifier correct)
- P(invoked, cluster_sum correct, verifier wrong)
```

This is more honest than reporting conditional verifier accuracy on hand-picked hard packets.

## Current Verdict

The research pitch is now more reviewer-resistant:

- repeated sampling creates large answer-cluster coverage,
- current selectors leave much of that coverage unused,
- hard cluster failures contain learnable signal,
- naive learned rescue selectors do not deploy safely,
- cheap failure detection is only moderately predictive,
- therefore the promising method target is calibrated failure detection plus stronger cluster evidence.

This is no longer just a selector-switching idea. It is a framework for measuring and attacking the hidden selection bottleneck in test-time scaling.

## Artifacts

Scripts:

- [failure_detector_diagnostics.py](failure_detector_diagnostics.py)
- [gated_rescue_selector.py](gated_rescue_selector.py)
- [hard_packet_feature_transfer.py](hard_packet_feature_transfer.py)

Reports:

- [MATH/Llama failure detector](failure_detector_math_llama_n128.md)
- [MATH/Gemma failure detector](failure_detector_math_gemma2b_n128.md)
- [v9 rescue-selector ablation](css_research_note_v9_rescue_selector.md)
