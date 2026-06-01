# Research Log

Use this as the compact source of truth for experiments that matter.

## 2026-06-01

- Initialized the repository as a Codex-friendly ML research staging ground.
- Started a CPU-only grokking diagnostic project around modular-arithmetic character interactions.
  The first result is documented in `docs/research-brief-character-timescales.md`: full Fourier
  interaction features solve held-out modular-addition pairs from 10% of the table for p=31 and
  p=43, while pair one-hot memorization stays at chance. No external datasets or committed
  artifacts were added.
- Added a CPU-only modular spectral split probe. Initial p=31 sweep shows sum-balanced latent residue coverage gives 1.000 Fourier-probe test accuracy at 3% train fraction, while random splits average 0.633 and operand-block splits 0.300; see `docs/modular-spectral-probe.md`.
- Added a lightweight symmetry-augmented sparse feature recovery study. The
  result: cyclic group augmentation improves known-feature recovery in a
  controlled sparse dictionary benchmark, especially with only 40 observations
  (0.481 -> 0.736 of true atoms recovered at cosine >= 0.90). See
  `docs/symmetry-augmented-sparse-recovery.md` and
  `experiments/symmetry_augmented_sparse_recovery.py`.
- Started the adaptive posterior self-consistency thread: a Dirichlet posterior early-stopping rule for answer-only self-consistency traces. Initial synthetic replay (`reports/adaptive-consistency.md`) matched fixed-32 accuracy with about half the samples; next step is replay on cached GSM8K/SVAMP traces from a small reasoning model.
- Added a CPU-only TTA seed project: Prior-Anchored Conservative Entropy (PACE) for bias-only adaptation. Initial five-seed digits experiments suggest small gains for logit prior drift (balanced stream: source 0.892 accuracy, PACE 0.909) and a useful negative result for image corruption, where bias-only adaptation does not repair feature damage. See `docs/pace-bias-tta-report.md` and `experiments/pace_bias_tta.py`.
- Added a CPU-only associative-recall probe for compact sequence memories. Initial
  run shows explicit nearest-neighbor retrieval stays near 0.982 cosine through
  64 pairs, while compact fast-weight variants degrade with length; a learned
  gate improves the 64-pair result over a residual delta rule (0.564 vs. 0.420)
  but does not solve interference. See `docs/sequence-memory-fast-weights.md`.
- Started EGPR (Entropy-Gated Prototype Replay), a low-compute test-time adaptation probe that freezes the source classifier and adapts class prototypes only from low-entropy/high-confidence target examples. Initial digits-corruption run: helps localized occlusion slightly (0.951 source-only vs 0.954 EGPR) but hurts brightness, mixed, and noisy shifts, suggesting the next research target should be adaptation-safety prediction rather than raw accuracy chasing. See `docs/egpr-brief.md` and `experiments/egpr_digits_tta.py`.
- Added a lightweight phase-state tracking probe. The working hypothesis is that tiny root-of-unity recurrence channels can give linear-time sequence models an exact finite-state reserve for parity/modular counters, complementing Mamba-style selective SSMs and DeltaNet-style associative memory. See `docs/phase-state-tracking.md` and `experiments/phase_state_tracking.py`.
- Deepened the merged research branch: sparse recovery now headlines strict one-to-one assignment, EGPR has true no-adapt and all-replay baselines with five-seed negative results, sequence memory includes scalar fast weights and key-dimension sweeps, modular spectral probes print coverage cards, and `docs/research-synthesis.md` ranks the threads by evidence level.
