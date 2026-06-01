# Research Log

Use this as the compact source of truth for experiments that matter.

## 2026-06-01

- Initialized the repository as a Codex-friendly ML research staging ground.

- Started the adaptive posterior self-consistency thread: a Dirichlet posterior early-stopping rule for answer-only self-consistency traces. Initial synthetic replay (`reports/adaptive-consistency.md`) matched fixed-32 accuracy with about half the samples; next step is replay on cached GSM8K/SVAMP traces from a small reasoning model.
