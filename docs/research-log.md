# Research Log

Use this as the compact source of truth for experiments that matter.

## 2026-06-01

- Initialized the repository as a Codex-friendly ML research staging ground.
- Started EGPR (Entropy-Gated Prototype Replay), a low-compute test-time adaptation probe that freezes the source classifier and adapts class prototypes only from low-entropy/high-confidence target examples. Initial digits-corruption run: helps localized occlusion slightly (0.951 source-only vs 0.954 EGPR) but hurts brightness, mixed, and noisy shifts, suggesting the next research target should be adaptation-safety prediction rather than raw accuracy chasing. See `docs/egpr-brief.md` and `experiments/egpr_digits_tta.py`.
