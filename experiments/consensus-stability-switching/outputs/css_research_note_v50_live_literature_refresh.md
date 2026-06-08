# v50 - Live Literature Refresh

## Why this exists

v40 positioned the project against recent test-time scaling work. This refresh checks the claim against live primary sources again on June 1, 2026.

## Current pressure map

| thread | primary sources | pressure on this project | response |
|---|---|---|---|
| Verification matters | [Scaling Test-Time Compute Without Verification or RL is Suboptimal](https://arxiv.org/abs/2502.12118) | Supports the premise that verification is not optional when reasoning traces are heterogeneous. | Good for motivation, but our work still needs measured verifier results. |
| Solve-vs-verify budget tradeoff | [When To Solve, When To Verify](https://arxiv.org/abs/2504.01005) | Warns that generative verification can be compute-inefficient versus more solution sampling at practical budgets. | Our v36-v44 token-matched generation baselines directly answer this pressure locally, but only under projected verifier success. |
| Cheap discriminative verification | [Budget-aware Test-time Scaling via Discriminative Verification](https://arxiv.org/abs/2510.14913) | Makes budget-aware discriminative verification a stronger competing baseline. | Our method should be pitched as depth allocation over answer clusters, not as generic verifier superiority. |
| Verifier failure under search | [Scaling Flaws of Verifier-Guided Search](https://arxiv.org/abs/2502.00271) | Imperfect verifiers can misrank or prune valid paths as sample count grows. | v45-v48 are exactly the right guardrail: regression-aware deployed mix, CI gate, power, and representativeness. |
| Multiple verifiers | [Multi-Agent Verification](https://arxiv.org/abs/2502.20379) | Scaling the number/aspects of verifiers is a competing axis. | Cluster-depth allocation is orthogonal; future run could use MAV as the verifier module. |
| Dynamic self-consistency | [Efficient Test-Time Scaling via Self-Calibration](https://arxiv.org/abs/2503.00031), [Seer Self-Consistency](https://arxiv.org/abs/2511.09345), [Optimal Self-Consistency](https://arxiv.org/abs/2511.12309) | Adaptive sampling and budget estimation make "just sample smarter" a much stronger objection. | v41-v44 are now essential, not optional: dynamic, token-matched, fine-grained, seed-swept generation baselines. |
| Simple early-stop TTS | [First Finish Search](https://arxiv.org/abs/2505.18149) | Very simple inference-time heuristics can be surprisingly strong. | Add a future baseline: shortest/early-finish selection on traces, if trace completion length is available or recoverable. |
| Judge training and distribution shift | [DAJ](https://arxiv.org/abs/2601.22230) | 2026 work emphasizes that LLM judges fail under task/trajectory distribution shift. | Strongly supports the deployed-mix and unique-source verifier asset work; our benchmark should report judge transfer/trajectory alignment. |
| Architecture-specific self-verification | [Prism](https://arxiv.org/abs/2602.01842) | TTS is becoming architecture-specific, with self-verification inside non-autoregressive decoding. | Our contribution should stay representation-agnostic: answer-cluster depth as an evaluation object, not a claim about one decoding family. |
| Agentic TTS | [Scaling Test-time Compute for LLM Agents](https://arxiv.org/abs/2506.12928), [AgentTTS](https://arxiv.org/abs/2508.00890) | Multi-stage tasks allocate compute across subtasks and rollouts, not only answer candidates. | This is adjacent, not central. The novelty remains single-problem answer-cluster depth under repeated sampling. |

## Updated novelty claim

The safest novelty claim is:

> Recent test-time scaling work allocates samples, verifier calls, verifier types, or search budget. This project measures and allocates over answer-cluster depth: how far down the cluster frontier a verifier must inspect before a generated correct answer becomes selectable.

The claim should not be:

> Verification beats sampling.

That is too broad and directly contradicted by solve-vs-verify budget work at some budgets.

## New experimental obligations

The live literature refresh adds three concrete obligations:

1. Treat dynamic self-consistency as the serious generation-only baseline. v41-v44 already do this on available traces, but the paper must foreground those results.
2. Treat verifier reliability as the central missing measurement. v45-v48 now define the deployed-mix decision protocol; the real verifier run remains decisive.
3. Add an early-finish/short-trace baseline if trace lengths are present. First Finish Search makes this too obvious to ignore.

## Current state after refresh

The package is better positioned than v40 because it now has:

- token-matched dynamic generation baselines,
- seed-swept fine-grained dynamic generation,
- regression-aware deployed-mix assets,
- confidence-threshold policy scoring,
- a bootstrap decision gate,
- a power plan,
- representativeness and unique-source prompt assets,
- a script-generated canonical number table.

The remaining missing benchmark has not changed: a real external/local verifier must be run.
