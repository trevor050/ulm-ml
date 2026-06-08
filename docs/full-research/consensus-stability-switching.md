# Consensus-Stability Switching

Status: `full_research`

## Claim

Repeated sampling on hard math often produces a correct answer that current answer-cluster selectors fail to identify. The surviving research direction is not naive self-consistency or full-cluster local judging; it is regression-aware answer-cluster routing, especially pairwise baseline-vs-candidate adjudication.

## Research Question

When a repeated-sampling trace contains multiple answer clusters, can a calibrated selector or pairwise judge recover buried correct candidates while preserving baseline-correct cases?

## Current Evidence

Imported project folder:

`experiments/consensus-stability-switching/`

Start with:

- `experiments/consensus-stability-switching/outputs/result_ledger.md`
- `experiments/consensus-stability-switching/outputs/reproducibility_manifest.md`
- `experiments/consensus-stability-switching/outputs/css_research_note_v122_pairwise_natural_rate.md`
- `experiments/consensus-stability-switching/outputs/css_research_note_v130_pairwise_rich_prompt_probe.md`

Current strongest measured path:

- Pairwise router-judge calibration transfers on Gemma-with-Llama accepted actions.
- Natural-rate pairwise gating reaches `+0.067` over `1776` held-out Gemma trials while reducing raw-router regressions from `20` to `1`.
- Mirror-direction Llama-with-Gemma control no-ops instead of fabricating a win.
- Leave-one-problem-out stress stays positive across `222/222` held-out `(seed,pid)` groups for the conservative pairwise result.
- Higher-budget pairwise variants improve recovery but expose qwen/union regression tails; v128-v130 document the guard frontier and prompt-stress boundary.

## Baselines And Controls

- `cluster_sum`: strongest fixed answer-cluster baseline.
- Oracle/top-k cluster visibility: measures headroom without claiming deployability.
- Learned cluster rankers and cheap selector features: mostly negative.
- Dynamic extra sampling and token-matched generation baselines: mostly fail to move realized selection in the hard MATH regime.
- Full-cluster local verifier prompts with qwen/gemma/mathstral: mostly negative or structurally brittle.
- Pairwise mirror direction: negative control showing the current positive does not automatically appear in the reverse target/auxiliary setup.

## Failure Conditions

Give up on this track as a deployable method if pairwise adjudication cannot survive broader held-out traces, stricter problem-disjoint calibration, or a larger auxiliary direction without restoring the raw-router regression tail.

Do not claim a solved verifier from projected depth/oracle rows, target-oracle calibration, or targeted hard-packet panels. The claim must stay tied to held-out natural-rate accounting and regression budgets.

## Next Full Experiment

Run the qwen `type_check` variant over all v125 accepted actions, then test whether v128-style cross-judge confirmation transfers to another target/auxiliary direction or larger trace. If a stronger endpoint becomes available, prioritize pairwise router adjudication before another full-cluster prompt variant.

