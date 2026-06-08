# v130 Pairwise Rich-Prompt Regression Probe

## Question

v126-v129 localized the higher-budget pairwise risk to a small `qwen14b/B` tail, especially `union_rank_top3` regression packets. This v130 probe asks whether a richer, still answer-only pairwise prompt repairs those known qwen regressions while preserving matched recoveries.

This is a targeted stress panel, not a natural-rate benchmark.

## Setup

Source packets:

- the four v126 budget-2 qwen/B regressions
- the nearby `p82/t2` regression contrast row
- two same-problem `p63` matched recoveries
- five same-problem `p88` neither-correct contrast rows

Prompt variants:

- `solve_first`: solve the problem independently, then compare A/B
- `type_check`: identify the requested answer type first, then reject wrong-type/intermediate answers

Models:

- `qwen3:14b`
- `mathstral:7b`
- `gemma4:26b`

Commands:

```bash
python3 work/make_pairwise_rich_probe_prompts.py

python3 work/run_ollama_native_verifier.py \
  --base-url http://127.0.0.1:11435 \
  --model qwen3:14b \
  --prompts outputs/pairwise_router_rich_probe_v130_prompts.jsonl \
  --output outputs/qwen14b_pairwise_router_rich_probe_v130_predictions.jsonl \
  --schema-mode answer_only \
  --num-predict 96 \
  --include-timing \
  --resume

python3 work/run_ollama_native_verifier.py \
  --base-url http://127.0.0.1:11435 \
  --model mathstral:7b \
  --prompts outputs/pairwise_router_rich_probe_v130_prompts.jsonl \
  --output outputs/mathstral_pairwise_router_rich_probe_v130_predictions.jsonl \
  --schema-mode answer_only \
  --num-predict 96 \
  --include-timing \
  --resume

python3 work/run_ollama_native_verifier.py \
  --base-url http://127.0.0.1:11435 \
  --model gemma4:26b \
  --prompts outputs/pairwise_router_rich_probe_v130_prompts.jsonl \
  --output outputs/gemma4_pairwise_router_rich_probe_v130_predictions.jsonl \
  --schema-mode answer_only \
  --num-predict 96 \
  --include-timing \
  --resume

python3 work/score_pairwise_router_judge.py \
  --manifest outputs/pairwise_router_rich_probe_v130_manifest.csv \
  --predictions outputs/qwen14b_pairwise_router_rich_probe_v130_predictions.jsonl \
  --output-prefix outputs/qwen14b_pairwise_router_rich_probe_v130_score \
  --thresholds 0,0.5,0.7,0.9

python3 work/score_pairwise_router_judge.py \
  --manifest outputs/pairwise_router_rich_probe_v130_manifest.csv \
  --predictions outputs/mathstral_pairwise_router_rich_probe_v130_predictions.jsonl \
  --output-prefix outputs/mathstral_pairwise_router_rich_probe_v130_score \
  --thresholds 0,0.5,0.7,0.9

python3 work/score_pairwise_router_judge.py \
  --manifest outputs/pairwise_router_rich_probe_v130_manifest.csv \
  --predictions outputs/gemma4_pairwise_router_rich_probe_v130_predictions.jsonl \
  --output-prefix outputs/gemma4_pairwise_router_rich_probe_v130_score \
  --thresholds 0,0.5,0.7,0.9

python3 work/summarize_pairwise_rich_probe.py
```

Outputs:

- `outputs/pairwise_router_rich_probe_v130_prompts.jsonl`
- `outputs/pairwise_router_rich_probe_v130_manifest.csv`
- `outputs/qwen14b_pairwise_router_rich_probe_v130_predictions.jsonl`
- `outputs/mathstral_pairwise_router_rich_probe_v130_predictions.jsonl`
- `outputs/gemma4_pairwise_router_rich_probe_v130_predictions.jsonl`
- `outputs/qwen14b_pairwise_router_rich_probe_v130_score.md`
- `outputs/mathstral_pairwise_router_rich_probe_v130_score.md`
- `outputs/gemma4_pairwise_router_rich_probe_v130_score.md`
- `outputs/pairwise_router_rich_probe_v130_summary.md`

## Aggregate

| model | variant | rows | choice acc | accepts | rec/reg | A | B | BOTH | NEITHER | invalid |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `qwen14b` | `solve_first` | `12` | `0.250` | `6` | `2/4` | `6` | `5` | `1` | `0` | `0` |
| `qwen14b` | `type_check` | `12` | `0.417` | `4` | `2/2` | `8` | `4` | `0` | `0` | `0` |
| `mathstral` | `solve_first` | `12` | `0.417` | `3` | `0/3` | `0` | `1` | `2` | `9` | `0` |
| `mathstral` | `type_check` | `12` | `0.417` | `1` | `0/1` | `0` | `1` | `0` | `11` | `0` |
| `gemma4` | `solve_first` | `12` | `0.000` | `0` | `0/0` | `0` | `0` | `0` | `0` | `12` |
| `gemma4` | `type_check` | `12` | `0.000` | `0` | `0/0` | `0` | `0` | `0` | `0` | `12` |

## Packet-Level Read

`qwen14b`:

- `type_check` fixes both repeated `p88` digit-cycle regressions (`A=1`, `B=5`) by switching from `B` to `A`.
- `type_check` preserves both matched `p63` recoveries (`A=0`, `B=1`).
- `type_check` still fails both `p82` weekday regressions, choosing `B` for `monday`/`wednesday` candidates against baseline `A=270`.
- on `p88` neither-correct contrast rows, qwen chooses `A`, not `NEITHER`; this is exact-choice wrong but candidate-safe because it falls back rather than accepting `B`.

`mathstral:7b`:

- richer prompts make mathstral mostly choose `NEITHER`.
- it correctly rejects the neither-correct contrast rows, but misses both matched `p63` recoveries.
- it still accepts at least one regression under `type_check`, so richer prompting does not make it a clean conservative guard on this panel.

`gemma4:26b`:

- under these rich prompts, gemma4 emits natural-language solutions instead of valid JSON, despite schema mode.
- score rows are therefore `INVALID`; this is a structural interface failure, not a useful mathematical verdict.

## Read

Richer pairwise prompting is not a free rescue. It helps qwen on the repeated `p88` digit-cycle family and keeps the matched `p63` recovery behavior, but it does not fix the `p82` weekday regressions. The best qwen variant on this targeted panel is still `2/2` rec/reg, not a safe improvement over v128's cross-judge confirmation guard.

The richer prompts also change other local judges in ways that matter. Mathstral becomes conservative enough to reject many candidates, but it loses all matched recoveries and still accepts a regression. Gemma4 becomes structurally non-JSON under this prompt family.

Current wording:

> Richer answer-only pairwise prompts can repair a specific qwen digit-cycle failure, but they do not eliminate the qwen/union regression tail and can destabilize other local judges. The safer v128 guard result should therefore be treated as a model/rule frontier, not as something that automatically improves with more verbose prompting.

Next useful pressure tests:

1. Build a minimal `type_check`-only qwen panel over all v125 accepted actions to see whether the p88 improvement generalizes or simply trades one regression family for another.
2. Add a structured answer-type classifier as a pre-gate for qwen/union actions, especially date/day and digit-cycle problems.
3. Keep the v128 cross-judge confirmation guard as the deployable candidate; use v130 as evidence that richer prompting alone is not enough.
