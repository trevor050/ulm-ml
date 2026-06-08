# v40 - Current Literature Pressure Test

**Status:** June 1, 2026 literature-pressure update. This is a claim-hardening note, not a new experiment.

## Why This Exists

The adaptive cluster-depth pitch has to survive the live test-time-scaling literature. The strongest reviewer objection is not "your table is wrong." It is:

> Why is this not just dynamic self-consistency, discriminative verification, generative verification, or multi-agent verifier search with extra bookkeeping?

The answer needs to be narrow and falsifiable.

## Current External Pressure

### Dynamic self-consistency is getting stronger

- Seer Self-Consistency proposes estimating budget need in advance using a fast System-1 entropy signal, then allocating System-2 self-consistency more efficiently: <https://arxiv.org/abs/2511.09345>.
- Optimal Self-Consistency studies self-consistency as mode estimation/voting, derives scaling behavior, and proposes Blend-ASC for sample-efficient allocation: <https://arxiv.org/abs/2511.12309>.

Pressure on us: a paper cannot merely say "adaptive budget good." It must show that the deployed bottleneck is not just insufficient dynamic sampling. v36 helps because N=128 to N=1024 mostly increases hidden any-correct coverage while barely moving `cluster_sum`, but a reviewer can still ask for a stronger dynamic-SC baseline.

Required defense:

- report `cluster_sum` as the deployed selector after additional samples,
- compare adaptive-depth verification against dynamic extra-sample policies at matched token budget,
- separate "creates correct answer" from "selects correct answer."

### Verification budget is contested

- When To Solve, When To Verify argues that, under many practical budgets, scaling solution generation can be more compute-efficient than generative verification and that GenRM may need much more compute to match self-consistency: <https://arxiv.org/abs/2504.01005>.
- Budget-aware Test-time Scaling via Discriminative Verification argues the opposite direction for a cheaper verifier regime: discriminative verification plus self-consistency can be a practical budget-aware hybrid and can outperform costly generative verification under fixed budget: <https://arxiv.org/abs/2510.14913>.

Pressure on us: "verification helps" is not a stable general claim. The paper must price verification and generation under the same accounting and avoid claiming that deeper cluster verification is universally better.

Required defense:

- keep v36 as the generation-only objection check,
- keep v30/v31/v32 as budget-frontier rather than fixed-depth booster claims,
- use v39 deployed-delta rows rather than raw hard-packet accuracy,
- report compact/full prompt token cost and fallback rate.

### Verifier behavior is problem- and generator-dependent

- Variation in Verification studies generative verifier dynamics across problem difficulty, generator strength, verifier strength, and 12 benchmarks; its core warning is that verifier effectiveness changes substantially with these axes: <https://arxiv.org/abs/2509.17995>.

Pressure on us: Llama/Gemma trace results are not enough to imply a universal cluster-depth law. The paper needs to frame itself as a measurement and allocation method, not a general theorem that every verifier can recover buried clusters.

Required defense:

- report by generator/model, not just aggregate,
- keep Gemma negative/flat detector results visible,
- include the no-visible/no-correct deployed-mix categories,
- make answer-label visibility audit part of the evaluation checklist.

### Multi-agent / structured test-time scaling will claim the high ground

- TMAS scales test-time compute through coordinated multi-agent trajectories, refinement, verification feedback, and memory-like reuse: <https://arxiv.org/abs/2605.10344>.

Pressure on us: multi-agent systems can inspect more trajectories and evidence, so "look deeper" is not novel by itself.

Required defense:

- define the unit of allocation as answer-cluster depth, not agent count or refinement rounds,
- make the method compatible with multi-agent verifiers by asking which clusters the agents inspect,
- preserve the diagnostic contribution even if a stronger multi-agent verifier becomes the downstream judge.

## Strongest Narrow Claim After This Pressure

The paper should not claim:

```text
Adaptive verification beats self-consistency.
```

It should claim:

```text
Repeated sampling creates a measurable cluster selectability gap: correct answer clusters often exist but are not selected. On the tested MATH traces, generating many more samples mostly increases hidden coverage, while realized selector accuracy barely moves. A budgeted adaptive-depth policy is a falsifiable way to spend verifier compute on the answer-cluster frontier, and deployed value must be scored with recovery, regression, confidence fallback, and natural-rate weighting.
```

That claim survives the current literature better because it is about measurement and allocation over answer clusters.

## Reviewer-Grade Baselines To Add Next

1. Dynamic self-consistency baseline:
   - allocate additional samples by entropy/cluster margin,
   - compare against fixed N=256/512/1024,
   - report final `cluster_sum`, not just any-correct.

2. Discriminative verification baseline:
   - train or simulate a per-candidate verifier score,
   - aggregate by answer cluster,
   - compare candidate-level best-of-N vs cluster-level depth inspection.

3. Generative verification accounting:
   - use the same prompt-token accounting as v36/v39,
   - ask whether verifier chains should score candidates or answer clusters,
   - report when extra solution generation beats verification.

4. Multi-verifier compatibility:
   - treat each verifier as producing a cluster preference,
   - measure whether diversity helps shallow top-5 or mostly helps buried top-10/top-20.

5. Deployed-mix policy result:
   - run v37 prompts,
   - score with v39,
   - replace v38 sensitivity thresholds with measured `deployed_delta`.

## Practical Next Move

If compute remains limited, the highest-value cheap addition is a dynamic-self-consistency proxy over the existing traces: use early N=32/64/128 cluster entropy or margin to decide where to spend extra samples up to N=256/512/1024, then compare realized `cluster_sum` improvement per token against the rank-bucket verifier projections.

This does not require a model endpoint because the samples already exist in the Monkey Business traces.
