# v111 Cross-Seed Router Placebo

## Question

v110 showed that the Gemma-with-Llama generator router survives cross-seed source-threshold transfer. This control asks whether that result is just threshold luck: if source utility labels are permuted before fitting and thresholding, can the same protocol still produce comparable held-out gains?

## Setup

Command:

```bash
python3 work/cross_seed_router_placebo.py --iterations 200 --output-prefix cross_seed_router_placebo_v111
```

Input rows:

- `outputs/cross_generator_risk_gate_v109_details.jsonl`
- Observed comparator: `outputs/cross_seed_generator_router_v110_aggregate.csv`

Protocol:

1. Use the same v110 held-out-seed split.
2. Permute source-seed nonzero utility labels within each fit.
3. Fit a fast centroid accept scorer from permuted labels.
4. Choose a source threshold with zero permuted source regressions.
5. Evaluate the frozen source-derived threshold on true held-out outcomes.

The centroid fitter is intentionally a cheap placebo, not a replacement for the v110 logistic router. The question is whether scrambled source utility labels can produce router-scale gains at all.

## Result

The v110 Gemma-with-Llama rows sit far above the placebo distribution.

| target | auxiliary | scope | observed | placebo mean | placebo p95 | placebo max | placebo >= observed | empirical p |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Gemma | Llama | `pool_all` | `+0.084` | `+0.008` | `+0.018` | `+0.030` | 0/200 | 0.005 |
| Gemma | Llama | `union_rank_top3` | `+0.078` | `+0.006` | `+0.014` | `+0.021` | 0/200 | 0.005 |
| Llama | Gemma | `union_rank_top3` | `+0.006` | `-0.000` | `+0.001` | `+0.003` | 0/200 | 0.005 |
| Llama | Gemma | `pool_all` | `+0.005` | `-0.000` | `+0.001` | `+0.003` | 0/200 | 0.005 |

## Interpretation

This control strengthens v110. The observed held-out gains are not reproduced by permuted source utility labels. For the main Gemma-with-Llama `pool_all` row, the observed gain is almost 3x the largest placebo gain and more than 4x the placebo 95th percentile.

The narrow claim now has three layers:

1. v108: raw cross-generator agreement is directional.
2. v109: same-seed risk-gating produces a calibrated positive Gemma-with-Llama branch.
3. v110/v111: source-seed threshold transfer survives held-out seed evaluation and beats a 200-run source-label permutation placebo.

This is still a two-generator trace result, not a semantic verifier and not evidence that Gemma helps Llama. The defensible method claim is asymmetric multi-generator answer-cluster routing: a stronger/diverse auxiliary trace can provide recoverable candidate evidence for a weaker target trace, and the accept gate is learning source utility signal rather than pure threshold luck.

## Artifacts

- Summary: [cross_seed_router_placebo_v111.md](cross_seed_router_placebo_v111.md)
- CSV: [cross_seed_router_placebo_v111.csv](cross_seed_router_placebo_v111.csv)
- Placebo iteration CSV: [cross_seed_router_placebo_v111_placebo_iterations.csv](cross_seed_router_placebo_v111_placebo_iterations.csv)
- Script snapshot: [cross_seed_router_placebo.py](cross_seed_router_placebo.py)
