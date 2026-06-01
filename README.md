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


## Active Research Threads

- Modular spectral split probe: a low-compute diagnostic for whether modular arithmetic train splits cover the latent Fourier coordinate before launching expensive grokking runs. See `docs/modular-spectral-probe.md` and `experiments/modular_spectral_probe.py`.

## Working Pattern

Use notebooks for exploration, then promote repeatable pieces into `src/ulm_ml/` and cover them with tests. Keep large data, generated artifacts, checkpoints, and secrets out of git.
