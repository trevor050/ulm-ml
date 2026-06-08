# Research Portfolio Verdicts

Date: 2026-06-01

Rule: every thread is either `full_research` or `given_up`. No "promising
scaffold" bucket is allowed.

## Binary Verdict Table

| status | project | folder | verdict |
| --- | --- | --- | --- |
| full_research | Cyclic representation probes | experiments/cyclic-representation-probes/ | Keep. Modular spectral, character, and phase probes become one track about cyclic representations and split coverage. |
| full_research | Symmetry-augmented sparse recovery | experiments/symmetry-sparse-recovery/ | Keep. Correct cyclic augmentation beats baseline under strict matching, while false shuffled augmentation fails. |
| full_research | Sequence-memory interference | experiments/sequence-memory-interference/ | Keep. Compact fast weights are useful as a negative benchmark for memory interference under load. |
| full_research | Doubt-TTS / reliability-action routing | experiments/doubt-tts/ | Keep. Generic doubt prompting failed the neutral-control bar, but route/action/source/verifier decomposition has runnable probes and sharp negative controls. |
| full_research | Consensus-Stability Switching | experiments/consensus-stability-switching/ | Keep. Hard math traces show a robust answer-cluster selectability gap, and pairwise baseline-vs-candidate adjudication is the first measured local-verifier route with held-out natural-rate gain and regression accounting. |
| given_up | Adaptive posterior self-consistency | experiments/adaptive-self-consistency/ | Give up as active research until real cached answer traces exist. |
| given_up | EGPR prototype replay | experiments/egpr-prototype-replay/ | Give up as an adaptation method; current online prototype updates mostly hurt. |
| given_up | PACE bias-only TTA | experiments/pace-bias-tta/ | Give up as a standalone project; keep only as a narrow prior-drift diagnostic baseline. |

## What "Full Research" Means Here

A surviving project must have:

- A falsifiable research question.
- A reproducible command.
- At least one honest baseline or negative control.
- A primary metric that cannot be trivially gamed by the method.
- A written failure condition that tells the next agent when to stop.

## Source Refresh

- Modular arithmetic work is anchored against the modular-grokking literature:
  [Gromov 2023](https://arxiv.org/abs/2301.02679),
  [He et al. 2026](https://arxiv.org/abs/2602.16849), and
  [Swaroop 2026](https://arxiv.org/abs/2603.23784).
- Sequence-memory work is framed against modern long-context memory mechanisms:
  [Titans](https://arxiv.org/abs/2501.00663) and
  [Gated Delta Networks](https://arxiv.org/abs/2412.06464).
- Sparse-recovery work is only a local toy analogue of dictionary-learning and
  SAE feature-recovery questions. It is not a claim about LLM activations yet.

## Enforcement

`README.md` is the public experiment list. `src/ulm_ml/research_portfolio.py`
is the compact machine-readable portfolio.
`tests/test_research_portfolio.py` makes the binary status explicit so a future
agent cannot quietly re-add vague zombie projects.
