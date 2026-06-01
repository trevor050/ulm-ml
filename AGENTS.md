# ULM ML Notes

Research staging repo for ULM machine-learning experiments. Keep this file tight: future agents need fast orientation, not a diary.

## Shape

- `src/ulm_ml/` is the importable Python package for reusable research code.
- `experiments/` is for runnable experiment scripts and configs.
- `notebooks/` is for exploratory notebooks. Move stable logic into `src/ulm_ml/`.
- `data/`, `artifacts/`, `models/`, and `reports/figures/` are intentionally ignored except for `.gitkeep` placeholders.
- `docs/research-log.md` is the lightweight running log for decisions, datasets, and results worth remembering.
- `docs/research-synthesis.md` is the current cross-thread ranking and caveat map.

## Commands

- Bootstrap locally: `bash scripts/bootstrap.sh`
- Install/update deps: `python -m pip install -e ".[dev]"`
- Run tests: `pytest`
- Lint: `ruff check .`

## Hazards

- Do not commit raw datasets, model checkpoints, generated figures, secrets, or notebooks with large embedded outputs.
- Prefer small reproducible scripts over one-off notebook-only logic when an experiment starts to matter.
- If adding external data sources, document source, license/terms, retrieval date, and preprocessing path in `docs/research-log.md`.
- Treat modular spectral features and phase channels as oracle/control probes unless a learned model actually discovers them.
- For sparse recovery, use the unique one-to-one metric as the headline; loose best-match recovery is only diagnostic.
- For EGPR, current evidence is mostly negative; frame future work around no-label safety prediction instead of raw accuracy claims.
