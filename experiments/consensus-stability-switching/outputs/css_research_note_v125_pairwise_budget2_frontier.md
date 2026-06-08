# v125 Higher-Budget Pairwise Router-Judge Frontier

## Question

v122 established the conservative budget-0 natural-rate result for Gemma-with-Llama routing:

- raw router: `+0.097`, with `192` recoveries and `20` regressions
- source-calibrated pairwise guard: `+0.067`, with `120` recoveries and `1` regression

This v125 audit asks whether that pairwise guard still helps when the upstream router is allowed a higher source-regression budget, exposing more recovery opportunities but also more raw regressions.

## Setup

Target direction: `MATH/Gemma` baseline with `MATH/Llama` auxiliary traces.

Raw router:

- score: `base_utility`
- router source regression budget: `2`
- policies: `target_intersection_top10`, `target_intersection_top20`, `union_rank_top3`
- rebuilt answer rows: `outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl`

Pairwise panel:

- prompts: `outputs/pairwise_router_judge_v125_budget2_all_prompts.jsonl`
- manifest: `outputs/pairwise_router_judge_v125_budget2_all_manifest.csv`
- accepted actions: `519`
- action mix: `240` recoveries, `30` regressions, `36` both-correct, `213` neither-correct
- local judges: `mathstral:7b`, `qwen3:14b`, `gemma4:26b`

Important reproducibility note: the default v118 answer-row cache in `outputs/` was empty during this continuation. The natural-rate scorer was rerun with the explicit rebuilt v125 answer-row file, and the shared loader now fails loudly when a target/other/policy filter returns zero rows.

Commands:

```bash
python3 work/build_cross_seed_answer_rows.py \
  --target-data work/MATH_Gemma-2B.json \
  --other-data work/MATH_Llama-3-8B-Instruct.json \
  --target-label MATH/Gemma \
  --other-label MATH/Llama \
  --output outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl \
  --seeds 60601,60602,60603 \
  --n 128 \
  --trials-per-problem 8 \
  --verifier-train-problems 30 \
  --audit-holdout-gap 24 \
  --verifier-samples-per-problem 800 \
  --policies target_intersection_top10,target_intersection_top20,union_rank_top3

python3 work/pairwise_router_judge_natural_rate.py \
  --answer-rows outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl \
  --manifest outputs/pairwise_router_judge_v125_budget2_all_manifest.csv \
  --mathstral outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --qwen14b outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --gemma4 outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --router-regression-budget 2 \
  --output-prefix pairwise_router_judge_natural_rate_v125_budget2
```

Key outputs:

- `outputs/pairwise_router_judge_natural_rate_v125_budget2.md`
- `outputs/pairwise_router_judge_natural_rate_v125_budget2.csv`
- `outputs/pairwise_router_judge_natural_rate_v125_budget2_aggregate.csv`
- `outputs/pairwise_router_judge_natural_rate_v125_budget2_details.csv`
- `outputs/pairwise_router_judge_calibration_v125_budget2.md`
- `outputs/*_pairwise_router_judge_v125_budget2_all_score.md`

## Result

Full natural held-out denominator: `1776` trials.

| pairwise source budget | baseline acc | raw router delta | pairwise delta | raw rec/reg | pairwise rec/reg | recovery kept | regression kept | selected rules |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `0` | `0.237` | `+0.118 [+.078,+.159]` | `+0.058 [+.033,+.087]` | `240/30` | `105/2` | `0.438` | `0.067` | `60601:mathstral/never`; `60602:gemma4/B`; `60603:qwen14b/B` |
| `1` | `0.237` | `+0.118 [+.080,+.159]` | `+0.083 [+.055,+.115]` | `240/30` | `150/2` | `0.625` | `0.067` | `60601:mathstral/B_or_BOTH`; `60602:gemma4/B`; `60603:qwen14b/B` |
| `2` | `0.237` | `+0.118 [+.079,+.159]` | `+0.099 [+.067,+.133]` | `240/30` | `180/4` | `0.750` | `0.133` | all `qwen14b/B` |
| `5` | `0.237` | `+0.118 [+.079,+.158]` | `+0.099 [+.068,+.133]` | `240/30` | `180/4` | `0.750` | `0.133` | all `qwen14b/B` |

Accepted-row scoring also improves over v120 because the higher-budget router exposes more recoveries:

| judge | accepted-row delta | accepts | recoveries | regressions |
|---|---:|---:|---:|---:|
| `mathstral:7b` | `+0.247` | `219` | `129/240` | `1/30` |
| `qwen3:14b` | `+0.337` | `315` | `180/240` | `5/30` |
| `gemma4:26b` | `+0.252` | `194` | `133/240` | `2/30` |

The natural-rate source calibration chooses between those behaviors. Budget `1` is the safer operating point (`+0.083`, `150/2`); budget `2` is the higher-gain frontier (`+0.099`, `180/4`).

## Read

v125 strengthens the pairwise-router path in the way v122 specifically demanded: it tests a higher-risk upstream router under the full natural denominator instead of only accepted actions.

The raw budget-2 router has more headroom than budget 0 (`240` vs `192` recoveries) but is less safe (`30` vs `20` regressions). Pairwise gating keeps most of the added recovery supply while cutting regressions sharply. The best natural row keeps `180/240` recoveries and only `4/30` regressions, yielding `+0.099` over all held-out trials.

The pitch should not be "the judge is perfect." It is:

> A stronger upstream auxiliary-generator router can be made substantially safer by a narrow pairwise answer adjudicator, and the resulting natural-rate gain remains positive under problem-bootstrap uncertainty.

Caveats:

- This is still local Ollama model evidence.
- Only three split seeds are available.
- The strongest v125 row relies on `qwen3:14b`, which is higher-recovery but less conservative than mathstral/gemma4.
- The v125 prompt panel reused overlapping v120 predictions and ran only the newly exposed prompts live; this is valid because packet identity is remapped by `(seed, pid, trial, policy)`, but it should be documented.
- Confidence thresholds remain unhelpful; rule selection is still discrete.

Next pressure tests:

1. Use v126 leave-one-problem-out and regression localization as the immediate concentration check.
2. Manually audit the four budget-2 pairwise regressions.
3. Run a rationale-inclusive pairwise prompt only on the budget1/budget2 regression and missed-recovery border.
4. If a stronger endpoint becomes available, prioritize this pairwise interface over another full-cluster prompt variant.
