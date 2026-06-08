# v92 Mathstral Verifier Boundary

**Date:** June 2, 2026  
**Question:** Does a math-specialized local verifier (`mathstral:7b`) change the negative local-verifier stopline from v75-v84?

## Setup

After permissions were widened, the Windows training PC was reachable through SSH:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 -o User=trevor trevors-pc.local "echo ok"
```

I pulled `mathstral:7b` on the remote Ollama host and used the explicit IPv4 tunnel:

```bash
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 trevors-pc.local
```

Ollama reported `mathstral:7b` loaded mostly on CPU:

```text
PROCESSOR 93%/7% CPU/GPU
CONTEXT   4096
```

That matters. The local endpoint is reachable, but this is not a clean high-throughput RTX verifier run.

## Runs

### 1. v75 slim concise deployed-mix smoke

Same 12-prompt panel used for qwen3.5:9b in v75:

- prompts: [deployed_mix_real_v75_slim_concise_percat1_prompts.jsonl](deployed_mix_real_v75_slim_concise_percat1_prompts.jsonl)
- predictions: [mathstral_7b_v92_deployed_mix_real_v75_slim_concise_percat1_predictions.jsonl](mathstral_7b_v92_deployed_mix_real_v75_slim_concise_percat1_predictions.jsonl)
- report: [mathstral_7b_v92_deployed_mix_real_v75_slim_concise_percat1_report.md](mathstral_7b_v92_deployed_mix_real_v75_slim_concise_percat1_report.md)

Outcome:

- Coverage complete: `6/6` MATH/Gemma, `6/6` MATH/Llama.
- Baseline-correct rows preserved: `1/1` Gemma, `1/1` Llama.
- Recoverable buckets recovered: `0/3` Gemma, `0/3` Llama.
- No threshold passes with a positive deployed delta.

This reproduces the qwen-style negative result under a math-specialized 7B model: clean enough to score, but no visible-cluster recovery.

### 2. Rich recoverable-only rerun

Same six v75/v76 recoverable failures, but with two representatives per cluster and 420 rationale chars:

- predictions: [mathstral_7b_v92_recoverable_failures_rich_concise_predictions.jsonl](mathstral_7b_v92_recoverable_failures_rich_concise_predictions.jsonl)
- report: [mathstral_7b_v92_recoverable_failures_rich_concise_report.md](mathstral_7b_v92_recoverable_failures_rich_concise_report.md)

Outcome:

- Coverage complete: `3/3` Gemma, `3/3` Llama.
- Recoveries: `0/6`.
- The answer field often contained generated prose rather than an exact candidate answer.

Richer problem-inclusive evidence did not rescue the model.

### 3. v77 answer-only evidence-only targeted rerun

Same six recoverable failures, but no problem statement, allowed-answer copy list, and answer/confidence JSON only:

- prompts: [v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl](v77_recoverable_failures_answeronly_evidenceonly_prompts.jsonl)
- predictions: [mathstral_7b_v92_recoverable_failures_answeronly_evidenceonly_predictions.jsonl](mathstral_7b_v92_recoverable_failures_answeronly_evidenceonly_predictions.jsonl)
- report: [mathstral_7b_v92_recoverable_failures_answeronly_evidenceonly_report.md](mathstral_7b_v92_recoverable_failures_answeronly_evidenceonly_report.md)

Outcome:

- Coverage complete.
- Gemma recoverable top20-only recovered `1/1` by selecting `-2`.
- Other recoverable rows: `0/5`.
- Llama remained `0/3`.

This is the first real local-model recovery on the v75 hard recoverable set, but it is one packet and it appears only under the richer answer-only evidence-only interface.

### 4. v77 answer-only evidence-only 12-row deployed-mix smoke

I filtered the v77 answer-only/evidence-only prompt family to the same 12 deployed-mix smoke IDs:

- ids: [mathstral_v92_v77_answeronly_evidenceonly_percat1_ids.txt](mathstral_v92_v77_answeronly_evidenceonly_percat1_ids.txt)
- prompts: [mathstral_v92_v77_answeronly_evidenceonly_percat1_prompts.jsonl](mathstral_v92_v77_answeronly_evidenceonly_percat1_prompts.jsonl)
- predictions: [mathstral_7b_v92_v77_answeronly_evidenceonly_percat1_predictions.jsonl](mathstral_7b_v92_v77_answeronly_evidenceonly_percat1_predictions.jsonl)
- report: [mathstral_7b_v92_v77_answeronly_evidenceonly_percat1_report.md](mathstral_7b_v92_v77_answeronly_evidenceonly_percat1_report.md)

Prompt cost was much higher than v75: average JSONL chars `12820`, max `19304`.

Outcome at threshold `0.0`:

| dataset | deployed delta | read |
|---|---:|---|
| MATH/Gemma | `+0.080` | one top20-only recovery and sampled baseline preserved |
| MATH/Llama | `-0.428` | sampled baseline-correct row regressed, no recoveries |

The Gemma row passes the report harness's lower-CI-positive rule only because the panel has one packet per category, so the bootstrap has no within-category variation. Treat it as a positive smoke datapoint, not a benchmark result.

### 5. v92 slim answer-only evidence-only 12-row deployed-mix smoke

To test whether the one Gemma recovery survives a cheaper interface, I generated a slim answer-only/evidence-only variant with one representative per cluster and 180 rationale chars:

```bash
python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v92_slim_answeronly_evidenceonly.jsonl \
  --representatives-per-cluster 1 \
  --rationale-chars 180 \
  --omit-problem \
  --allowed-answers \
  --answer-only

python3 work/make_cluster_verifier_prompts.py \
  --packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20.jsonl \
  --output outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v92_slim_answeronly_evidenceonly.jsonl \
  --representatives-per-cluster 1 \
  --rationale-chars 180 \
  --omit-problem \
  --allowed-answers \
  --answer-only
```

Artifacts:

- prompts: [mathstral_v92_slim_answeronly_evidenceonly_percat1_prompts.jsonl](mathstral_v92_slim_answeronly_evidenceonly_percat1_prompts.jsonl)
- predictions: [mathstral_7b_v92_slim_answeronly_evidenceonly_percat1_predictions.jsonl](mathstral_7b_v92_slim_answeronly_evidenceonly_percat1_predictions.jsonl)
- report: [mathstral_7b_v92_slim_answeronly_evidenceonly_percat1_report.md](mathstral_7b_v92_slim_answeronly_evidenceonly_percat1_report.md)

Prompt cost was back near v75: average JSONL chars `6150`, max `7425`.

Outcome:

- Gemma recoveries: `0/3`.
- Llama recoveries: `0/3`.
- Llama baseline-correct row regressed again.
- One Gemma row emitted invalid confidence `23`, so confidence-threshold deployment should not be trusted without confidence validation/clamping.
- No threshold passes with positive deployed delta.

The one rich Gemma recovery does not survive the slim answer-only ablation.

## Failed Expansion Attempt

I attempted a full 72-prompt Gemma v77 answer-only/evidence-only run. It stalled after one completed row. I then tried a length-capped short3-per-category Gemma panel; it stalled after three completed rows. The local endpoint was reporting `93%/7% CPU/GPU`, so these stalls are best treated as an operational boundary of the available Ollama setup, not as meaningful verifier accuracy evidence.

Partial artifacts are retained:

- [mathstral_7b_v92_gemma_v77_answeronly_evidenceonly_full_predictions.jsonl](mathstral_7b_v92_gemma_v77_answeronly_evidenceonly_full_predictions.jsonl), `1` row
- [mathstral_7b_v92_gemma_v77_answeronly_evidenceonly_short3_percat_predictions.jsonl](mathstral_7b_v92_gemma_v77_answeronly_evidenceonly_short3_percat_predictions.jsonl), `3` rows

## Read

`mathstral:7b` changes the local-verifier story from "zero recoveries anywhere" to "one fragile Gemma top20-only recovery under a rich answer-only/evidence-only interface." That is useful, but it is not a positive deployed verifier result.

The reviewer-resistant conclusion is:

- A math-specialized 7B local model can sometimes identify a buried correct cluster.
- The signal is not robust across prompt budgets: rich v77 gets one Gemma recovery, slim answer-only loses it.
- It does not transfer across the paired Llama smoke: Llama remains `0/3` recoverable and regresses the sampled baseline-correct case under answer-only evidence-only.
- Confidence outputs are not deployable as-is; one slim run produced confidence `23`.
- Full rich expansion is operationally blocked on the current Ollama path because `mathstral:7b` runs mostly CPU-bound with bad tail latency.

So v92 strengthens the paper by narrowing the missing piece. The adaptive-depth projection still needs a stronger measured verifier, but the next attempt should not be another casual local chat-model prompt variant. It needs either a substantially stronger endpoint, a validated confidence/clamping layer plus larger deployed-mix panel, or a non-generative cluster-scoring interface.
