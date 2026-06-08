# v87 Rank-Bucket Cross-Seed Transfer

## Question

v85 showed that the rank-bucket depth allocator transfers across MATH/Llama and MATH/Gemma when the train and target splits share the same split seed. v86 showed that this transfer is not tied to one verifier-quality assumption.

The remaining reviewer attack is sharper:

> Did the cross-model result only work because the source and target train/test split seed was coupled?

v87 breaks that coupling. It trains the bucket allocator on every source model/seed calibration split and deploys it on every target model/seed test split.

## Command

```bash
python3 work/test_rank_bucket_cross_seed_transfer.py
python3 work/rank_bucket_cross_seed_transfer.py \
  --output-prefix rank_bucket_cross_seed_transfer_v87
```

## Artifacts

- [rank_bucket_cross_seed_transfer_v87.md](rank_bucket_cross_seed_transfer_v87.md)
- [rank_bucket_cross_seed_transfer_v87.csv](rank_bucket_cross_seed_transfer_v87.csv)
- [rank_bucket_cross_seed_transfer_v87_raw.csv](rank_bucket_cross_seed_transfer_v87_raw.csv)
- [rank_bucket_cross_seed_transfer_v87_summary.csv](rank_bucket_cross_seed_transfer_v87_summary.csv)
- [rank_bucket_cross_seed_transfer.py](rank_bucket_cross_seed_transfer.py)
- [test_rank_bucket_cross_seed_transfer.py](test_rank_bucket_cross_seed_transfer.py)

## Headline At 1024 Verifier Tokens/Problem

| train | target | transfer | pairs | projected acc | delta | gap vs within-same | gap vs fixed |
|---|---|---|---:|---:|---:|---:|---:|
| Gemma | Llama | cross-model/cross-seed | 6 | `0.639` | `+0.209` | `-0.019` | `+0.018` |
| Llama | Gemma | cross-model/cross-seed | 6 | `0.431` | `+0.184` | `-0.010` | `+0.036` |
| Gemma | Llama | cross-model/same-seed | 3 | `0.652` | `+0.221` | `-0.007` | `+0.031` |
| Llama | Gemma | cross-model/same-seed | 3 | `0.432` | `+0.185` | `-0.009` | `+0.037` |

## Read

The harsher cross-model/cross-seed rows still beat fixed compact rows at the high budget. On Llama targets, the transferred allocator is `+0.018` above fixed compact while trailing the target-trained within-same allocator by `0.019`. On Gemma targets, it is `+0.036` above fixed compact while trailing within-same by `0.010`.

This is a stronger allocation-transfer result than v85. The policy is not only surviving a shared split seed. The loss from decoupling seeds is visible but modest, and the cross-seed policy still spends depth usefully.

## Boundary

This is still projected allocation evidence, not a measured semantic-verifier result. The target side still supplies target-trace candidate scores, and the gains depend on assumed verifier success/false-regression rates. Use v87 to defend the allocation rule. Do not use it to claim that the verifier itself transfers or that the end-to-end method is solved.
