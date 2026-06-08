# v121 Pairwise Router-Judge Held-Out Calibration

## Question

v120 showed strong post-hoc pairwise judge behavior on all accepted budget-0 Gemma-with-Llama router actions. This v121 audit asks the calibration question:

> If we choose the pairwise judge model and accept rule on source accepted rows, does that choice transfer to the held-out seed?

## Setup

Inputs:

- `outputs/pairwise_router_judge_v120_budget0_all_manifest.csv`
- `outputs/mathstral_pairwise_router_judge_v120_budget0_all_predictions.jsonl`
- `outputs/qwen14b_pairwise_router_judge_v120_budget0_all_predictions.jsonl`
- `outputs/gemma4_pairwise_router_judge_v120_budget0_all_predictions.jsonl`

For each held-out seed:

1. Test rows are accepted router actions from that seed.
2. Source rows are accepted router actions from the other seeds.
3. Source rows whose problem id appears in the held-out seed are excluded.
4. Select model/rule on source rows under an explicit source regression budget.
5. Evaluate the selected model/rule on the held-out seed.

Candidate pairwise rules:

- `never`: always fall back to baseline A
- `B`: accept only when the model chooses B
- `B_or_BOTH`: accept when the model chooses B or BOTH

`always` was tested as an anti-pattern and removed from the default because source splits can contain too few regression rows, causing all-accept to look safe and then fail on held-out regressions.

Script and outputs:

- `work/pairwise_router_judge_calibration.py`
- `outputs/pairwise_router_judge_calibration_v121.md`
- `outputs/pairwise_router_judge_calibration_v121.csv`
- `outputs/pairwise_router_judge_calibration_v121_aggregate.csv`

Command:

```bash
python3 work/pairwise_router_judge_calibration.py --output-prefix pairwise_router_judge_calibration_v121
```

## Result

Pairwise judge calibration transfers with a large accepted-row gain, but not zero held-out regressions.

| source regression budget | mean delta | signs | accepts | recoveries | regressions | selected rules |
|---:|---:|---:|---:|---:|---:|---|
| `0` | `+0.368` | `3/3` | `151` | `120` | `1` | `60601:qwen14b/B`; `60602:gemma4/B`; `60603:gemma4/B` |
| `1` | `+0.368` | `3/3` | `151` | `120` | `1` | same |
| `2` | `+0.349` | `3/3` | `154` | `117` | `1` | `60601:qwen14b/B`; `60602:qwen14b/B`; `60603:gemma4/B` |
| `5` | `+0.349` | `3/3` | `154` | `117` | `1` | same |

The selected source-budget-0 policy accepts only explicit `B` choices. It recovers `120/192` accepted recovery rows while causing `1/20` accepted regression on held-out seeds.

## Read

This is stronger than v119/v120 post-hoc scoring because model/rule choice is made without seeing the held-out seed and source rows exclude held-out problem ids. The result says pairwise answer adjudication is not merely a nice interface; it can be source-calibrated into a high-gain accepted-row policy.

But the safety story is not solved:

- Source zero-regression calibration still transfers one held-out regression.
- The benchmark is conditioned on accepted auxiliary-router actions, not natural problem-level traffic.
- The source split has sparse regression rows, so risk estimates remain fragile.
- Confidence is not useful yet; the calibrated rule is discrete model/choice selection.

Next step:

1. Bootstrap or leave-one-family-out over accepted rows to quantify uncertainty.
2. Build the same held-out calibration test for higher router budgets and for Llama-with-Gemma as a negative/control direction.
3. Convert accepted-row deltas back to natural problem-level deltas using router invocation rates.
4. Try pairwise prompts with short candidate rationales, not just final answers, to see whether the single held-out regression can be eliminated without killing recovery.

The updated branch claim:

> Pairwise answer adjudication can be source-calibrated into a high-recovery, low-regression guard for accepted auxiliary-generator router actions on MATH/Gemma with Llama auxiliary traces.

