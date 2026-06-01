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
