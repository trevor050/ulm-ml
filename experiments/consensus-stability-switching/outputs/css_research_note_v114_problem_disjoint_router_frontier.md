# v114 Problem-Disjoint Router Frontier

## Question

v110-v113 use cross-seed threshold transfer, but the same problem ids can appear in both source seeds and the held-out seed. That leaves a reviewer objection:

> Is the auxiliary-generator router learning portable routing behavior, or is it benefiting from repeated problem ids across seeds?

v114 stress-tests that directly.

## Setup

For each held-out seed, source training and threshold selection remove every source row whose `pid` appears in the held-out seed's test set. The held-out test set is unchanged.

This makes the source side much thinner:

- Held-out test problems per seed: `74`.
- Source train problems after excluding held-out pids: `44`.
- Excluded source problem ids per seed: about `62`.
- Mean usable learned-router fit examples for Gemma-with-Llama `pool_all`: `141.7`.

The experiment reuses the v113 scoring/frontier machinery:

- Same v109 raw candidate rows.
- Same held-out seed protocol.
- Same source-regression budgets: `0,1,2,5,10,20`.
- Source-selected thresholds only. No target-oracle thresholds in this stress note.

Artifacts:

- [`cross_seed_router_problem_disjoint_frontier_v114.md`](cross_seed_router_problem_disjoint_frontier_v114.md)
- [`cross_seed_router_problem_disjoint_frontier_v114.csv`](cross_seed_router_problem_disjoint_frontier_v114.csv)
- [`cross_seed_router_problem_disjoint_frontier_v114_aggregate.csv`](cross_seed_router_problem_disjoint_frontier_v114_aggregate.csv)
- [`cross_seed_router_problem_disjoint_frontier.py`](cross_seed_router_problem_disjoint_frontier.py)

## Main Result

The auxiliary-generator signal survives problem-disjoint training, but low-regression calibration does not.

For Gemma with Llama as auxiliary:

| score | source budget | mean delta | v113 delta | signs | accepts | recoveries | held-out regressions |
|---|---:|---:|---:|---:|---:|---:|---:|
| `learned_base` | 0 | `+0.097` | `+0.084` | 3/3 | 377 | 192 | 20 |
| `learned_base` | 1 | `+0.099` | `+0.108` | 3/3 | 417 | 199 | 24 |
| `learned_base` | 2 | `+0.118` | `+0.119` | 3/3 | 519 | 240 | 30 |
| `learned_base` | 5 | `+0.131` | `+0.139` | 3/3 | 607 | 271 | 39 |
| `learned_base` | 10 | `+0.138` | `+0.140` | 3/3 | 687 | 288 | 43 |
| `learned_base` | 20 | `+0.147` | `+0.141` | 3/3 | 756 | 306 | 45 |

The learned mean delta remains close to v113. The problem is regression count: a source budget of zero no longer implies low held-out regressions.

Per-seed learned `pool_all` examples:

| held-out seed | source budget | delta | accepts | recoveries | regressions | fit examples |
|---:|---:|---:|---:|---:|---:|---:|
| 60601 | 0 | `+0.111` | 91 | 67 | 1 | 111 |
| 60602 | 0 | `+0.044` | 52 | 27 | 1 | 156 |
| 60603 | 0 | `+0.135` | 234 | 98 | 18 | 158 |
| 60601 | 2 | `+0.144` | 155 | 90 | 5 | 111 |
| 60602 | 2 | `+0.076` | 97 | 50 | 5 | 156 |
| 60603 | 2 | `+0.135` | 267 | 100 | 20 | 158 |

The instability is concentrated: seed `60603` keeps high recovery but regresses many already-correct baseline cases.

## Low-Regression Rows

If we require at most five held-out regressions across all three held-out seeds, learned routing drops out of the frontier. The best rows are simple heuristics:

| score | source budget | mean delta | v113 delta | signs | accepts | recoveries | held-out regressions |
|---|---:|---:|---:|---:|---:|---:|---:|
| `target_weak_other_conf` | 0 | `+0.049` | `+0.025` | 3/3 | 128 | 92 | 5 |
| `margin_gap` | 0 | `+0.046` | `+0.029` | 3/3 | 122 | 84 | 3 |

So the v113 claim must be narrowed:

- Positive auxiliary-generator routing signal survives a problem-disjoint source split.
- Low-regression learned threshold transfer does **not** survive this stricter split.
- The current learned router is useful as a recovery-oriented scorer, but not yet as a deployment-calibrated low-risk policy under problem-disjoint calibration.

## Interpretation

This is a good negative/pressure result. It does not kill the auxiliary-generator direction, but it prevents an overclaim.

The corrected story is:

1. v109-v113 establish a real Gemma-with-Llama auxiliary signal under cross-seed protocols.
2. v112 shows tie-safe simple heuristics do not explain v110.
3. v113 shows explicit source-regression budgets improve the learned frontier when problem overlap is allowed.
4. v114 shows problem-disjoint source calibration keeps recovery signal but breaks held-out regression control.

The next method should therefore separate ranking from calibration:

- Train/use the learned router as a candidate recovery scorer.
- Add a stricter regression predictor or abstention rule calibrated on problem-disjoint source data.
- Report recovery and regression as a frontier, not a single "safe" threshold.

## Caveats

- The problem-disjoint source split is thin: only `44` train problem ids per held-out seed.
- This is still a two-generator local-trace result.
- The high-delta learned rows are not deployable low-risk policies because held-out regressions are too high.
- The low-regression heuristic rows are positive but much smaller than v113's learned frontier.
