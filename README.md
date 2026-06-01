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

## Research Portfolio

Every project is now forced into one of two buckets: `full_research` or
`given_up`. See `docs/research-portfolio.md` for the binary verdict table and
`src/ulm_ml/research_portfolio.py` for the machine-readable manifest.

### Full Research Tracks

- Cyclic representation probes: modular spectral diagnostics, modular character
  baselines, and phase-state tracking are one track about cyclic representations
  and data-split geometry, now including a learned MLP memorization sanity
  check. See `docs/full-research/cyclic-representation-probes.md`.
- Symmetry-augmented sparse recovery: cyclic augmentation improves strict
  one-to-one sparse feature recovery while a size-matched false-symmetry control
  fails. See `docs/full-research/symmetry-sparse-recovery.md`.
- Sequence-memory interference: associative-recall load curves expose where
  compact fast-weight, delta, gated, and orthogonalized memories fail against
  retrieval baselines. See `docs/full-research/sequence-memory-interference.md`.

### Given Up As Active Projects

- Adaptive posterior self-consistency: parked until cached real-model answer
  traces exist. See `docs/given-up/adaptive-self-consistency.md`.
- EGPR prototype replay: given up as an adaptation method after no-adapt
  baselines beat online updates. See `docs/given-up/egpr-prototype-replay.md`.
- PACE bias-only TTA: kept only as a narrow prior-drift diagnostic baseline.
  See `docs/given-up/pace-bias-tta.md`.

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
