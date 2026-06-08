# v60 Literature Boundary Addendum

**Date:** June 1, 2026  
**Question:** After v58/v59, how should the claim be positioned against recent test-time scaling, verifier, and judge-shift work?

## Sources Checked

- [First Finish Search: Efficient Test-Time Scaling in Large Language Models](https://arxiv.org/abs/2505.18149), submitted May 23, 2025.
- [Putting the Value Back in RL: Better Test-Time Scaling by Unifying LLM Reasoners With Verifiers](https://arxiv.org/abs/2505.04842), submitted May 7, 2025, revised Apr 12, 2026.
- [Budget-aware Test-time Scaling via Discriminative Verification](https://arxiv.org/abs/2510.14913), submitted Oct 16, 2025.
- [A Theoretical Study on Bridging Internal Probability and Self-Consistency for LLM Reasoning](https://arxiv.org/abs/2510.15444), submitted Oct 17, 2025.
- [Seer Self-Consistency: Advance Budget Estimation for Adaptive Test-Time Scaling](https://arxiv.org/abs/2511.09345), submitted Nov 12, 2025, revised Jan 21, 2026.
- [DAJ: Data-Reweighted LLM Judge for Test-Time Scaling in Code Generation](https://arxiv.org/abs/2601.22230), submitted Jan 29, 2026.

## Pressure Map

**Short-trace pressure is real.** First Finish Search argues that shorter traces can be much more likely to be correct and gives a simple parallel-decoding strategy. This directly pressures any "inspect more candidates" story. Our response should not be hand-wavy: v51 already showed shortest-cluster selection is weak on the available MATH traces, and v58/v59 now explain why this may be regime-dependent. GSM8K/Llama is shallow/surfaced; hard MATH is depth-limited.

**Budget-aware verification is now a live frontier.** Budget-aware discriminative verification and RL^V both support the broad direction that verifiers matter under test-time compute. That means "use a verifier" is not novel enough. The novelty claim must be narrower: answer-cluster selectability diagnostics, depth-aware cluster inspection, and regression-aware deployment scoring.

**Dynamic self-consistency and confidence estimation are adjacent, not replacements.** SeerSC and RPC emphasize deciding how much sampling to perform or improving confidence estimates over generated paths. Our useful distinction is after coverage: once a correct answer cluster exists, the bottleneck may be surfacing it. That is why v36/v41-v44 generation-only baselines and v58/v59 trace-regime classification matter.

**Judge distribution shift is a serious objection.** DAJ explicitly calls out hard/easy imbalance, task mismatch, and trajectory mismatch for LLM judges in test-time scaling. This reinforces v55: final cluster selection transfer can look stable while candidate-level confidence/calibration shifts. Any external verifier benchmark must report calibration, fallback behavior, false regression, and transfer boundaries.

## Updated Position

The strongest current positioning is:

> Test-time scaling should report trace regime. In shallow/surfaced regimes, short-trace or shallow self-consistency methods may be enough. In coverage-limited regimes, better generation or stronger base models matter first. In depth-limited regimes, answer-cluster selectability becomes the bottleneck: correct answer clusters exist, but the deployed selector fails to surface them. Adaptive cluster-depth verification is a budgeted method target for that regime.

## What This Rules Out

Do not claim:

- "Verification beats generation."
- "Cluster selectability dominates all test-time scaling."
- "The method is novel because it uses a verifier."

Do claim:

- The diagnostic decomposes coverage, realized selection, and depth visibility.
- The local traces now show three regimes, with a three-seed stability check.
- The prepared external-verifier benchmark must measure not just raw packet accuracy, but deployed delta, false regression, calibration, confidence fallback, and judge shift.

## Paper Edit Implication

The introduction should cite the recent TTS/verifier work as friendly pressure, then immediately narrow:

1. Existing work asks how to allocate samples or train/use verifiers under budget.
2. This work asks when the correct answer is already generated but not surfaced.
3. The contribution is a diagnostic and benchmark protocol for depth-limited answer-cluster selectability, plus a projected adaptive-depth method whose missing step is measured verifier replacement.

