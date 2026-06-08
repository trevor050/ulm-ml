# Research Synthesis

Date: 2026-06-01

This repo now follows a hard portfolio rule: every thread is either
`full_research` or `given_up`. The current source of truth is
`docs/research-portfolio.md`, with a machine-readable mirror in
`src/ulm_ml/research_portfolio.py`.

## Full Research Tracks

| rank | track | evidence level | current verdict | next compute-light experiment |
| ---: | --- | --- | --- | --- |
| 1 | Cyclic representation probes | Strong oracle/control plus learned memorization sanity check | Keep. Modular spectral, modular character, phase-state, and MLP split probes form one coherent track about cyclic representations, data geometry, and learned discovery. | Turn the MLP probe into a checkpointed dynamics sweep with Fourier alignment logs. |
| 2 | Symmetry-augmented sparse recovery | Controlled synthetic recovery with false-symmetry control | Keep. Correct cyclic augmentation improves strict one-to-one recovery; shuffled augmentation shows that the win is not just row multiplication. | Move from handmade nonnegative dictionaries to controlled activation-like data with a known or estimated group action. |
| 3 | Sequence-memory interference | Useful negative toy benchmark | Keep. Compact memories degrade predictably with `pairs/key_dim`; nearest-neighbor retrieval remains the ceiling, which is the point. | Add a constrained-retrieval setting where the lookup baseline has an explicit memory budget. |
| 4 | Doubt-TTS / reliability-action routing | Strong negative controls plus small route/source/verifier probes | Keep. Generic doubt prompts are not the method; the live research object is selective QA as validity, action, source, verifier, and response-policy control. | Run the cue-balanced reliability-action controller against deterministic and text-only baselines under family-held-out and human-paraphrase splits. |

## Given Up As Active Research

| thread | verdict | reason |
| --- | --- | --- |
| Adaptive posterior self-consistency | Given up until real traces exist | Synthetic streams and replay code are infrastructure, not evidence about real chain-of-thought sample streams. |
| EGPR prototype replay | Given up as an adaptation method | True no-adapt prototype baselines beat or match online prototype updates on the shifted-digits suite. |
| PACE bias-only TTA | Given up as standalone research | Bias-only adaptation is a narrow prior-drift diagnostic, not enough for an independent research project. |

## Cross-Thread Lessons

- **Oracle controls must be fenced.** Modular Fourier and phase-channel probes
  are useful because they mark representation boundaries. They do not prove a
  learned model discovers those representations.
- **Strict metrics are non-negotiable.** Sparse recovery uses one-to-one
  assignment as the headline metric. Loose best-match scores remain diagnostic.
- **Negative results can graduate.** Sequence memory survives because the
  interference curve is the object of study. EGPR does not survive because the
  method itself loses to the no-adapt baseline.
- **Infrastructure is not research.** Adaptive self-consistency has useful
  replay tooling, but no real-model trace evidence. It is parked until data
  exists.
- **Prompt wording is not a mechanism.** Doubt-TTS only survives because the
  neutral controls demoted "doubt prompting" and exposed route/action/source
  selection as the measurable object.

## Evidence Ladder

| level | meaning | tracks currently here |
| --- | --- | --- |
| Real replay | Same cached real-model traces or real dataset stream, policies compared on identical prefixes/seeds | None |
| Controlled toy data with negative controls | Synthetic or sklearn-scale data with ground truth, meaningful metrics, and a false-positive control | Symmetry sparse recovery, sequence-memory interference |
| Oracle/control | Handed the representation or transition believed to solve the task | Cyclic representation probes |
| Simulator/infrastructure | Synthetic distributions used only to debug mechanics | Adaptive posterior self-consistency, given up as active research |

## Immediate Next Batch

1. Cyclic: checkpoint the tiny learned-model split sweep and compare hidden
   character readouts to coverage cards.
2. Sparse: build an activation-like bridge fixture and rerun baseline, cyclic,
   and shuffled augmentation with strict matching.
3. Sequence: add a retrieval-memory-budget baseline so compact memories are not
   compared only against unlimited lookup.
