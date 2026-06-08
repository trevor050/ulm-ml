# v123 Llama-With-Gemma Pairwise Mirror Control

## Question

v122 is positive for `MATH/Gemma` with `MATH/Llama` auxiliary traces. This v123 control asks whether the same pairwise machinery fabricates a win in the reverse direction:

> If the upstream auxiliary-router has little or negative signal, does the pairwise judge still force a positive result, or does source calibration choose no-op?

## Setup

Target direction: `MATH/Llama` baseline with `MATH/Gemma` auxiliary traces.

New answer-bearing rows were rebuilt because the old reverse-direction cache had labels and features but not answer strings:

```bash
python3 work/build_cross_seed_answer_rows.py \
  --target-data work/MATH_Llama-3-8B-Instruct.json \
  --other-data work/MATH_Gemma-2B.json \
  --target-label MATH/Llama \
  --other-label MATH/Gemma \
  --output outputs/cross_seed_answer_rows_llama_with_gemma_v123.jsonl
```

Accepted-action prompt panel:

```bash
python3 work/make_pairwise_router_judge_prompts.py \
  --answer-rows outputs/cross_seed_answer_rows_llama_with_gemma_v123.jsonl \
  --data work/MATH_Llama-3-8B-Instruct.json \
  --target MATH/Llama \
  --other MATH/Gemma \
  --dataset-label MATH/Llama \
  --output outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_prompts.jsonl \
  --manifest outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_manifest.csv \
  --score-mode base_utility \
  --regression-budget 0 \
  --per-category 999 \
  --packet-prefix pairwise_router_v123_llama_with_gemma_budget0_all
```

Panel size:

| category | rows |
|---|---:|
| neither correct | `9` |
| recovery | `1` |
| regression | `5` |
| total accepted actions | `15` |

The same three local judges were run: `mathstral:7b`, `qwen3:14b`, and `gemma4:26b`.

Natural-rate command:

```bash
python3 work/pairwise_router_judge_natural_rate.py \
  --answer-rows outputs/cross_seed_answer_rows_llama_with_gemma_v123.jsonl \
  --manifest outputs/pairwise_router_judge_v123_llama_with_gemma_budget0_all_manifest.csv \
  --mathstral outputs/mathstral_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl \
  --qwen14b outputs/qwen14b_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl \
  --gemma4 outputs/gemma4_pairwise_router_judge_v123_llama_with_gemma_budget0_all_predictions.jsonl \
  --target MATH/Llama \
  --other MATH/Gemma \
  --output-prefix pairwise_router_judge_natural_rate_v123_llama_with_gemma
```

## Results

Accepted-action scores at threshold `0.0`:

| model | panel baseline acc | gated acc | delta | accepts | recoveries | regressions |
|---|---:|---:|---:|---:|---:|---:|
| `mathstral:7b` | `0.333` | `0.333` | `+0.000` | `1` | `0/1` | `0/5` |
| `qwen3:14b` | `0.333` | `0.400` | `+0.067` | `1` | `1/1` | `0/5` |
| `gemma4:26b` | `0.333` | `0.333` | `+0.000` | `1` | `0/1` | `0/5` |

Natural-rate source-calibrated result:

| pairwise source budget | trials | baseline | raw router delta | pairwise delta | raw rec/reg | pairwise rec/reg | selected |
|---:|---:|---:|---:|---:|---:|---:|---|
| `0` | `1776` | `0.445` | `-0.002 [-.006,+.001]` | `+0.000 [+0.000,+0.000]` | `1/5` | `0/0` | all folds select `mathstral/never` |
| `1` | `1776` | `0.445` | `-0.002 [-.006,+.001]` | `+0.000 [+0.000,+0.000]` | `1/5` | `0/0` | same |
| `2` | `1776` | `0.445` | `-0.002 [-.006,+.001]` | `+0.000 [+0.000,+0.000]` | `1/5` | `0/0` | same |

## Read

This is a useful negative/control result.

The reverse raw router has almost no useful budget-0 action supply: only `15` accepted actions, with `1` recovery and `5` regressions. The calibrated pairwise policy does not hallucinate a deployed improvement from that bad upstream signal. Under the full natural denominator it chooses no-op on every held-out fold and returns exactly to baseline.

So the current story is asymmetric:

- `Gemma` with `Llama` auxiliary traces has recoverable action supply and a positive pairwise-gated natural delta.
- `Llama` with `Gemma` auxiliary traces does not; source calibration shuts it off.

This strengthens the method framing. The claim should not be "pairwise judges always improve auxiliary routing." The claim should be:

> A trace-derived router can expose direction-specific auxiliary-generator opportunities, and a source-calibrated pairwise judge can either safely exploit them or abstain when the upstream action supply is bad.

Next:

1. Build the higher-router-budget mirror panel only if the raw reverse router first shows nontrivial positive source-safe action supply.
2. Use v122/v123 together as the reviewer-facing control pair.
3. Audit the single v122 held-out regression and the v123 lone recovery to see whether rationale-inclusive prompts separate them.
