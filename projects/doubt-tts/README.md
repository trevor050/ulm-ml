# Doubt-TTS / Reliability-Action Routing

Status: `full_research`

This folder packages the Doubt-TTS research thread as a self-contained monorepo
project. The current claim is not that generic self-doubt prompts work. The
useful object is an evidence-gated selective-compute controller that separates:

1. validity: answerable, false premise, ambiguous;
2. compute action: direct answer, premise check, retrieval, retrieval-backed
   premise check, deterministic verification, clarify;
3. source selection;
4. verifier execution;
5. response policy.

The strongest packet is `docs/doubt_tts_aggressive_submission_blueprint_v29.md`.
The paper-style draft is `docs/doubt_tts_paper_draft_v8.md`. The conservative
claim ledger is `docs/doubt_tts_claim_ledger.md`.

## Layout

- `docs/`: paper drafts, claim ledger, evidence manifest, benchmark reports, and
  controller analyses.
- `benchmarks/`: small route/event probes plus locked/blind/key JSONL exports for
  the reliability-action candidate benchmark.
- `scripts/`: runnable probe/scoring scripts copied from the Codex research
  harness.
- `runs/`: selected small run reports and stats needed to support the current
  claims.

Large caches, wiki fetch dumps, model outputs beyond selected scored summaries,
and one-off scratch artifacts are intentionally not included.

## Quick Checks

Run the deterministic event-verifier smoke test:

```bash
python projects/doubt-tts/scripts/doubt_probe.py \
  --data projects/doubt-tts/benchmarks/event_contrast_route_questions.jsonl \
  --route-only --event-verifier-only \
  --out /tmp/doubt_tts_table_event_results.jsonl \
  --report /tmp/doubt_tts_table_event_report.md
```

Expected route accuracy: `72/72`.

Run the held-out retrieval verifier with clean source inference:

```bash
python projects/doubt-tts/scripts/doubt_probe.py \
  --data projects/doubt-tts/benchmarks/heldout_event_retrieval_questions.jsonl \
  --route-only --retrieval-event-verifier-only --ignore-event-source-title \
  --out /tmp/doubt_tts_heldout_retrieval_results.jsonl \
  --report /tmp/doubt_tts_heldout_retrieval_report.md
```

Expected route accuracy: `32/32`.

## Current Verdict

Keep as full research. The negative controls are the point: directed challenge
wording is not validated, while route/action/source/verifier decomposition
exposes measurable failure modes. The next real gate is whether the controller
beats deterministic and text-only baselines under family-held-out,
cue-balanced, and human-paraphrase evaluation without hiding behind
over-retrieval or abstention.

