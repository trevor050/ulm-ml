# Adaptive Posterior Self-Consistency

Status: `given_up`

This is given up as an active standalone research project until real cached
answer traces exist.

## What Remains Useful

`src/ulm_ml/adaptive_consistency.py` has useful replay machinery: fixed-budget
rules, vote-margin rules, posterior-confidence rules, and an answer-only CSV
trace loader. `docs/adaptive-posterior-self-consistency.md` defines the schema
needed for real traces.

## Why It Is Given Up

The current positive result is synthetic. It shows that a Dirichlet posterior
stopping rule behaves plausibly under clean categorical assumptions, but it does
not prove call savings on GSM8K, SVAMP, or any real LLM workload. No real model
answers, token counts, extraction errors, or correlated samples have been
replayed yet.

## Revival Gate

Revive only after collecting answer-only traces with:

```text
task_id,sample_index,answer,correct_answer,token_count
```

Then run:

```bash
PYTHONPATH=src python experiments/adaptive-self-consistency/adaptive_consistency_replay.py traces.csv --max-samples 32
```

The project becomes research again only if posterior stopping beats fixed and
margin baselines on identical prefixes while reporting accuracy, mean calls,
p90 calls, and token use.
