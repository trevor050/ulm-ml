# v122 Pairwise Router-Judge Natural-Rate Scoring

## Question

v121 showed that pairwise answer adjudication transfers on accepted auxiliary-router actions. This v122 audit asks the deployable-denominator question:

> If every held-out trial is counted, including trials where the router proposes no switch, how much natural accuracy does the source-calibrated pairwise guard preserve?

## Setup

Target direction: `MATH/Gemma` baseline with `MATH/Llama` auxiliary traces.

Raw router:

- answer rows: `outputs/cross_seed_router_symbolic_guard_v118_answer_rows.jsonl`
- score: `base_utility`
- router source regression budget: `0`
- policies: `target_intersection_top10`, `target_intersection_top20`, `union_rank_top3`

Pairwise judges:

- `mathstral:7b`
- `qwen3:14b`
- `gemma4:26b`

Pairwise source rule selection now excludes every problem id in the held-out seed, not only held-out problem ids that appear among accepted router actions. This is stricter than the accepted-row v121 split and matches the natural-rate denominator.

Command:

```bash
python3 work/pairwise_router_judge_natural_rate.py --output-prefix pairwise_router_judge_natural_rate_v122
```

Key outputs:

- `outputs/pairwise_router_judge_natural_rate_v122.md`
- `outputs/pairwise_router_judge_natural_rate_v122.csv`
- `outputs/pairwise_router_judge_natural_rate_v122_aggregate.csv`
- `outputs/pairwise_router_judge_natural_rate_v122_details.csv`

## Result

Full held-out denominator: `1776` trials.

| pairwise source budget | baseline acc | raw router delta | pairwise delta | raw rec/reg | pairwise rec/reg | recovery kept | regression kept | selected rules |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `0` | `0.237` | `+0.097 [+.061,+.134]` | `+0.067 [+.040,+.096]` | `192/20` | `120/1` | `0.625` | `0.050` | `60601:qwen14b/B`; `60602:gemma4/B`; `60603:gemma4/B` |
| `1` | `0.237` | `+0.097 [+.062,+.136]` | `+0.067 [+.041,+.097]` | `192/20` | `120/1` | `0.625` | `0.050` | same |
| `2` | `0.237` | `+0.097 [+.061,+.135]` | `+0.065 [+.039,+.094]` | `192/20` | `117/1` | `0.609` | `0.050` | `60601:qwen14b/B`; `60602:qwen14b/B`; `60603:gemma4/B` |

Bootstrap CIs are problem-bootstrap intervals over `(seed, pid)` groups.

## Read

This is the cleanest current positive result.

The pairwise guard does not maximize raw accuracy. Accepting every router action has larger natural delta (`+0.097`) because it takes all recoveries, but it also takes all `20` regressions. The source-calibrated pairwise guard keeps `120/192` raw-router recoveries and cuts regressions from `20` to `1`, yielding a natural `+0.067` gain with a positive problem-bootstrap interval.

That changes the pitch:

> The router finds recoverable auxiliary-generator opportunities; the pairwise judge is a regression scrubber that converts an aggressive, unsafe router into a lower-gain but deployable-looking policy.

Remaining caveats:

- The judge is still local Ollama, not a stronger external verifier.
- Only three held-out split seeds are available.
- The single held-out regression matters and should be audited by problem family.
- Confidence thresholds still do not add useful calibration; rule choice is discrete.

Next pressure tests:

1. Run the same natural-rate scorer for the mirror `MATH/Llama` with `MATH/Gemma` auxiliary direction.
2. Score higher raw-router budgets and plot the risk/recovery frontier after pairwise gating.
3. Add family-aware bootstrap or leave-one-family-out on the accepted-action panel.
4. Try short rationale-inclusive pairwise prompts only on the single transferred regression and the recovered/missed border cases.
