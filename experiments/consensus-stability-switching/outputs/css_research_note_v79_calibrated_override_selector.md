# CSS v79: Calibrated Override Selector

**Status:** v79 research note, June 1, 2026  
**Question:** can v78's raw trained selector be turned into a safer deployed policy by keeping `cluster_sum` unless a non-baseline cluster clears a calibrated override margin?

## Why This Experiment

v78 showed that a trained visible-cluster feature selector is a better post-qwen route than another local chat prompt. It recovered `3/12` top5 deployed-mix failures in both cross-model directions. But it was not deployable:

- top10/top20 recoveries remained `0/12`,
- confidence was poorly calibrated,
- hard-packet training caused large false regressions,
- no configuration passed the conservative lower-CI-positive rule.

v79 tests the obvious next control:

```text
fit cluster selector on source packets
score baseline cluster and best non-baseline cluster
override cluster_sum only if alt_prob - baseline_prob >= calibrated threshold
score with the same v74 deployed-mix report
```

## Implementation

Scripts:

- [calibrated_override_selector.py](calibrated_override_selector.py)
- [test_calibrated_override_selector.py](test_calibrated_override_selector.py)

The script splits source packets by `orig_dset_idx` into fit/calibration sets, trains the same visible-cluster logistic selector used in v78, sweeps override margin thresholds on the source calibration split, and applies the chosen threshold to the held-out target trace.

Important bug fix: the threshold grid includes an explicit `999` no-op option. Without it, calibration can be forced to choose a negative-delta active override policy.

## Source-Calibrated Cross-Model Result

Main report:

- [source-calibrated unique cross-model report](calibrated_override_v79_unique_cross_model_report.md)

| direction | chosen threshold | calibration delta | test delta | test overrides | test recoveries | test regressions |
|---|---:|---:|---:|---:|---:|---:|
| Llama unique32 -> Gemma balanced | `999.000` | `+0.000` | `+0.000` | `0/72` | `0` | `0` |
| Gemma unique16 -> Llama balanced | `0.050` | `+0.059` | `-0.014` | `26/72` | `0` | `1` |

Read:

- Llama -> Gemma correctly calibrates to no-op once no-op is in the grid.
- Gemma -> Llama looks positive on source calibration but transfers negative.
- Source-calibrated override is not robust enough to claim deployed improvement.

## Balanced-Source Cross-Model Check

Report:

- [balanced-source cross-model report](calibrated_override_v79_balanced_cross_model_report.md)

| direction | chosen threshold | calibration delta | test delta | top5 recoveries | baseline regressions |
|---|---:|---:|---:|---:|---:|
| Llama balanced -> Gemma balanced | `0.050` | `+0.043` | `+0.000` | `3/12` | `3` |
| Gemma balanced -> Llama balanced | `999.000` | `+0.000` | `+0.000` | `0/12` | `0` |

Read:

- Balanced-source calibration does not fix the problem.
- Llama -> Gemma keeps v78's `3/12` top5 recoveries, but pays for them with `3/12` baseline-correct regressions.
- Gemma -> Llama chooses no-op.

## Target-Oracle Threshold Bound

This is not deployable. It is a diagnostic upper bound showing whether the margin score contains useful signal if threshold selection were solved.

Report:

- [oracle-threshold unique cross-model report](calibrated_override_v79_oracle_unique_cross_model_report.md)

| direction | oracle threshold | test delta | recoveries | baseline regressions | top5 recovery |
|---|---:|---:|---:|---:|---:|
| Llama unique32 -> Gemma balanced | `0.300` | `+0.014` | `1` | `0` | `1/12` |
| Gemma unique16 -> Llama balanced | `-0.025` | `+0.056` | `5` | `1` | `5/12` |

The oracle-threshold Llama result is the important one: it recovers `5/12` top5 failures and improves test-set deployed accuracy by `+0.056`, but its conservative bootstrap CI is still uncertain (`-0.036..+0.144` in the v74 report).

## Interpretation

v79 does not solve the verifier bottleneck. It does sharpen it.

What v79 proves:

- The v78 selector has real but shallow margin signal.
- A no-op option is mandatory in calibrated override search.
- Source-calibrated thresholds do not transfer reliably across Llama/Gemma traces.
- The best target-threshold policy can recover top5 failures, but not top10/top20 tails.

What v79 rules out:

- Raw feature-selector confidence is not enough.
- Simple source split calibration is not enough.
- Balanced-source calibration is not enough.
- A margin-only override policy is not yet a reviewer-safe deployed method.

## Next Experiment

The next method should be a two-head policy, not a single margin threshold:

1. a failure detector estimates whether `cluster_sum` is likely wrong and visible-correct recovery is plausible,
2. a cluster selector ranks non-baseline alternatives,
3. the override decision is trained directly against deployed utility:

```text
utility = recovery_reward - false_regression_penalty - unhelpful_override_penalty
```

The key is to learn *when* to challenge `cluster_sum`, not only which alternative cluster looks better once challenged.

## Artifacts

Core:

- [calibrated_override_selector.py](calibrated_override_selector.py)
- [test_calibrated_override_selector.py](test_calibrated_override_selector.py)
- [source-calibrated unique cross-model report](calibrated_override_v79_unique_cross_model_report.md)
- [balanced-source cross-model report](calibrated_override_v79_balanced_cross_model_report.md)
- [oracle-threshold unique cross-model report](calibrated_override_v79_oracle_unique_cross_model_report.md)

Prediction files:

- [source-calibrated Llama->Gemma predictions](calibrated_override_v79_unique_llama_to_gemma_predictions.jsonl)
- [source-calibrated Gemma->Llama predictions](calibrated_override_v79_unique_gemma_to_llama_predictions.jsonl)
- [balanced Llama->Gemma predictions](calibrated_override_v79_balanced_llama_to_gemma_predictions.jsonl)
- [balanced Gemma->Llama predictions](calibrated_override_v79_balanced_gemma_to_llama_predictions.jsonl)
- [oracle Llama->Gemma predictions](calibrated_override_v79_oracle_unique_llama_to_gemma_predictions.jsonl)
- [oracle Gemma->Llama predictions](calibrated_override_v79_oracle_unique_gemma_to_llama_predictions.jsonl)
