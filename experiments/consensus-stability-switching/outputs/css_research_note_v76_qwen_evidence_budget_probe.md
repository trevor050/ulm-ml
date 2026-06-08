# v76 Qwen Evidence-Budget Probe

**Date:** June 1, 2026  
**Question:** Did the v75 qwen3.5:9b smoke fail because the slim prompt was evidence-starved, because the prompt encouraged scratch-solving, or because the local 9B verifier is too weak for these recoverable cluster failures?

## Setup

v75 ran qwen3.5:9b on a 12-prompt slim concise deployed-mix smoke and recovered `0/6` visible recoverable buckets. v76 reuses exactly those six recoverable failures:

```text
cluster_packets_math_gemma2b_n128_deployed_mix_top20-0004  recoverable_top5
cluster_packets_math_gemma2b_n128_deployed_mix_top20-0012  recoverable_top20_only
cluster_packets_math_gemma2b_n128_deployed_mix_top20-0023  recoverable_top10_only
cluster_packets_math_llama_n128_deployed_mix_top20-0000    recoverable_top5
cluster_packets_math_llama_n128_deployed_mix_top20-0004    recoverable_top10_only
cluster_packets_math_llama_n128_deployed_mix_top20-0007    recoverable_top20_only
```

I added [filter_verifier_prompt_panel.py](filter_verifier_prompt_panel.py) to build targeted prompt panels from generated prompt JSONL files without hand-splicing rows.

## Rich Prompt

First rerun: two representatives per cluster, 420 chars per rationale, concise answer instruction.

```bash
python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_concise.jsonl \
  --representatives-per-cluster 2 \
  --rationale-chars 420 \
  --concise-reason-words 20

python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_concise.jsonl \
  --representatives-per-cluster 2 \
  --rationale-chars 420 \
  --concise-reason-words 20

python3 work/filter_verifier_prompt_panel.py \
  --prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_concise.jsonl outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_concise.jsonl \
  --ids outputs/qwen35_9b_v76_recoverable_failures_ids.txt \
  --output outputs/qwen35_9b_v76_recoverable_failures_rich_concise_prompts.jsonl \
  --add-dataset
```

The resulting six prompts average about `13.2k` JSONL chars, versus the v75 slim prompt family at lower evidence density.

Result report: [qwen35_9b_v76_recoverable_failures_rich_concise_report.md](qwen35_9b_v76_recoverable_failures_rich_concise_report.md).

Outcome: `0/6` recoveries. Rich evidence did not rescue qwen. It also made formatting worse: five of six rows lacked parseable `answer`/`confidence` keys under the runner's strict-plus-salvage parser.

## Evidence-Only Prompt

Second rerun: same richer cluster evidence, but omit the original problem statement and include an allowed-answer copy list. This tests whether qwen was failing by solving from scratch instead of judging candidate rationales.

```bash
python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_evidenceonly.jsonl \
  --representatives-per-cluster 2 \
  --rationale-chars 420 \
  --concise-reason-words 20 \
  --omit-problem \
  --allowed-answers

python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_evidenceonly.jsonl \
  --representatives-per-cluster 2 \
  --rationale-chars 420 \
  --concise-reason-words 20 \
  --omit-problem \
  --allowed-answers
```

Run:

```bash
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local

python3 work/run_ollama_native_verifier.py \
  --base-url http://127.0.0.1:11435 \
  --model qwen3.5:9b \
  --prompts outputs/qwen35_9b_v76_recoverable_failures_rich_evidenceonly_prompts.jsonl \
  --output outputs/qwen35_9b_v76_recoverable_failures_rich_evidenceonly_predictions.jsonl \
  --timeout 240 \
  --retries 1 \
  --log-every 1 \
  --include-timing \
  --num-predict 256 \
  --resume
```

Result report: [qwen35_9b_v76_recoverable_failures_rich_evidenceonly_report.md](qwen35_9b_v76_recoverable_failures_rich_evidenceonly_report.md).

Outcome: again `0/6` recoveries. Evidence-only prompting produced the same scored pattern as the rich prompt: qwen still failed all recoverable buckets.

## Gemma Probe

I also tried `gemma4:26b` on one v75 slim concise row. It returned a malformed/prose response with a wrong salvaged answer (`22`) and continued self-correction after a fenced JSON fragment. It is not usable as deployed verifier evidence without a better prompt/control strategy.

Artifact: [gemma4_26b_deployed_mix_real_v76_slim_concise_probe_predictions.jsonl](gemma4_26b_deployed_mix_real_v76_slim_concise_probe_predictions.jsonl).

## Operational Note

The local tunnel should be made explicit IPv4:

```bash
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local
```

Using `localhost` hit an IPv6/duplicate-forward failure mode where the tunnel accepted TCP but returned an empty HTTP reply. Use `http://127.0.0.1:11435` for verifier runs.

## Read

v76 strengthens the negative result from v75. The failure is no longer just "one slim prompt was too small." On the same six v75 recoverable failures:

- slim concise qwen: `0/6`,
- rich concise qwen: `0/6`,
- rich evidence-only qwen: `0/6`.

This does not refute adaptive-depth verification. It does refute a cheap local `qwen3.5:9b` implementation as sufficient evidence for the method, even when the prompt includes more cluster evidence and discourages scratch-solving.

The next positive experiment should use a stronger verifier with reliable structured output, or a different verification interface entirely, such as full-prompt fallback with a frontier/API model, a math-specialized judge, or a cluster-choice model trained/calibrated on these packet formats.
