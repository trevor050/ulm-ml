# v62 Phase Seed Sweep

**Date:** June 1, 2026  
**Question:** Is the v61 sample-count phase diagram stable across held-out splits and trial seeds?

## Run

I repeated the `N = 4, 8, 16, 32, 64, 128` cross-trace phase diagram over three seeds.

```bash
python3 work/cross_trace_phase_seed_sweep.py \
  --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json \
            MATH/Gemma=work/MATH_Gemma-2B.json \
            GSM8K/Llama=work/GSM8K_Llama-3-8B-Instruct.json \
            MATH/Pythia=work/MATH_Pythia-1B.json \
  --ns 4 8 16 32 64 128 \
  --seeds 60601 60602 60603 \
  --trials-per-problem 12 \
  --verifier-train-problems 30 \
  --audit-holdout-gap 24 \
  --verifier-samples-per-problem 800 \
  --output-prefix cross_trace_phase_seed_sweep
```

Primary artifact: [cross_trace_phase_seed_sweep.md](cross_trace_phase_seed_sweep.md).

## Result

| dataset | majority phase path | max headroom | final N=128 read |
|---|---|---:|---|
| GSM8K/Llama | mixed -> shallow/surfaced -> shallow/surfaced -> shallow/surfaced -> shallow/surfaced -> shallow/surfaced | `N=64 0.137 +/- 0.030` | shallow/surfaced, oracle `0.996`, `cluster_sum 0.865` |
| MATH/Gemma | coverage-limited -> coverage-limited -> mixed -> depth-limited -> depth-limited -> depth-limited | `N=128 0.455 +/- 0.047` | depth-limited, oracle `0.691`, `cluster_sum 0.236` |
| MATH/Llama | mixed -> mixed -> mixed -> depth-limited -> depth-limited -> depth-limited | `N=128 0.384 +/- 0.028` | depth-limited, oracle `0.826`, `cluster_sum 0.442` |
| MATH/Pythia | coverage-limited -> coverage-limited -> coverage-limited -> coverage-limited -> coverage-limited -> coverage-limited | `N=128 0.271 +/- 0.007` | coverage-limited, oracle `0.313`, `cluster_sum 0.042` |

The high-N regime labels are stable:

| dataset | N=64 votes | N=128 votes | read |
|---|---|---|---|
| GSM8K/Llama | shallow/surfaced:3 | shallow/surfaced:3 | surfaced early |
| MATH/Gemma | depth-limited:3 | depth-limited:3 | depth-limited at high N |
| MATH/Llama | depth-limited:3 | depth-limited:3 | depth-limited at high N |
| MATH/Pythia | coverage-limited:3 | coverage-limited:3 | coverage-limited throughout |

The exact transition row can wobble near the mixed/depth boundary. At `N=32`, MATH/Llama and MATH/Gemma each have `depth-limited:2; mixed:1`. That is not a problem; it is the expected boundary behavior. By `N=64` and `N=128`, the high-N assignment is unanimous.

## Read

v61’s phase diagram is not a one-split cartoon. Across three seeds:

- GSM8K/Llama becomes shallow/surfaced early and stays there.
- MATH/Pythia remains coverage-limited even as N rises.
- MATH/Llama and MATH/Gemma move into a depth-limited phase at higher N.

This is the best current framing:

> Increasing sample count can create a phase transition: once coverage is high enough, the bottleneck shifts from generating a correct answer to surfacing the correct answer cluster. Adaptive cluster-depth verification is aimed at that depth-limited phase.

## Reviewer Use

If a reviewer says "your regime map is arbitrary," point to:

1. v58 for bootstrap uncertainty on all local traces at `N=128`.
2. v59 for split stability at `N=128`.
3. v61 for the N-sweep phase diagram.
4. v62 for seed stability of the N-sweep.

