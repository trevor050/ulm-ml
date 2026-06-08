# Candidate-Set Selector Switching, Real-Benchmark Revision

**Status:** v3 research pitch, June 1, 2026  
**Main update:** CSS now has a real repeated-sampling benchmark on `ScalingIntelligence/monkey_business`, not just synthetic stress tests.

## Claim

Repeated sampling creates a **coverage/selectability gap**: the candidate set often contains a correct answer, but available selectors fail to choose it. Candidate-Set Selector Switching (CSS) treats test-time scaling selection as a routing problem:

> Given a candidate set, route this problem to the selector most likely to work on this instance.

The current implementation routes between self-consistency and a cheap learned verifier selector. The method is small, black-box, and calibration-driven. It does not require model internals.

## What Is New Since v2

I tested CSS on real rollouts from the Monkey Business dataset released with *Large Language Monkeys*. These are actual model samples, not synthetic candidates:

- GSM8K / Llama-3-8B-Instruct: 127 problems, 10,000 samples per problem.
- MATH / Llama-3-8B-Instruct: 128 problems, 10,000 samples per problem.
- Each sample has a correctness label from the dataset's original grader.

The benchmark trains:

1. A cheap candidate verifier from text-only features on train problems.
2. A CSS router on separate calibration problems.
3. Selectors are evaluated on held-out problems, not held-out samples from the same problems.

The verifier is intentionally weak and inspectable. That makes this a conservative test of the selector-switching idea.

Code:

- [monkey_css_realbench.py](monkey_css_realbench.py)
- [monkey_css_weight_sweep.py](monkey_css_weight_sweep.py)

Reports:

- [monkey_css_gsm8k_realbench.md](monkey_css_gsm8k_realbench.md)
- [monkey_css_math_realbench.md](monkey_css_math_realbench.md)
- [monkey_css_math_weight_sweep.md](monkey_css_math_weight_sweep.md)

## Real Benchmark Results

### GSM8K: Negative / Weak Result

On GSM8K, self-consistency is already very strong. The cheap verifier is worse, and CSS has little room to matter.

| Method | Accuracy |
|---|---:|
| first sample | 0.777 |
| verifier Best-of-N | 0.789 |
| self-consistency | 0.846 |
| CSS switch | 0.847 |
| oracle switch | 0.886 |
| any-correct coverage | 0.973 |

Interpretation:

- There is a large selectability gap: 0.973 any-correct vs 0.846 self-consistency.
- But the available verifier is too weak to exploit much of it.
- CSS barely improves over self-consistency, closing only about 1.4% of oracle-switch headroom in this setup.

This is useful because it prevents overclaiming. CSS is not magic. It needs selector diversity.

### MATH: Small Positive Result

MATH is harder and answer clustering is messier. Here CSS produces a small but real lift over self-consistency, especially at larger N.

Overall held-out accuracy:

| Method | Accuracy |
|---|---:|
| first sample | 0.296 |
| verifier Best-of-N | 0.293 |
| support-weighted verifier | 0.328 |
| self-consistency | 0.394 |
| margin gate | 0.389 |
| CSS switch | 0.399 |
| oracle switch | 0.434 |
| any-correct coverage | 0.689 |

At high N:

| N | self-consistency | CSS | oracle switch | any-correct |
|---:|---:|---:|---:|---:|
| 32 | 0.412 | 0.416 | 0.444 | 0.736 |
| 64 | 0.419 | 0.432 | 0.451 | 0.816 |
| 128 | 0.426 | 0.431 | 0.461 | 0.861 |

Interpretation:

- The any-correct coverage gap is huge: 0.861 at N=128 vs 0.426 self-consistency.
- CSS improves over self-consistency by 0.5 points overall and 1.3 points at N=64.
- It closes about 12.5% of the oracle-switch headroom in the best tested configuration.
- This is not a giant win, but it is a real held-out improvement on real repeated-sampling traces.

## Weight Sweep

I swept support-weighted verifier selectors. The best tested MATH setting was support weight 0.10 routing between hybrid verifier and self-consistency:

| support weight | routed selector | verifier BoN | hybrid BoN | SC | CSS | oracle | headroom closed |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0.00 | pure verifier | 0.293 | 0.293 | 0.394 | 0.397 | 0.438 | 0.076 |
| 0.10 | hybrid verifier | 0.293 | 0.328 | 0.394 | 0.399 | 0.434 | 0.125 |
| 0.25 | hybrid verifier | 0.293 | 0.357 | 0.394 | 0.398 | 0.432 | 0.104 |
| 1.00 | hybrid verifier | 0.293 | 0.381 | 0.394 | 0.395 | 0.420 | 0.053 |
| 3.00 | hybrid verifier | 0.293 | 0.390 | 0.394 | 0.394 | 0.412 | 0.000 |

Interpretation:

- Too much support weighting collapses toward self-consistency.
- Too little support weighting leaves the verifier too weak.
- The useful selector is not "a better verifier" alone; it is a partially different selector that sometimes chooses minority candidates.

That supports the selector-portfolio framing.

## Synthetic Stress Tests Still Matter

The synthetic simulator remains useful because it isolates verifier-trap behavior that GSM8K does not stress enough.

Key synthetic findings:

- CSS beats both Best-of-N and self-consistency when verifier traps are mixed into the distribution.
- Feature ablation showed that candidate-set consensus/support features dominate perturbation-stability features.
- Disagreement-mined calibration is far more label-efficient than uniform calibration in the toy setup.
- Training only on clean verifier cases fails under trap-heavy tests.
- Training at low N transfers poorly to high-N over-optimization regimes.

Reports:

- [css_ablation_lab.md](css_ablation_lab.md)
- [stability_gated_tts_results.csv](stability_gated_tts_results.csv)
- [css_formalism_and_metrics.md](css_formalism_and_metrics.md)

## The Strongest Current Version Of The Idea

The publishable idea is not "CSS beats self-consistency everywhere." It does not.

The stronger and more defensible version is:

> Test-time scaling evaluations should measure selector portfolios, oracle-switch headroom, and selectability gaps. A lightweight candidate-set router can close some of that headroom when base selectors make different errors.

This reframes the research contribution from "new selector beats all baselines" to "selector reliability is a first-class test-time scaling problem."

That is more reviewer-resistant because the negative GSM8K result fits the theory:

- If self-consistency dominates the verifier, CSS has little useful work to do.
- If selectors have complementary errors, CSS can help.
- If any-correct coverage is far above all selectors, the right research target is not more sampling alone, it is better selection and selector routing.

## What Must Happen Next

### 1. Use A Stronger Verifier

The current text-feature verifier is deliberately weak. The obvious next run is:

- Qwen/Gemma/LLM judge scores,
- PRM-style scoring if available,
- logprob-based scoring from a local model,
- SCATR-like hidden-state features if model internals are available.

Prediction: CSS becomes more useful when verifier Best-of-N sometimes beats self-consistency but also has trap cases.

### 2. Run More Monkey Business Configs

Priority configs:

- `MATH_Gemma-2B`
- `MATH_Gemma-7B`
- `MATH_Pythia-1B`
- `MATH_Llama-3-70B-Instruct`
- `CodeContests_Llama-3-8B-Instruct`

The ideal regime is medium base accuracy where:

```text
P(BoN correct, SC wrong) > 0
P(SC correct, BoN wrong) > 0
```

### 3. Mine Calibration Examples By Selector Disagreement

The synthetic result says random calibration is wasteful. The real benchmark should explicitly compare:

- random calibration problems,
- high entropy problems,
- verifier/SC disagreement problems,
- high coverage but low selector success problems.

### 4. Report Headroom Closure, Not Just Accuracy

Every result should report:

- any-correct coverage,
- best base selector,
- CSS accuracy,
- oracle-switch accuracy,
- percentage of oracle-switch headroom closed.

Without headroom, a tiny accuracy gain is impossible to interpret.

## Current Verdict

This is now a real research direction, but still early.

What is solid:

- The framing is clean.
- The synthetic stress tests expose useful failure modes.
- The Monkey Business benchmark gives real repeated-sampling evidence.
- MATH shows a small held-out gain over self-consistency.
- GSM8K gives an honest negative case that sharpens the scope.

What is not solved:

- The verifier is too weak.
- The real gains are small so far.
- The router is binary; a real system should route over a larger selector portfolio.
- The benchmark needs more configs and stronger selectors before this becomes a paper-grade empirical story.

The next best shot is to combine Monkey Business rollouts with a better verifier, then evaluate CSS in the medium-accuracy, high-disagreement regime.

## References

- Scaling Intelligence. [Monkey Business dataset](https://huggingface.co/datasets/ScalingIntelligence/monkey_business).
- Brown et al., 2024. [Large Language Monkeys: Scaling Inference Compute with Repeated Sampling](https://arxiv.org/abs/2407.21787).
- Snell et al., 2024. [Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters](https://arxiv.org/abs/2408.03314).
- Dorner et al., 2025. [ROC-n-reroll: How verifier imperfection affects test-time scaling](https://arxiv.org/abs/2507.12399).
- Shyamal et al., 2026. [SCATR: Simple Calibrated Test-Time Ranking](https://arxiv.org/abs/2604.16535).
