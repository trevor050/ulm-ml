# ULM ML

Research staging ground for ULM machine-learning experiments, notes, and reusable analysis code.

## Quick Start

```bash
bash scripts/bootstrap.sh
source .venv/bin/activate
pytest
```

The bootstrap script uses `uv` for Python 3.11 when available, then falls back to the system `python3`.
Or install manually:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Current Research Threads

- Adaptive posterior self-consistency: a lightweight stopping rule for chain-of-thought self-consistency that spends fewer samples on converged prompts. See `docs/adaptive-posterior-self-consistency.md`, `src/ulm_ml/adaptive_consistency.py`, and `experiments/adaptive_consistency_synthetic.py`.
- Modular spectral split probe: a low-compute diagnostic for whether modular arithmetic train splits cover the latent Fourier coordinate before launching expensive grokking runs. See `docs/modular-spectral-probe.md` and `experiments/modular_spectral_probe.py`.
- Modular character baseline: explicit cyclic-character interaction features as a control for grokking-style modular arithmetic. See `docs/research-brief-character-timescales.md` and `experiments/modular_character_timescales.py`.
- Symmetry-augmented sparse recovery: cyclic augmentation as a controlled sparse-dictionary feature recovery probe. See `docs/symmetry-augmented-sparse-recovery.md`.
- PACE bias TTA: Prior-Anchored Conservative Entropy for bias-only logit calibration under unlabeled target drift. See `docs/pace-bias-tta-report.md`.
- EGPR prototype replay: mostly negative TTA scaffold now framed around predicting when adaptation is unsafe. See `docs/egpr-brief.md`.
- Sequence-memory fast weights: associative-recall harness with nearest-neighbor, scalar fast-weight, delta-rule, and learned-gate baselines. See `docs/sequence-memory-fast-weights.md`.
- Phase state tracking: root-of-unity finite-state sidecar as a constructive oracle/probe for recurrent models. See `docs/phase-state-tracking.md`.
- Cross-thread ranking and next experiments: see `docs/research-synthesis.md`.

## Repository Layout

```text
src/ulm_ml/        reusable package code
experiments/       runnable experiment scripts and configs
notebooks/         exploratory notebooks
data/              local datasets, ignored by git
artifacts/         generated experiment outputs, ignored by git
models/            local checkpoints/weights, ignored by git
reports/figures/   generated figures, ignored by git
docs/              research notes and decisions
tests/             regression tests for reusable code
```

## Working Pattern

Use notebooks for exploration, then promote repeatable pieces into `src/ulm_ml/` and cover them with tests. Keep large data, generated artifacts, checkpoints, and secrets out of git.
