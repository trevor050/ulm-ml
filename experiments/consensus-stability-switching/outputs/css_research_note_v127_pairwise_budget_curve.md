# v127 Pairwise Budget Curve

## Question

v125/v126 identified two useful operating points for the higher-risk Gemma-with-Llama router:

- pairwise budget 1: natural `+0.083`, with `150/2` recoveries/regressions
- pairwise budget 2: natural `+0.099`, with `180/4` recoveries/regressions

This v127 audit asks whether those rows are budget cherry-picks. It sweeps the source regression budget beyond the originally reported `0,1,2,5` points, then adds an unsafe `always` rule as a raw-router control.

## Setup

Target direction: `MATH/Gemma` baseline with `MATH/Llama` auxiliary traces.

Shared inputs:

- answer rows: `outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl`
- manifest: `outputs/pairwise_router_judge_v125_budget2_all_manifest.csv`
- judges: `mathstral:7b`, `qwen3:14b`, `gemma4:26b`
- full natural denominator: `1776` held-out trials
- upstream raw router source budget: `2`

Guard-only curve:

```bash
python3 work/pairwise_router_judge_natural_rate.py \
  --answer-rows outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl \
  --manifest outputs/pairwise_router_judge_v125_budget2_all_manifest.csv \
  --mathstral outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --qwen14b outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --gemma4 outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --router-regression-budget 2 \
  --pairwise-regression-budgets 0,1,2,3,4,5,6,8,10,12,15,20,25,30 \
  --rules never,B,B_or_BOTH \
  --output-prefix pairwise_router_judge_guard_curve_v127
```

Unsafe raw-pass control:

```bash
python3 work/pairwise_router_judge_natural_rate.py \
  --answer-rows outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl \
  --manifest outputs/pairwise_router_judge_v125_budget2_all_manifest.csv \
  --mathstral outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --qwen14b outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --gemma4 outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --router-regression-budget 2 \
  --pairwise-regression-budgets 0,1,2,3,4,5,6,8,10,12,15,20,25,30,40,60,100 \
  --rules never,B,B_or_BOTH,always \
  --output-prefix pairwise_router_judge_budget_curve_v127
```

## Guard-Only Result

This is the deployable pairwise-gate view. It only lets a judge accept answer `B` or `BOTH`, otherwise it falls back to the baseline answer.

| source budget | natural delta | 95% CI | rec/reg | rec kept | reg kept | selected |
|---:|---:|---:|---:|---:|---:|---|
| 0 | `+0.058` | `[+0.033,+0.087]` | `105/2` | `0.438` | `0.067` | `60601:mathstral/never`; `60602:gemma4/B`; `60603:qwen14b/B` |
| 1 | `+0.083` | `[+0.055,+0.115]` | `150/2` | `0.625` | `0.067` | `60601:mathstral/B_or_BOTH`; `60602:gemma4/B`; `60603:qwen14b/B` |
| 2 | `+0.099` | `[+0.067,+0.133]` | `180/4` | `0.750` | `0.133` | all `qwen14b/B` |
| 3-30 | `+0.099` | lower bound `>= +0.067` | `180/4` | `0.750` | `0.133` | all `qwen14b/B` |

The guard-only curve has three steps, then plateaus. Raising the source budget above `2` does not find a stronger guarded rule under this model/rule menu.

## Unsafe `always` Control

Adding `always` lets calibration choose to accept every upstream router action, ignoring the pairwise answer judgment. This is not the pairwise method; it is a useful control for how quickly source calibration can drift toward raw-router behavior.

| source budget | natural delta | rec/reg | rec kept | reg kept | selected |
|---:|---:|---:|---:|---:|---|
| 0 | `+0.061` | `128/20` | `0.533` | `0.667` | includes `60603:mathstral/always` |
| 1 | `+0.086` | `173/20` | `0.721` | `0.667` | includes `60603:mathstral/always` |
| 2-6 | `+0.102` | `203/22` | `0.846` | `0.733` | includes `60603:mathstral/always` |
| 8-12 | `+0.114` | `229/26` | `0.954` | `0.867` | includes two `mathstral/always` folds |
| 15+ | `+0.118` | `240/30` | `1.000` | `1.000` | raw router behavior |

This control is the cautionary row. It approaches the raw router gain, but it also restores most or all raw-router regressions. The clearest calibration failure is held-out seed `60603`: source rows allow `mathstral/always` at budget `0` with `54/0` source rec/reg, but the held-out fold pays `100/20`.

## Regression Anatomy

The four budget-2 guard regressions are all `qwen3:14b` choosing `B` for `union_rank_top3` actions:

| packet | family | A | B | model pattern |
|---|---|---:|---:|---|
| `...0494_s60601_p88_t0` | 453rd digit of `6/13` | `1` | `5` | qwen picks `B`; mathstral says `NEITHER` |
| `...0499_s60602_p63_t6` | max of two squares | `1` | `2` | qwen picks `B`; same family also has qwen-correct recoveries when `A=0`, `B=1` |
| `...0510_s60603_p82_t7` | day-of-week offset | `270` | `wednesday` | all three judges pick `B` on this row |
| `...0511_s60603_p88_t4` | 453rd digit of `6/13` | `1` | `5` | qwen picks `B`; mathstral says `NEITHER` |

The repeated `p88` family looks like model overcommitment rather than a one-off malformed prompt. The `p63` family is more interesting as a matched recovery/regression case: qwen correctly accepts `B` on same-problem recovery packets with `A=0`, `B=1`, but wrongly accepts `B=2` against baseline `A=1`.

## Read

v127 makes the v125/v126 frontier less cherry-pickable:

- The deployable guard-only curve reaches `+0.099` at source budget `2` and stays there through budget `30`.
- Budget `1` remains the safer operating point: it keeps `150` recoveries with only `2` regressions.
- Budget `2` is the higher-gain guarded frontier: it keeps `180/240` recoveries and only `4/30` raw regressions.
- Allowing `always` shows why this must be pitched as pairwise gating, not just source-calibrated raw routing: higher apparent gain mostly comes from giving back regression control.

Reviewer-resistant wording:

> Under the guarded pairwise rule set, the higher-budget router frontier is stable rather than a single lucky budget choice. The gain plateaus at `+0.099` once source budget reaches `2`, while the raw-pass control recovers slightly more accuracy only by restoring most raw-router regressions.

Key outputs:

- `outputs/pairwise_router_judge_guard_curve_v127.md`
- `outputs/pairwise_router_judge_guard_curve_v127_aggregate.csv`
- `outputs/pairwise_router_judge_guard_curve_v127.csv`
- `outputs/pairwise_router_judge_guard_curve_v127_details.csv`
- `outputs/pairwise_router_judge_budget_curve_v127.md`
- `outputs/pairwise_router_judge_budget_curve_v127_aggregate.csv`
- `outputs/pairwise_router_judge_budget_curve_v127.csv`
- `outputs/pairwise_router_judge_budget_curve_v127_details.csv`
