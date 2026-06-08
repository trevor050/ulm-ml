# Candidate-Set Selector Switching, Selectability Audit Revision

**Status:** v7 research note, June 1, 2026  
**Main update:** I added a cluster selectability audit to measure whether missed correct clusters are near the top of the current cluster ranking or buried deeper in the candidate set.

## Why This Experiment

The v6 cluster-ranker result showed a large gap between `cluster_sum` and the oracle cluster selector:

- MATH/Llama: `cluster_sum` 0.408 vs oracle cluster 0.690.
- MATH/Gemma-2B: `cluster_sum` 0.194 vs oracle cluster 0.483.

That gap alone does not tell us what kind of method should come next. If correct clusters are usually rank 2 or 3 by existing score mass, a local reranker over the top few clusters may be enough. If correct clusters are much lower, the current evidence is not surfacing them and we need a stronger cluster verifier.

## New Script And Reports

Script:

- [cluster_selectability_audit.py](cluster_selectability_audit.py)

Reports:

- [MATH/Llama selectability audit](cluster_selectability_math_llama.md)
- [MATH/Gemma-2B selectability audit](cluster_selectability_math_gemma2b.md)
- [MATH/Llama loss decomposition](monkey_selectability_math_llama.md)
- [MATH/Gemma-2B loss decomposition](monkey_selectability_math_gemma2b.md)

The audit keeps the same held-out-problem split shape as the cluster-ranker run:

- train a cheap candidate verifier on verifier-train problems,
- skip the calibration/ranker split,
- audit random candidate sets from held-out test problems,
- rank answer clusters by support and by verifier-score mass (`cluster_sum`).

## Overall Results

| config | any-correct | SC | cluster_sum | headroom | correct top-2 by sum | correct top-3 by sum | miss top-2 by sum | miss top-3 by sum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.689 | 0.405 | 0.402 | 0.287 | 0.703 | 0.776 | 0.288 | 0.463 |
| MATH/Gemma-2B | 0.481 | 0.200 | 0.201 | 0.280 | 0.524 | 0.610 | 0.183 | 0.331 |

Definitions:

- `correct top-k by sum`: among candidate sets where any correct answer exists, whether a correct cluster is ranked in the top k by `cluster_sum`.
- `miss top-k by sum`: among candidate sets where any correct answer exists but `cluster_sum` chooses a wrong cluster, whether a correct cluster is still ranked in the top k by `cluster_sum`.

## High-N Results

At N=128:

| config | any-correct | SC | cluster_sum | headroom | miss top-2 by sum | miss top-3 by sum |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.846 | 0.448 | 0.445 | 0.401 | 0.183 | 0.317 |
| MATH/Gemma-2B | 0.725 | 0.243 | 0.240 | 0.485 | 0.125 | 0.254 |

This is the important slice. Repeated sampling is creating the correct cluster, but the current score-mass ranking often does not place it in the top two or three once N is large.

## Loss Decomposition Cross-Check

A second diagnostic decomposes every trial into: no correct candidate, `cluster_sum` correct, correct cluster top-3 but not top-1, or correct cluster buried.

| config | cluster_sum correct | no correct candidate | correct top-3 but not top-1 | correct buried |
|---|---:|---:|---:|---:|
| MATH/Llama | 0.409 | 0.306 | 0.121 | 0.164 |
| MATH/Gemma-2B | 0.201 | 0.525 | 0.084 | 0.190 |

At N=128:

| config | any-correct | cluster_sum | recoverable cluster_sum miss | correct top-3 by sum | avg clusters | avg correct clusters |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.864 | 0.455 | 0.409 | 0.577 | 31.4 | 1.55 |
| MATH/Gemma-2B | 0.720 | 0.236 | 0.483 | 0.339 | 57.9 | 1.49 |

This cross-check agrees with the audit: the coverage gap is real, and high-N failures are often recoverable in principle but not exposed cleanly by current verifier mass.

## Interpretation

The audit makes the next-step decision sharper:

1. At low N, missed correct clusters are often near the top. A local top-k reranker could recover some errors.
2. At high N, where the oracle gap is largest, correct clusters are less often near the top by `cluster_sum`.
3. Gemma-2B is the hardest case: at N=128, any-correct is 0.725, but on `cluster_sum` misses the correct cluster is rank <=2 only 12.5% of the time.
4. Therefore, the main bottleneck is not just choosing better among the current top few clusters. The scoring evidence itself has to improve.

The v6 conclusion survives, but with a stronger justification:

> The next serious method should be a cluster verifier that changes the evidence signal, not merely a router or shallow reranker over the existing candidate-level verifier mass.

## Updated Research Claim

The most defensible pitch is now:

> Repeated-sampling systems should report answer-cluster coverage, realized selector accuracy, and top-k cluster selectability. Large gaps between any-correct coverage and top-k cluster rank reveal when test-time compute is producing useful answers that current selectors cannot surface.

CSS remains useful as the diagnostic frame:

- define the selector portfolio,
- measure fixed selector performance,
- measure oracle/headroom,
- audit where the missed correct cluster ranks,
- then decide whether to use a local reranker or build stronger cluster evidence.

## Next Experiment

Build a cluster verifier that scores clusters with information not already captured by support and verifier mass:

- within-cluster derivation agreement,
- equation/intermediate-value consistency,
- contradiction rate across rationales,
- problem-conditioned LLM judge scores for a small number of representative rationales,
- maybe a pairwise preference model between the selected wrong cluster and the best available correct cluster.

The target metric should be high-N headroom closure against `cluster_sum`, plus top-k migration: does the correct cluster move into rank 1-3 more often after the new evidence is added?

## Current Verdict

This audit is a useful negative constraint. It says:

- the oracle gap is real,
- the correct cluster is often present,
- the current score-mass ranking does not reliably put the correct cluster near the top at high N,
- so the research direction should focus on cluster evidence, not another shallow selector switch.
