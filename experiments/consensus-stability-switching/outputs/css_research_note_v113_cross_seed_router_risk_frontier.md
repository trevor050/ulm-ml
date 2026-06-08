# v113 Cross-Seed Router Risk Frontier

## Question

v110 showed that a learned auxiliary-generator router transfers across held-out seeds for the Gemma-with-Llama branch. v112 showed that dumb auxiliary-rank heuristics can exceed the v110 raw delta, but only by taking many more regressions.

v113 asks the sharper question:

> Under the same cross-seed transfer protocol, is there a better low-regression risk-return frontier if we combine the learned router score with simple auxiliary-rank/support signals and sweep explicit source-regression budgets?

## Setup

Command:

```bash
python3 work/cross_seed_router_frontier.py
```

Input rows are the corrected v109 candidate rows:

- `outputs/cross_generator_risk_gate_v109_details.jsonl`

For each target/auxiliary direction, scope, score family, source-regression budget, and held-out seed, the script:

1. Trains the v110 logistic accept model on two source seeds when the score family needs it.
2. Scores candidate switches with one of:
   - `learned`
   - `heur_*` v112 heuristic scores
   - `combo_*`, a train-standardized sum of learned-router probability plus the matching heuristic score.
3. Chooses a source-seed threshold that maximizes source recoveries subject to the explicit source-regression budget.
4. Deploys the frozen score and threshold on the held-out seed.
5. Reports held-out recoveries, regressions, accepts, delta, and problem-bootstrap CIs.

Source budgets are `0,1,2,4,8,16,32`. Scopes are `pool_all` and `union_rank_top3`.

## Result

The combined score family improves the Gemma-with-Llama low-regression frontier.

For `MATH/Gemma` target with `MATH/Llama` auxiliary under `pool_all`:

| held-out regression cap | best score family | source budget | mean delta | signs | CI+ seeds | accepts | recoveries | regressions |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `combo_candidate_ratio_gap` | 0 | `+0.108` | 3/3 | 3/3 | 289 | 193 | 1 |
| 2 | `combo_other_rank` | 1 | `+0.119` | 3/3 | 3/3 | 332 | 214 | 2 |
| 4 | `combo_other_conf` | 2 | `+0.131` | 3/3 | 3/3 | 385 | 235 | 3 |
| 8 | `combo_target_weak_other_conf` | 4 | `+0.144` | 3/3 | 3/3 | 442 | 262 | 7 |
| 16 | `combo_other_conf` | 8 | `+0.146` | 3/3 | 3/3 | 481 | 272 | 12 |
| 64 | `combo_other_rank` | 32 | `+0.149` | 3/3 | 3/3 | 811 | 312 | 48 |

The cleanest comparison to v110 is the 2-regression point:

| row | mean delta | recoveries | regressions |
|---|---:|---:|---:|
| v110 `pool_all` learned score | `+0.084` | 152 | 2 |
| v113 `combo_other_rank`, source budget 1 | `+0.119` | 214 | 2 |

At a 1-regression held-out point, `combo_candidate_ratio_gap` gets `+0.108` with 193 recoveries and 1 regression.

The high-recall end is not surprising: aggressive rank-like scores still reach about `+0.148` to `+0.149`, but they take dozens of regressions. The useful new result is that combined learned-plus-heuristic scores also improve the low-regression frontier, not only the high-regression frontier.

The reverse direction remains weak. Llama-with-Gemma is flat, with best low-regression rows around `+0.005` to `+0.007`.

## Interpretation

v113 strengthens the auxiliary-generator routing story. v112 was a necessary dumb-control boundary: a simple rank heuristic could beat the learned router only by paying a large regression cost. v113 shows the learned router and simple auxiliary evidence are complementary enough that their combined score improves the same Gemma-with-Llama branch at low held-out regression counts.

This still is not a no-regression theorem. The held-out regression-cap frontier is a diagnostic summary over the sweep. The deployable protocol is the source-budget threshold: train on two seeds, choose a threshold from source-seed labels under a specified source-regression budget, then report what happens on the held-out seed.

Best narrow claim:

> In this MATH trace pair, Llama auxiliary cluster evidence improves Gemma answer-cluster selection under cross-seed threshold transfer. A train-standardized combination of learned utility probability and simple auxiliary confidence/rank evidence improves the low-regression risk-return frontier over the plain v110 learned router.

## Artifacts

- [`cross_seed_router_frontier_v113.md`](cross_seed_router_frontier_v113.md)
- [`cross_seed_router_frontier_v113.csv`](cross_seed_router_frontier_v113.csv)
- [`cross_seed_router_frontier_v113_aggregate.csv`](cross_seed_router_frontier_v113_aggregate.csv)
- [`cross_seed_router_frontier_v113_frontier.csv`](cross_seed_router_frontier_v113_frontier.csv)
- [`cross_seed_router_frontier_v113_details.jsonl`](cross_seed_router_frontier_v113_details.jsonl)
- [`../work/cross_seed_router_frontier.py`](../work/cross_seed_router_frontier.py)
