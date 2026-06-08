# v61 Selectability Phase Diagram

**Date:** June 1, 2026  
**Question:** How do trace regimes change as sample count increases?

## Run

I swept `N = 4, 8, 16, 32, 64, 128` across every local Monkey Business trace, using the same cheap verifier and answer-cluster depth metrics as v57-v59.

```bash
python3 work/cross_trace_phase_diagram.py \
  --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json \
            MATH/Gemma=work/MATH_Gemma-2B.json \
            GSM8K/Llama=work/GSM8K_Llama-3-8B-Instruct.json \
            MATH/Pythia=work/MATH_Pythia-1B.json \
  --ns 4 8 16 32 64 128 \
  --trials-per-problem 12 \
  --seed 60601 \
  --verifier-train-problems 30 \
  --audit-holdout-gap 24 \
  --verifier-samples-per-problem 800 \
  --output-prefix cross_trace_phase_diagram
```

Primary artifact: [cross_trace_phase_diagram.md](cross_trace_phase_diagram.md).

## Result

| dataset | regime path | max headroom | final N=128 read |
|---|---|---:|---|
| GSM8K/Llama | mixed -> shallow/surfaced -> shallow/surfaced -> shallow/surfaced -> shallow/surfaced -> shallow/surfaced | `N=64 0.153` | oracle `1.000`, `cluster_sum 0.849` |
| MATH/Gemma | coverage-limited -> coverage-limited -> mixed -> depth-limited -> depth-limited -> depth-limited | `N=128 0.508` | oracle `0.747`, `cluster_sum 0.239` |
| MATH/Llama | mixed -> mixed -> mixed -> depth-limited -> depth-limited -> depth-limited | `N=128 0.414` | oracle `0.856`, `cluster_sum 0.441` |
| MATH/Pythia | coverage-limited -> coverage-limited -> coverage-limited -> coverage-limited -> coverage-limited -> coverage-limited | `N=128 0.278` | oracle `0.314`, `cluster_sum 0.036` |

The key transition is at roughly `N=32` for the hard MATH traces:

| dataset | N=16 headroom | N=32 headroom | N=128 headroom | read |
|---|---:|---:|---:|---|
| MATH/Llama | `0.262` | `0.312` | `0.414` | depth-limited from N=32 onward |
| MATH/Gemma | `0.221` | `0.324` | `0.508` | depth-limited from N=32 onward |
| GSM8K/Llama | `0.134` | `0.132` | `0.151` | high coverage, shallow/surfaced |
| MATH/Pythia | `0.078` | `0.132` | `0.278` | coverage-limited throughout |

## Read

This is the cleanest form of the diagnostic so far.

At low N, many traces are still coverage-limited or mixed. As N rises, stronger hard-MATH models generate enough correct answer clusters that selection becomes the bottleneck. The gap does not appear because the model never sampled the answer; it appears because the answer exists but is buried below the selector frontier. That is the depth-limited regime.

GSM8K/Llama shows the opposite boundary: by `N=8`, the trace is mostly surfaced. A shallow/self-consistency-like method is much closer to sufficient there.

MATH/Pythia shows the low-capability boundary: even at `N=128`, oracle coverage is only `0.314`. More or better generation still matters before adaptive depth can be the main story.

## Claim Update

Safe wording:

> Answer-cluster selectability is a phase diagnostic for test-time scaling. Increasing N can move a trace from coverage-limited to depth-limited once correct answer clusters are generated often enough. Adaptive cluster-depth verification is aimed at the depth-limited phase, not at shallow/surfaced traces or low-coverage traces.

This makes the method pitch more precise:

1. Diagnose the trace regime as N changes.
2. If shallow/surfaced, use cheap selectors or short-trace methods.
3. If coverage-limited, spend on generation/model capability.
4. If depth-limited, spend on failure-activated cluster-depth verification.

