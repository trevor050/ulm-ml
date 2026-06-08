# v85 Rank-Bucket Cross-Model Transfer

**Date:** June 2, 2026  
**Question:** Is the projected adaptive-depth result just same-model calibration, or does the rank-bucket depth-allocation mapping transfer across generator traces?

## Verdict

The rank-bucket policy transfers better than the cheap override gates did.

Training the bucket predictor on one MATH generator trace and applying it to the other keeps projected adaptive-depth gains close to within-model training. At `1024` verifier tokens/problem:

- Gemma-trained bucket allocation on Llama reaches `0.652` projected accuracy versus Llama-within `0.659`, a `-0.007` gap.
- Llama-trained bucket allocation on Gemma reaches `0.432` projected accuracy versus Gemma-within `0.441`, a `-0.009` gap.
- Both cross rows beat the fixed compact frontier at `1024`: Llama `0.652` vs `0.621`, Gemma `0.432` vs `0.395`.

This does not solve the measured-verifier hole. It does strengthen the projected method story: the learned depth-allocation mapping is not obviously a one-model artifact, even though final deployment still needs measured verifier success and false-regression rates.

## Run

```bash
python3 work/rank_bucket_cross_model_transfer.py \
  --output-prefix rank_bucket_cross_model_transfer_v85
```

The run uses three seeds (`60601,60631,60661`), MATH/Llama and MATH/Gemma N=128 traces, budgets `128,256,512,1024`, and the same projected verifier setting as v32/v33: `0.80` success and `0.02` false regression.

Artifacts:

- [rank_bucket_cross_model_transfer_v85.md](rank_bucket_cross_model_transfer_v85.md)
- [rank_bucket_cross_model_transfer_v85.csv](rank_bucket_cross_model_transfer_v85.csv)
- [rank_bucket_cross_model_transfer_v85_raw.csv](rank_bucket_cross_model_transfer_v85_raw.csv)

## Focus Table

| train | target | budget | transfer | acc mean | delta mean | gap vs within | fixed compact | invoke | depth mix |
|---|---|---:|---|---:|---:|---:|---:|---:|---|
| Gemma | Llama | 512 | cross | `0.605` | `+0.174` | `+0.015` | `0.621` | `0.53` | 5:`0.10`, 10:`0.42`, 20:`0.01` |
| Gemma | Llama | 1024 | cross | `0.652` | `+0.221` | `-0.007` | `0.621` | `0.83` | 5:`0.18`, 10:`0.55`, 20:`0.09` |
| Llama | Gemma | 512 | cross | `0.367` | `+0.120` | `-0.001` | `0.348` | `0.48` | 5:`0.10`, 10:`0.37`, 20:`0.02` |
| Llama | Gemma | 1024 | cross | `0.432` | `+0.185` | `-0.009` | `0.395` | `0.75` | 5:`0.11`, 10:`0.44`, 20:`0.20` |

The 512-token rows are mixed. Gemma-to-Llama at 512 is close to within training but trails the fixed compact Llama row (`0.605` vs `0.621`), while Llama-to-Gemma beats fixed compact (`0.367` vs `0.348`). At 1024 tokens, both cross-transfer rows beat fixed compact rows.

## Relation To v78-v84

v78-v82 showed that cheap deployed override gates are shallow and calibration-fragile. Source-calibrated gates can be safe but flat, and target-oracle gains mostly recover shallow top5 cases rather than top10/top20 tails.

v83-v84 showed that available local qwen3:14b verifier prompts are not deployable, even with the original problem and richer evidence.

v85 is a different question. It does not ask whether the local judge can identify the correct cluster. It asks whether the **allocation policy over depth** is stable across generator traces, assuming a verifier with known success/regression rates. The answer is encouraging: the bucket-depth policy is much more transferable than the cheap override gates.

## Pitch Impact

The paper can now separate three claims:

1. **Diagnostic claim:** hard MATH has a large answer-cluster selectability gap with correct clusters often buried beyond top-3.
2. **Policy claim:** rank-bucket adaptive depth is a plausible budget allocator and transfers across Llama/Gemma under the projected verifier model.
3. **Deployment claim:** no available local qwen/gemma verifier has yet supplied the measured recovery/preservation rates needed for an end-to-end positive result.

This is a better story than "adaptive depth works in one split." The method-facing result is now: depth allocation has seed stability (v33) and cross-model transfer (v85), while the missing ingredient is measured semantic verification quality, not an obviously overfit allocation rule.

## Caveat

The target rows still use the target trace's own candidate-verifier scores and labels. This isolates transfer of the bucket-depth mapping, not full transfer of an external verifier or confidence model. Treat v85 as projected allocation robustness, not measured deployed accuracy.
