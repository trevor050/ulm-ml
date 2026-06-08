# Cluster Selectability v17: Detector-Triggered Verifier Frontier

**Status:** v17 research note, June 1, 2026  
**Question:** if the cluster verifier is strong, what deployed gain is actually available after detector gating?

## Setup

The v16 full-packet audit made the semantic verifier hypothesis much more plausible:

- `111/120` against trace keys,
- `111/111` when the manual mathematical answer is visible after normalization.

But conditional verifier accuracy is not deployed accuracy. The deployed method needs a detector that decides when to spend verifier compute without regressing ordinary `cluster_sum` hits.

This note converts the existing failure-detector diagnostics into cost/gain frontiers:

- [detector_verifier_frontier.md](detector_verifier_frontier.md)
- [detector_verifier_frontier.csv](detector_verifier_frontier.csv)
- [detector_verifier_frontier.svg](detector_verifier_frontier.svg)

## Projection Assumptions

Start from ordinary `cluster_sum` accuracy on N=128 held-out trials.

For each invoke rate, use the existing visible-miss detector ranking and estimate:

```text
projected accuracy =
  cluster_sum
  + verifier_success_on_flagged_visible_misses
  - regressions_on_false_or_unhelpful_invocations
```

Scenarios:

| scenario | visible-miss success | false/unhelpful regression |
|---|---:|---:|
| perfect visible verifier | 1.000 | 0.000 |
| trace-key credit | 0.925 | 0.000 |
| external 80 + mild regression | 0.800 | 0.020 |
| external 70 + harsher regression | 0.700 | 0.050 |

## Key Frontier Points

| dataset | scenario | invoke rate | projected acc | delta vs cluster_sum |
|---|---|---:|---:|---:|
| MATH/Llama | perfect visible verifier | 0.20 | 0.518 | +0.075 |
| MATH/Llama | external 80 + mild regression | 0.20 | 0.500 | +0.058 |
| MATH/Llama | perfect visible verifier | 0.50 | 0.599 | +0.157 |
| MATH/Gemma | perfect visible verifier | 0.20 | 0.302 | +0.063 |
| MATH/Gemma | external 80 + mild regression | 0.20 | 0.286 | +0.047 |
| MATH/Gemma | perfect visible verifier | 0.50 | 0.365 | +0.126 |

## Interpretation

This is a useful reality check:

1. The verifier is no longer the only blocker. Conditional hard-packet recovery looks strong.
2. The detector is now the deployed bottleneck. At 20% invoke, a perfect visible verifier still only reaches `0.518` on Llama and `0.302` on Gemma.
3. Large headroom remains. These gains are far below any-correct coverage (`0.861` Llama, `0.725` Gemma), because many correct clusters are outside the bounded visible set or not flagged.
4. A publishable method needs either a better detector, a verifier that can pull buried clusters into view, or both.

## Updated Method Claim

The reviewer-safe method target is:

> Use cheap selectors by default; use a calibrated failure detector to invoke semantic cluster verification; report the full frontier of invoke rate, verifier success, false-invocation regression, and deployed net gain.

The strongest current result is not "we solved test-time scaling." It is:

> Coverage is not selectability. On MATH traces, repeated sampling often creates correct answer clusters that selectors miss; semantic verification can recover visible hard failures, but deployed gains are detector-limited.

## Next Required Experiment

Run the same 120 prompts through a reproducible external/local model. If that model reaches even the `external_80` scenario, the detector frontier predicts nontrivial deployed gains. Then improve the detector or expand the verifier beyond bounded top-five packets.
