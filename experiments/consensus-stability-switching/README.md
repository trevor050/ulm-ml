# Consensus-Stability Switching

This folder is a compact import of the local Cluster Selectability / Consensus-Stability Switching sprint from:

`/Users/trevorrosato/Documents/Codex/2026-06-01/all-right-suck-it-i-believe-2`

## Status

`full_research`

## Short Version

Repeated sampling on hard math often generates the correct answer, but the default selector chooses the wrong answer cluster. The sprint asks whether answer-cluster selection, routing, and pairwise verification can recover that hidden correct answer without adding unacceptable regressions.

The current best result is not a generic verifier win. Full-cluster local verifier prompts mostly failed. The useful direction is narrower pairwise adjudication: compare the baseline answer against a candidate answer and only accept the candidate when a calibrated judge/rule says to.

## What Is Included

- `work/`: runnable analysis scripts and tests copied from the local sprint, including the current pairwise-router harness.
- `outputs/`: curated research notes, ledgers, reproducibility manifest, and v119-v130 pairwise-router artifacts.
- `AGENTS.source.md`: the original local project notes, kept as context for future agents.

## What Is Not Included

Large local trace files are intentionally omitted from git:

- `work/GSM8K_Llama-3-8B-Instruct.json`
- `work/MATH_Llama-3-8B-Instruct.json`
- `work/MATH_Gemma-2B.json`
- `work/MATH_Pythia-1B.json`
- `outputs/cross_seed_router_frontier_v113_details.jsonl`

The source data came from local Monkey Business traces. Keep raw traces in local data storage, not in this monorepo.

## Start Here

- `outputs/README.md`: full artifact index.
- `outputs/result_ledger.md`: compact scoreboard of what worked and failed.
- `outputs/reproducibility_manifest.md`: command ledger.
- `outputs/css_research_note_v130_pairwise_rich_prompt_probe.md`: latest pairwise prompt stress result.
- `outputs/css_research_note_v122_pairwise_natural_rate.md`: natural-rate denominator correction for the strongest conservative pairwise result.

## Current Claim

Hard MATH traces show a robust selectability gap: correct answers are often generated before current selectors identify them. Cheap selector/ranker/full-cluster verifier variants mostly fail. Pairwise baseline-vs-candidate adjudication is the first measured local-verifier interface with meaningful held-out natural-rate gain and regression accounting.

## Representative Commands

```bash
python experiments/consensus-stability-switching/work/make_pairwise_rich_probe_prompts.py
python experiments/consensus-stability-switching/work/summarize_pairwise_rich_probe.py
```

Most reruns need the omitted raw trace files restored under `experiments/consensus-stability-switching/work/` or path arguments pointed at local copies.

