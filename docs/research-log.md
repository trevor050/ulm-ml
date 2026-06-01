# Research Log

Use this as the compact source of truth for experiments that matter.

## 2026-06-01

- Initialized the repository as a Codex-friendly ML research staging ground.
- Added a CPU-only TTA seed project: Prior-Anchored Conservative Entropy (PACE) for bias-only adaptation. Initial five-seed digits experiments suggest small gains for logit prior drift (balanced stream: source 0.892 accuracy, PACE 0.909) and a useful negative result for image corruption, where bias-only adaptation does not repair feature damage. See `docs/pace-bias-tta-report.md` and `experiments/pace_bias_tta.py`.
