# CSS v78: Deployed-Mix Feature Selector

**Status:** v78 research note, June 1, 2026  
**Question:** after local chat verifiers failed, can a trained cluster-choice model over visible packet features recover deployed-mix failures while preserving already-correct baselines?

## Why This Experiment

v75-v77 make the local qwen/gemma chat-verifier route look weak. Qwen3.5:9b is `0/6` on visible recoverable failures under slim, rich, evidence-only, and answer-only prompts. Gemma4:26b is also `0/6` and structurally unreliable.

The next plausible non-frontier route is not another prompt tweak. It is a trained cluster-choice interface:

```text
visible clusters -> feature selector -> answer/confidence -> deployed-mix report
```

This v78 test uses the same deployed-mix scoring harness as the LLM verifier runs, so recoveries, regressions, threshold fallback, natural-rate deltas, and CIs are directly comparable.

## Setup

Script:

- [deployed_mix_feature_selector.py](deployed_mix_feature_selector.py)
- [test_deployed_mix_feature_selector.py](test_deployed_mix_feature_selector.py)

The selector is a logistic cluster-correctness model over visible cluster features inherited from the hard-packet transfer baseline:

- support and support fraction,
- verifier score sum/max/mean,
- rank-by-sum,
- answer mention/proximity/magnitude features,
- digit density, text length, repetition, and representative score moments.

It emits normal verifier-style JSONL predictions:

```json
{"packet_id": "...", "answer": "...", "confidence": 0.52}
```

Those predictions are then scored by `work/deployed_mix_verifier_report.py`.

## Main Cross-Model Result

Train on the balanced deployed-mix packets from one trace and test on the other trace.

Report:

- [cross-model report](deployed_mix_feature_selector_v78_cross_model_report.md)

Raw category result:

| test dataset | train trace | baseline preserved | recoverable top5 | recoverable top10-only | recoverable top20-only | natural-rate delta |
|---|---|---:|---:|---:|---:|---:|
| MATH/Llama | Gemma | `12/12` baseline-correct | `3/12` | `0/12` | `0/12` | `+0.054`, CI `+0.000..+0.108` |
| MATH/Gemma | Llama | `9/12` baseline-correct | `3/12` | `0/12` | `0/12` | `-0.035`, CI `-0.125..+0.042` |

Read:

- This is the first post-v77 route with nonzero real deployed-mix recoveries on both traces.
- The signal is shallow: it recovers only top-5 visible failures.
- The Llama direction is nearly point-positive under the conservative bootstrap, but the lower-CI rule still refuses a positive decision.
- Gemma suffers too many baseline regressions in the balanced cross-model direction.

## Expanded Lower-Duplication Training

Train on lower-duplication expanded assets, then test on the original balanced opposite trace:

- Llama unique32 -> Gemma balanced,
- Gemma unique16 -> Llama balanced.

Report:

- [unique-train cross-model report](deployed_mix_feature_selector_v78_unique_train_cross_model_report.md)

Raw category result:

| test dataset | train asset | baseline preserved | recoverable top5 | recoverable top10-only | recoverable top20-only | natural-rate delta |
|---|---|---:|---:|---:|---:|---:|
| MATH/Gemma | Llama unique32 | `12/12` baseline-correct | `1/12` | `0/12` | `0/12` | `+0.013`, CI `+0.000..+0.040` |
| MATH/Llama | Gemma unique16 | `11/12` baseline-correct | `3/12` | `0/12` | `0/12` | `+0.018`, CI `-0.071..+0.090` |

Read:

- More/lower-duplication training makes the selector much more conservative.
- Conservative training improves baseline preservation and gives small positive point deltas.
- It reduces Gemma top-5 recovery from `3/12` to `1/12`.
- The CI gate remains negative/uncertain.

## Negative Controls

### Hard-Packet Training

Train on conditioned hard packets where `cluster_sum` is known wrong and a correct cluster is visible, then deploy on the balanced mix.

Report:

- [hardtrain cross-model report](deployed_mix_feature_selector_v78_hardtrain_cross_model_report.md)

Result:

- baseline preservation collapses to `0/12` on both baseline-correct categories,
- natural-rate deltas are strongly negative (`-0.267` Gemma, `-0.303` Llama),
- this training distribution is too aggressive for deployed use.

### Same-Model Unique-To-Balanced With Problem Filtering

Train on same-model unique assets after excluding any train packet whose `orig_dset_idx` appears in the balanced test set.

Report:

- [same-model filtered report](deployed_mix_feature_selector_v78_unique_filtered_same_model_report.md)

Result:

- Llama becomes almost pure baseline preservation: `12/12` baseline-correct preserved but `0/12` top5 recovery.
- Gemma recovers `1/12` top5 but regresses `3/12` baseline-correct rows.
- After overlap filtering, same-model training is not stronger than cross-model training.

## Interpretation

v78 changes the post-v77 story.

The cheap local LLM verifier is not just underprompted; it is currently the wrong tool. A small trained selector over cluster features can recover some visible failures that qwen/gemma chat prompts miss, but it is not yet a deployable verifier:

- it recovers top-5 failures, not buried top10/top20 tails,
- confidence is poorly aligned with true rescue cases,
- hard-failure training overcorrects and causes regressions,
- conservative expanded training preserves baselines but loses recall,
- no configuration passes the lower-CI-positive rule.

The strongest current claim is therefore:

> Cluster-choice supervision is a credible replacement research path after the local LLM verifier failure, but the current feature interface is only a top-5 rescue signal. The paper still needs either stronger reasoning-aware cluster evidence or a better calibrated invocation policy to close the depth-limited top10/top20 gap.

## Next Experiment

Do not spend more time trying to rescue local qwen/gemma prompt formats. The next aggressive route is a two-stage trained selector:

1. failure detector estimates whether to override `cluster_sum`,
2. cluster-choice model ranks non-baseline clusters only when override risk is high,
3. calibration objective directly optimizes deployed-mix delta with false-regression penalties,
4. report the same v74/v45 category, target, and CI tables.

The key missing piece is not another answer-only schema. It is calibrated override control.

## Artifacts

Core:

- [deployed_mix_feature_selector.py](deployed_mix_feature_selector.py)
- [test_deployed_mix_feature_selector.py](test_deployed_mix_feature_selector.py)
- [cross-model report](deployed_mix_feature_selector_v78_cross_model_report.md)
- [unique-train cross-model report](deployed_mix_feature_selector_v78_unique_train_cross_model_report.md)
- [hardtrain cross-model report](deployed_mix_feature_selector_v78_hardtrain_cross_model_report.md)
- [same-model filtered report](deployed_mix_feature_selector_v78_unique_filtered_same_model_report.md)

Prediction files:

- [balanced Llama->Gemma predictions](deployed_mix_feature_selector_v78_train_llama_test_gemma_predictions.jsonl)
- [balanced Gemma->Llama predictions](deployed_mix_feature_selector_v78_train_gemma_test_llama_predictions.jsonl)
- [unique Llama->Gemma predictions](deployed_mix_feature_selector_v78_unique_train_llama_test_gemma_predictions.jsonl)
- [unique Gemma->Llama predictions](deployed_mix_feature_selector_v78_unique_train_gemma_test_llama_predictions.jsonl)
