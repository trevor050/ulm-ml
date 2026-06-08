# v120 Full Accepted-Row Pairwise Router-Judge Panel

## Question

v119 found a promising 77-row smoke for a narrower verifier interface: ask a local model to adjudicate only two surfaced answers, baseline answer A versus auxiliary-router candidate B. This v120 run scales that to the full accepted action set from the problem-disjoint `base_utility`, source-regression-budget `0`, Gemma-with-Llama router.

The test is:

> On every row where the base auxiliary-router would accept a candidate, can a pairwise local judge recover many candidate-correct rows while refusing the accepted regression rows?

## Panel

Prompt source:

- `outputs/cross_seed_router_symbolic_guard_v118_answer_rows.jsonl`
- `base_utility`
- source regression budget `0`
- held-out problem-disjoint folds
- policies: `target_intersection_top10`, `target_intersection_top20`, `union_rank_top3`

Panel size:

| category | rows |
|---|---:|
| recovery | `192` |
| regression | `20` |
| neither correct | `132` |
| both correct / trace-label-equivalent | `33` |
| total accepted actions | `377` |

The all-accept base router gets `225/377 = 0.597` candidate correctness on this conditioned panel, but it accepts all `20` regression rows. Falling back to the original baseline on every row gets `53/377 = 0.141`.

## Commands

Prompt build:

```bash
python3 work/make_pairwise_router_judge_prompts.py --per-category 999 --packet-prefix pairwise_router_v120_budget0_all --output outputs/pairwise_router_judge_v120_budget0_all_prompts.jsonl --manifest outputs/pairwise_router_judge_v120_budget0_all_manifest.csv
```

Remote Ollama tunnel:

```bash
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local
```

Runs:

```bash
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model mathstral:7b --prompts outputs/pairwise_router_judge_v120_budget0_all_prompts.jsonl --output outputs/mathstral_pairwise_router_judge_v120_budget0_all_predictions.jsonl --schema-mode answer_only --num-predict 64 --timeout 180 --include-timing --log-every 50 --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model qwen3:14b --prompts outputs/pairwise_router_judge_v120_budget0_all_prompts.jsonl --output outputs/qwen14b_pairwise_router_judge_v120_budget0_all_predictions.jsonl --schema-mode answer_only --num-predict 64 --timeout 240 --include-timing --log-every 50 --resume
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model gemma4:26b --prompts outputs/pairwise_router_judge_v120_budget0_all_prompts.jsonl --output outputs/gemma4_pairwise_router_judge_v120_budget0_all_predictions.jsonl --schema-mode answer_only --num-predict 64 --timeout 300 --include-timing --log-every 50 --resume
```

Scoring:

```bash
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v120_budget0_all_manifest.csv --predictions outputs/mathstral_pairwise_router_judge_v120_budget0_all_predictions.jsonl --output-prefix outputs/mathstral_pairwise_router_judge_v120_budget0_all_score
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v120_budget0_all_manifest.csv --predictions outputs/qwen14b_pairwise_router_judge_v120_budget0_all_predictions.jsonl --output-prefix outputs/qwen14b_pairwise_router_judge_v120_budget0_all_score
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v120_budget0_all_manifest.csv --predictions outputs/gemma4_pairwise_router_judge_v120_budget0_all_predictions.jsonl --output-prefix outputs/gemma4_pairwise_router_judge_v120_budget0_all_score
```

## Results

Acceptance rule: accept candidate B if the model chooses `B` or `BOTH`; otherwise fall back to A. Confidence is not useful here because all thresholds give the same rows.

| model | panel baseline acc | gated acc | delta vs fallback | accepted candidates | recovery accepted | regression accepted |
|---|---:|---:|---:|---:|---:|---:|
| `mathstral:7b` | `0.141` | `0.419` | `+0.279` | `171` | `105/192` | `0/20` |
| `gemma4:26b` | `0.141` | `0.435` | `+0.294` | `160` | `111/192` | `0/20` |
| `qwen3:14b` | `0.141` | `0.496` | `+0.355` | `231` | `137/192` | `3/20` |
| accept all router candidates | `0.141` | `0.597` | `+0.456` | `377` | `192/192` | `20/20` |

Category behavior:

| model | recovery B/BOTH | regression B/BOTH | neither B/BOTH |
|---|---:|---:|---:|
| `mathstral:7b` | `105/192` | `0/20` | `38/132` |
| `gemma4:26b` | `111/192` | `0/20` | `19/132` |
| `qwen3:14b` | `137/192` | `3/20` | `64/132` |

## Read

This materially strengthens v119. The pairwise interface does not merely work on a hand-sized stratified smoke; it preserves all accepted regression rows for two local models on the full accepted budget-0 panel, while recovering more than half of accepted recovery opportunities.

The result is still conditioned on the auxiliary router deciding to act. It does not prove natural deployed improvement by itself. It does show a credible route to regression-controlled auxiliary routing:

1. Use the auxiliary generator/router to propose a small number of answer candidates.
2. Use a pairwise answer adjudicator as the regression guard.
3. Calibrate accept/fallback thresholds on held-out accepted rows, not on full-cluster packets.

The next benchmark should be v120 but stricter:

- source-unique or family-aware bootstrap over accepted rows
- held-out calibration for model choice and confidence/fallback
- target Llama-with-Gemma and higher source-regression budgets as negative/quality controls
- comparison against all-accept and no-accept policies under natural problem-level rates

The key claim is now narrower and stronger:

> Full-cluster local verification failed, but pairwise answer adjudication is a promising local verifier interface for regression-controlled auxiliary-generator routing.

