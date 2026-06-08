# v33 Rank-Bucket Seed Sweep

## Question

v32 made rank-bucket depth allocation look promising on one split. The obvious reviewer objection is:

> Is the learned rank-bucket policy robust, or did it win on one lucky train/calibration/test split?

## Setup

New script:

```bash
python3 work/test_rank_bucket_seed_sweep.py
python3 work/rank_bucket_seed_sweep.py --output-prefix rank_bucket_seed_sweep
```

Seeds:

```text
60601, 60631, 60661
```

The sweep reruns the rank-bucket policy for both MATH/Llama and MATH/Gemma, then aggregates projected accuracy, projected delta over `cluster_sum`, depth mix, and verifier-token spend.

## Result

At the two most relevant budgets:

| dataset | budget | acc mean | acc std | delta mean | delta std | depth mix |
|---|---:|---:|---:|---:|---:|---|
| MATH/Llama | 512 | 0.590 | 0.027 | +0.159 | 0.012 | 5:0.20, 10:0.37, 20:0.00 |
| MATH/Llama | 1024 | 0.659 | 0.021 | +0.228 | 0.008 | 5:0.25, 10:0.55, 20:0.12 |
| MATH/Gemma | 512 | 0.368 | 0.013 | +0.120 | 0.020 | 5:0.10, 10:0.40, 20:0.00 |
| MATH/Gemma | 1024 | 0.441 | 0.017 | +0.194 | 0.024 | 5:0.12, 10:0.63, 20:0.11 |

Report: `outputs/rank_bucket_seed_sweep.md`.

## Interpretation

The high-budget rank-bucket improvement survives a small seed sweep. The important quantity is the mean delta over `cluster_sum`, because each seed changes the held-out split and baseline accuracy:

```text
MATH/Llama 1024-token budget: +0.228 +/- 0.008
MATH/Gemma 1024-token budget: +0.194 +/- 0.024
```

The depth mix is also stable in shape: most invoked cases use top-10, with top-20 reserved for about `0.11-0.12` of all test trials at the high budget.

## Caveat

This is still a projected verifier-success result. It validates the rank-bucket allocation policy under the current projection model, not the external verifier itself.
