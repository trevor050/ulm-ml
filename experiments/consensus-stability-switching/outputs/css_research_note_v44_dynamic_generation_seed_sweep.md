# v44 - Dynamic Generation Seed Sweep

**Status:** June 1, 2026. Three-seed robustness sweep for the fine-grained token-matched generation baseline.

## Why This Exists

v43 removed the obvious coarse-chunk objection by rerunning token-matched dynamic extra sampling with 8-sample chunks. But it was still one train/calibration/test split.

v44 asks:

> Is the weak fine-grained dynamic generation result just a lucky split?

## Artifacts

```text
outputs/dynamic_generation_seed_sweep.md
outputs/dynamic_generation_seed_sweep.csv
outputs/dynamic_generation_seed_sweep_seed_summary.csv
outputs/dynamic_generation_seed_sweep_dynamic_raw.csv
```

Script:

```text
work/dynamic_generation_seed_sweep.py
```

Command:

```bash
python3 work/dynamic_generation_seed_sweep.py \
  --output-prefix dynamic_generation_seed_sweep
```

Seeds:

```text
60601,60631,60661
```

Setup:

- base N = 128,
- max N = 1024,
- 8-sample allocation chunks,
- budgets = 512 and 1024 extra generation tokens/problem,
- best non-oracle dynamic generation row selected per seed and budget.

## Result

| dataset | budget | best fine-grained generation delta mean | std | any-correct delta mean | oracle generation delta mean | projected rank-bucket verifier delta mean |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 512 | +0.000 | 0.000 | +0.000 | +0.000 | +0.159 |
| MATH/Llama | 1024 | +0.000 | 0.000 | +0.000 | +0.000 | +0.228 |
| MATH/Gemma | 512 | +0.000 | 0.000 | +0.009 | +0.005 | +0.120 |
| MATH/Gemma | 1024 | +0.005 | 0.006 | +0.023 | +0.005 | +0.194 |

The generation-side result is not split-fragile in the direction a reviewer would hope. Across three seeds, the deployed-selector delta remains essentially zero.

## Interpretation

The generation-only objection has now been tested at several levels:

1. fixed N=128 to N=1024: coverage rises, `cluster_sum` barely moves,
2. uncertainty-targeted generation: coverage rises, `cluster_sum` barely moves,
3. token-matched generation at verifier-scale budgets: dynamic generation has little room to buy samples,
4. fine-grained 8-sample chunks: still no deployed-selector movement,
5. three seed splits: still near-zero generation delta.

This does **not** prove the verifier method. The verifier-side rank-bucket rows are still projected. But it sharply narrows the comparison:

```text
The measured verifier run does not need to beat an omnipotent generation baseline.
It needs to beat a token-matched dynamic generation baseline that currently moves realized selection by ~0.
```

That is a much more concrete target for the missing external/local verifier benchmark.

## Caveats

- The generation sweep uses fixed trace prefixes from Monkey Business, not fresh model sampling.
- The dynamic generation policies are simple uncertainty heuristics plus a tiny hidden-gain logistic model.
- The rank-bucket verifier rows remain projected with assumed verifier success/regression.
- A stronger learned dynamic-SC policy could still be added, but it would need to improve realized `cluster_sum`, not merely hidden any-correct coverage.

## Verification

```bash
python3 work/test_dynamic_generation_seed_sweep.py
python3 work/dynamic_generation_seed_sweep.py \
  --output-prefix dynamic_generation_seed_sweep
```

Both commands passed locally.
