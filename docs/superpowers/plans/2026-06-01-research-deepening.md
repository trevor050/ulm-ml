# ULM ML Research Deepening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate the eight cloud research PRs into one stronger research branch, fix the weak evidence paths, and add enough reproducible experiment scaffolding that future Codex cloud agents can push from real baselines instead of toy claims.

**Architecture:** Keep each research thread as a small CPU-first module plus a runnable experiment and a short report. Add shared metrics only where they prevent inflated results or repeated mistakes. Prefer honest negative results over cosmetic wins.

**Tech Stack:** Python 3.11, NumPy, pandas, SciPy, scikit-learn, pytest, ruff, GitHub Actions.

---

## File Map

- `src/ulm_ml/modular_arithmetic.py`: modular operation datasets and explicit Fourier/character baselines.
- `src/ulm_ml/modular_spectral.py`: split-family diagnostics and Fourier oracle coverage probes.
- `src/ulm_ml/symmetry_sparse.py`: cyclic sparse recovery generator, NMF fit helpers, strict recovery metrics.
- `src/ulm_ml/sequence_memory/`: associative-recall task and fast-weight memory baselines.
- `src/ulm_ml/tta.py` and `src/ulm_ml/egpr.py`: lightweight test-time adaptation utilities.
- `src/ulm_ml/adaptive_consistency.py`: self-consistency stopping policies.
- `src/ulm_ml/state_tracking.py`: finite-state sequence tracking probes.
- `experiments/`: runnable CPU-first experiments; generated outputs go to ignored `artifacts/` or `reports/`.
- `docs/research-synthesis.md`: final cross-thread synthesis, ranking, caveats, and next experiments.

## Task 1: Integrate Research Threads

**Files:**
- Modify: `README.md`
- Modify: `docs/research-log.md`
- Add/merge: research modules, docs, experiments, and tests from PRs #1-#8.

- [ ] **Step 1: Merge the strongest grokking and sparse-recovery branches first**

Run:

```bash
git merge --no-ff origin/pr/5 -m "Merge modular character baseline"
git merge --no-ff origin/pr/7 -m "Merge modular spectral split probe"
git merge --no-ff origin/pr/2 -m "Merge symmetry sparse recovery study"
```

Expected: conflicts may appear in `README.md`, `docs/research-log.md`, and `experiments/README.md`; resolve by keeping all research entries while avoiding duplicate headings.

- [ ] **Step 2: Merge utility and adaptation branches**

Run:

```bash
git merge --no-ff origin/pr/6 -m "Merge adaptive consistency study"
git merge --no-ff origin/pr/1 -m "Merge PACE bias TTA study"
git merge --no-ff origin/pr/3 -m "Merge associative recall fast-weight probe"
git merge --no-ff origin/pr/4 -m "Merge EGPR prototype replay scaffold"
git merge --no-ff origin/pr/8 -m "Merge phase state tracking probe"
```

Expected: all files are present locally; weak PRs are not left as final claims until later tasks rewrite their reports.

- [ ] **Step 3: Verify the merged tree**

Run:

```bash
.venv/bin/ruff check .
.venv/bin/pytest
```

Expected: lint and tests pass before deeper edits begin.

## Task 2: Fix Inflated Sparse-Recovery Metrics

**Files:**
- Modify: `src/ulm_ml/symmetry_sparse.py`
- Modify: `tests/test_symmetry_sparse.py`
- Modify: `docs/symmetry-augmented-sparse-recovery.md`

- [ ] **Step 1: Add a strict one-to-one recovery metric**

Implement `unique_feature_recovery(learned_atoms, true_atoms, threshold=0.90)` using `scipy.optimize.linear_sum_assignment` on negative cosine similarity. Return mean assigned cosine and fraction of true atoms above threshold.

- [ ] **Step 2: Test duplicate-atom inflation**

Add a test where two learned atoms both match one true atom and another true atom is unmatched. `feature_recovery()` may score high, but `unique_feature_recovery()` must penalize the missing atom.

- [ ] **Step 3: Update experiment and report**

Have `experiments/symmetry_augmented_sparse_recovery.py` write both loose and unique recovery metrics. Rewrite the report to treat the unique metric as the headline and the loose metric as a diagnostic.

Run:

```bash
.venv/bin/pytest tests/test_symmetry_sparse.py
PYTHONPATH=src .venv/bin/python experiments/symmetry_augmented_sparse_recovery.py --output artifacts/symmetry_sparse_summary.csv
```

## Task 3: Strengthen Modular Grokking Diagnostics

**Files:**
- Modify: `src/ulm_ml/modular_arithmetic.py`
- Modify: `src/ulm_ml/modular_spectral.py`
- Modify: `experiments/modular_character_timescales.py`
- Modify: `experiments/modular_spectral_probe.py`
- Modify: `docs/research-brief-character-timescales.md`
- Modify: `docs/modular-spectral-probe.md`

- [ ] **Step 1: Make the oracle boundary explicit**

Add docstrings and report language that distinguish explicit character interaction features from the `addition_fourier_features()` oracle over the latent sum coordinate.

- [ ] **Step 2: Add latent coverage card output**

Add a small `coverage_card()` formatter in `modular_spectral.py` that reports train fraction, missing latent sums, sum-count CV, Fourier design condition, and ridge oracle accuracy for each split family.

- [ ] **Step 3: Cross-link #5 and #7**

Update both modular docs to say #5 is a representation baseline and #7 is a split/data-geometry oracle. The final synthesis should recommend using them together before neural grokking sweeps.

Run:

```bash
.venv/bin/pytest tests/test_modular_arithmetic.py tests/test_modular_spectral.py
PYTHONPATH=src .venv/bin/python experiments/modular_character_timescales.py --moduli 31 --train-fractions 0.10 --seeds 0 1 --output artifacts/modular_character_smoke.csv
PYTHONPATH=src .venv/bin/python experiments/modular_spectral_probe.py --modulus 31 --fractions 0.03 0.10 --seeds 0 1
```

## Task 4: Repair TTA Baselines

**Files:**
- Modify: `src/ulm_ml/egpr.py`
- Modify: `experiments/egpr_digits_tta.py`
- Modify: `docs/egpr-brief.md`
- Modify: `docs/pace-bias-tta-report.md`
- Modify: `tests/test_egpr.py`

- [ ] **Step 1: Add a true no-adaptation prototype baseline**

Measure `source_plus_prototype_no_adapt` by using initialized source prototypes with no target updates. This isolates prototype interpolation from online adaptation.

- [ ] **Step 2: Add a true all-replay baseline**

Bypass entropy gating for `all_replay` so every target example above no confidence floor can update prototypes. Do not call it naive replay if it still has hidden gates.

- [ ] **Step 3: Run multi-seed EGPR and rewrite the claim**

Report mean/std across at least five seeds. If EGPR hurts, say so and pivot the thread to no-label adaptation safety diagnostics.

Run:

```bash
.venv/bin/pytest tests/test_egpr.py tests/test_tta.py
PYTHONPATH=src .venv/bin/python experiments/egpr_digits_tta.py --seeds 0 1 2 3 4 --output artifacts/egpr_digits_tta.csv
PYTHONPATH=src .venv/bin/python experiments/pace_bias_tta.py --seeds 0 1 2 --out-dir artifacts/pace_bias_tta_smoke
```

## Task 5: Improve Fast-Weight Memory Baselines

**Files:**
- Modify: `src/ulm_ml/sequence_memory/models.py`
- Modify: `experiments/sequence_memory/associative_recall_fast_weights.py`
- Modify: `docs/sequence-memory-fast-weights.md`
- Modify: `tests/sequence_memory/test_associative_recall.py`

- [ ] **Step 1: Add a scalar-write fast-weight baseline**

Add `ScalarFastWeightsMemory` with a fixed global write scale. This tests whether the learned gate does anything beyond shrinking writes.

- [ ] **Step 2: Add dimension-scaling sweep support**

Allow the experiment to sweep `key_dim` and report recall against `pairs / key_dim`.

- [ ] **Step 3: Rewrite conclusions**

State whether learned gating beats scalar writes at equal dimension; if not, the useful result is that interference dominates simple gating.

Run:

```bash
.venv/bin/pytest tests/sequence_memory/test_associative_recall.py
PYTHONPATH=src .venv/bin/python experiments/sequence_memory/associative_recall_fast_weights.py --epochs 4 --train-size 1024 --test-size 512
```

## Task 6: Make Synthetic-Only Threads Honest and Actionable

**Files:**
- Modify: `src/ulm_ml/adaptive_consistency.py`
- Modify: `docs/adaptive-posterior-self-consistency.md`
- Modify: `docs/phase-state-tracking.md`
- Modify: `docs/research-synthesis.md`

- [ ] **Step 1: Adaptive consistency replay API**

Add a simple CSV/JSON trace replay loader or document the exact schema needed: prompt id, sample index, normalized answer, correctness, token count.

- [ ] **Step 2: Phase tracking reframing**

Rewrite the phase-state report so the current root-of-unity result is clearly a constructive oracle/probe, and the next real experiment is a learnable rotation sidecar with resets.

- [ ] **Step 3: Cross-thread synthesis**

Write `docs/research-synthesis.md` with ranked threads, what evidence exists, what is weak, and the next two compute-light experiments most worth running in Codex cloud.

Run:

```bash
.venv/bin/pytest tests/test_adaptive_consistency.py tests/test_state_tracking.py
PYTHONPATH=src .venv/bin/python experiments/adaptive_consistency_synthetic.py
PYTHONPATH=src .venv/bin/python experiments/phase_state_tracking.py
```

## Task 7: Verify and Publish

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `docs/research-log.md`

- [ ] **Step 1: Final local gates**

Run:

```bash
.venv/bin/ruff check .
.venv/bin/pytest
git status --short
```

- [ ] **Step 2: Commit and push**

Run:

```bash
git add .
git commit -m "Deepen ULM ML research synthesis"
git push -u origin research/deep-research-synthesis
```

- [ ] **Step 3: Open a synthesis PR**

Run:

```bash
gh pr create --repo trevor050/ulm-ml --base main --head research/deep-research-synthesis --title "Deepen ULM ML research synthesis" --body-file docs/research-synthesis.md
```
