# ULM ML Notes

Public monorepo for ULM machine-learning experiments. Keep this file tight: future agents need fast orientation, not a diary.

## Shape

- `src/ulm_ml/` is the importable Python package for reusable research code.
- `experiments/` is the public shelf: one folder per research experiment, each with a README containing question, verdict, answer so far, interesting bit, commands, and deeper notes.
- `notebooks/` is for exploratory notebooks. Move stable logic into `src/ulm_ml/`.
- `data/`, `artifacts/`, `models/`, and `reports/figures/` are intentionally ignored except for `.gitkeep` placeholders.
- This is a monorepo by policy: add new ML ideas as experiment folders plus shared code/tests before creating separate packages.
- `docs/research-log.md` is the lightweight running log for decisions, datasets, and results worth remembering.
- `docs/research-synthesis.md` is the current cross-thread ranking and caveat map.
- `docs/research-portfolio.md` and `src/ulm_ml/research_portfolio.py` are the binary project map: every thread is either `full_research` or `given_up`.
- `docs/research-portfolio.md` is the hard binary keep/give-up map. Use it before spending time deepening a thread.

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
- Doubt-TTS / reliability-action routing now lives in `experiments/doubt-tts/` as a full-research track; keep its claims negative-controlled and do not rebrand it as generic self-doubt prompting.
- Consensus-Stability Switching now lives in `experiments/consensus-stability-switching/` as a full-research track; keep raw Monkey Business traces out of git and use its local `README.md` / `outputs/result_ledger.md` before editing.
- The active full-research tracks are cyclic representation probes, symmetry-augmented sparse recovery, sequence-memory interference, Doubt-TTS / reliability-action routing, and Consensus-Stability Switching.
- Adaptive self-consistency, EGPR prototype replay, and PACE bias-only TTA are given up as active standalone projects unless their `docs/given-up/` resurrection gates are satisfied.
