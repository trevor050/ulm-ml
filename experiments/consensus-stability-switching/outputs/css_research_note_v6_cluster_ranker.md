# Candidate-Set Selector Switching, Cluster-Ranker Revision

**Status:** v6 research note, June 1, 2026  
**Main update:** I tested the obvious next step from v5, a learned answer-cluster ranker. It did **not** beat the simple fixed `cluster_sum` selector. That negative result is now part of the pitch.

## Why This Experiment

The portfolio lab showed that candidate-level routing was too narrow:

- `cluster_sum` beat self-consistency on MATH/Llama and MATH/Gemma-2B.
- portfolio oracles were far above any fixed selector.
- learned routers failed to recover the oracle headroom.

So the natural next hypothesis was:

> Instead of routing among candidate selectors, train a selector over answer clusters directly.

This should be the right abstraction if repeated sampling creates multiple answer clusters and the goal is to pick the correct cluster.

## New Script And Reports

Script:

- [monkey_cluster_ranker.py](monkey_cluster_ranker.py)

Reports:

- [MATH/Llama cluster ranker](monkey_cluster_ranker_math_llama.md)
- [MATH/Gemma-2B cluster ranker](monkey_cluster_ranker_math_gemma2b.md)

The ranker uses cluster features:

- cluster support,
- support rank,
- max/mean/sum verifier score,
- score variance,
- candidate length and numeric-feature averages,
- arithmetic-validity features,
- top-candidate arithmetic features,
- sample budget N.

It trains a logistic cluster-correctness model on calibration problems. I also tried a direct tuned formula over support/rank/score/arithmetic features.

## Results

### MATH / Llama-3-8B-Instruct

| selector | accuracy |
|---|---:|
| first | 0.301 |
| self-consistency | 0.406 |
| cluster max | 0.297 |
| cluster sum | 0.408 |
| cluster support max | 0.407 |
| learned cluster ranker | 0.406 |
| tuned cluster scorer | 0.406 |
| oracle cluster | 0.690 |
| any-correct | 0.690 |

At N=128:

| selector | accuracy |
|---|---:|
| self-consistency | 0.447 |
| cluster sum | 0.449 |
| learned cluster ranker | 0.447 |
| tuned cluster scorer | 0.447 |
| oracle cluster | 0.861 |

### MATH / Gemma-2B

| selector | accuracy |
|---|---:|
| first | 0.101 |
| self-consistency | 0.191 |
| cluster max | 0.128 |
| cluster sum | 0.194 |
| cluster support max | 0.190 |
| learned cluster ranker | 0.187 |
| tuned cluster scorer | 0.193 |
| oracle cluster | 0.483 |
| any-correct | 0.483 |

At N=128:

| selector | accuracy |
|---|---:|
| self-consistency | 0.218 |
| cluster sum | 0.222 |
| learned cluster ranker | 0.218 |
| tuned cluster scorer | 0.218 |
| oracle cluster | 0.723 |

## Interpretation

The result is sharp:

> A learned cluster-level ranker with these features still does not beat the dumb fixed `cluster_sum` rule.

That is not fatal. It tells us what is actually missing.

`cluster_sum` is a strong baseline because it combines support and verifier mass without needing calibrated probabilities. The learned ranker has to infer the same thing from a small calibration set where correct clusters are sparse. In MATH/Llama, only about 8.6% of training clusters are positive. In MATH/Gemma-2B, only about 3.2% are positive. That is a brutal ranking problem.

The oracle cluster result is the real alarm bell:

- MATH/Llama oracle cluster: 0.690 overall, 0.861 at N=128.
- MATH/Gemma oracle cluster: 0.483 overall, 0.723 at N=128.

Because cluster oracle equals any-correct under this cluster correctness definition, the problem is almost purely cluster ranking. The candidate set has the right answer cluster. We just cannot rank it yet.

## Updated Research Claim

The research direction is now cleaner:

1. Repeated sampling creates high answer-cluster coverage.
2. Self-consistency and simple cluster-sum recover only part of that coverage.
3. Learned rankers with cheap surface features do not yet beat cluster-sum.
4. Therefore, the missing ingredient is stronger cluster evidence, not more logistic routing.

This points away from the original CSS framing and toward:

> **Cluster-level verification for test-time scaling.**

CSS becomes the broader diagnostic framework: measure selectability gaps, selector oracles, and headroom closure. The concrete next method should be a better cluster verifier.

## What A Better Cluster Verifier Needs

The current features are surface-level. A stronger cluster verifier should inspect the reasoning inside a cluster:

- agreement of intermediate quantities across candidates,
- consistency of final answer derivations,
- symbolic validity of arithmetic/algebra steps,
- verifier/judge scores aggregated at the cluster level,
- contradiction rate within a cluster,
- whether independent derivation templates converge on the same answer,
- model logprob or hidden-state confidence if available.

For MATH, the biggest opportunity is not candidate scoring; it is **cluster evidence aggregation**.

## Stronger Next Experiment

Build a cluster verifier with pairwise or within-cluster consistency:

1. For each answer cluster, sample 3-5 candidate rationales.
2. Extract equations, final transformations, and key intermediate values.
3. Score intra-cluster consistency.
4. Score cluster-vs-problem plausibility with a stronger verifier or LLM judge when compute allows.
5. Combine:

```text
cluster_score =
  support_mass
+ verifier_mass
+ intra_cluster_consistency
- contradiction_penalty
```

Compare against:

- self-consistency,
- cluster sum,
- learned cluster ranker,
- oracle cluster.

The goal is no longer a cute router. The goal is to close the huge cluster-oracle gap.

## Current Verdict

This sprint has produced a real research trajectory:

- Synthetic stress tests showed verifier over-optimization and calibration issues.
- Monkey Business real rollouts showed huge selectability gaps.
- Multi-config results showed CSS helps only in a medium-accuracy selector-complementarity regime.
- Portfolio experiments showed cluster-level selectors beat SC in MATH settings.
- Learned cluster-ranker experiments showed cheap features are not enough.

The strongest paper-shaped claim is now:

> **Repeated-sampling systems should evaluate answer-cluster coverage and cluster selectability, because the correct cluster is often present long before current selectors can identify it.**

That is legitimately useful.

## References

- Scaling Intelligence. [Monkey Business dataset](https://huggingface.co/datasets/ScalingIntelligence/monkey_business).
- Brown et al., 2024. [Large Language Monkeys: Scaling Inference Compute with Repeated Sampling](https://arxiv.org/abs/2407.21787).
- Snell et al., 2024. [Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters](https://arxiv.org/abs/2408.03314).
- Dorner et al., 2025. [ROC-n-reroll: How verifier imperfection affects test-time scaling](https://arxiv.org/abs/2507.12399).
- Shyamal et al., 2026. [SCATR: Simple Calibrated Test-Time Ranking](https://arxiv.org/abs/2604.16535).
