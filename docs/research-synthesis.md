# Research Synthesis

Date: 2026-06-01

This repo is a staging ground for cheap ML research probes. The common rule for
reading the results: oracle controls and synthetic fixtures are allowed, but they
must stay labeled as such. A good thread either survives a real trace/toy-data
replay or clearly becomes a negative control that saves future GPU time.

## Ranking

| rank | thread | evidence level | current verdict | next compute-light experiment |
| ---: | --- | --- | --- | --- |
| 1 | Modular arithmetic spectral diagnostics | Strong oracle/control | The Fourier character family and latent-sum coverage diagnostics are the cleanest current tools. They do not prove neural grokking, but they sharply separate data coverage from representation discovery. | Train one tiny MLP/transformer across random, sum-balanced, and operand-block splits, logging Fourier readout coverage at checkpoints. |
| 2 | Symmetry-augmented sparse recovery | Controlled synthetic recovery | Cyclic augmentation improves strict one-to-one feature recovery in the toy dictionary setting. This is promising because the metric now resists duplicate learned atoms. | Move from synthetic coordinate shifts to a controlled activation space with a known or estimated group action. |
| 3 | Sequence-memory fast weights | Useful negative toy benchmark | Compact outer-product memories degrade with length; learned gating helps but does not close the gap to explicit key storage. | Sweep key dimension and report recall against `pairs / key_dim`, including scalar write-scale and learned-gate baselines. |
| 4 | Phase-state tracking | Constructive oracle/probe | Root-of-unity channels solve modular counting exactly when the transition is handed to the model. This is a boundary condition, not evidence of learnability. | Train small recurrent transition families to see when rotations are discovered rather than supplied. |
| 5 | Adaptive posterior self-consistency | Synthetic policy sanity check | The posterior stopping rule behaves plausibly on simulated answer streams, but there is no real LLM trace replay yet. | Collect answer-only traces from one small reasoning model and replay policies from the CSV schema. |
| 6 | TTA prototype replay / EGPR | Mostly negative toy dataset result | Freezing the source classifier and gating prototype updates is auditable, but current digits shifts are seed- and corruption-sensitive. The better thread is adaptation-safety prediction. | Run multi-seed sweeps with true no-adapt and all-replay baselines, then predict when adaptation should be disabled. |
| 7 | PACE bias-only TTA | Narrow positive/negative split | Bias-only adaptation helps some prior-shift cases and fails on feature corruption, which is exactly the limitation it should expose. | Treat it as a diagnostic baseline for label-prior drift before trying richer adaptation. |

## Cross-thread lessons

- **Oracle features are useful when named honestly.** The modular Fourier and
  phase-channel probes tell us what a good representation can do, not whether a
  neural model will learn it.
- **Strict metrics matter.** Sparse recovery looked stronger under loose
  best-match scoring; one-to-one assignment is the metric that should headline
  future claims.
- **Negative results are not dead ends.** EGPR and compact fast weights are most
  useful when they expose failure surfaces: unsafe adaptation and memory
  interference.
- **Replay beats re-generation.** Adaptive self-consistency should move to
  cached answer traces before any new policy tuning. TTA experiments should also
  compare methods on identical streams and seeds.

## Evidence ladder

| level | meaning | threads currently here |
| --- | --- | --- |
| Real replay | Same cached real-model traces or real dataset stream, policies compared on identical prefixes/seeds | None yet |
| Controlled toy data | Synthetic or sklearn-scale data with ground truth and meaningful metrics | Symmetry sparse recovery, EGPR/PACE, sequence memory |
| Oracle/control | Handed the representation or transition believed to solve the task | Modular spectral/character, phase-state |
| Simulator sanity check | Synthetic distributions used only to debug policy mechanics | Adaptive posterior self-consistency |

## Caveats

- None of these results should be described as benchmark wins.
- Most experiments are CPU-scale and intentionally small, so effect sizes are
  only useful if they survive stronger baselines and multiple seeds.
- Several docs cite current research for orientation, but the repo evidence is
  local: scripts, tests, and generated summaries. External citations should not
  carry more weight than the actual reproduced runs.
- The highest-risk pattern is confusing an oracle boundary with a learned model
  result. Keep that distinction in abstracts, tables, and summaries.

## Immediate next batch

1. Add real answer-trace replay for adaptive self-consistency using
   `load_answer_trace_csv`.
2. Run the modular spectral coverage card alongside one neural modular-addition
   training sweep.
3. Finish the fast-weight key-dimension sweep and scalar-write baseline.
4. Re-run sparse recovery with strict unique assignment as the headline metric.
5. Convert EGPR from "does adaptation improve accuracy?" to "can diagnostics
   predict when adaptation will hurt?"
