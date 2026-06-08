# v86 Rank-Bucket Transfer Quality Sweep

**Date:** June 2, 2026  
**Question:** Does the v85 rank-bucket cross-model transfer result depend on the favorite `80%` verifier-success / `2%` false-regression assumption?

## Verdict

No. Lower verifier quality reduces absolute projected gains, as expected, but cross-model allocation does not collapse relative to within-model allocation.

At the focus budget of `1024` verifier tokens/problem, cross-vs-within gaps stay small across a `3 x 3` quality grid:

- harsh quality, `50%` success / `5%` false regression:
  - Gemma-trained on Llama: `0.548` projected accuracy, gap `-0.006`
  - Llama-trained on Gemma: `0.343` projected accuracy, gap `-0.005`
- default quality, `80%` success / `2%` false regression:
  - Gemma-trained on Llama: `0.652`, gap `-0.007`
  - Llama-trained on Gemma: `0.432`, gap `-0.009`
- optimistic quality, `100%` success / `0%` false regression:
  - Gemma-trained on Llama: `0.726`, gap `+0.001`
  - Llama-trained on Gemma: `0.494`, gap `-0.012`

The strongest read is not that the projected verifier assumption is proven. It is that the **allocation transfer claim** is not especially fragile to verifier-quality assumptions. v85 was not a lucky point on the quality grid.

## Run

```bash
python3 work/test_rank_bucket_transfer_quality_sweep.py
python3 work/rank_bucket_transfer_quality_sweep.py \
  --output-prefix rank_bucket_transfer_quality_sweep_v86
```

The script computes candidate scores and bucket probabilities once per seed, then sweeps the quality assumptions when computing action utility and selected depth actions.

Artifacts:

- [rank_bucket_transfer_quality_sweep_v86.md](rank_bucket_transfer_quality_sweep_v86.md)
- [rank_bucket_transfer_quality_sweep_v86.csv](rank_bucket_transfer_quality_sweep_v86.csv)
- [rank_bucket_transfer_quality_sweep_v86_raw.csv](rank_bucket_transfer_quality_sweep_v86_raw.csv)
- [rank_bucket_transfer_quality_sweep_v86_summary.csv](rank_bucket_transfer_quality_sweep_v86_summary.csv)

## Focus Table

| quality | train | target | acc mean | delta mean | gap vs within | invoke | depth20 |
|---|---|---|---:|---:|---:|---:|---:|
| `50% / 5%` | Gemma | Llama | `0.548` | `+0.117` | `-0.006` | `0.78` | `0.13` |
| `50% / 5%` | Llama | Gemma | `0.343` | `+0.096` | `-0.005` | `0.69` | `0.25` |
| `80% / 2%` | Gemma | Llama | `0.652` | `+0.221` | `-0.007` | `0.83` | `0.09` |
| `80% / 2%` | Llama | Gemma | `0.432` | `+0.185` | `-0.009` | `0.75` | `0.20` |
| `100% / 0%` | Gemma | Llama | `0.726` | `+0.295` | `+0.001` | `0.95` | `0.07` |
| `100% / 0%` | Llama | Gemma | `0.494` | `+0.247` | `-0.012` | `0.78` | `0.19` |

Across all nine quality settings at `1024` tokens/problem, the cross-model gap range is:

- Gemma -> Llama: `-0.013` to `+0.001`
- Llama -> Gemma: `-0.012` to `-0.005`

## Interpretation

The v85 result could have been a fragile artifact of one quality point. v86 says it is not. When verifier quality gets worse, the policy invokes less or shifts depth mix, but the cross-trained allocator remains close to the within-trained allocator.

This matters because v78-v82 showed that cheap override gates fail under calibration transfer, and v83-v84 showed that available local qwen3:14b judges fail under measured deployment accounting. v85-v86 carve out a more precise positive result: **the projected rank-bucket depth allocator itself is stable over seeds, trace-model transfer, and verifier-quality assumptions.**

## Caveat

This is still projected verifier-quality evidence. The decisive end-to-end benchmark still needs measured semantic verifier success and false-regression rates. v86 should be used to defend the allocation rule, not to claim a completed deployed verifier.
