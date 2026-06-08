# v63 Phase-Aware Verifier Triage

**Date:** June 1, 2026  
**Question:** Does the seed-stable phase diagram imply a concrete verifier-spend policy?

## Run

I converted the v62 phase seed sweep into a spend/no-spend audit for a hypothetical top-20 answer-cluster verifier.

```bash
python3 work/phase_aware_verifier_triage.py \
  --phase-csv outputs/cross_trace_phase_seed_sweep.csv \
  --output-prefix phase_aware_verifier_triage
```

Primary artifact: [phase_aware_verifier_triage.md](phase_aware_verifier_triage.md).

## Result

Under an 80% success / 2% false-regression assumption, the N=128 reads are:

| dataset | phase | action | cluster_sum | oracle | top20 gain | projected delta | projected acc |
|---|---|---|---:|---:|---:|---:|---:|
| GSM8K/Llama | shallow/surfaced | defer/mostly-surfaced | `0.865` | `0.996` | `0.132` | `+0.088` | `0.952` |
| MATH/Gemma | depth-limited | spend/depth-20 | `0.236` | `0.691` | `0.372` | `+0.285` | `0.521` |
| MATH/Llama | depth-limited | spend/depth-20 | `0.442` | `0.826` | `0.343` | `+0.261` | `0.703` |
| MATH/Pythia | coverage-limited | defer/generate-coverage | `0.042` | `0.313` | `0.224` | `+0.163` | `0.206` |

The first clean spend point for both hard MATH traces is `N=32`. At that point:

- MATH/Gemma has top20 gain `0.306` and top20 closes `0.965` of available headroom.
- MATH/Llama has top20 gain `0.303` and top20 closes `0.990` of available headroom.

The break-even recovery requirement is low in the intended regime. At `N=128`, if false regression is 2%, the required verifier success is only `0.034` for MATH/Gemma and `0.038` for MATH/Llama. At 5% false regression, it is still only `0.084` and `0.096`. That is the strongest local argument for testing a real verifier on depth-limited MATH first.

## Read

v63 turns the phase diagram into an operational rule:

- **Depth-limited:** spend verifier budget on cluster depth.
- **Shallow/surfaced:** use as a control or skip unless residual accuracy is worth the cost.
- **Coverage-limited:** improve generation/model coverage first; top20 verification may recover some misses but cannot make the system broadly accurate.

This avoids the sloppy claim "verification helps test-time scaling." The narrower claim is:

> Once a trace enters the depth-limited phase, answer-cluster verification has a large possible payoff and a low break-even recovery requirement; outside that phase, verifier budget is either lower priority or solving the wrong bottleneck.

## Reviewer Use

If a reviewer says "your phase labels are descriptive, not methodological," point to v63. It gives a pre-verifier routing decision:

1. Run the measured semantic verifier first on MATH/Llama and MATH/Gemma depth-limited top20 prompts.
2. Keep GSM8K/Llama and MATH/Pythia as boundary controls.
3. Report success/regression separately by phase, not just aggregate accuracy.

This still does not replace the missing real verifier run. It makes that run sharper and harder to waste.
