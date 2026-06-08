# v84 Qwen3:14B Rich Problem-Prompt Stopline

**Date:** June 2, 2026  
**Question:** Was the v83 qwen3:14b failure caused by an overly austere answer-only / evidence-only interface that omitted the original problem and richer cluster evidence?

## Verdict

No. Rich, problem-inclusive prompts improve the raw full-panel recovery count slightly, but they still do not produce a deployable verifier.

The full v84 rich-concise panel completes `144/144` prompts and recovers `4/72` recoverable failures, up from `2/72` in the v83 answer-only / evidence-only full panel. That small gain is not enough: it preserves only `12/24` already-correct baselines, still recovers `0` top20-only failures across both datasets, and no confidence threshold has a lower-CI-positive deployed delta.

The targeted hard-failure rerun is even cleaner: on the original six recoverable qwen failure cases, problem-inclusive richer prompts remain `0/6`.

## Runs

### Targeted recoverable-failure panel

```bash
python3 work/run_ollama_native_verifier.py \
  --base-url http://127.0.0.1:11435 \
  --model qwen3:14b \
  --prompts outputs/qwen35_9b_v76_recoverable_failures_rich_concise_prompts.jsonl \
  --output outputs/qwen3_14b_v84_recoverable_failures_rich_concise_predictions.jsonl \
  --timeout 480 \
  --retries 1 \
  --log-every 1 \
  --include-timing \
  --num-predict 128 \
  --schema-mode answer_reason \
  --resume
```

Result: complete `6/6`; recoverable correct `0/6`; no threshold positive.

Report: [qwen3_14b_v84_recoverable_failures_rich_concise_report.md](qwen3_14b_v84_recoverable_failures_rich_concise_report.md).

### Full deployed-mix rich-concise panel

The full run used the v76 rich-concise prompt family, which includes the original problem plus two representatives per cluster.

```bash
python3 work/deployed_mix_verifier_report.py \
  --predictions outputs/qwen3_14b_v84_llama_full72_rich_concise_predictions.jsonl outputs/qwen3_14b_v84_gemma_full72_rich_concise_predictions.jsonl \
  --answer-keys outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_concise.answer_key.json outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_concise.answer_key.json \
  --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_category_stats.csv outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_category_stats.csv \
  --expected-prompts outputs/cluster_verifier_prompts_math_llama_n128_deployed_mix_top20_v76_rich_concise.jsonl outputs/cluster_verifier_prompts_math_gemma2b_n128_deployed_mix_top20_v76_rich_concise.jsonl \
  --thresholds 0,0.5,0.75,0.9 \
  --bootstrap-rounds 1000 \
  --seed 60601 \
  --output-prefix qwen3_14b_v84_full144_rich_concise_report
```

Report: [qwen3_14b_v84_full144_rich_concise_report.md](qwen3_14b_v84_full144_rich_concise_report.md).

## Full-Panel Category Read

| dataset | baseline-correct preserved | recoverable_top5 | recoverable_top10_only | recoverable_top20_only | best CI read |
|---|---:|---:|---:|---:|---|
| MATH/Gemma | `4/12` | `0/12` | `1/12` | `0/12` | all thresholds negative; best delta `-0.141` at threshold `0.90` |
| MATH/Llama | `8/12` | `2/12` | `1/12` | `0/12` | no positive CI; best delta `-0.035` at thresholds `0.75`/`0.90` |

Combined recoverable recovery is `4/72`. Combined baseline-correct preservation is `12/24`.

The v71 target check fails for both datasets and both depths. With observed baseline regressions, the required recovery count rises, while qwen3:14b supplies only shallow recoveries and no top20-only tail evidence.

## Comparison To v83

| run | prompt/interface | coverage | recoverable correct | baseline preservation | read |
|---|---|---:|---:|---:|---|
| v83 full144 | answer-only, evidence-only | `144/144` | `2/72` | `13/24` | weak recovery, regression-heavy, CI-negative |
| v84 targeted | problem-inclusive rich-concise | `6/6` | `0/6` | not measured | hard failures still missed |
| v84 full144 | problem-inclusive rich-concise | `144/144` | `4/72` | `12/24` | slightly more shallow recovery, worse preservation, CI-negative |

Richer prompts therefore do not rescue qwen3:14b. They add a couple shallow recoveries, but the regression cost remains fatal and the depth-limited tail remains untouched.

## Operational Notes

During the full rich-concise run, the remote Ollama HTTP stream dropped with `http.client.RemoteDisconnected`. `work/run_ollama_native_verifier.py` now treats `RemoteDisconnected` as retryable, alongside URL/time/JSON errors, so resumed long runs survive transient tunnel failures.

The usual `trevors-pc.local` path became flaky during v84. Direct SSH to `192.168.1.151` worked for the tunnel:

```bash
ssh -4 -o User=trevor -N -L 127.0.0.1:11435:127.0.0.1:11434 192.168.1.151
```

## Pitch Impact

v84 closes the cleanest reviewer objection to v83:

> Maybe qwen3:14b failed because the prompt hid the original problem or supplied too little cluster evidence.

That objection has now been tested. The available local qwen3:14b verifier is still not deployable under regression-aware scoring. The next route is a substantially stronger verifier endpoint, richer semantic cluster scoring, or expanded positive recovery data for a learned gate, not more local qwen/gemma prompt variants.
