# v58 Cross-Trace Gap Bootstrap

**Date:** June 1, 2026  
**Question:** Is the selectability gap just a two-model MATH cherry-pick, or does the same diagnostic give a useful boundary across the local Monkey Business traces?

## Run

I reused the v57 problem-bootstrap harness with the same `N=128`, `12` trials/problem, held-out split, cheap verifier training setup, and `2000` bootstrap rounds, but added every local trace:

```bash
python3 work/canonical_gap_bootstrap_ci.py \
  --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json \
            MATH/Gemma=work/MATH_Gemma-2B.json \
            GSM8K/Llama=work/GSM8K_Llama-3-8B-Instruct.json \
            MATH/Pythia=work/MATH_Pythia-1B.json \
  --n 128 \
  --trials-per-problem 12 \
  --seed 60601 \
  --verifier-train-problems 30 \
  --audit-holdout-gap 24 \
  --verifier-samples-per-problem 800 \
  --bootstrap-rounds 2000 \
  --output-prefix cross_trace_gap_bootstrap_ci \
  --report-title "Cross-Trace Gap Bootstrap CI" \
  --report-description "Problem-bootstrap uncertainty for the same N=128 selector/oracle/depth audit across all local Monkey Business traces." \
  --read-note "The selectability gap is largest on hard MATH traces, nearly saturated on GSM8K/Llama, and still present but lower-coverage on MATH/Pythia. This makes the claim sharper: answer-cluster selectability is a stress-condition diagnostic, not a universal promise that every dataset has the same failure mode."
```

Primary artifact: [cross_trace_gap_bootstrap_ci.md](cross_trace_gap_bootstrap_ci.md).

## Result

| dataset | `cluster_sum` | oracle | headroom | top20 gain | miss p50/p75/p90 |
|---|---:|---:|---:|---:|---:|
| MATH/Llama | `0.448 [0.347, 0.561]` | `0.852 [0.778, 0.917]` | `0.404 [0.309, 0.501]` | `0.360 [0.269, 0.455]` | `6 / 11 / 21` |
| MATH/Gemma | `0.233 [0.146, 0.324]` | `0.725 [0.643, 0.803]` | `0.492 [0.402, 0.582]` | `0.402 [0.315, 0.492]` | `8 / 16 / 33` |
| GSM8K/Llama | `0.854 [0.772, 0.925]` | `0.999 [0.997, 1.000]` | `0.145 [0.075, 0.226]` | `0.144 [0.075, 0.225]` | `2 / 2 / 5` |
| MATH/Pythia | `0.046 [0.014, 0.087]` | `0.303 [0.225, 0.383]` | `0.257 [0.191, 0.324]` | `0.217 [0.154, 0.284]` | `8 / 17 / 27` |

## Read

This is a boundary result, not just another positive result.

The MATH/Llama and MATH/Gemma headline remains: repeated sampling has already generated many correct answer clusters, but the deployed selector fails to surface them. The bootstrap intervals keep that gap large.

GSM8K/Llama behaves differently. It has almost complete oracle coverage and much shallower miss ranks. That means the method should not be sold as "every benchmark has deep buried clusters." The better claim is that selectability diagnostics tell you whether a trace is in a shallow, already-surfaced regime or a hard, depth-limited regime.

MATH/Pythia is also clarifying. The model is weak and oracle coverage is only `0.303`, so generation/model capability is still a real bottleneck. Even so, among generated correct clusters, top20 inspection recovers most of the available selector headroom. This supports the decomposition: low coverage and low selectability are distinct failure modes.

## Claim Update

Safe wording:

> Across all local Monkey Business traces, the same N=128 bootstrap audit separates regimes: GSM8K/Llama is mostly surfaced, MATH/Pythia is coverage-limited but still has buried recoverable clusters, and high-N MATH/Llama/Gemma have large robust answer-cluster selectability gaps. The method should therefore be framed as a diagnostic and budget-allocation target for traces where correct answer clusters exist but are not surfaced.

Avoid wording:

> Cluster selectability is always the dominant bottleneck.

The Pythia trace shows that generation coverage can dominate. The useful contribution is the decomposition and the adaptive-depth target once coverage exists.

