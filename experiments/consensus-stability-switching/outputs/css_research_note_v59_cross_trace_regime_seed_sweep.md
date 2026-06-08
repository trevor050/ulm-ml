# v59 Cross-Trace Regime Seed Sweep

**Date:** June 1, 2026  
**Question:** Does the v58 trace-regime boundary survive different held-out splits and trial samples?

## Run

I ran a three-seed split/trial sweep over the same four local Monkey Business traces. This reuses the v57/v58 metrics, but summarizes point estimates across seeds instead of running a bootstrap interval for only one split.

```bash
python3 work/cross_trace_regime_seed_sweep.py \
  --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json \
            MATH/Gemma=work/MATH_Gemma-2B.json \
            GSM8K/Llama=work/GSM8K_Llama-3-8B-Instruct.json \
            MATH/Pythia=work/MATH_Pythia-1B.json \
  --seeds 60601 60602 60603 \
  --n 128 \
  --trials-per-problem 12 \
  --verifier-train-problems 30 \
  --audit-holdout-gap 24 \
  --verifier-samples-per-problem 800 \
  --output-prefix cross_trace_regime_seed_sweep
```

Primary artifact: [cross_trace_regime_seed_sweep.md](cross_trace_regime_seed_sweep.md).

## Result

| dataset | regime | `cluster_sum` | oracle | headroom | top20 gain | top20 closed | miss p50/p90 |
|---|---|---:|---:|---:|---:|---:|---:|
| GSM8K/Llama | shallow/surfaced | `0.868 +/- 0.027` | `0.995 +/- 0.003` | `0.127 +/- 0.030` | `0.127 +/- 0.030` | `0.997 +/- 0.005` | `2 / 3` |
| MATH/Gemma | depth-limited | `0.229 +/- 0.013` | `0.691 +/- 0.034` | `0.462 +/- 0.026` | `0.374 +/- 0.024` | `0.810 +/- 0.019` | `7 / 33` |
| MATH/Llama | depth-limited | `0.442 +/- 0.010` | `0.824 +/- 0.031` | `0.381 +/- 0.022` | `0.339 +/- 0.019` | `0.890 +/- 0.002` | `5 / 22` |
| MATH/Pythia | coverage-limited | `0.049 +/- 0.012` | `0.310 +/- 0.015` | `0.261 +/- 0.005` | `0.220 +/- 0.005` | `0.845 +/- 0.026` | `7 / 27` |

## Read

The v58 boundary is not a single split artifact. Across three seeds:

- GSM8K/Llama stays shallow/surfaced: high `cluster_sum`, near-complete oracle coverage, and shallow misses.
- MATH/Pythia stays coverage-limited: oracle coverage is low, so more/better generation still matters, but top20 closes most of the available selectability headroom once a correct cluster exists.
- MATH/Llama and MATH/Gemma stay depth-limited: large selector/oracle gaps, robust top20 gains, and buried miss ranks.

This strengthens the reviewer-resistant framing. The paper should not say "cluster selectability is always the bottleneck." It should say:

> Answer-cluster selectability is a trace-regime diagnostic. It separates shallow/surfaced, coverage-limited, and depth-limited regimes; adaptive cluster-depth verification is the right target for the depth-limited regime where correct answer clusters are already generated but not surfaced.

