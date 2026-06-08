# v113 Cross-Seed Router Regression Frontier

## Question

v112 fixed the simple-heuristic control with tie-safe thresholding. That made the zero-source-regression comparison cleaner: rank/prior heuristics collapse to no-op, and the best support/confidence heuristics trail v110.

v113 asks the next harder question:

> If we allow an explicit source-regression budget instead of requiring zero source regressions, does the learned router still dominate the simple heuristic frontier?

## Setup

The experiment reuses the v109 raw candidate rows and the v110 held-out seed protocol.

For each target/auxiliary direction, scope, score family, held-out seed, and regression budget:

1. Fit the learned router on the two source seeds when `score_mode=learned_base`.
2. Score candidates with either the learned router or a simple heuristic.
3. Choose the threshold that maximizes source recoveries subject to a source regression budget.
4. Deploy that threshold on the held-out seed.

It also reports a `target_oracle` diagnostic frontier where the threshold is chosen on the held-out seed itself. Those rows are not deployable; they answer whether a score family has low-regression ranking headroom if calibration were perfect.

Budgets: `0,1,2,5,10,20,40,80`.

Score families:

- `learned_base`
- `other_conf`
- `other_rank`
- `other_support`
- `target_weak_other_conf`
- `margin_gap`
- `candidate_ratio_gap`
- `policy_prior`

Artifacts:

- [`cross_seed_router_regression_frontier_v113.md`](cross_seed_router_regression_frontier_v113.md)
- [`cross_seed_router_regression_frontier_v113.csv`](cross_seed_router_regression_frontier_v113.csv)
- [`cross_seed_router_regression_frontier_v113_aggregate.csv`](cross_seed_router_regression_frontier_v113_aggregate.csv)
- [`cross_seed_router_regression_frontier.py`](cross_seed_router_regression_frontier.py)

## Source-Selected Result

For the useful Gemma-with-Llama `pool_all` direction, the learned router is the best low-regression deployable frontier.

| selector | score | source budget | mean delta | signs | accepts | recoveries | held-out regressions |
|---|---|---:|---:|---:|---:|---:|---:|
| source | `other_conf` | 0 | `+0.054` | 3/3 | 133 | 97 | 1 |
| source | `learned_base` | 0 | `+0.084` | 3/3 | 208 | 152 | 2 |
| source | `learned_base` | 1 | `+0.108` | 3/3 | 299 | 195 | 3 |
| source | `learned_base` | 2 | `+0.119` | 3/3 | 349 | 214 | 3 |
| source | `learned_base` | 5 | `+0.139` | 3/3 | 492 | 257 | 11 |

Among source-selected rows with at most five held-out regressions, the best heuristic reaches v110-level delta but not the budgeted learned frontier:

| selector | score | source budget | mean delta | signs | accepts | recoveries | held-out regressions |
|---|---|---:|---:|---:|---:|---:|---:|
| source | `learned_base` | 2 | `+0.119` | 3/3 | 349 | 214 | 3 |
| source | `learned_base` | 1 | `+0.108` | 3/3 | 299 | 195 | 3 |
| source | `learned_base` | 0 | `+0.084` | 3/3 | 208 | 152 | 2 |
| source | `candidate_ratio_gap` | 2 | `+0.084` | 3/3 | 255 | 153 | 3 |
| source | `candidate_ratio_gap` | 1 | `+0.069` | 3/3 | 210 | 124 | 2 |
| source | `other_conf` | 2 | `+0.068` | 3/3 | 173 | 125 | 4 |

So v113 improves the operating point: v110's zero-source-regression row was `+0.084` with 2 held-out regressions; allowing two source regressions raises the learned row to `+0.119` with only 3 held-out regressions.

## Target-Oracle Diagnostic

The target-oracle frontier says the learned score is also the best low-regression ranking family when threshold calibration is perfect:

| selector | score | target budget | mean delta | signs | accepts | recoveries | held-out regressions |
|---|---|---:|---:|---:|---:|---:|---:|
| target_oracle | `learned_base` | 0 | `+0.086` | 3/3 | 205 | 152 | 0 |
| target_oracle | `learned_base` | 1 | `+0.127` | 3/3 | 389 | 229 | 3 |
| target_oracle | `learned_base` | 2 | `+0.136` | 3/3 | 447 | 248 | 6 |
| target_oracle | `learned_base` | 20 | `+0.148` | 3/3 | 832 | 310 | 47 |
| target_oracle | `other_rank` | 20 | `+0.149` | 3/3 | 792 | 313 | 48 |

The rank heuristic only catches up at a high-regression target-oracle point. It is not the low-risk ranking frontier.

## Interpretation

v113 makes the auxiliary-generator claim sharper:

- v110 is not just a lucky zero-regression threshold.
- v112 tie-safe heuristics do not match v110.
- v113 shows the learned router continues to dominate the low-regression source-selected frontier when the source regression budget is relaxed.
- The best heuristic, `candidate_ratio_gap`, can match the v110 zero-budget delta at a similar held-out regression count, but it does not match the learned budgeted row.

This turns the next method direction from "try another heuristic" into "calibrate the learned auxiliary-generator router under explicit regression budgets."

## Caveats

- v113 is still a two-generator local-trace result, not a general multi-generator theorem.
- Source budget is not identical to held-out budget; the result is useful because the low-budget learned rows remain low-regression on held-out seeds here.
- `target_oracle` rows are diagnostic only and must not be reported as deployed policies.
- No new verifier evidence is introduced; this is a router/calibration frontier over existing generated traces.
