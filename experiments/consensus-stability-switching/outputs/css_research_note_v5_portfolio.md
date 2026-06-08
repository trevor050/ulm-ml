# Candidate-Set Selector Switching, Portfolio Revision

**Status:** v5 research note, June 1, 2026  
**Main update:** the strongest new evidence is not that the learned router is good. It is that broader selector portfolios expose much larger recoverable headroom than the binary CSS setup.

## Updated Thesis

The research direction should be framed as:

> **Selector reliability is a bottleneck in test-time scaling, and selector portfolios expose recoverable headroom that single selectors hide.**

CSS remains the routing probe, but the immediate empirical win is portfolio construction:

- self-consistency is often strong,
- verifier Best-of-N is often weak with the cheap verifier,
- cluster-level selectors can beat self-consistency in some MATH regimes,
- oracle portfolio accuracy is far above the best fixed selector,
- the current learned router does not yet recover that oracle headroom.

That is a more honest and more useful story than "CSS beats SC."

## New Portfolio Lab

New script:

- [monkey_portfolio_lab.py](monkey_portfolio_lab.py)

Reports:

- [MATH/Llama portfolio lab](monkey_portfolio_math_llama.md)
- [MATH/Gemma-2B portfolio lab](monkey_portfolio_math_gemma2b.md)

Selectors tested:

- first sample,
- verifier Best-of-N,
- support-weighted verifier Best-of-N,
- self-consistency,
- cluster max verifier score,
- cluster mean verifier score,
- cluster sum verifier score,
- cluster support plus max verifier score,
- binary SC-vs-selector routers,
- multi-selector portfolio router,
- oracle portfolio.

## MATH / Llama-3-8B-Instruct

| selector | accuracy |
|---|---:|
| first | 0.299 |
| verifier Best-of-N | 0.290 |
| hybrid Best-of-N | 0.328 |
| self-consistency | 0.399 |
| cluster max | 0.290 |
| cluster mean | 0.192 |
| cluster sum | 0.403 |
| cluster support max | 0.402 |
| binary router: SC vs hybrid | 0.400 |
| binary router: SC vs cluster sum | 0.401 |
| binary router: SC vs cluster support max | 0.401 |
| multi-selector router | 0.396 |
| oracle SC/hybrid | 0.442 |
| oracle portfolio | 0.484 |
| any-correct | 0.690 |

High-N behavior:

| N | SC | best fixed selector | learned router | oracle portfolio | any-correct |
|---:|---:|---:|---:|---:|---:|
| 32 | 0.421 | 0.427 | 0.405 | 0.519 | 0.749 |
| 64 | 0.428 | 0.428 | 0.422 | 0.507 | 0.805 |
| 128 | 0.430 | 0.436 | 0.426 | 0.510 | 0.854 |

Interpretation:

- Cluster-sum selection beats self-consistency by 0.4 points overall.
- At N=128, the best fixed selector beats SC by 0.6 points.
- The oracle portfolio reaches 0.484 overall and 0.510 at N=128.
- Any-correct coverage remains huge: 0.854 at N=128.
- The learned routers fail to beat the best fixed selector.

The selector portfolio creates real headroom. The current router does not recover it.

## MATH / Gemma-2B

| selector | accuracy |
|---|---:|
| first | 0.101 |
| verifier Best-of-N | 0.119 |
| hybrid Best-of-N | 0.138 |
| self-consistency | 0.178 |
| cluster max | 0.120 |
| cluster mean | 0.075 |
| cluster sum | 0.185 |
| cluster support max | 0.181 |
| portfolio router | 0.178 |
| oracle SC/hybrid | 0.212 |
| oracle portfolio | 0.243 |
| any-correct | 0.483 |

High-N behavior:

| N | SC | best fixed selector | router | oracle portfolio | any-correct |
|---:|---:|---:|---:|---:|---:|
| 32 | 0.194 | 0.207 | 0.198 | 0.287 | 0.535 |
| 64 | 0.213 | 0.213 | 0.207 | 0.279 | 0.640 |
| 128 | 0.206 | 0.206 | 0.191 | 0.275 | 0.723 |

Interpretation:

- This reverses the earlier "Gemma is just a negative" read.
- Binary CSS hurt, but the broader fixed portfolio finds a better selector: cluster sum.
- The portfolio oracle is still much higher than fixed selectors.
- The router again fails.

The failure is no longer "CSS has no signal." It is more specific:

> The current router cannot reliably learn when to leave self-consistency for a minority/cluster selector.

## Why Cluster Sum Helps

Self-consistency chooses the largest answer cluster. Verifier Best-of-N chooses one high-scoring candidate. Cluster-sum selection does something in between:

```text
choose answer cluster argmax_a sum_{i: answer_i = a} verifier_score_i
```

It rewards both support and verifier confidence. This is useful when:

- the majority cluster is wrong but shallow,
- a minority cluster has multiple moderately convincing solutions,
- single-candidate verifier scores are too noisy for pure Best-of-N.

This suggests a better selector family:

- cluster mass,
- cluster mean verifier score,
- cluster max verifier score,
- cluster entropy,
- cluster-level calibration.

The next model should score answer clusters, not individual candidates.

## Router Failure Is Now The Main Problem

The naive router trains logistic correctness predictors over selectors and chooses the selector with highest predicted correctness. It fails to beat fixed cluster-sum selection.

Likely reasons:

1. Calibration set is too small for selector-specific routing.
2. Router features are mostly global candidate-set features, not selector-local enough.
3. The router objective is misaligned: it predicts correctness, but should predict relative advantage over SC.
4. Selector wins are sparse, so class imbalance is brutal.
5. Disagreement mining is too crude.

The next router should be conservative:

```text
default to SC or cluster_sum
switch only when estimated advantage exceeds a learned threshold
```

And it should train on pairwise selector advantages:

```text
P(selector_a correct and selector_b wrong | features)
```

not independent selector correctness.

## Stronger Next Experiment

The best immediate research step is a **cluster-level selector model**:

For each answer cluster, compute:

- support,
- max verifier score,
- mean verifier score,
- sum verifier score,
- score variance,
- average length/equation-validity features,
- whether cluster contains the first sample,
- cluster rank under SC and verifier.

Train a cluster-level ranker on calibration problems and choose the highest-ranked cluster.

This should be compared against:

- SC,
- cluster sum,
- support-weighted verifier,
- binary CSS,
- oracle portfolio.

This is likely a stronger path than trying to improve the current candidate-level router.

## Updated Verdict

The research idea has matured from:

> "Can CSS route between verifier BoN and self-consistency?"

to:

> "Can candidate-set features expose and exploit selector reliability in repeated-sampling test-time scaling?"

The answer so far:

- yes, the selectability gap is huge;
- yes, simple cluster selectors improve over SC in MATH/Llama and MATH/Gemma;
- yes, selector portfolios expose much larger oracle headroom;
- no, the current learned router is not good enough.

That is a much better research state. It has a real empirical obstacle, not just a vague next step.

## References

- Scaling Intelligence. [Monkey Business dataset](https://huggingface.co/datasets/ScalingIntelligence/monkey_business).
- Brown et al., 2024. [Large Language Monkeys: Scaling Inference Compute with Repeated Sampling](https://arxiv.org/abs/2407.21787).
- Snell et al., 2024. [Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters](https://arxiv.org/abs/2408.03314).
- Dorner et al., 2025. [ROC-n-reroll: How verifier imperfection affects test-time scaling](https://arxiv.org/abs/2507.12399).
- Shyamal et al., 2026. [SCATR: Simple Calibrated Test-Time Ranking](https://arxiv.org/abs/2604.16535).
