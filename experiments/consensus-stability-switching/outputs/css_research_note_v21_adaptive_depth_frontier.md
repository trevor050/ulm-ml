# v21 Adaptive Cluster-Depth Frontier

## Question

The v20 audit showed that correct clusters on high-N MATH misses are often buried around rank 6-20, and sometimes deeper. That creates an obvious reviewer objection:

> Top-k oracles are unconditional. What happens when expensive verification is only invoked on a fraction of examples?

This note turns the depth audit into a deployed projection.

## Setup

Script: `work/adaptive_depth_frontier.py`.

For each depth `k in {5, 10, 20, 50}`, I train a separate cheap detector for the target:

```text
cluster_sum is wrong AND a correct cluster is ranked <= k by cluster_sum
```

Then I invoke a hypothetical semantic verifier on the highest-risk held-out trials at rates `10%, 20%, 30%, 50%`.

Projection scenarios:

- perfect verifier, no regression,
- 80% success on recoverable invoked misses, 2% regression on false/unhelpful invocations,
- 70% success, 5% regression.

## Base Oracles

| dataset | cluster_sum | any-correct | top5 oracle | top10 oracle | top20 oracle | top50 oracle |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.450 | 0.861 | 0.654 | 0.762 | 0.820 | 0.857 |
| MATH/Gemma | 0.239 | 0.725 | 0.423 | 0.550 | 0.635 | 0.712 |

## Deployed Projection At 20% Invoke

| dataset | depth | perfect projected acc | conservative projected acc | conservative delta | detector AUC |
|---|---:|---:|---:|---:|---:|
| MATH/Llama | 5 | 0.526 | 0.508 | +0.058 | 0.727 |
| MATH/Llama | 10 | 0.555 | 0.532 | +0.082 | 0.702 |
| MATH/Llama | 20 | 0.572 | 0.546 | +0.096 | 0.723 |
| MATH/Llama | 50 | 0.581 | 0.554 | +0.103 | 0.729 |
| MATH/Gemma | 5 | 0.300 | 0.285 | +0.046 | 0.639 |
| MATH/Gemma | 10 | 0.337 | 0.315 | +0.076 | 0.659 |
| MATH/Gemma | 20 | 0.370 | 0.343 | +0.104 | 0.700 |
| MATH/Gemma | 50 | 0.389 | 0.358 | +0.119 | 0.705 |

Full report: `outputs/adaptive_depth_frontier.md`.

## Interpretation

Depth matters under deployment. At the same 20% invocation rate, moving from top-5 to top-20 raises the conservative projection:

```text
MATH/Llama: 0.508 -> 0.546
MATH/Gemma: 0.285 -> 0.343
```

That is a materially better pitch than top-5 verification, especially for Gemma. It also keeps the result honest: even top-20 verification at 20% invoke is still far below full any-correct coverage. The remaining gap is detector recall and verifier cost, not merely semantic judging ability.

## Current Method Thesis

The best tested proposal is now:

> Failure-activated adaptive cluster-depth verification: sample many candidates, cluster by final answer, use cheap uncertainty features to decide when selection is unreliable, then spend semantic verification compute over a variable-depth cluster frontier.

This is more aggressive than CSS and more testable than "use a better verifier." It defines concrete axes:

- invocation rate,
- inspected cluster depth,
- detector AUC/capture,
- verifier success on recoverable misses,
- regression on false invocations,
- net deployed accuracy.

## Caveat

This is still a projection, not a completed method. The next real experiment is to run an external/local LLM verifier on top-10/top-20 cluster packets, not only top-5 hard packets, and measure actual success/regression instead of assuming it.
