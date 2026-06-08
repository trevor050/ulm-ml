# v67 Phase Depth Cost ROI

**Date:** June 1, 2026  
**Question:** Does the top-20 depth gain survive a prompt-cost accounting, or is the efficient policy really top-5/top-10 with top-20 reserved for expensive tail cases?

## Run

I combined v66 marginal depth gains with measured compact verifier prompt sizes for the MATH/Llama and MATH/Gemma `N=128` depth assets.

```bash
python3 work/phase_depth_cost_roi.py \
  --marginal-csv outputs/phase_depth_marginal_utility.csv \
  --output-prefix phase_depth_cost_roi
```

Primary artifact: [phase_depth_cost_roi.md](phase_depth_cost_roi.md).

## Result

At `N=128`:

| dataset | depth | cumulative gain | avg prompt tok | marginal gain | marginal tok | marginal gain / 1k tok |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Gemma | 5 | `0.185` | `647` | `0.185` | `647` | `0.285` |
| MATH/Gemma | 10 | `0.302` | `1116` | `0.117` | `469` | `0.250` |
| MATH/Gemma | 20 | `0.372` | `2266` | `0.070` | `1150` | `0.061` |
| MATH/Llama | 5 | `0.206` | `639` | `0.206` | `639` | `0.323` |
| MATH/Llama | 10 | `0.296` | `1011` | `0.089` | `372` | `0.240` |
| MATH/Llama | 20 | `0.343` | `2369` | `0.047` | `1357` | `0.035` |

Top-5 is the best marginal-ROI row. Top-10 remains efficient on both high-N MATH traces. Top-20 buys real extra accuracy, but the tail is expensive: the top10-to-top20 marginal cost is about `16.5k` tokens per +1.0 gain for Gemma and `28.9k` tokens per +1.0 gain for Llama under this compact prompt proxy.

## Read

This is a useful negative constraint on the method. The evidence does not support "always run top-20." It supports a budget-aware policy:

1. Use top-5/top-10 as the efficient default when the trace is depth-limited but budget-constrained.
2. Reserve top-20 for high-value depth-limited cases, high uncertainty, or max-accuracy settings.
3. Keep surfaced and coverage-limited phases out of expensive deep verification unless there is a separate reason to inspect them.

That makes the pitch more reviewer-resistant. v66 showed that top-20 is not a universal depth knob across phases; v67 adds that even inside hard MATH, top-20 is a deliberate tail spend rather than the cost-efficient default.

## Caveat

Prompt cost is estimated as prompt characters / `4`, using existing compact MATH verifier prompt assets. The top-20 prompt family is the diverse rank11-20 compact set, so this is a cost proxy for deep inspection rather than a live endpoint tokenizer measurement or a full deployed prompt distribution.
