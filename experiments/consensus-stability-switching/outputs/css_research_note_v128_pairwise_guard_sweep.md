# v128 Pairwise Guard Sweep

## Question

v126 localized every pairwise budget-2 regression to the same pattern:

- judge: `qwen14b`
- accepted choice: `B`
- router policy: `union_rank_top3`

v127 showed the source-budget frontier is not a single lucky budget choice: the guarded pairwise rule set reaches `+0.099` at source budget `2` and plateaus there through budget `30`.

This v128 audit asks whether a simple deployable guard can reduce that qwen/union tail risk while keeping most of the higher-budget recovery.

## Setup

Shared inputs:

- answer rows: `outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl`
- manifest: `outputs/pairwise_router_judge_v125_budget2_all_manifest.csv`
- predictions:
  - `outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl`
  - `outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl`
  - `outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl`
- natural denominator: `1776` held-out Gemma trials
- upstream raw router source budget: `2`

Command:

```bash
python3 work/pairwise_router_judge_guard_sweep.py \
  --answer-rows outputs/cross_seed_answer_rows_gemma_with_llama_v125.jsonl \
  --manifest outputs/pairwise_router_judge_v125_budget2_all_manifest.csv \
  --mathstral outputs/mathstral_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --qwen14b outputs/qwen14b_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --gemma4 outputs/gemma4_pairwise_router_judge_v125_budget2_all_predictions.jsonl \
  --router-regression-budget 2 \
  --pairwise-regression-budgets 1,2 \
  --guard-regression-budgets 0,1,2 \
  --output-prefix pairwise_router_judge_guard_sweep_v128
```

## Result

Fixed guards:

| pairwise budget | guard | natural delta | 95% CI | rec/reg | accepts |
|---:|---|---:|---:|---:|---:|
| 1 | none | `+0.083` | `[+0.055,+0.115]` | `150/2` | `237` |
| 1 | qwen union needs another candidate vote | `+0.079` | `[+0.051,+0.110]` | `142/1` | `208` |
| 1 | at least two `B` votes | `+0.074` | `[+0.047,+0.104]` | `133/1` | `184` |
| 2 | none | `+0.099` | `[+0.068,+0.133]` | `180/4` | `288` |
| 2 | qwen union needs another candidate vote | `+0.083` | `[+0.055,+0.115]` | `149/1` | `223` |
| 2 | at least two `B` votes | `+0.082` | `[+0.053,+0.115]` | `147/1` | `213` |
| 2 | no qwen union actions | `+0.022` | `[+0.010,+0.037]` | `39/0` | `77` |

Source-selected guard rows:

| pairwise budget | guard source budget | natural delta | 95% CI | rec/reg | selected guards |
|---:|---:|---:|---:|---:|---|
| 1 | 0 | `+0.066` | `[+0.040,+0.095]` | `119/2` | no-union on one fold, none on two folds |
| 1 | 1 | `+0.083` | `[+0.054,+0.115]` | `150/2` | none on all folds |
| 2 | 0 | `+0.068` | `[+0.042,+0.097]` | `123/2` | mixed no-qwen-union / other-candidate / none |
| 2 | 1 | `+0.086` | `[+0.057,+0.119]` | `155/2` | other-candidate on two folds, none on one fold |
| 2 | 2 | `+0.099` | `[+0.067,+0.133]` | `180/4` | none on all folds |

Leave-one-problem-out checks on the most relevant guarded rows:

| row | positive groups | min natural delta | remaining regressions |
|---|---:|---:|---:|
| fixed budget2 qwen-union confirmation | `222/222` | `+0.079` | `1` |
| fixed budget2 at-least-two-B | `222/222` | `+0.078` | `1` |
| source-selected budget2 guard-budget1 | `222/222` | `+0.082` | `2` |

## Read

The guard sweep gives a cleaner operating frontier rather than a single winner:

- Maximum gain remains the unguarded pairwise budget-2 row: `+0.099`, `180/4`.
- A fixed cross-judge guard recovers almost the safer budget-1 result using budget-2 action supply: `+0.083`, `149/1`.
- Source-selected guard budget 1 is slightly stronger: `+0.086`, `155/2`.
- Completely banning qwen/union actions is too conservative: it drops to `+0.022`, even though it removes all regressions.
- Source guard budgets are calibration constraints, not test-set guarantees; budget 0 still has two held-out regressions.

Reviewer-resistant wording:

> The higher-budget pairwise result has a useful safety frontier. Unguarded qwen decisions maximize recovery, but a simple cross-judge confirmation guard on qwen `union_rank_top3` actions cuts budget-2 regressions from `4` to `1` while preserving a budget-1-sized natural gain. This does not prove a final deployable verifier, but it makes the recovery/regression tradeoff explicit and non-oracle.

## Artifacts

- `work/pairwise_router_judge_guard_sweep.py`
- `outputs/pairwise_router_judge_guard_sweep_v128.md`
- `outputs/pairwise_router_judge_guard_sweep_v128.csv`
- `outputs/pairwise_router_judge_guard_sweep_v128_aggregate.csv`
- `outputs/pairwise_router_judge_guard_sweep_v128_details.csv`
