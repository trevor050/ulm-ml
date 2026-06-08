# v70 Live Literature Positioning Refresh

**Date:** June 1, 2026  
**Question:** After the v63-v69 phase/cost/policy results, what does current 2025/2026 test-time scaling literature force us to claim more narrowly?

## Sources Checked

- [When More Thinking Hurts: Overthinking in LLM Test-Time Compute Scaling](https://arxiv.org/abs/2604.10739), arXiv 2026.
- [The Art of Scaling Test-Time Compute for Large Language Models](https://arxiv.org/abs/2512.02008), arXiv 2025.
- [Reasoning on a Budget: A Survey of Adaptive and Controllable Test-Time Compute in LLMs](https://arxiv.org/abs/2507.02076), arXiv 2025.
- [Seer Self-Consistency: Advance Budget Estimation for Adaptive Test-Time Scaling](https://arxiv.org/abs/2511.09345), arXiv 2025/2026 revision.
- [Putting the Value Back in RL: Better Test-Time Scaling by Unifying LLM Reasoners With Verifiers](https://arxiv.org/abs/2505.04842), arXiv 2025/2026 revision.
- [Linguistic Generalizability of Test-Time Scaling in Mathematical Reasoning](https://arxiv.org/abs/2502.17407), arXiv 2025.
- [Evaluating the Role of Verifiers in Test-Time Scaling for Legal Reasoning Tasks](https://arxiv.org/abs/2510.25623), arXiv 2025.

## Pressure on the Claim

The generic claim "adaptive test-time compute is useful" is not novel. Current work already emphasizes:

- Fixed compute is wasteful; adaptive or controllable compute is the current framing.
- More reasoning can hurt through overthinking or abandoning a previously correct answer.
- No single TTS strategy dominates across model, budget, and problem difficulty.
- Verifier utility depends on domain, verifier supervision, model size, and available budget.
- Dynamic self-consistency can use cheap early signals such as entropy to decide when to spend more samples.

So the paper should not pitch itself as a new general theory of test-time scaling or as a generic verifier win.

## Surviving Novelty Slice

The stronger and safer claim is:

> Repeated sampling should be diagnosed at the answer-cluster level. Some traces are surfaced, some are coverage-limited, and some are depth-limited. In depth-limited traces, the correct answer may already exist but be buried beyond cheap selectors. A phase-aware policy can allocate verifier depth over answer clusters with explicit quality and token-value tradeoffs.

The v63-v69 results now make this slice concrete:

- v63: phase-aware triage says where verifier budget should be spent.
- v64: high-N phase labels are not threshold-fragile.
- v65: depth-limited MATH does not require heroic verifier-quality assumptions.
- v66: depth must be adaptive; top20 is not universal.
- v67: prompt-cost ROI says top5/top10 are efficient and top20 is tail spend.
- v68: utility frontier gives an explicit value threshold for top20.
- v69: quality sweep shows the frontier degrades toward no-verifier/top10 when verifier success is worse.

## Positioning Against Specific Threads

**Overthinking / budgeted reasoning.** The overthinking paper supports the direction: uniform extra compute is not always better. Our contribution is not another stop-length rule; it is a cluster-level diagnostic for whether the bottleneck is coverage, surfaced selection, or buried correct clusters.

**Broad TTS strategy comparisons.** Large-scale TTS comparisons argue no strategy dominates universally. Our result should be framed as a routing diagnostic that chooses when cluster-depth verification is appropriate, not as a universal replacement for self-consistency, reward-model best-of-N, or budget forcing.

**Dynamic self-consistency.** SeerSC-style work estimates whether more samples are worth generating. Our route is complementary: once samples exist, decide whether the answer set is worth verifying and how deep in the cluster ranking to inspect.

**Verifier-training work.** RL^V-style work improves the verifier itself. Our artifact is verifier-agnostic: any measured verifier can be plugged into the v68/v69 frontier via success and false-regression rates.

**Domain / language generalization.** Legal and multilingual TTS papers warn that verifier gains do not transfer automatically. That supports reporting phase/regime diagnostics and quality sweeps instead of claiming broad domain generalization from MATH.

## Required Wording Change

Use this wording in the paper:

> We do not claim that verifier-based test-time scaling is generally superior. We claim that answer-cluster phase diagnostics expose a specific failure mode in high-sample reasoning traces: coverage exists, but deployed selectors fail because correct answer clusters are buried. For that failure mode, adaptive cluster-depth verification provides a costed routing policy.

## Still Missing

The live literature makes the missing experiment more important, not less important: run a real verifier and measure success, false regression, and confidence fallback. Without that, this is a strong diagnostic/policy paper package, not a completed deployed-verifier result.
