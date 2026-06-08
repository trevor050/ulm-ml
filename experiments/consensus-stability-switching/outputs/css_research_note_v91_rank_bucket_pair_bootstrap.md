# v91 Rank-Bucket Pair-Bootstrap Transfer Audit

## Question

v87-v90 make the portable fixed-frontier transfer claim increasingly explicit. The next reviewer attack is:

> Are the cross-model/cross-seed gaps stable across train/target seed pairs, or is the mean hiding bad split-pair variance?

v91 bootstraps the six cross-model/cross-seed train/target seed-pair rows from v87.

## Command

```bash
python3 work/test_rank_bucket_pair_bootstrap.py
python3 work/rank_bucket_pair_bootstrap.py \
  --input outputs/rank_bucket_cross_seed_transfer_v87_raw.csv \
  --output-prefix rank_bucket_pair_bootstrap_v91
```

## Artifacts

- [rank_bucket_pair_bootstrap_v91.md](rank_bucket_pair_bootstrap_v91.md)
- [rank_bucket_pair_bootstrap_v91.csv](rank_bucket_pair_bootstrap_v91.csv)
- [rank_bucket_pair_bootstrap_v91_summary.csv](rank_bucket_pair_bootstrap_v91_summary.csv)
- [rank_bucket_pair_bootstrap.py](rank_bucket_pair_bootstrap.py)
- [test_rank_bucket_pair_bootstrap.py](test_rank_bucket_pair_bootstrap.py)

## Result

| train | target | budget | fixed gap mean | pair signs | bootstrap 95% | Pr(mean>0) |
|---|---|---:|---:|---:|---:|---:|
| Gemma | Llama | 1024 | `+0.018` | `5/6` | `[-0.006,+0.038]` | `0.938` |
| Llama | Gemma | 1024 | `+0.036` | `6/6` | `[+0.027,+0.044]` | `1.000` |

## Read

This is a useful split in the claim. Llama-trained allocation on Gemma is the cleaner portable fixed-frontier result: all six seed pairs are positive, and the pair-bootstrap interval stays above zero. Gemma-trained allocation on Llama remains directionally positive at 1024, but its lower bound is fragile because one seed pair is negative and the 95% bootstrap interval crosses zero.

The paper should therefore phrase the transfer evidence asymmetrically:

> Cross-model/cross-seed transfer clearly supports Llama-trained-on-Gemma as a stable fixed-frontier improvement, while Gemma-trained-on-Llama is promising at high budget but lower-bound fragile under the current six-pair audit.

## Boundary

v91 is a seed-pair bootstrap over projected allocation rows. It does not introduce measured verifier evidence, and six pair rows are too few for a strong statistical claim. It is an honest robustness audit, not a final generalization proof.
