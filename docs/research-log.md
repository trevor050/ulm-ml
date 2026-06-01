# Research Log

Use this as the compact source of truth for experiments that matter.

## 2026-06-01

- Initialized the repository as a Codex-friendly ML research staging ground.

- Added a CPU-only associative-recall probe for compact sequence memories. Initial
  run shows explicit nearest-neighbor retrieval stays near 0.982 cosine through
  64 pairs, while compact fast-weight variants degrade with length; a learned
  gate improves the 64-pair result over a residual delta rule (0.564 vs. 0.420)
  but does not solve interference. See `docs/sequence-memory-fast-weights.md`.
