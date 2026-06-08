# v90 Rank-Bucket Quality Region Map

## Question

v89 gives break-even verifier-quality thresholds. The next pressure test is:

> Is the transferred allocation claim stable across a quality region, or does it survive only at one hand-picked success/regression point?

v90 scans a two-dimensional verifier-quality grid for the harsh cross-model/cross-seed transfer rows.

## Command

```bash
python3 work/test_rank_bucket_quality_region_map.py
python3 work/rank_bucket_quality_region_map.py \
  --input outputs/rank_bucket_verifier_quality_targets_v89.csv \
  --output-prefix rank_bucket_quality_region_map_v90
```

## Artifacts

- [rank_bucket_quality_region_map_v90.md](rank_bucket_quality_region_map_v90.md)
- [rank_bucket_quality_region_map_v90.csv](rank_bucket_quality_region_map_v90.csv)
- [rank_bucket_quality_region_map_v90_summary.csv](rank_bucket_quality_region_map_v90_summary.csv)
- [rank_bucket_quality_region_map.py](rank_bucket_quality_region_map.py)
- [test_rank_bucket_quality_region_map.py](test_rank_bucket_quality_region_map.py)

## Region

Grid: recovery success `0.50..1.00` by `0.025`; false regression `0.00..0.10` by `0.005`.

| train | target | best budget vs fixed | fixed pass fraction | best budget vs within | within pass fraction |
|---|---|---:|---:|---:|---:|
| Gemma | Llama | 1024 | `0.422` | 512 | `0.186` |
| Llama | Gemma | 1024 | `0.565` | 128 | `0.395` |

## Read

This confirms the v88/v89 discipline. Gemma-trained allocation on Llama has a genuine but narrow fixed-frontier quality region at the high budget; the lower-budget rows are essentially not claimable. Llama-trained allocation on Gemma has a broader fixed-frontier region across budgets, with the largest region at 1024.

The target-calibrated within-same region is smaller in both directions. The safe wording remains:

> Portable rank-bucket allocation is a fixed-frontier budget result with explicit quality targets, not a claim that transferred allocation beats target-calibrated allocation.

## Boundary

v90 is a grid analysis over v89/v87 projected rows. It introduces no measured verifier evidence and inherits the same need for a stronger real verifier benchmark.
