# v112 Cross-Seed Router Heuristic Ablation

## Question

v110/v111 make the auxiliary-generator router look real: train and threshold on two source seeds, deploy on the held-out seed, and the Gemma-with-Llama branch remains positive; permuted source labels do not reproduce the gain. The obvious reviewer objection is simpler:

> Is the learned router just doing a dumb version of "trust the Llama cluster when it is high-ranked or high-support"?

v112 tests that directly.

## Setup

I reran the v110 cross-seed threshold-transfer protocol with no learned logistic accept model. For each target/auxiliary direction, scope, and held-out seed:

1. Score candidate policy switches using a hand-built heuristic.
2. Choose a source-seed threshold that has zero source regressions and maximizes source recoveries.
3. Deploy that threshold on the held-out seed.
4. Compare the held-out aggregate to the v110 learned-router aggregate for the same direction and scope.

Important correction: thresholds are now tie-safe. If many candidates have the same score, a real threshold must accept all of them together. The first v112 draft used an incremental threshold scan that could accidentally accept only part of a tied score group during source threshold selection. v113 caught this; the v112 script and outputs now group ties before choosing a threshold.

The heuristic scores are:

- `other_rank`: auxiliary cluster rank/confidence feature.
- `other_support`: auxiliary support feature.
- `other_conf`: simple auxiliary confidence/support/ratio sum.
- `target_weak_other_conf`: target weakness plus auxiliary confidence/support.
- `margin_gap`: auxiliary confidence minus target confidence.
- `candidate_ratio_gap`: auxiliary candidate-ratio minus target candidate-ratio.
- `policy_prior`: simple prior over candidate policy/source family.

Artifacts:

- [`cross_seed_router_heuristic_v112.md`](cross_seed_router_heuristic_v112.md)
- [`cross_seed_router_heuristic_v112.csv`](cross_seed_router_heuristic_v112.csv)
- [`cross_seed_router_heuristic_v112_aggregate.csv`](cross_seed_router_heuristic_v112_aggregate.csv)
- [`cross_seed_router_heuristic_ablation.py`](cross_seed_router_heuristic_ablation.py)

## Result

The learned router is not reproduced by simple tie-safe heuristics.

For Gemma with Llama as auxiliary, the best dumb source-selected heuristics trail v110:

| target | auxiliary | scope | heuristic | mean delta | v110 delta | accepts | recoveries | regressions |
|---|---|---|---|---:|---:|---:|---:|---:|
| MATH/Gemma | MATH/Llama | `pool_all` | `other_conf` | `+0.054` | `+0.084` | 133 | 97 | 1 |
| MATH/Gemma | MATH/Llama | `pool_all` | `other_support` | `+0.054` | `+0.084` | 133 | 97 | 1 |
| MATH/Gemma | MATH/Llama | `union_rank_top3` | `other_conf` | `+0.054` | `+0.078` | 133 | 97 | 1 |
| MATH/Gemma | MATH/Llama | `pool_all` | `margin_gap` | `+0.029` | `+0.084` | 66 | 54 | 2 |
| MATH/Gemma | MATH/Llama | `pool_all` | `candidate_ratio_gap` | `+0.018` | `+0.084` | 67 | 34 | 2 |

The most obvious rank/prior controls collapse to no-op under valid source thresholding:

| target | auxiliary | scope | heuristic | mean delta | v110 delta | accepts | recoveries | regressions |
|---|---|---|---|---:|---:|---:|---:|---:|
| MATH/Gemma | MATH/Llama | `pool_all` | `other_rank` | `+0.000` | `+0.084` | 0 | 0 | 0 |
| MATH/Gemma | MATH/Llama | `pool_all` | `policy_prior` | `+0.000` | `+0.084` | 0 | 0 | 0 |
| MATH/Gemma | MATH/Llama | `union_rank_top3` | `other_rank` | `+0.000` | `+0.078` | 0 | 0 | 0 |
| MATH/Gemma | MATH/Llama | `union_rank_top3` | `policy_prior` | `+0.000` | `+0.078` | 0 | 0 | 0 |

The reverse direction remains weak. Llama-with-Gemma rows are flat, with best deltas around `+0.005` to `+0.006`.

## Interpretation

v112 is now a stronger control than the first draft. The high-level conclusion is:

- v110 is not merely "trust the auxiliary top-ranked cluster."
- Simple support/confidence heuristics have real signal, but not enough to match the learned low-regression router.
- Coarse rank/prior heuristics are especially brittle because tied scores force all-or-nothing threshold moves.
- The auxiliary-generator asymmetry survives: Llama helps Gemma; Gemma mostly does not help Llama.

This should be reported as a regression-aware dumb-control pass for v110, not as a universal validation of generator routing.

## Consequence

The auxiliary-generator route now has four layers of evidence:

1. v109: same-seed calibrated risk-gating finds a narrow positive Gemma-with-Llama branch.
2. v110: source-seed threshold transfer preserves that branch on held-out seeds.
3. v111: source-label placebo does not reproduce the branch.
4. v112: tie-safe simple heuristic routers do not match the learned router.

v113 should be read together with this note: it turns the same comparison into a regression-budget frontier and shows learned thresholds can buy more held-out gain as the allowed source-regression budget increases.
