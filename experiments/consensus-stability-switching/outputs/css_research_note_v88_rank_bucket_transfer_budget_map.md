# v88 Rank-Bucket Transfer Budget Map

## Question

v87 showed that cross-model/cross-seed rank-bucket transfer still beats fixed compact rows at 1024 verifier tokens/problem. That is the right high-budget headline, but a reviewer can ask:

> Does the transfer result only look good because you are quoting the most favorable budget?

v88 reads the full v87 budget grid and reports where the harsh cross-model/cross-seed allocator beats fixed compact.

## Command

```bash
python3 work/test_rank_bucket_transfer_budget_map.py
python3 work/rank_bucket_transfer_budget_map.py \
  --input outputs/rank_bucket_cross_seed_transfer_v87.csv \
  --output-prefix rank_bucket_transfer_budget_map_v88
```

## Artifacts

- [rank_bucket_transfer_budget_map_v88.md](rank_bucket_transfer_budget_map_v88.md)
- [rank_bucket_transfer_budget_map_v88.csv](rank_bucket_transfer_budget_map_v88.csv)
- [rank_bucket_transfer_budget_map_v88_summary.csv](rank_bucket_transfer_budget_map_v88_summary.csv)
- [rank_bucket_transfer_budget_map.py](rank_bucket_transfer_budget_map.py)
- [test_rank_bucket_transfer_budget_map.py](test_rank_bucket_transfer_budget_map.py)

## Budget Map

| train | target | positive budgets vs fixed | best budget | best gap | worst budget | worst gap |
|---|---|---|---:|---:|---:|---:|
| Gemma | Llama | `1024` | `1024` | `+0.018` | `512` | `-0.044` |
| Llama | Gemma | `128,256,512,1024` | `1024` | `+0.036` | `256` | `+0.005` |

## Read

This does not weaken the method pitch. It makes it more precise. The transferred allocator is not a universal all-budget improvement. On Llama targets, the cross-model/cross-seed allocator loses to fixed compact at 128, 256, and 512 tokens/problem, then beats fixed at 1024. On Gemma targets, it beats fixed compact across all tested budgets, with the largest gap at 1024.

The safe claim is therefore:

> Rank-bucket transfer is a high-budget adaptive-depth allocation result for depth-limited traces. It should be reported as a budget frontier, not as universal dominance at every token budget.

## Boundary

v88 is a secondary analysis of v87. It introduces no new measured verifier evidence and inherits v87's projected verifier-success assumptions.
