# v34 Measured-Verifier Handoff

## Question

v33 made the rank-bucket depth policy look robust under the current projection model. The next reviewer-killer gap is still:

> Does a reproducible external/local verifier actually recover buried correct clusters on the compact top-20 prompt assets, and can compact confidence decide when to spend the full prompt?

## Current Runtime Status

Checked on June 1, 2026:

- Local Ollama/OpenAI-compatible endpoint at `http://localhost:11434` is not running.
- `OPENAI_API_KEY` and `OPENAI_BASE_URL` are unset in this shell.
- `ssh pc` resolves to the DHCP-reserved `192.168.1.223`, but the connection times out.
- `ssh trevors-pc.local` resolves, but current SSH auth is rejected.

So no measured verifier benchmark was run in this pass. The assets and scorer are ready; the blocker is model endpoint availability.

## Runner Update

`work/run_openai_compatible_verifier.py` now supports:

```bash
--limit <n>
```

This makes safe smoke tests possible without creating temporary prompt slices. With `--resume`, the limit applies to pending packets after already-written `packet_id`s are skipped.

Smoke helper test:

```bash
python3 work/test_run_openai_compatible_verifier.py
```

## Best First Smoke

Once a local/OpenAI-compatible endpoint exists, run only 3 compact Llama packets:

```bash
python3 work/run_openai_compatible_verifier.py \
  --base-url http://localhost:11434/v1 \
  --model <model> \
  --prompts outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.jsonl \
  --output outputs/<model>_llama_top20_diverse_compact_smoke_predictions.jsonl \
  --limit 3 \
  --resume
```

Score the smoke:

```bash
python3 work/score_llm_judges.py \
  --predictions outputs/<model>_llama_top20_diverse_compact_smoke_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.answer_key.json \
  --output-prefix <model>_llama_top20_diverse_compact_smoke
```

The compact diverse prompt set has 27 Llama packets, average prompt length about `9475` characters, and 40 Gemma packets, average prompt length about `9064` characters.

## Minimum Real Benchmark

After the 3-packet smoke is valid JSON and scores cleanly, run the compact diverse sets:

```bash
python3 work/run_openai_compatible_verifier.py \
  --base-url http://localhost:11434/v1 \
  --model <model> \
  --prompts outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.jsonl \
  --output outputs/<model>_llama_top20_diverse_compact_predictions.jsonl \
  --resume

python3 work/run_openai_compatible_verifier.py \
  --base-url http://localhost:11434/v1 \
  --model <model> \
  --prompts outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse_compact.jsonl \
  --output outputs/<model>_gemma_top20_diverse_compact_predictions.jsonl \
  --resume
```

Score:

```bash
python3 work/score_llm_judges.py \
  --predictions outputs/<model>_llama_top20_diverse_compact_predictions.jsonl outputs/<model>_gemma_top20_diverse_compact_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse_compact.answer_key.json \
  --output-prefix <model>_top20_diverse_compact_verifier
```

## Full-Prompt Fallback Sensitivity

Rerun full prompts for compact failures and low-confidence cases. If the first pass is cheap enough, the cleanest sensitivity run is full diverse on all packets:

```bash
python3 work/run_openai_compatible_verifier.py \
  --base-url http://localhost:11434/v1 \
  --model <model> \
  --prompts outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse.jsonl \
  --output outputs/<model>_llama_top20_diverse_full_predictions.jsonl \
  --resume

python3 work/run_openai_compatible_verifier.py \
  --base-url http://localhost:11434/v1 \
  --model <model> \
  --prompts outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse.jsonl \
  --output outputs/<model>_gemma_top20_diverse_full_predictions.jsonl \
  --resume
```

Then sweep compact-confidence fallback thresholds:

```bash
python3 work/score_verifier_cascade.py \
  --answer-key outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_diverse_compact.answer_key.json \
  --compact-predictions outputs/<model>_llama_top20_diverse_compact_predictions.jsonl \
  --full-predictions outputs/<model>_llama_top20_diverse_full_predictions.jsonl \
  --output-prefix outputs/<model>_llama_top20_diverse_cascade

python3 work/score_verifier_cascade.py \
  --answer-key outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_diverse_compact.answer_key.json \
  --compact-predictions outputs/<model>_gemma_top20_diverse_compact_predictions.jsonl \
  --full-predictions outputs/<model>_gemma_top20_diverse_full_predictions.jsonl \
  --output-prefix outputs/<model>_gemma_top20_diverse_cascade
```

## Pass / Fail Read

The method story gets much stronger if:

- compact verifier accuracy is clearly above cheap buried-packet baselines,
- full prompts rescue a meaningful share of compact failures,
- confidence or invalid-output status predicts enough failures to make the cascade cheaper than full-only,
- measured success/regression rates can replace the current `80% success / 2% false-regression` projection.

The method should be downgraded if compact accuracy collapses, full prompts do not rescue compact misses, or confidence does not separate success from failure.

## Paper Impact

This is the shortest path from "rank-bucket policy under projected verifier success" to a measured method result. Until this run exists, v33 should be described as robust projected allocation, not external verifier evidence.
