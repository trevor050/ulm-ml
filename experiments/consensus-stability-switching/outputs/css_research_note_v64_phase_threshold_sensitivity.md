# v64 Phase Threshold Sensitivity

**Date:** June 1, 2026
**Question:** Does the v61/v62 phase diagram survive plausible changes to the hand-set regime thresholds?

## Run

This reuses the existing three-seed phase sweep raw CSV and reclassifies every dataset/N/seed row under a grid of threshold choices. It does not rescore the large traces.

```bash
python3 work/phase_threshold_sensitivity.py --input outputs/cross_trace_phase_seed_sweep_raw.csv --output-prefix phase_threshold_sensitivity --note-version v64
```

Threshold grid: surfaced oracle `[0.9, 0.95, 0.98]`, surfaced headroom `[0.15, 0.2, 0.25]`, coverage oracle `[0.35, 0.4, 0.45]`, depth headroom `[0.25, 0.3, 0.35]`. Total configs: `81`.

Primary artifact: [phase_threshold_sensitivity.csv](phase_threshold_sensitivity.csv).

## Result

| dataset | N | dominant regime | dominant share | coverage | mixed | depth | surfaced | oracle | cluster_sum | headroom | top20 gain |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GSM8K/Llama | 4 | mixed | 0.667 | 0.000 | 0.667 | 0.000 | 0.333 | 0.925 | 0.832 | 0.093 | 0.093 |
| GSM8K/Llama | 8 | shallow/surfaced | 0.667 | 0.000 | 0.333 | 0.000 | 0.667 | 0.964 | 0.844 | 0.120 | 0.120 |
| GSM8K/Llama | 16 | shallow/surfaced | 0.889 | 0.000 | 0.111 | 0.000 | 0.889 | 0.983 | 0.858 | 0.125 | 0.125 |
| GSM8K/Llama | 32 | shallow/surfaced | 1.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.989 | 0.861 | 0.127 | 0.127 |
| GSM8K/Llama | 64 | shallow/surfaced | 0.778 | 0.000 | 0.222 | 0.000 | 0.778 | 0.993 | 0.856 | 0.137 | 0.137 |
| GSM8K/Llama | 128 | shallow/surfaced | 0.889 | 0.000 | 0.111 | 0.000 | 0.889 | 0.996 | 0.865 | 0.132 | 0.132 |
| MATH/Gemma | 4 | coverage-limited | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.229 | 0.140 | 0.089 | 0.089 |
| MATH/Gemma | 8 | coverage-limited | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.305 | 0.163 | 0.142 | 0.142 |
| MATH/Gemma | 16 | mixed | 0.556 | 0.444 | 0.556 | 0.000 | 0.000 | 0.402 | 0.182 | 0.221 | 0.221 |
| MATH/Gemma | 32 | depth-limited | 0.556 | 0.000 | 0.444 | 0.556 | 0.000 | 0.517 | 0.199 | 0.317 | 0.306 |
| MATH/Gemma | 64 | depth-limited | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.595 | 0.223 | 0.372 | 0.321 |
| MATH/Gemma | 128 | depth-limited | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.691 | 0.236 | 0.455 | 0.372 |
| MATH/Llama | 4 | mixed | 1.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.479 | 0.327 | 0.152 | 0.152 |
| MATH/Llama | 8 | mixed | 1.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.576 | 0.366 | 0.211 | 0.211 |
| MATH/Llama | 16 | mixed | 0.667 | 0.000 | 0.667 | 0.333 | 0.000 | 0.667 | 0.398 | 0.270 | 0.270 |
| MATH/Llama | 32 | depth-limited | 0.556 | 0.000 | 0.444 | 0.556 | 0.000 | 0.728 | 0.422 | 0.306 | 0.303 |
| MATH/Llama | 64 | depth-limited | 0.778 | 0.000 | 0.222 | 0.778 | 0.000 | 0.776 | 0.431 | 0.345 | 0.327 |
| MATH/Llama | 128 | depth-limited | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.826 | 0.442 | 0.384 | 0.343 |
| MATH/Pythia | 4 | coverage-limited | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.034 | 0.019 | 0.015 | 0.015 |
| MATH/Pythia | 8 | coverage-limited | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.068 | 0.021 | 0.047 | 0.047 |
| MATH/Pythia | 16 | coverage-limited | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.099 | 0.025 | 0.074 | 0.074 |
| MATH/Pythia | 32 | coverage-limited | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.145 | 0.030 | 0.115 | 0.115 |
| MATH/Pythia | 64 | coverage-limited | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.229 | 0.034 | 0.195 | 0.180 |
| MATH/Pythia | 128 | coverage-limited | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.313 | 0.042 | 0.271 | 0.224 |

## Paths

| dataset | threshold-sensitive path | high-N read | min high-N dominant share |
|---|---|---|---:|
| GSM8K/Llama | N=4:mixed(0.667) -> N=8:shallow/surfaced(0.667) -> N=16:shallow/surfaced(0.889) -> N=32:shallow/surfaced(1.000) -> N=64:shallow/surfaced(0.778) -> N=128:shallow/surfaced(0.889) | N=64 shallow/surfaced 0.778; N=128 shallow/surfaced 0.889 | 0.778 |
| MATH/Gemma | N=4:coverage-limited(1.000) -> N=8:coverage-limited(1.000) -> N=16:mixed(0.556) -> N=32:depth-limited(0.556) -> N=64:depth-limited(1.000) -> N=128:depth-limited(1.000) | N=64 depth-limited 1.000; N=128 depth-limited 1.000 | 1.000 |
| MATH/Llama | N=4:mixed(1.000) -> N=8:mixed(1.000) -> N=16:mixed(0.667) -> N=32:depth-limited(0.556) -> N=64:depth-limited(0.778) -> N=128:depth-limited(1.000) | N=64 depth-limited 0.778; N=128 depth-limited 1.000 | 0.778 |
| MATH/Pythia | N=4:coverage-limited(1.000) -> N=8:coverage-limited(1.000) -> N=16:coverage-limited(1.000) -> N=32:coverage-limited(1.000) -> N=64:coverage-limited(1.000) -> N=128:coverage-limited(1.000) | N=64 coverage-limited 1.000; N=128 coverage-limited 1.000 | 1.000 |

## Read

The high-N conclusion is not a fragile artifact of one cutoff. MATH/Gemma is unanimously depth-limited at N=64/128 across the threshold grid; MATH/Llama is depth-limited under all N=128 settings and remains dominantly depth-limited at N=64. MATH/Pythia remains unanimously coverage-limited. GSM8K/Llama is the deliberately threshold-sensitive edge case: it has near-perfect oracle coverage but headroom around 0.13, so strict shallow-headroom thresholds can relabel some rows as mixed. That sensitivity is informative rather than damaging, because GSM8K is still not a buried-depth stress case.

Reviewer-facing language should quote the continuous metrics first and the regime words second. The regime labels are useful shorthand, but the durable evidence is the oracle/cluster_sum/headroom/top20 pattern.

CSV: [phase_threshold_sensitivity.csv](phase_threshold_sensitivity.csv).
Transitions CSV: [phase_threshold_sensitivity_transitions.csv](phase_threshold_sensitivity_transitions.csv).