# Cluster Selectability v11: Failure Detector Feature Ablation

**Status:** v11 research note, June 1, 2026  
**Question:** which cheap candidate-set features actually predict `cluster_sum` failures?

## Why This Matters

The v10 result showed cheap failure detectors are moderately predictive:

- MATH/Llama `miss` AUC: `0.723`.
- MATH/Gemma `miss` AUC: `0.709`.

But reviewers will ask whether this is a brittle artifact of one feature bundle. This ablation splits the detector into cheap feature families.

## Feature Groups

The detector feature vector contains:

- support features: top support, second support, support gap,
- score-mass features: top/second cluster-sum score, score margin, score share,
- top-score features: max/mean/std verifier score inside the top cluster,
- diversity features: cluster count, answer entropy, support distribution spread,
- sample budget.

The ablation trains the same logistic detector on each group or leave-one-group-out variant.

## MATH/Llama Results

| target | best groups | AUC | optimistic oracle acc at 20% invoke |
|---|---|---:|---:|
| miss | diversity_only | 0.733 | 0.517 |
| miss | support_only | 0.723 | 0.520 |
| miss | all | 0.723 | 0.515 |
| visible_miss | support_only | 0.725 | 0.523 |
| visible_miss | score_mass_only | 0.719 | 0.521 |
| visible_miss | all | 0.714 | 0.518 |

Top-score-only is poor:

| target | top_score_only AUC |
|---|---:|
| miss | 0.382 |
| visible_miss | 0.494 |

Interpretation: on MATH/Llama, failure risk is mostly about answer-cluster structure. If many clusters remain plausible and support is diffuse, `cluster_sum` is more likely wrong. The score of the top cluster itself is not a reliable safety signal.

## MATH/Gemma-2B Results

| target | best groups | AUC | optimistic oracle acc at 20% invoke |
|---|---|---:|---:|
| miss | no_support | 0.717 | 0.300 |
| miss | all | 0.709 | 0.296 |
| miss | no_score_mass | 0.700 | 0.296 |
| visible_miss | all | 0.661 | 0.302 |
| visible_miss | no_support | 0.657 | 0.297 |
| visible_miss | no_diversity | 0.631 | 0.295 |

Again, top-score-only is weak:

| target | top_score_only AUC |
|---|---:|
| miss | 0.541 |
| visible_miss | 0.467 |

Interpretation: Gemma is different from Llama. Support-only is weak, and the best broad-miss detector excludes support. This matches the qualitative behavior of smaller/weaker traces: incorrect answer clusters proliferate, and simple support structure is less informative.

## Takeaways

1. Failure-detection signal is real but model-dependent.
2. Top-cluster confidence features are weak and sometimes anti-informative.
3. Llama failures are largely cluster-structure failures.
4. Gemma failures require score/diversity interactions; support alone is not enough.
5. No feature group makes the detector strong enough to erase the selectability gap.

This strengthens the method implication:

> A deployable verifier gate should be calibrated per model/task regime and should use cluster-structure diagnostics, not just the selected cluster's score.

It also adds another reason not to overclaim: if the failure detector changes across model regimes, then a general cluster-verification method needs either robust uncertainty features or model-specific calibration.

## Artifacts

Scripts:

- [failure_detector_feature_ablation.py](failure_detector_feature_ablation.py)

Reports:

- [MATH/Llama failure-detector ablation](failure_detector_ablation_math_llama_n128.md)
- [MATH/Gemma failure-detector ablation](failure_detector_ablation_math_gemma2b_n128.md)
