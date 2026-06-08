# v119 Pairwise Router-Judge Smoke

## Question

Previous local cluster-verifier runs asked models to choose the correct answer from a large cluster set and mostly failed. v118 says cheap answer-shape guards do not fix auxiliary-generator routing. This smoke tests a narrower verifier interface:

> Given the original problem plus two surfaced answers, the baseline answer A and the auxiliary-router candidate B, can a local model decide whether to accept B or fall back to A?

This is not a broad verifier benchmark. It is a targeted regression-control smoke on rows where the v118/v114 base router already wants to act.

## Setup

I sampled accepted rows from the `base_utility`, source-regression-budget `0`, problem-disjoint Gemma-with-Llama router. The prompt gives:

- problem statement
- Answer A: current baseline selector answer
- Answer B: auxiliary-generator candidate answer
- forced JSON choice: `A`, `B`, `BOTH`, or `NEITHER`

Prompt panel:

| category | rows |
|---|---:|
| recovery | `20` |
| regression | `20` |
| neither correct | `20` |
| both correct | `17` |

The decisive categories are recovery and regression. The `both_correct` category is noisy because trace labels can mark non-identical final-answer strings as correct.

Scripts and outputs:

- `work/make_pairwise_router_judge_prompts.py`
- `work/score_pairwise_router_judge.py`
- `outputs/pairwise_router_judge_v119_prompts.jsonl`
- `outputs/pairwise_router_judge_v119_manifest.csv`
- `outputs/mathstral_pairwise_router_judge_v119_score.md`
- `outputs/qwen14b_pairwise_router_judge_v119_score.md`
- `outputs/gemma4_pairwise_router_judge_v119_score.md`

Prompt command:

```bash
python3 work/make_pairwise_router_judge_prompts.py --per-category 20 --output outputs/pairwise_router_judge_v119_prompts.jsonl --manifest outputs/pairwise_router_judge_v119_manifest.csv
```

Remote Ollama tunnel:

```bash
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local
```

Runner template:

```bash
python3 work/run_ollama_native_verifier.py --base-url http://127.0.0.1:11435 --model <model> --prompts outputs/pairwise_router_judge_v119_prompts.jsonl --output outputs/<model>_pairwise_router_judge_v119_predictions.jsonl --schema-mode answer_only --num-predict 64 --timeout 300 --include-timing --log-every 10 --resume
python3 work/score_pairwise_router_judge.py --manifest outputs/pairwise_router_judge_v119_manifest.csv --predictions outputs/<model>_pairwise_router_judge_v119_predictions.jsonl --output-prefix outputs/<model>_pairwise_router_judge_v119_score
```

## Results

Confidence was not useful in these runs, so the reported acceptance rule is simply: accept B when the model chooses `B` or `BOTH`, otherwise fall back to A.

| model | choice acc | panel baseline acc | gated acc | delta | accepts | recoveries | accepted regressions |
|---|---:|---:|---:|---:|---:|---:|---:|
| `mathstral:7b` | `0.390` | `0.481` | `0.597` | `+0.117` | `25` | `9` | `0` |
| `gemma4:26b` | `0.506` | `0.481` | `0.610` | `+0.130` | `28` | `10` | `0` |
| `qwen3:14b` | `0.481` | `0.481` | `0.636` | `+0.156` | `38` | `15` | `3` |

Recovery/regression category behavior:

| model | recovery B/BOTH | regression B/BOTH |
|---|---:|---:|
| `mathstral:7b` | `9/20` | `0/20` |
| `gemma4:26b` | `10/20` | `0/20` |
| `qwen3:14b` | `15/20` | `3/20` |

## Read

This is the first positive live local-verifier signal after the v75-v94 cluster-verifier and binary-judge stoplines. The interface matters: pairwise adjudication is much easier than choosing from a whole candidate cluster set.

The result is not yet deployable evidence:

- The panel is conditioned on accepted base-router rows, not natural traffic.
- It has only `77` prompts, with duplicated problem families/trials.
- The regression category has only `20` events and fewer unique problem ids.
- Confidence is uncalibrated and does not create a threshold frontier.
- `both_correct` labels expose trace-equivalence/label noise.

But the signal is real enough to change the next experiment. The live route should be:

1. Build a larger pairwise panel from problem-disjoint accepted rows, especially all accepted regressions and a larger recovery set.
2. Make the panel source-unique where possible and report duplicate pressure explicitly.
3. Test pairwise judge transfer across router budgets and across Llama target rows, not only Gemma-with-Llama.
4. Convert model choices into a calibrated accept/fallback rule with held-out threshold selection.

The current pitch should not say "local verifiers fail." It should say: full-cluster local verification failed, but pairwise answer adjudication is a promising narrower verifier interface for regression-controlled auxiliary routing.

