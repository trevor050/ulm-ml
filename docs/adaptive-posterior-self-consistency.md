# Adaptive Posterior Self-Consistency

## One-sentence idea

Self-consistency spends a fixed number of reasoning samples even when the answer distribution has already converged; replace the fixed budget with a tiny Dirichlet posterior test that asks, "how likely is the current majority answer to remain the winner if we kept sampling?"

## Why this is worth trying now

Recent reasoning systems are increasingly bottlenecked by test-time compute rather than training-time novelty.  Chain-of-thought prompting made reasoning traces useful, self-consistency showed that sampling diverse traces and majority-voting final answers can substantially improve accuracy, and the 2024--2026 inference-scaling literature has made adaptive compute allocation a first-class research question.  The practical gap is simple: if 32 samples are useful on hard prompts, they are often wasteful on easy prompts.

This note proposes an intentionally small method that can be evaluated without training a model:

1. Generate up to `N` stochastic reasoning samples per problem.
2. Extract normalized final answers.
3. Maintain answer counts.
4. Stop early when a posterior stability test says the current leader is very likely to be the true sampling-distribution argmax.
5. Otherwise continue until the hard cap.

The method is model-agnostic, works with cached traces, and turns expensive LLM calls into a replayable policy-selection problem.

## Method

Let `c` be answer counts after `t` samples and use a symmetric Dirichlet prior `Dirichlet(alpha)`.  The posterior over the model's answer probabilities is:

```text
p(answer probabilities | c) = Dirichlet(c + alpha)
```

Let `a* = argmax(c)` be the current majority answer.  Estimate:

```text
P(p[a*] > max_j!=a* p[j] | c)
```

by Monte Carlo draws from the posterior.  Stop if this probability exceeds a confidence threshold, subject to a minimum sample count and a maximum budget.

## Why it might beat simple vote margins

Vote-margin stopping only sees the integer gap between first and second place.  A posterior stability rule sees more structure:

- A 5--2 lead over one rival is less stable than a 5--1--1--1--1 lead spread across many rivals.
- A 7--4 lead after 11 samples is not equivalent to a 3--0 lead after 3 samples.
- The confidence threshold is calibratable on cached traces, making it possible to target "save as many samples as possible while losing at most X accuracy points."

## Current synthetic result

The first executable result is in `reports/adaptive-consistency.md`.  On a heterogeneous synthetic answer-sampler suite, the posterior rule matched the fixed-32 accuracy while using roughly half the samples.  This is not evidence of a benchmark win; it is a sanity check showing the rule behaves plausibly enough to justify a trace-replay experiment with a small open model.

## Minimum viable real experiment

A realistic next run should avoid any new training:

1. Use a small instruction/reasoning model that fits available hardware or an inexpensive API batch.
2. Select GSM8K, SVAMP, or another answer-extractable reasoning benchmark.
3. For each problem, sample 32 reasoning traces with temperature > 0 and store only prompt id, normalized final answer, correctness, and token count.  Do not commit raw large trace files.
4. Replay fixed budgets, vote-margin stopping, and posterior stopping over identical trace prefixes.
5. Tune only the posterior confidence threshold on a validation split.
6. Report accuracy, mean calls, mean generated tokens, p90 calls, and the Pareto frontier.

## References used for orientation

- Wei et al. introduced chain-of-thought prompting as a way to elicit intermediate reasoning from sufficiently large language models: https://arxiv.org/abs/2201.11903
- Wang et al. introduced self-consistency decoding, sampling multiple reasoning paths and marginalizing final answers: https://arxiv.org/abs/2203.11171
- Snell et al. studied how to spend inference-time compute and compare that scaling path with larger pretrained models: https://arxiv.org/abs/2408.03314
- Zelikman et al. explored models learning to generate useful latent/hidden rationales before speaking in Quiet-STaR: https://arxiv.org/abs/2403.09629
- Recent adaptive-compute work frames budget controllability and difficulty-aware stopping as a central issue for reasoning systems: https://arxiv.org/abs/2507.02076
