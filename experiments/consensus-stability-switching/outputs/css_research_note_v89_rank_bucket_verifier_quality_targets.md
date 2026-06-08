# v89 Rank-Bucket Verifier Quality Targets

## Question

v88 made the budget caveat explicit. The next reviewer question is:

> What verifier quality would the transferred rank-bucket allocator actually need for the budget-frontier claim to survive?

v89 solves the projected deployment equation for each harsh cross-model/cross-seed transfer row:

`accuracy = cluster_sum + success * recoverable_invoked_rate - false_regress * false_or_unhelpful_invoked_rate`

## Command

```bash
python3 work/test_rank_bucket_verifier_quality_targets.py
python3 work/rank_bucket_verifier_quality_targets.py \
  --input outputs/rank_bucket_cross_seed_transfer_v87_raw.csv \
  --output-prefix rank_bucket_verifier_quality_targets_v89
```

## Artifacts

- [rank_bucket_verifier_quality_targets_v89.md](rank_bucket_verifier_quality_targets_v89.md)
- [rank_bucket_verifier_quality_targets_v89.csv](rank_bucket_verifier_quality_targets_v89.csv)
- [rank_bucket_verifier_quality_targets_v89_summary.csv](rank_bucket_verifier_quality_targets_v89_summary.csv)
- [rank_bucket_verifier_quality_targets.py](rank_bucket_verifier_quality_targets.py)
- [test_rank_bucket_verifier_quality_targets.py](test_rank_bucket_verifier_quality_targets.py)

## Fixed-Frontier Contract

At the reference `80%` verifier success / `2%` false-regression operating point:

| train | target | budget | gap vs fixed | success needed at 2% false | false ceiling at 80% success |
|---|---|---:|---:|---:|---:|
| Gemma | Llama | 128 | `-0.015` | `1.063` | `-0.157` |
| Gemma | Llama | 256 | `-0.020` | `0.977` | `-0.104` |
| Gemma | Llama | 512 | `-0.044` | `1.027` | `-0.112` |
| Gemma | Llama | 1024 | `+0.018` | `0.734` | `0.054` |
| Llama | Gemma | 128 | `+0.007` | `0.664` | `0.095` |
| Llama | Gemma | 256 | `+0.005` | `0.745` | `0.050` |
| Llama | Gemma | 512 | `+0.017` | `0.693` | `0.070` |
| Llama | Gemma | 1024 | `+0.036` | `0.651` | `0.089` |

## Stricter Stress Test

Against target-calibrated within-model/same-seed allocation, transfer is mostly below the within-same row. Gemma-trained allocation on Llama loses at every tested budget; Llama-trained allocation on Gemma is positive only at 128 and 256 tokens/problem under the reference assumption.

This should discipline the wording:

> The portable rank-bucket result is a fixed-frontier/budget-frontier claim, not a claim that zero-shot allocation beats target-calibrated allocation.

## Read

The v87/v88 high-budget transfer claim is now quality-testable. The cleanest portable headline is still the 1024-token fixed-frontier row: Gemma-trained allocation on Llama needs about `73%` recovery success at `2%` false regression, while Llama-trained allocation on Gemma needs about `65%`. Lower-budget Gemma-to-Llama rows should not be claimed, because they require unrealistic or impossible quality under the same false-regression level.

## Boundary

v89 is algebra over v87 projected rows. It introduces no measured verifier evidence, but it converts the projection into explicit success/regression targets for the next real verifier benchmark.
