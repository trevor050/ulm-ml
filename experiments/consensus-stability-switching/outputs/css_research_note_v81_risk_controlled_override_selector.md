# v81 Risk-Controlled Override Selector

## Question

Can the v80 utility gate be made more reviewer-safe by calibrating it as an abstention policy?

Instead of maximizing source calibration delta, v81 asks:

```text
Only allow an active override threshold if source calibration has at least one recovery
and zero baseline-correct regressions. Otherwise choose no-op.
```

This is the conservative version of the two-head override idea: the selector proposes the best non-baseline alternative, while the gate may challenge `cluster_sum` only when calibration evidence clears a fixed regression budget.

## Implementation

New script:

- [risk_controlled_override_selector.py](risk_controlled_override_selector.py)
- [test_risk_controlled_override_selector.py](test_risk_controlled_override_selector.py)

The script reuses the v80 selector/gate implementation, but changes threshold selection:

- source-risk threshold: choose the highest-recovery threshold with calibration recoveries `>= 1` and baseline regressions `<= 0`;
- no-op fallback: if no threshold qualifies, choose the no-op threshold;
- target-oracle row: choose the best threshold under the same rule on the target split, for diagnostics only.

## Source-Risk Cross-Model Result

Main reports:

- [balanced cross-model report](risk_controlled_override_v81_balanced_cross_model_report.md)
- [unique-source cross-model report](risk_controlled_override_v81_unique_cross_model_report.md)
- [balanced Llama->Gemma policy](risk_controlled_override_v81_balanced_llama_to_gemma.md)
- [balanced Gemma->Llama policy](risk_controlled_override_v81_balanced_gemma_to_llama.md)
- [unique Llama->Gemma policy](risk_controlled_override_v81_unique_llama_to_gemma.md)
- [unique Gemma->Llama policy](risk_controlled_override_v81_unique_gemma_to_llama.md)

| train -> test | source threshold | source calibration evidence | test delta | test recoveries | test regressions |
|---|---:|---|---:|---:|---:|
| Llama balanced -> Gemma balanced | `0.500` | `2` recoveries, `0` regressions | `+0.000` | `0` | `0` |
| Gemma balanced -> Llama balanced | `2.000` | no eligible safe recovery | `+0.000` | `0` | `0` |
| Llama unique32 -> Gemma balanced | `0.250` | `4` recoveries, `0` regressions | `+0.000` | `0` | `0` |
| Gemma unique16 -> Llama balanced | `2.000` | no eligible safe recovery | `+0.000` | `0` | `0` |

The risk control does what it is supposed to do: it avoids target baseline regressions. But it still recovers no target failures. In the two Llama->Gemma directions, source calibration sees apparently safe recoveries and transfers to zero target recoveries.

## Target-Oracle Diagnostic

Target-oracle reports:

- [target-oracle balanced report](risk_controlled_override_v81_target_oracle_balanced_cross_model_report.md)
- [target-oracle unique-source report](risk_controlled_override_v81_target_oracle_unique_cross_model_report.md)

| train -> test | target-oracle threshold | test delta | recoveries | regressions | depth recovered |
|---|---:|---:|---:|---:|---|
| Llama balanced -> Gemma balanced | `2.000` | `+0.000` | `0` | `0` | none |
| Gemma balanced -> Llama balanced | `0.050` | `+0.028` | `2` | `0` | top5 only |
| Llama unique32 -> Gemma balanced | `2.000` | `+0.000` | `0` | `0` | none |
| Gemma unique16 -> Llama balanced | `0.950` | `+0.028` | `2` | `0` | top5 only |

Even when threshold choice is solved with target labels, the policy finds only two Llama top5 recoveries and no top10/top20 recoveries. The deployed-mix CI reports remain conservative non-passes; the lower CI does not become positive.

## Interpretation

v81 is useful as a safety-calibration falsification.

What it adds over v80:

- source-risk thresholding removes the obvious overactive-gate failure mode;
- apparent source-safe recoveries still do not transfer to Gemma;
- target-oracle signal is smaller than the v79/v80 optimistic oracle rows and remains shallow;
- the feature-selector family still cannot reach the top10/top20 tail that motivates adaptive depth.

What not to claim:

- Do not claim risk-controlled override improves deployed accuracy.
- Do not claim cheap surface-feature gates solve regression-aware calibration.
- Do not use the target-oracle rows as deployed evidence.

## Paper Consequence

Use v81 as the final cheap-selector guardrail result:

> A conservative abstention gate can make the trained override policy safe, but only by becoming flat out-of-source. Even source thresholds with apparent safe recoveries transfer to zero target recoveries, and target-oracle thresholds recover only shallow Llama top5 cases. The deployed-mix bottleneck remains a real verifier or a substantially stronger calibration signal, not another shallow feature gate.

That strengthens the current pitch: answer-cluster depth is real, but local cheap selectors are diagnostic foils rather than the method.

## Next Experiment

Stop spending primary effort on one-off shallow selector variants. The next decisive experiment is a measured verifier on the deployed-mix panels with a stronger model endpoint.

If staying local, the narrow follow-up is a calibration-stability audit over many source splits, but v81 says the expected outcome is mostly no-op unless the positive recovery pool is expanded.

## Artifacts

- [risk_controlled_override_selector.py](risk_controlled_override_selector.py)
- [test_risk_controlled_override_selector.py](test_risk_controlled_override_selector.py)
- [balanced cross-model report](risk_controlled_override_v81_balanced_cross_model_report.md)
- [unique-source cross-model report](risk_controlled_override_v81_unique_cross_model_report.md)
- [target-oracle balanced report](risk_controlled_override_v81_target_oracle_balanced_cross_model_report.md)
- [target-oracle unique-source report](risk_controlled_override_v81_target_oracle_unique_cross_model_report.md)
