# ULM ML

Repo of machine-learning research experiments. Each experiment has its own
folder, short verdict, runnable scripts, and notes.

## Experiments

| experiment | question | verdict | answer so far | interesting bit | open |
| --- | --- | --- | --- | --- | --- |
| Cyclic representation probes | Can modular arithmetic generalization be explained through cyclic representations and split coverage? | Yes, keep going. | Fourier/spectral probes expose when a split covers the latent sum coordinate; learned MLP sanity checks still memorize train splits and fail held-out addition. | Strong oracle-vs-learned gap, useful for deciding what a model actually discovered. | `experiments/cyclic-representation-probes/` |
| Symmetry-augmented sparse recovery | Does the right cyclic symmetry help recover sparse features under a stricter one-to-one metric? | Yes, keep going. | Correct cyclic augmentation improves strict recovery; a shuffled false-symmetry control fails. | The strict metric matters, loose best-match recovery was too flattering. | `experiments/symmetry-sparse-recovery/` |
| Sequence-memory interference | Where do compact fast-weight memory rules break under associative-recall load? | Yes, keep going. | Fast-weight, delta, gated, and orthogonalized memories show visible load/interference curves against retrieval baselines. | Useful as a failure benchmark, not just a toy success demo. | `experiments/sequence-memory-interference/` |
| Doubt-TTS / reliability-action routing | Can selective-compute QA route uncertainty into the right action instead of generic self-doubt? | Yes, keep going. | Generic doubt prompts failed the neutral-control bar; route/action/source/verifier decomposition has runnable probes and sharp negative controls. | The negative controls are the point: directed challenge wording is weak, controller decomposition is measurable. | `experiments/doubt-tts/` |
| Adaptive posterior self-consistency | Can posterior stopping beat fixed self-consistency without real answer traces? | No, parked. | Synthetic traces are only replay infrastructure; the idea needs cached real-model answer traces before it is research again. | Resurrection gate is concrete: real traces plus a win over fixed and oracle-ish baselines. | `experiments/adaptive-self-consistency/` |
| EGPR prototype replay | Can entropy-gated prototype replay improve test-time adaptation without labels? | No, parked. | True no-adapt baselines beat or match online prototype replay on the shifted-digits suite. | The failure may still be useful for adaptation-risk prediction. | `experiments/egpr-prototype-replay/` |
| PACE bias-only TTA | Is bias-only adaptation enough for a standalone TTA project? | No, parked. | It is only useful as a narrow label-prior-drift diagnostic, not as an independent method. | Good negative control for separating prior drift from feature corruption. | `experiments/pace-bias-tta/` |

## Layout

```text
experiments/       one folder per research experiment
src/ulm_ml/        shared reusable code used by experiments
docs/              longer research notes, synthesis, and parked-project gates
tests/             regression tests for shared code and portfolio rules
artifacts/         generated outputs, ignored by git
data/              local datasets, ignored by git
models/            local checkpoints/weights, ignored by git
```

## Run

```bash
bash scripts/bootstrap.sh
source .venv/bin/activate
pytest
```

Each experiment folder has its own README with representative commands.

## Add An Experiment

Create a new folder under `experiments/`, add a short README, keep reusable
logic in `src/ulm_ml/`, and update this table with:

- question
- verdict
- answer so far
- interesting bit
- folder link
