# ULM ML Monorepo

Public monorepo for Trevor's machine-learning research threads: small
CPU-first experiments, reusable probes, blunt negative results, and project
notes that are useful enough to survive contact with GitHub.

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

The repo is intentionally a monorepo. Shared implementation lives in
`src/ulm_ml/`; each research track gets its own docs, experiments, and tests
without becoming a separate package until it earns that complexity.

## Project Index

| status | project | code | experiment/docs |
| --- | --- | --- | --- |
| `full_research` | Cyclic representation probes | `src/ulm_ml/modular_*.py`, `src/ulm_ml/state_tracking.py` | `experiments/modular_*`, `experiments/phase_state_tracking.py`, `docs/full-research/cyclic-representation-probes.md` |
| `full_research` | Symmetry-augmented sparse recovery | `src/ulm_ml/symmetry_sparse.py` | `experiments/symmetry_augmented_sparse_recovery.py`, `docs/full-research/symmetry-sparse-recovery.md` |
| `full_research` | Sequence-memory interference | `src/ulm_ml/sequence_memory/` | `experiments/sequence_memory/`, `docs/full-research/sequence-memory-interference.md` |
| `full_research` | Doubt-TTS / reliability-action routing | `projects/doubt-tts/scripts/` | `projects/doubt-tts/` |
| `given_up` | Adaptive posterior self-consistency | `src/ulm_ml/adaptive_consistency.py` | `experiments/adaptive_consistency_*.py`, `docs/given-up/adaptive-self-consistency.md` |
| `given_up` | EGPR prototype replay | `src/ulm_ml/egpr.py` | `experiments/egpr_digits_tta.py`, `docs/given-up/egpr-prototype-replay.md` |
| `given_up` | PACE bias-only TTA | `src/ulm_ml/tta.py` | `experiments/pace_bias_tta.py`, `docs/given-up/pace-bias-tta.md` |

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
- Doubt-TTS / reliability-action routing: negative-controlled selective QA work
  showing generic doubt prompts are weak, while validity/action/source/verifier
  decomposition gives a sharper controller target. See `projects/doubt-tts/`.

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

When a new ML idea lands here, start it as a focused experiment plus a short
doc. It graduates only when the portfolio can give it a binary verdict:
`full_research` with a falsifiable question and a real control, or `given_up`
with a clear resurrection gate.
