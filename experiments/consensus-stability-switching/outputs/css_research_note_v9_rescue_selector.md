# Cluster Selectability v9: Hard-Packet Rescue Selector Ablation

**Status:** v9 research note, June 1, 2026  
**Question:** can a shallow supervised selector rescue `cluster_sum` failures, or do we really need stronger cluster-level verification?

## Motivation

The v8 result established the cluster-selectability gap:

- MATH/Llama at `N=128`: `cluster_sum ~0.445`, full cluster oracle `~0.846`.
- MATH/Gemma-2B at `N=128`: `cluster_sum ~0.240`, full cluster oracle `~0.725`.

The obvious reviewer objection is:

> Maybe the right answer cluster is easy to pick with a small supervised model over cluster features. You do not need a real verifier.

So I built a hard-packet rescue benchmark and tested that objection directly.

## Hard Packet Construction

Each hard packet is built from an `N=128` candidate set where:

1. `cluster_sum` selects a wrong answer cluster,
2. at least one correct answer cluster exists,
3. the packet exposes five clusters with up to three representative rationales each,
4. a correct cluster is forced into the visible packet if it is not already in the top five.

Packet sets:

- [MATH/Llama hard packets](cluster_packets_math_llama_n128.jsonl), 60 packets.
- [MATH/Gemma hard packets](cluster_packets_math_gemma2b_n128.jsonl), 60 packets.

This is intentionally not a deployed selector benchmark. It is a conditional rescue task: if we know `cluster_sum` failed and show a correct cluster, can shallow features recover it?

## Cheap Baselines On Hard Packets

| packet set | support | max score | mean score | cheap sanity |
|---|---:|---:|---:|---:|
| MATH/Llama N=128 | 0.000 | 0.050 | 0.233 | 0.100 |
| MATH/Gemma N=128 | 0.017 | 0.083 | 0.317 | 0.183 |

`cluster_sum` is zero by construction.

## Shallow Supervised Packet Selector

I trained a logistic selector over visible cluster features:

- support and support fraction,
- verifier sum/max/mean,
- rank by verifier mass,
- answer mention count in rationales,
- answer magnitude/proximity to problem numbers,
- digit density,
- rationale length,
- repetition/junk score,
- representative verifier-score moments.

Results:

| experiment | train packets | test packets | cluster_sum | support | max_score | mean_score | learned shallow selector |
|---|---:|---:|---:|---:|---:|---:|---:|
| llama_half_to_llama_half | 30 | 30 | 0.000 | 0.000 | 0.033 | 0.333 | 0.567 |
| gemma_half_to_gemma_half | 30 | 30 | 0.000 | 0.033 | 0.067 | 0.333 | 0.733 |
| llama_to_gemma | 60 | 60 | 0.000 | 0.017 | 0.083 | 0.317 | 0.650 |
| gemma_to_llama | 60 | 60 | 0.000 | 0.000 | 0.050 | 0.233 | 0.617 |
| pooled_half_to_pooled_half | 60 | 60 | 0.000 | 0.017 | 0.050 | 0.333 | 0.550 |

This is an important surprise. The packet task is learnable, and the learned selector transfers across Llama/Gemma hard packets. That means the visible hard cases contain a real signal, not pure noise.

But it does **not** prove a deployable selector, because the packet construction has two strong advantages:

- it conditions on `cluster_sum` being wrong,
- it ensures a correct cluster is visible.

## Deployment Test: Always Apply The Rescue Selector

The rescue selector was then trained on hard packets and deployed on ordinary held-out `N=128` trials, where `cluster_sum` may already be correct and where correct clusters may be absent or outside the visible top five.

| dataset | any-correct | cluster_sum | mean_score | always-learned rescue | rescues misses | regresses hits |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.865 | 0.455 | 0.160 | 0.108 | 0.052 | 0.399 |
| MATH/Gemma-2B | 0.741 | 0.232 | 0.131 | 0.095 | 0.070 | 0.207 |

Always applying the rescue selector is disastrous. It finds some missed correct clusters, but it destroys far more cases where `cluster_sum` was already right.

## Deployment Test: Calibrated Gate

Next I tuned a gate on reserved calibration problems. The gate invokes the rescue selector only when `cluster_sum` appears uncertain:

```text
use rescue if:
  learned answer differs from cluster_sum
  top support <= threshold
  cluster_sum margin <= threshold
  top sum share <= threshold
  learned probability margin >= threshold
```

With 12 trials per held-out problem:

| dataset | calib cluster_sum | calib gated | test cluster_sum | test always-learned | test gated |
|---|---:|---:|---:|---:|---:|
| MATH/Llama | 0.333 | 0.333 | 0.443 | 0.096 | 0.443 |
| MATH/Gemma-2B | 0.160 | 0.184 | 0.250 | 0.107 | 0.242 |

The gate does not produce a robust held-out gain. On Llama, tuning correctly learns to do nothing. On Gemma, calibration improves but held-out test accuracy drops below `cluster_sum`.

## Interpretation

This ablation sharpens the story:

1. Conditional hard cases are learnable from shallow features.
2. A rescue selector trained on those cases does not become a safe deployed selector.
3. The hard part is not only "which visible cluster is correct?" It is also "when should I distrust the current selector?"
4. This is the original CSS/router problem reappearing at the cluster level.

The result also changes the next method proposal. A cluster verifier should probably not be deployed as an unconditional replacement for `cluster_sum`. It should be used as an uncertainty-triggered verifier, and the uncertainty trigger must itself be evaluated as carefully as the verifier.

## Updated Method Target

The next serious method should have two coupled components:

```text
1. Failure detector:
   Estimate when current cluster_sum evidence is unreliable.

2. Cluster evidence verifier:
   When invoked, inspect competing cluster rationales and choose the best-supported final answer.
```

Both parts need held-out evaluation:

- failure-detector precision/recall on `cluster_sum` misses,
- verifier accuracy conditional on true misses,
- regression rate when the detector fires on `cluster_sum` hits,
- total deployed accuracy.

## Current Verdict

The shallow rescue selector is useful as a diagnostic and benchmark baseline, but not yet as a method. It shows the hard packets contain learnable signal while also showing why deployment is harder than conditional reranking.

That makes the research pitch more defensible:

> The cluster selectability gap is not solved by a naive learned reranker. The missing method is a calibrated failure detector plus cluster-level verification that improves the evidence only when the default selector is likely wrong.

## Artifacts

Scripts:

- [hard_packet_feature_transfer.py](hard_packet_feature_transfer.py)
- [evaluate_rescue_selector_full.py](evaluate_rescue_selector_full.py)
- [gated_rescue_selector.py](gated_rescue_selector.py)

Reports:

- [hard-packet feature transfer](hard_packet_feature_transfer.md)
- [MATH/Llama full rescue deployment](rescue_selector_full_llama_train_llama_eval_llama.md)
- [MATH/Gemma full rescue deployment](rescue_selector_full_gemma_train_gemma_eval_gemma.md)
- [MATH/Llama gated rescue, 12 trials](gated_rescue_math_llama_n128_t12.md)
- [MATH/Gemma gated rescue, 12 trials](gated_rescue_math_gemma2b_n128_t12.md)
