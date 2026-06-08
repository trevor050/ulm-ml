# v65 Verifier Quality Sensitivity

**Date:** June 1, 2026  
**Question:** Does phase-aware verifier triage depend on one optimistic verifier-quality assumption?

## Run

I swept verifier success and false-regression assumptions over the v62/v63 phase rows.

```bash
python3 work/verifier_quality_sensitivity.py \
  --phase-csv outputs/cross_trace_phase_seed_sweep.csv \
  --output-prefix verifier_quality_sensitivity
```

Primary artifact: [verifier_quality_sensitivity.md](verifier_quality_sensitivity.md).

## Result

At `N=128`:

| dataset | phase read | stress label | positive grid share | min success at 5% false regression | delta at 50% success / 5% regression |
|---|---|---|---:|---:|---:|
| GSM8K/Llama | shallow/surfaced | positive-but-low-priority | `0.600` | `0.330` | `+0.022` |
| MATH/Gemma | depth-limited | robust-spend | `0.900` | `0.084` | `+0.155` |
| MATH/Llama | depth-limited | robust-spend | `0.900` | `0.096` | `+0.138` |
| MATH/Pythia | coverage-limited | positive-but-coverage-capped | `0.767` | `0.173` | `+0.073` |

The key stress result:

> Depth-limited MATH remains a positive top20 verifier target even if the verifier succeeds only 50% of the time and false-regresses 5% of unhelpful invocations.

## Read

v65 strengthens v63. The MATH verifier-spend recommendation does not rely on an 80% success / 2% false-regression point estimate. That does not prove a real verifier will work, but it means the next measured verifier benchmark is not a toy: if a real verifier fails on depth-limited MATH, the failure is informative.

The controls stay useful:

- GSM8K/Llama can be positive, but it is low-priority because the baseline selector is already strong.
- MATH/Pythia can recover some top20 misses, but the final accuracy remains coverage-capped.

## Reviewer Use

If a reviewer attacks the projected verifier model, v65 gives the honest answer:

1. The real verifier is still missing.
2. The spend decision is robust over a broad quality grid for depth-limited MATH.
3. The benchmark should report measured success/regression by phase, because surfaced and coverage-limited regimes have different interpretations.
