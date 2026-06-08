# Cluster Selectability: A Sharper Research Proposal

**Status:** v8 draft, June 1, 2026  
**Working title:** *The Cluster Selectability Gap in Test-Time Scaling*

## Abstract

Repeated sampling often produces a correct solution before current selectors can identify it. On public Monkey Business traces, MATH/Llama reaches `0.846-0.864` any-correct coverage at `N=128`, while self-consistency and simple verifier-mass cluster selection remain around `0.445-0.455`. MATH/Gemma-2B shows an even larger selection failure: `0.720-0.725` any-correct coverage at `N=128`, but only `0.236-0.240` cluster-sum accuracy.

This suggests a useful diagnostic and method target: evaluate test-time scaling not only by coverage or final selected accuracy, but by **cluster selectability**, the ability to surface the correct final-answer cluster from a sampled candidate set. The current experiments show that shallow routers and cheap surface-feature rankers do not close this gap. Even adding crude intra-cluster rationale-consistency features produces only a tiny gain on MATH/Llama and remains negative on MATH/Gemma-2B. The next credible method is therefore not another selector switch; it is a stronger cluster verifier that changes the evidence available for ranking answer clusters.

## Core Claim

Repeated-sampling systems should report three quantities:

```text
coverage_N = P(any sampled candidate is correct)
selector_accuracy_N = P(the deployed selector chooses a correct candidate)
cluster_selectability_N(k) = P(a correct answer cluster is ranked in top-k)
```

The gap

```text
coverage_N - selector_accuracy_N
```

is the **selectability gap**. A large gap means test-time compute is producing useful answers that the selector cannot surface.

The top-k variant matters because it distinguishes two regimes:

- **Local reranking regime:** the correct cluster is usually rank 2-3, so a cheap top-k reranker may recover meaningful headroom.
- **Evidence failure regime:** the correct cluster is buried, so the current verifier/support signal is not exposing it and a stronger cluster verifier is required.

## Evidence So Far

All results below use public repeated-sampling traces from the Monkey Business dataset and held-out problem splits. The selectors are intentionally simple and reproducible: first sample, self-consistency, candidate-level verifier Best-of-N, cluster-sum verifier mass, learned cluster rankers, and oracle cluster coverage.

### Multi-Config Selector Results

| config | first | self-consistency | CSS/router | any-correct | selectability gap |
|---|---:|---:|---:|---:|---:|
| GSM8K/Llama-3-8B | 0.777 | 0.846 | 0.849 | 0.973 | 0.127 |
| MATH/Llama-3-8B | 0.295 | 0.398 | 0.403 | 0.691 | 0.293 |
| MATH/Gemma-2B | 0.102 | 0.181 | 0.177 | 0.481 | 0.300 |
| MATH/Pythia-1B | 0.010 | 0.012 | 0.012 | 0.150 | 0.135 |

Reading: CSS-style selector switching is only marginally helpful in the medium-accuracy MATH/Llama regime and fails on Gemma. The robust signal is the gap between any-correct coverage and realized selector accuracy.

### Cluster-Ranker Results

| config | self-consistency | cluster_sum | learned cluster ranker | oracle cluster |
|---|---:|---:|---:|---:|
| MATH/Llama | 0.406 | 0.408 | 0.406 | 0.690 |
| MATH/Gemma-2B | 0.191 | 0.194 | 0.187 | 0.483 |

The obvious learned cluster ranker did not beat the simple `cluster_sum` rule. This is a negative result against the naive "just train a router" hypothesis.

### Intra-Cluster Consistency Feature Results

New v8 experiment: add cheap rationale-consistency features to answer clusters:

- pairwise overlap of non-final numeric tokens,
- core-number support inside a cluster,
- duplicate numeric-trajectory concentration,
- repeated-character/junk penalty.

| config | self-consistency | cluster_sum | learned ranker + consistency | oracle cluster |
|---|---:|---:|---:|---:|
| MATH/Llama | 0.405 | 0.402 | 0.407 | 0.689 |
| MATH/Gemma-2B | 0.191 | 0.194 | 0.190 | 0.483 |

At `N=128`:

| config | self-consistency | cluster_sum | learned ranker + consistency | oracle cluster |
|---|---:|---:|---:|---:|
| MATH/Llama | 0.448 | 0.445 | 0.447 | 0.846 |
| MATH/Gemma-2B | 0.218 | 0.222 | 0.222 | 0.723 |

The cheap consistency features are not enough. They slightly help some MATH/Llama slices, but they do not materially close headroom and do not rescue Gemma. This is useful because it narrows the method target: the verifier has to reason about cluster correctness, not merely count overlapping numbers.

### Selectability Audit

The audit asks where the best correct answer cluster ranks under current cluster-sum evidence.

| config | any-correct | cluster_sum | headroom | correct top-2 by sum | correct top-3 by sum | miss top-2 by sum | miss top-3 by sum |
|---|---:|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.689 | 0.402 | 0.287 | 0.703 | 0.776 | 0.288 | 0.463 |
| MATH/Gemma-2B | 0.481 | 0.201 | 0.280 | 0.524 | 0.610 | 0.183 | 0.331 |

At `N=128`:

| config | any-correct | cluster_sum | headroom | miss top-2 by sum | miss top-3 by sum |
|---|---:|---:|---:|---:|---:|
| MATH/Llama | 0.846 | 0.445 | 0.401 | 0.183 | 0.317 |
| MATH/Gemma-2B | 0.725 | 0.240 | 0.485 | 0.125 | 0.254 |

Interpretation: at low to medium N, a top-k reranker could recover some failures. At high N, where coverage is best and the oracle gap is largest, the correct cluster is often not near the top under current verifier mass. That makes this an evidence problem, not just a tie-breaking problem.

### Top-k Oracle Bound

If a perfect verifier could inspect only the top clusters ranked by current `cluster_sum` evidence, the upper bound would be:

| config | slice | cluster_sum | full oracle | top-2 oracle | top-3 oracle |
|---|---|---:|---:|---:|---:|
| GSM8K/Llama | overall | 0.847 | 0.973 | 0.943 | 0.954 |
| MATH/Llama | overall | 0.402 | 0.689 | 0.484 | 0.535 |
| MATH/Gemma-2B | overall | 0.201 | 0.481 | 0.252 | 0.294 |
| MATH/Pythia-1B | overall | 0.031 | 0.155 | 0.059 | 0.083 |
| GSM8K/Llama | N=128 | 0.852 | 1.000 | 0.970 | 0.977 |
| MATH/Llama | N=128 | 0.445 | 0.846 | 0.518 | 0.572 |
| MATH/Gemma-2B | N=128 | 0.240 | 0.725 | 0.301 | 0.363 |
| MATH/Pythia-1B | N=128 | 0.038 | 0.322 | 0.092 | 0.122 |

This is useful because it prevents overclaiming. GSM8K is a local-reranking-friendly regime: the correct cluster is usually near the top. MATH/Llama and MATH/Gemma are evidence-failure regimes: a top-3 verifier is worth building, but at high N it can only close about `0.127` absolute accuracy on MATH/Llama and `0.123` on Gemma unless the verifier also changes the ranking evidence enough to pull buried correct clusters into the inspected set. Pythia is different again: coverage itself remains too low for verification to be the main bottleneck.

## Proposed Method

The next method should be **Cluster Evidence Verification**:

```text
1. Sample N candidate solutions.
2. Extract final answers and form answer clusters.
3. Rank clusters by cheap support/verifier mass.
4. Keep a bounded top-k candidate cluster set, plus optional diversity clusters.
5. Build a cluster packet from representative rationales per cluster.
6. Score each cluster with evidence unavailable to candidate-level BoN:
   - agreement of intermediate quantities,
   - validity of derivation steps,
   - contradiction rate within the cluster,
   - problem-conditioned plausibility of representative rationales,
   - pairwise comparison against the currently selected wrong cluster.
7. Select the cluster, then return a representative candidate from it.
```

The key constraint is compute. Do not judge every sampled candidate. Spend extra verification only on a small number of clusters after cheap clustering has compressed the candidate set.

## Minimal First Implementable Version

For a compute-light experiment, use top-k cluster packets:

```text
cluster_packet(c) =
  problem text
  final answer for cluster c
  3 representative rationales from c
  2 rationales from the current top wrong/competing clusters
```

Then ask a verifier model or stronger local LLM:

```text
Which final answer is best supported by the reasoning shown?
Return one final answer and a confidence.
```

Evaluate:

- `cluster_sum`,
- self-consistency,
- learned cluster ranker,
- cluster-packet verifier,
- oracle top-k verifier,
- full oracle cluster.

The main metric is headroom closure:

```text
(Acc(method) - Acc(cluster_sum)) / (Acc(oracle_cluster) - Acc(cluster_sum))
```

Also report top-k migration: does the new evidence move the correct cluster into rank 1 more often than `cluster_sum`?

## Why This Is Different From Existing Work

Self-consistency selects the most common final answer. It does not measure whether correct minority clusters are present or recoverable.

Large Language Monkeys shows repeated sampling scales coverage and that majority/reward-model selection can plateau without automatic verifiers. Cluster selectability is a diagnostic microscope for that plateau.

Compute-optimal test-time scaling work asks how to allocate inference compute. Cluster selectability can be one of the routing signals: if top-k selectability is high, spend compute on reranking; if it is low, generate more or use stronger verification.

Process reward models and generative verifiers score candidate reasoning, usually one trajectory at a time. The proposed method scores answer clusters as evidence bundles.

Representation Consistency is the closest neighbor because it uses internal consistency across responses to improve aggregation. The current pitch is distinct in two ways: it first measures public-trace selectability gaps and top-k recoverability, and it does not assume hidden activations are available. Hidden-state consistency would be an excellent stronger variant if traces can be regenerated.

## Reviewer-Resistant Claims

Safe claims:

- Public repeated-sampling traces show large selectability gaps on MATH.
- Simple selector switching produces only marginal wins and can fail.
- Simple learned cluster rankers with cheap features do not close the gap.
- Cheap numeric-overlap rationale consistency is insufficient.
- Top-k cluster audits reveal when local reranking is plausible and when stronger evidence is needed.

Claims not yet safe:

- "CSS is a new state-of-the-art selector."
- "Stability features solve test-time selection."
- "Correct clusters are usually near the top at high N."
- "A lightweight verifier can recover most oracle headroom."

The strongest honest claim is diagnostic plus method target:

> Test-time scaling papers should report cluster coverage and cluster selectability, because any-correct coverage can dramatically overstate usable performance when the selector cannot identify the correct answer cluster.

## Threats To Validity

- The candidate verifier is intentionally cheap and text-only; stronger verifier baselines could reduce the gap.
- Monkey Business traces are fixed samples; hidden states and token logprobs are unavailable here.
- MATH final-answer extraction and normalization are imperfect.
- Cluster correctness is based on whether any candidate in the answer cluster is labeled correct, which can hide flawed rationales that land on the right answer.
- Results are from small held-out problem splits, not full benchmark-scale regeneration.
- The top-k audit uses randomized subsets of fixed traces, so exact rates vary by seed and trials.

## Next Experiments

1. **Cluster-packet verifier on top-k clusters.** Use the PC/RTX 4070 if available, or a small remote/local model if not. Start with MATH/Llama at `N=32,64,128`, `k=3`.
2. **Oracle top-k bound.** Report how much of the oracle cluster headroom is theoretically recoverable if a perfect verifier only sees top-k clusters.
3. **Hard-pair dataset.** Construct pairs where `cluster_sum` selects a wrong cluster while a correct cluster is present. Train/evaluate a pairwise cluster preference model.
4. **Regenerate small traces with hidden states/logprobs.** Test representation consistency and SCATR-like features if model access allows.
5. **Compute budget curves.** Compare generating more candidates vs spending verification on top-k clusters.

## Artifacts

Core scripts:

- [monkey_css_realbench.py](monkey_css_realbench.py)
- [monkey_cluster_ranker.py](monkey_cluster_ranker.py)
- [cluster_selectability_audit.py](cluster_selectability_audit.py)
- [build_cluster_packet_dataset.py](build_cluster_packet_dataset.py)
- [topk_cluster_oracle_bounds.py](topk_cluster_oracle_bounds.py)
- [make_cluster_verifier_prompts.py](make_cluster_verifier_prompts.py)
- [evaluate_cluster_verifier_predictions.py](evaluate_cluster_verifier_predictions.py)

Core reports:

- [multi-config summary](monkey_css_multiconfig_summary.md)
- [MATH/Llama cluster ranker](monkey_cluster_ranker_math_llama.md)
- [MATH/Gemma cluster ranker](monkey_cluster_ranker_math_gemma2b.md)
- [MATH/Llama consistency ranker](monkey_cluster_ranker_consistency_math_llama.md)
- [MATH/Gemma consistency ranker](monkey_cluster_ranker_consistency_math_gemma2b.md)
- [MATH/Llama selectability audit](cluster_selectability_math_llama.md)
- [MATH/Gemma selectability audit](cluster_selectability_math_gemma2b.md)
- [GSM8K/Llama selectability audit](cluster_selectability_gsm8k_llama.md)
- [MATH/Pythia selectability audit](cluster_selectability_math_pythia1b.md)
- [cluster selectability gap plot](cluster_selectability_gap_plot.svg)
- [top-k cluster oracle bounds](topk_cluster_oracle_bounds.md)
- [MATH/Llama hard cluster packets](cluster_packets_math_llama_n128.md)
- [MATH/Gemma hard cluster packets](cluster_packets_math_gemma2b_n128.md)
- [cluster-packet verifier protocol](cluster_packet_verifier_protocol.md)
- [v9 rescue-selector ablation](css_research_note_v9_rescue_selector.md)
- [v10 failure-detector diagnostics](css_research_note_v10_failure_detector.md)
- [research package README](README.md)
- [literature map](css_literature_map.md)

## Related Work

- Wang et al. [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171).
- Brown et al. [Large Language Monkeys: Scaling Inference Compute with Repeated Sampling](https://arxiv.org/abs/2407.21787).
- Snell et al. [Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters](https://arxiv.org/abs/2408.03314).
- Zhao et al. [Sample, Scrutinize and Scale: Effective Inference-Time Search by Scaling Verification](https://arxiv.org/abs/2502.01839).
- Singhi et al. [When To Solve, When To Verify: Compute-Optimal Problem Solving and Generative Verification for LLM Reasoning](https://arxiv.org/abs/2504.01005).
- Jiang et al. [Representation Consistency for Accurate and Coherent LLM Answer Aggregation](https://arxiv.org/abs/2506.21590).
- Lightman et al. [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050).

## Bottom Line

The original Hail Mary idea got beaten into a more credible shape:

> The interesting object is not selector switching. The interesting object is the selectability gap between sampled-solution coverage and the selector's ability to surface the correct answer cluster.

That is a clean diagnostic, it is measurable on existing public traces, and it points to a specific next method: bounded cluster-level verification.
