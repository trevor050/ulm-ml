# v66 Phase Depth Marginal Utility

**Date:** June 1, 2026  
**Question:** Does the phase-aware verifier policy really need deep top-20 inspection, or would shallow top-5/top-10 reranking capture the same headroom?

## Run

I computed cumulative and marginal top-k answer-cluster gains from the v62 seed-swept phase table.

```bash
python3 work/phase_depth_marginal_utility.py \
  --phase-csv outputs/cross_trace_phase_seed_sweep.csv \
  --output-prefix phase_depth_marginal_utility
```

Primary artifact: [phase_depth_marginal_utility.md](phase_depth_marginal_utility.md).

## Result

At `N=128`:

| dataset | phase | depth label | top5 gain | top10 gain | top20 gain | top10->top20 increment |
|---|---|---|---:|---:|---:|---:|
| GSM8K/Llama | shallow/surfaced | shallow-control | `0.123` | `0.131` | `0.132` | `0.001` |
| MATH/Gemma | depth-limited | deep-top20 | `0.185` | `0.302` | `0.372` | `0.070` |
| MATH/Llama | depth-limited | deep-top20 | `0.206` | `0.296` | `0.343` | `0.047` |
| MATH/Pythia | coverage-limited | coverage-first | `0.108` | `0.182` | `0.224` | `0.041` |

The phase/depth paths are also useful:

- GSM8K/Llama becomes a shallow-control case from `N=8` onward; top20 adds almost nothing beyond top10 at high N.
- MATH/Gemma becomes deep-top20 at `N=32` and stays there.
- MATH/Llama is medium-top10 around `N=16-32`, then deep-top20 at `N=64-128`.
- MATH/Pythia is coverage-first throughout, even though deeper inspection recovers some visible misses.

## Read

This tightens the adaptive-depth claim:

> The method should not always run top-20. It should use phase and marginal-depth diagnostics to decide when deeper semantic inspection is worth paying for.

That is important because a reviewer can reasonably attack "top20 verification" as an expensive post-hoc knob. v66 shows the knob is phase- and model-dependent. The hard MATH depth-limited traces have nontrivial top10->top20 increments at high N; the surfaced GSM8K trace does not; Pythia's deeper gains remain bounded by low coverage.

## Reviewer Use

If a reviewer says "why not just inspect top5 or top10?", answer:

1. On GSM8K/Llama, yes, top20 is mostly unnecessary.
2. On MATH/Llama, top10 is a good mid-N target, but top20 adds `0.047` at `N=128`.
3. On MATH/Gemma, top20 adds `0.070` beyond top10 at `N=128`.
4. On MATH/Pythia, depth helps but is not the primary bottleneck because the trace is coverage-limited.

This is the cleanest current evidence that adaptive depth should be conditional, not a universal fixed-depth recipe.
