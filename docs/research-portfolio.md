# Research Portfolio Verdicts

Date: 2026-06-01

Rule: every thread is either `full_research` or `given_up`. No "promising
scaffold" bucket is allowed.

## Binary Verdict Table

| status | project | doc | verdict |
| --- | --- | --- | --- |
| full_research | Cyclic representation probes | docs/full-research/cyclic-representation-probes.md | Keep. Modular spectral, character, and phase probes become one track about cyclic representations and split coverage. |
| full_research | Symmetry-augmented sparse recovery | docs/full-research/symmetry-sparse-recovery.md | Keep. Correct cyclic augmentation beats baseline under strict matching, while false shuffled augmentation fails. |
| full_research | Sequence-memory interference | docs/full-research/sequence-memory-interference.md | Keep. Compact fast weights are useful as a negative benchmark for memory interference under load. |
| given_up | Adaptive posterior self-consistency | docs/given-up/adaptive-self-consistency.md | Give up as active research until real cached answer traces exist. |
| given_up | EGPR prototype replay | docs/given-up/egpr-prototype-replay.md | Give up as an adaptation method; current online prototype updates mostly hurt. |
| given_up | PACE bias-only TTA | docs/given-up/pace-bias-tta.md | Give up as a standalone project; keep only as a narrow prior-drift diagnostic baseline. |

## What "Full Research" Means Here

A surviving project must have:

- A falsifiable research question.
- A reproducible CPU-scale command.
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

`src/ulm_ml/research_portfolio.py` is the compact machine-readable portfolio.
`tests/test_research_portfolio.py` makes the binary status explicit so a future
agent cannot quietly re-add vague zombie projects.

