# v82 Override Calibration Stability Audit

## Question

Were v80 and v81 just unlucky single-split failures, or is the cheap override family systematically unable to transfer calibration and recover the depth-limited tail?

v82 repeats the v80/v81 source calibration story over eight problem-level split seeds and four train/test directions:

- Llama unique32 -> Gemma balanced
- Gemma unique16 -> Llama balanced
- Llama balanced -> Gemma balanced
- Gemma balanced -> Llama balanced

For each split, it scores four policies:

- `source_utility`: v80 source-calibrated utility-max threshold.
- `source_risk`: v81 risk-controlled threshold, requiring source recoveries and zero source baseline regressions.
- `target_oracle_utility`: target-label best utility threshold, diagnostic only.
- `target_oracle_risk`: target-label risk-controlled threshold, diagnostic only.

## Implementation

New script:

- [override_calibration_stability_audit.py](override_calibration_stability_audit.py)
- [test_override_calibration_stability_audit.py](test_override_calibration_stability_audit.py)

Main artifacts:

- [audit report](override_calibration_stability_v82.md)
- [summary CSV](override_calibration_stability_v82_summary.csv)
- [detail CSV](override_calibration_stability_v82_details.csv)

The default run uses seeds `60601..60608`, threshold grid `0.05..0.95,2`, source split `0.45 selector / 0.30 gate / remainder calibration`, and smaller but still nontrivial training loops (`1200` selector steps, `800` gate steps) to make the seed sweep feasible on the M1 Air.

## Results

The source-calibrated policies are not reliable deployable methods:

- Deployable source-calibrated rows selected active gates in `23/64` runs.
- Those active source gates produced zero target recoveries in `12/23` active runs.
- Source policies frequently traded shallow recovery against baseline regression, or transferred to no recovery at all.

The target-oracle diagnostics are also shallow:

- Across all target-oracle rows, top10-only recoveries totaled `2`.
- Across all target-oracle rows, top20-only recoveries totaled `0`.
- The strongest oracle rows are Gemma->Llama and still only recover top5 cases.

Representative summary rows:

| config | policy | active | mean delta | pos delta | mean rec | mean reg | top5 | top10-only | top20-only |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unique_gemma_to_llama | target_oracle_utility | `1.000` | `+0.033` | `1.000` | `2.62` | `0.25` | `2.62` | `0.00` | `0.00` |
| unique_gemma_to_llama | target_oracle_risk | `0.875` | `+0.030` | `0.875` | `2.12` | `0.00` | `2.12` | `0.00` | `0.00` |
| unique_llama_to_gemma | target_oracle_utility | `0.250` | `+0.016` | `0.250` | `1.38` | `0.25` | `1.25` | `0.12` | `0.00` |
| balanced_llama_to_gemma | target_oracle_utility | `0.000` | `+0.000` | `0.000` | `0.00` | `0.00` | `0.00` | `0.00` | `0.00` |

## Interpretation

v82 turns the v80/v81 result from a one-split failure into a stability claim.

The cheap selector family is not merely failing because a single calibration split was unlucky. Across repeated source splits:

- source-calibrated active thresholds often do not transfer,
- target-oracle headroom remains small and shallow,
- top10-only recovery is nearly absent,
- top20-only recovery is absent,
- conservative risk control mostly makes the policy safe by making it flat.

This is useful because it draws a hard line around what the current feature-only selector family can and cannot do.

## Paper Consequence

Use v82 to support this wording:

> We tested the natural cheap-selector follow-up family after the local LLM verifier failed: raw feature selection, margin override, utility-gated override, risk-controlled abstention, and an eight-seed calibration stability audit. These methods can sometimes recover shallow top5 failures, but they do not recover the top10/top20 tail that motivates adaptive cluster-depth verification. The remaining bottleneck is not another shallow surface-feature gate; it is a stronger measured verifier or a richer cluster-scoring signal.

This strengthens the adaptive-depth pitch. The method target is not "learn a cheap selector that magically fixes deployment." The target is to measure and allocate verifier depth where shallow selectors demonstrably run out.

## Next Experiment

The next decisive route is a measured deployed-mix verifier with a stronger endpoint.

If no stronger endpoint is available, the best local follow-up is not another one-off gate. It is either:

1. expand positive recovery calibration data by adding more traces/models/tasks, or
2. build a verifier-interface experiment that creates richer semantic cluster scores than current surface features.

Pulling a stronger Ollama model onto the RTX box may be worthwhile, but should be an explicit compute/disk choice because the currently installed models are only `llama3.2:1b`, `qwen3.5:9b`, and `gemma4:26b`, and the plausible installed judges have already produced targeted negative probes.
