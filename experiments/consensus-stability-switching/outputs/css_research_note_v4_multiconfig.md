# Candidate-Set Selector Switching, Multi-Config Evidence

**Status:** v4 research note, June 1, 2026  
**Main update:** CSS has now been tested on four real repeated-sampling configurations from `ScalingIntelligence/monkey_business`, not just one GSM8K/MATH pair.

![Multi-config CSS plot](monkey_css_multiconfig_plot.svg)

## Short Claim

Repeated sampling creates a large **selectability gap**: correct answers are present in the candidate set far more often than current selectors recover them. Candidate-Set Selector Switching (CSS) is a lightweight router over selector portfolios. It helps only when the portfolio contains selectors with complementary errors.

That last sentence is the important correction. CSS is not a universal replacement for self-consistency. It is a diagnostic and routing layer for test-time scaling systems.

## Real Benchmark Setup

Dataset: [ScalingIntelligence/monkey_business](https://huggingface.co/datasets/ScalingIntelligence/monkey_business), released with *Large Language Monkeys*.

Configs tested:

- `GSM8K_Llama-3-8B-Instruct`
- `MATH_Llama-3-8B-Instruct`
- `MATH_Gemma-2B`
- `MATH_Pythia-1B`

Each config has 10,000 samples per problem plus correctness labels. The benchmark splits by problem:

- train problems for a cheap candidate verifier,
- separate calibration problems for CSS,
- held-out test problems for evaluation.

Selectors:

- first sample,
- verifier Best-of-N,
- support-weighted verifier,
- self-consistency,
- margin gate,
- CSS router,
- oracle switch,
- any-correct coverage.

Implementation:

- [monkey_css_realbench.py](monkey_css_realbench.py)
- [aggregate_monkey_results.py](aggregate_monkey_results.py)
- [render_multiconfig_svg.py](render_multiconfig_svg.py)

Main aggregate:

- [monkey_css_multiconfig_summary.md](monkey_css_multiconfig_summary.md)
- [monkey_css_multiconfig_summary.csv](monkey_css_multiconfig_summary.csv)

## Multi-Config Results

| config | first | BoN | hybrid | SC | CSS | oracle | any-correct | CSS-SC | selectability gap | headroom closed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GSM8K_Llama-3-8B-Instruct | 0.777 | 0.789 | 0.828 | 0.846 | 0.849 | 0.871 | 0.973 | +0.002 | 0.127 | 0.093 |
| MATH_Llama-3-8B-Instruct | 0.295 | 0.289 | 0.325 | 0.398 | 0.403 | 0.437 | 0.691 | +0.006 | 0.293 | 0.141 |
| MATH_Gemma-2B | 0.102 | 0.122 | 0.145 | 0.181 | 0.177 | 0.216 | 0.481 | -0.004 | 0.300 | -0.113 |
| MATH_Pythia-1B | 0.010 | 0.015 | 0.015 | 0.012 | 0.012 | 0.023 | 0.150 | +0.001 | 0.135 | -0.407 |

High-N slice:

| config | N | SC | CSS | oracle | any-correct |
|---|---:|---:|---:|---:|---:|
| GSM8K_Llama-3-8B-Instruct | 128 | 0.849 | 0.851 | 0.875 | 1.000 |
| MATH_Llama-3-8B-Instruct | 128 | 0.438 | 0.451 | 0.474 | 0.852 |
| MATH_Gemma-2B | 128 | 0.211 | 0.209 | 0.250 | 0.725 |
| MATH_Pythia-1B | 128 | 0.010 | 0.010 | 0.022 | 0.314 |

## Interpretation

### 1. The Selectability Gap Is Real

The strongest result is not CSS's raw gain. It is the gap between any-correct coverage and selector accuracy.

At `N=128`:

- GSM8K/Llama has any-correct coverage 1.000 while SC is 0.849.
- MATH/Llama has any-correct coverage 0.852 while SC is 0.438.
- MATH/Gemma-2B has any-correct coverage 0.725 while SC is 0.211.
- MATH/Pythia-1B has any-correct coverage 0.314 while SC is 0.010.

That means repeated sampling often already contains useful work. Selection is the bottleneck.

### 2. CSS Helps In The Medium-Accuracy, Complementary-Selector Regime

The best current case is `MATH_Llama-3-8B-Instruct`.

With 32 random candidate-set trials per held-out problem per N:

- overall SC: 0.398
- overall CSS: 0.403
- overall oracle switch: 0.437
- CSS closes 14.1% of oracle-switch headroom

At `N=128`:

- SC: 0.438
- CSS: 0.451
- oracle switch: 0.474
- any-correct: 0.852

This is a small but real held-out gain on real repeated-sampling traces. It is also exactly the regime the theory predicts: base success is not saturated, but selectors have enough signal to make routing possible.

### 3. CSS Fails When The Selector Portfolio Is Bad

`MATH_Gemma-2B` is the most important negative case. It has high any-correct coverage, 0.725 at N=128, but CSS underperforms SC. That means the current cheap verifier and router do not extract the available signal.

This is not a cosmetic caveat. It is the main research obstacle.

The lesson:

> CSS is only as useful as the diversity and quality of its selector portfolio.

If the alternative selector is weak in the wrong way, routing can hurt.

### 4. Extremely Low-Accuracy Regimes Are Mostly Diagnostic

`MATH_Pythia-1B` has any-correct coverage 0.314 at N=128, but all selectors remain near zero. This suggests candidate correctness exists but is too sparse/noisy for the current text-feature verifier and answer clustering to recover.

This is where stronger verifiers, execution, or model-internal features are necessary.

## What Changed In The Research Pitch

Earlier versions sounded too much like "CSS is a new selector that beats Best-of-N and self-consistency." The real evidence says something subtler and better:

1. Test-time scaling needs **selector diagnostics**: any-correct coverage, oracle-switch headroom, selector disagreement, and headroom closure.
2. CSS is a **router**, not a standalone selector.
3. It helps in medium-accuracy regimes with complementary selector errors.
4. It fails in regimes where the selector portfolio lacks a useful alternative to self-consistency.
5. The next-order research problem is building better selector portfolios, then routing between them.

That is more reviewer-resistant than a single happy table.

## Current Method Details

The current candidate verifier is intentionally cheap:

- text length,
- word count,
- line count,
- number count,
- presence/location of final answer,
- arithmetic consistency of `<<expr=result>>` snippets when available.

The support-weighted verifier adds a small bonus to candidates whose final-answer cluster has support in the candidate set.

CSS features include:

- verifier top-answer support,
- majority-answer support,
- answer entropy,
- whether verifier top answer matches majority answer,
- score margin,
- normalized top score,
- normalized self-consistency score,
- sample budget,
- unique-answer ratio.

The router is logistic regression trained on calibration candidate sets, with disagreement-mined ordering.

## Strongest Next Experiments

### Stronger Verifier

The current verifier is too weak. The next serious run should replace or augment it with:

- local LLM judge scores,
- PRM-style reward scores,
- logprob scores,
- SCATR-like hidden-state features,
- symbolic or execution-based checkers where possible.

Prediction: CSS gains should grow when the verifier sometimes beats SC but also has identifiable failure cases.

### Larger Selector Portfolio

Binary routing is too narrow. A real selector portfolio should include:

- SC,
- verifier BoN,
- support-weighted verifier,
- margin gate,
- entropy-conditioned SC,
- cluster-level verifier,
- possibly minimum-risk selection over answer clusters.

### More Configs

Priority Monkey Business configs:

- `MATH_Gemma-7B`
- `MATH_Llama-3-70B-Instruct`
- `CodeContests_Llama-3-8B-Instruct`
- `MiniF2F-MATH_Llama-3-8B-Instruct`

The target is not every benchmark. The target is finding the selector-complementarity regime.

## Verdict

This is now a legitimate research direction, not just a toy idea.

The empirical story is still early and the gains are small, but the work has:

- a clear problem definition,
- real repeated-sampling traces,
- positive and negative benchmark cases,
- a measurable headroom framework,
- a plausible path to stronger results.

The honest paper title is probably not "CSS Solves Test-Time Scaling." It is closer to:

> **Selector Reliability Is A Bottleneck In Test-Time Scaling**

CSS is the first small probe in that direction.

## References

- Scaling Intelligence. [Monkey Business dataset](https://huggingface.co/datasets/ScalingIntelligence/monkey_business).
- Brown et al., 2024. [Large Language Monkeys: Scaling Inference Compute with Repeated Sampling](https://arxiv.org/abs/2407.21787).
- Snell et al., 2024. [Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters](https://arxiv.org/abs/2408.03314).
- Dorner et al., 2025. [ROC-n-reroll: How verifier imperfection affects test-time scaling](https://arxiv.org/abs/2507.12399).
- Shyamal et al., 2026. [SCATR: Simple Calibrated Test-Time Ranking](https://arxiv.org/abs/2604.16535).
