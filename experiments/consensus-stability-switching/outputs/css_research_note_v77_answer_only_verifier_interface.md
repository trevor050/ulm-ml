# v77 Answer-Only Verifier Interface

**Date:** June 1, 2026  
**Question:** Are the v75/v76 local-verifier failures caused by the reason field and long-form output format, or by the verifier model/interface itself?

## Change

I added an answer-only verifier mode:

- [run_ollama_native_verifier.py](run_ollama_native_verifier.py) now has `--schema-mode answer_only`.
- [make_cluster_verifier_prompts.py](make_cluster_verifier_prompts.py) now has `--answer-only`.

The prompt asks for:

```json
{"answer": "...", "confidence": 0.0}
```

with no `reason` field. This directly attacks a v75/v76 failure mode: qwen and gemma often spent their output budget on reasons, scratch-solving, or alternate schemas.

## Prompt Panel

I reused the same six recoverable qwen failures from v75/v76 and generated evidence-only answer-copy prompts:

```bash
python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl \
  --representatives-per-cluster 2 \
  --rationale-chars 420 \
  --omit-problem \
  --allowed-answers \
  --answer-only

python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl \
  --representatives-per-cluster 2 \
  --rationale-chars 420 \
  --omit-problem \
  --allowed-answers \
  --answer-only

python3 work/filter_verifier_prompt_panel.py \
  --prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v77_answeronly_evidenceonly.jsonl \
  --ids outputs/qwen35_9b_v76_recoverable_failures_ids.txt \
  --output outputs/v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl \
  --add-dataset
```

## Qwen 9B

Run:

```bash
python3 work/run_ollama_native_verifier.py \
  --base-url http://127.0.0.1:11435 \
  --model qwen3.5:9b \
  --prompts outputs/v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl \
  --output outputs/qwen35_9b_v77_recoverable_failures_answeronly_evidenceonly_predictions.jsonl \
  --timeout 240 \
  --retries 1 \
  --log-every 1 \
  --include-timing \
  --num-predict 64 \
  --schema-mode answer_only \
  --resume
```

Report: [qwen35_9b_v77_recoverable_failures_answeronly_evidenceonly_report.md](qwen35_9b_v77_recoverable_failures_answeronly_evidenceonly_report.md).

Result:

- Coverage: complete, 3 MATH/Gemma and 3 MATH/Llama.
- Formatting: clean answer/confidence JSON on all six rows.
- Recovery: `0/6`.
- The model is now confidently wrong rather than malformed:
  - Gemma recoverable top5: predicted `4`, correct `1`.
  - Gemma recoverable top20-only: predicted `1/33`, correct `-2`.
  - Gemma recoverable top10-only: predicted `360`, correct `3`.
  - Llama recoverable top5: predicted `17`, correct `11`.
  - Llama recoverable top10-only: predicted baseline `5`, correct `1`.
  - Llama recoverable top20-only: predicted `187000`, correct `54000`.

## Gemma 26B

Run:

```bash
python3 work/run_ollama_native_verifier.py \
  --base-url http://127.0.0.1:11435 \
  --model gemma4:26b \
  --prompts outputs/v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl \
  --output outputs/gemma4_26b_v77_recoverable_failures_answeronly_evidenceonly_predictions.jsonl \
  --timeout 240 \
  --retries 1 \
  --log-every 1 \
  --include-timing \
  --num-predict 64 \
  --schema-mode answer_only \
  --resume
```

Report: [gemma4_26b_v77_recoverable_failures_answeronly_evidenceonly_report.md](gemma4_26b_v77_recoverable_failures_answeronly_evidenceonly_report.md).

Result:

- Coverage: complete, 3 MATH/Gemma and 3 MATH/Llama.
- Recovery: `0/6`.
- Formatting remains unreliable: several rows ignore the answer-only schema and return scratch-solving prose or fenced JSON missing confidence.
- The only high-confidence parsed row repeats the baseline answer `5` on a Llama recoverable top10-only case where the correct answer is `1`.

## Read

v77 isolates a key interface failure. Removing the reason field improves qwen's parseability but not correctness. Gemma still does not reliably obey the structured-output interface, and it also recovers nothing on this targeted panel.

Across the same six recoverable failures:

| verifier/interface | recoveries |
|---|---:|
| qwen3.5:9b slim concise | `0/6` |
| qwen3.5:9b rich concise | `0/6` |
| qwen3.5:9b rich evidence-only | `0/6` |
| qwen3.5:9b answer-only evidence-only | `0/6` |
| gemma4:26b answer-only evidence-only | `0/6` |

This is now a strong negative result for the available local Ollama verifier stack. The failure is not merely malformed JSON or too much rationale text. qwen can produce clean answer-only outputs and still chooses wrong answer clusters.

## Next Move

Stop spending more time trying to rescue local qwen/gemma prompts as positive evidence. The next credible positive route is either:

1. a stronger external/frontier verifier with the v74/v77 report harness,
2. a trained/calibrated cluster-choice model on packet formats,
3. a non-generative verifier interface that scores each cluster independently rather than asking a chat model to choose among many clusters.
