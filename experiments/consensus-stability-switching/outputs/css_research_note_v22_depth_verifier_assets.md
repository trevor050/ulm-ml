# v22 Depth-Verifier Prompt Assets

## Purpose

v21 made the adaptive-depth argument by projection. The next thing a reviewer should demand is measured verifier success at top-10/top-20 depth. I prepared strict prompt assets for that experiment.

## Builder Fix

The original hard-packet builder could force-insert a correct cluster into the visible packet if the correct cluster was outside top-k. That was useful for an early semantic-signal smoke test, but it is not valid for depth-frontier evaluation.

The builder now supports:

```bash
--no-force-correct-visible
--require-correct-visible
--min-correct-rank <rank>
--max-correct-rank <rank>
--representatives-per-cluster <n>
```

This lets us create honest natural top-k windows and rank-stratified buried-cluster tests.

## New Assets

Unstratified strict natural-visible packets:

- `outputs/cluster_packets_math_llama_n128_top10_strict.jsonl` and prompts `outputs/cluster_verifier_prompts_math_llama_n128_top10_strict.jsonl`
- `outputs/cluster_packets_math_gemma2b_n128_top10_strict.jsonl` and prompts `outputs/cluster_verifier_prompts_math_gemma2b_n128_top10_strict.jsonl`
- `outputs/cluster_packets_math_llama_n128_top20_strict.jsonl` and prompts `outputs/cluster_verifier_prompts_math_llama_n128_top20_strict.jsonl`
- `outputs/cluster_packets_math_gemma2b_n128_top20_strict.jsonl` and prompts `outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_strict.jsonl`

Rank-stratified buried-cluster packets:

- `outputs/cluster_packets_math_llama_n128_top10_rank6_10_strict.jsonl` and prompts `outputs/cluster_verifier_prompts_math_llama_n128_top10_rank6_10_strict.jsonl`
- `outputs/cluster_packets_math_gemma2b_n128_top10_rank6_10_strict.jsonl` and prompts `outputs/cluster_verifier_prompts_math_gemma2b_n128_top10_rank6_10_strict.jsonl`
- `outputs/cluster_packets_math_llama_n128_top20_rank11_20_strict.jsonl` and prompts `outputs/cluster_verifier_prompts_math_llama_n128_top20_rank11_20_strict.jsonl`
- `outputs/cluster_packets_math_gemma2b_n128_top20_rank11_20_strict.jsonl` and prompts `outputs/cluster_verifier_prompts_math_gemma2b_n128_top20_rank11_20_strict.jsonl`

Audit: `outputs/depth_packet_asset_audit.md`.

## Why This Matters

The top-20 rank11-20 sets are the clean test of the aggressive claim. If a real verifier cannot recover these packets above shallow baselines, adaptive-depth verification is probably not enough by itself; the method needs an evidence-retrieval or ranking-improvement step before semantic judging.

If a real verifier does recover them, the v21 projection can be upgraded from assumed verifier success to measured success/regression.
