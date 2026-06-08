# v75 Remote Ollama Verifier Smoke

**Date:** June 1, 2026  
**Question:** Once the Windows RTX box is reachable, can a local Ollama model produce real deployed-mix verifier evidence, and what does the first smoke say?

## Setup

The previous compute note was stale. The SSH alias `pc` still points at `192.168.1.223`, but mDNS resolves `trevors-pc.local` to `192.168.1.151`, and SSH works when the user is forced explicitly:

```bash
ssh -o User=trevor trevors-pc.local
```

The Windows host reports an RTX 4070 with about 12GB VRAM, and Ollama exposes:

- `llama3.2:1b`
- `qwen3.5:9b`
- `gemma4:26b`

Direct LAN access to Ollama timed out, but an SSH tunnel was already available on `localhost:11435`.

## Runner Changes

I added [run_ollama_native_verifier.py](run_ollama_native_verifier.py), because Ollama's OpenAI-compatible endpoint put Qwen/Gemma output in reasoning fields or returned empty content. The native `/api/chat` route supports `think: false` and structured-output schema mode, matching Ollama's current docs:

- [Ollama thinking docs](https://docs.ollama.com/capabilities/thinking)
- [Ollama structured output docs](https://docs.ollama.com/capabilities/structured-outputs)

The runner now:

- calls native `/api/chat`,
- disables thinking by default,
- sends an answer/confidence/reason JSON schema,
- caps output with `num_predict`,
- records timing fields,
- salvages leading `answer` and `confidence` from truncated JSON when the model starts with valid fields but overruns the reason.

I also updated:

- [make_cluster_verifier_prompts.py](make_cluster_verifier_prompts.py) with `--concise-reason-words`,
- [build_blind_deployed_mix_panel.py](build_blind_deployed_mix_panel.py) with custom prompt/key paths,
- [deployed_mix_verifier_report.py](deployed_mix_verifier_report.py) with `--expected-prompts` so subset smokes report coverage against the intended panel rather than the full 72/model answer key.

## Prompt Assets

The original compact top20 prompts were too slow or too verbose for the local endpoint. v75 adds a slim concise deployed-mix variant:

```bash
python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v75_slim_concise.jsonl \
  --representatives-per-cluster 1 \
  --rationale-chars 180 \
  --concise-reason-words 20

python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v75_slim_concise.jsonl \
  --representatives-per-cluster 1 \
  --rationale-chars 180 \
  --concise-reason-words 20

python3 work/build_blind_deployed_mix_panel.py \
  --output-prefix deployed_mix_real_v75_slim_concise_percat1 \
  --per-category 1 \
  --chunks 1 \
  --llama-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v75_slim_concise.jsonl \
  --gemma-prompts outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v75_slim_concise.jsonl \
  --llama-answer-key outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v75_slim_concise.answer_key.json \
  --gemma-answer-key outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v75_slim_concise.answer_key.json
```

This creates a 12-prompt smoke panel: one prompt per deployment category per dataset.

## Model Attempts

`qwen3.5:9b` failed under OpenAI-compatible JSON mode and under native mode before `think:false`: it either returned empty content or rambled into malformed JSON. After the native runner fixes and concise prompt variant, it completed the 12-prompt panel.

`gemma4:26b` was too slow on the original compact panel. On the slim panel with `think:false` and `num_predict`, it still ignored the JSON/schema request on the first row and generated prose from scratch rather than a deployable verifier decision. I did not score it as method evidence.

`llama3.2:1b` completed the same slim panel as an endpoint/control model, but it is too small to treat as a meaningful verifier. Its complete report is retained as a sanity check.

## Qwen 9B Smoke Result

Run:

```bash
python3 work/run_ollama_native_verifier.py \
  --base-url http://localhost:11435 \
  --model qwen3.5:9b \
  --prompts outputs/deployed_mix_real_v75_slim_concise_percat1_prompts.jsonl \
  --output outputs/qwen35_9b_deployed_mix_real_v75_slim_concise_percat1_predictions.jsonl \
  --timeout 180 \
  --retries 1 \
  --log-every 1 \
  --include-timing \
  --num-predict 256 \
  --resume

python3 work/deployed_mix_verifier_report.py \
  --predictions outputs/qwen35_9b_deployed_mix_real_v75_slim_concise_percat1_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v75_slim_concise.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v75_slim_concise.answer_key.json \
  --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv \
  --expected-prompts outputs/deployed_mix_real_v75_slim_concise_percat1_prompts.jsonl \
  --thresholds 0,0.5,0.75,0.9 \
  --bootstrap-rounds 500 \
  --output-prefix qwen35_9b_deployed_mix_real_v75_slim_concise_percat1_report
```

Primary report: [qwen35_9b_deployed_mix_real_v75_slim_concise_percat1_report.md](qwen35_9b_deployed_mix_real_v75_slim_concise_percat1_report.md).

Result:

- Coverage: complete for the 12-prompt smoke, 6 MATH/Gemma and 6 MATH/Llama.
- Baseline preservation: `1/1` on Gemma baseline-correct and `1/1` on Llama baseline-correct.
- Recoveries: `0/3` recoverable buckets for Gemma and `0/3` for Llama.
- v71 target check: fails all top10/top20 point-positive and tail checks.
- CI decision: no threshold passes; deployed delta remains `+0.000` because the model preserves the sampled baselines but recovers nothing.

This is real endpoint evidence, but it is negative and tiny. It does not disprove adaptive-depth verification; it shows that a small local `qwen3.5:9b` verifier with very slim evidence is not enough.

## Read

The missing benchmark is now split into two concrete problems:

1. **Endpoint-fit prompting:** thinking mode, JSON/schema enforcement, generation caps, and concise reasons are necessary for local Ollama runs. The old OpenAI-compatible runner silently produced empty-content failures for thinking models.
2. **Verifier strength/evidence budget:** a 9B local model with one 180-char rationale per cluster preserved the sampled already-correct baselines but did not recover any hidden visible-correct cluster in the balanced smoke.

This strengthens the reviewer story by preventing an easy overclaim. The paper can no longer say only "we need a real verifier run"; it can say "a small local 9B smoke was insufficient, so the positive claim requires either stronger verifier capacity, richer compact/full evidence, or both."

## Next Run

Run `gemma4:26b` or another stronger verifier on the same concise panel only after fixing its JSON obedience, then scale to the full 72/model balanced deployed-mix set. If Qwen is used again, try full-prompt fallback on the six recoverable smoke failures; the v75 result may be evidence-starved rather than purely model-capability-starved.
