# v110 Cross-Seed Generator Router

## Question

v109 found a narrow calibrated auxiliary-generator win, but it still fit and calibrated within each seed's held-out problem split. This audit asks a harsher transfer question: if the accept model and its zero-source-regression threshold are learned on two seeds, does the policy still improve the third seed?

## Setup

Input rows come from the corrected v109 raw candidate details:

```bash
python3 work/cross_seed_generator_router.py --rows outputs/cross_generator_risk_gate_v109_details.jsonl --feature-mode base --output-prefix cross_seed_generator_router_v110
```

For each direction and policy scope, the router:

1. Trains a logistic accept model on changed, nonzero-utility candidate rows from two source seeds.
2. Chooses a threshold on those source seeds with zero source regressions, maximizing source recoveries.
3. Applies the frozen model and threshold to the held-out seed.
4. Groups all policy candidates by `(problem, trial)` and falls back to the target baseline unless at least one candidate is accepted.

Scopes:

- `pool_all`: choose among `target_intersection_top10`, `target_intersection_top20`, and `union_rank_top3`.
- Individual policy scopes for each of those policies.

## Result

The Gemma-with-Llama branch survives cross-seed threshold transfer.

| target | auxiliary | scope | mean delta | positive seeds | CI-positive seeds | accepts | recoveries | regressions |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Gemma | Llama | `pool_all` | `+0.084` | 3/3 | 3/3 | 208 | 152 | 2 |
| Gemma | Llama | `union_rank_top3` | `+0.078` | 3/3 | 3/3 | 186 | 140 | 1 |
| Gemma | Llama | `target_intersection_top10` | `+0.039` | 3/3 | 2/3 | 259 | 73 | 3 |
| Gemma | Llama | `target_intersection_top20` | `+0.031` | 3/3 | 2/3 | 175 | 56 | 1 |
| Llama | Gemma | best rows | `+0.000` to `+0.006` | weak | 0/3 | small | small | small |

The strongest per-held-out-seed `pool_all` rows are:

| held-out seed | baseline | gated | delta | CI |
|---:|---:|---:|---:|---:|
| 60601 | 0.240 | 0.336 | `+0.096` | `[+0.051,+0.150]` |
| 60602 | 0.226 | 0.299 | `+0.073` | `[+0.030,+0.120]` |
| 60603 | 0.245 | 0.329 | `+0.084` | `[+0.035,+0.140]` |

## Interpretation

This strengthens v109 materially. The auxiliary-generator signal is not just same-seed threshold luck. A source-seed calibrated router can transfer to held-out seeds and recover a large number of Gemma failures with very few Llama-auxiliary regressions.

The result is still directional. Gemma as auxiliary for Llama remains flat or weak and never CI-positive. The deployable claim should be asymmetric:

> In this MATH trace pair, a stronger/diverse auxiliary generator can provide candidate-cluster evidence that a calibrated router uses to improve a weaker target generator. The reverse direction does not transfer.

This is not semantic verification and not a no-regression theorem. It is a calibrated multi-generator routing result over existing repeated-sampling traces.

## Artifacts

- Summary: [cross_seed_generator_router_v110.md](cross_seed_generator_router_v110.md)
- CSV: [cross_seed_generator_router_v110.csv](cross_seed_generator_router_v110.csv)
- Aggregate CSV: [cross_seed_generator_router_v110_aggregate.csv](cross_seed_generator_router_v110_aggregate.csv)
- Details: [cross_seed_generator_router_v110_details.jsonl](cross_seed_generator_router_v110_details.jsonl)
- Script snapshot: [cross_seed_generator_router.py](cross_seed_generator_router.py)
