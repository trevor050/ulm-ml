# v28 Cost-Aware Verifier Cascade

## Question

v27 says compact evidence does not collapse projected accuracy. The next reviewer question is cost:

> Does the proposed compact-first/full-fallback verifier policy buy enough accuracy per token to be a real test-time scaling method?

## Setup

Script: `work/cost_aware_verifier_cascade.py`.

Inputs:

- `outputs/adaptive_depth_frontier.csv`
- `outputs/packet_representative_visibility.csv`
- compact diverse top-20 prompt JSONL files,
- full diverse top-20 prompt JSONL files.

I use the same `depth=20`, `20%` invoke, `80%` success / `2%` false-regression assumption as v27. Prompt token cost is estimated as `chars / 4`.

The cascade row is deliberately labeled as a lower-bound diagnostic: run compact prompts on every invoked case, then run full prompts only when compact top-1 evidence is missing but full top-2 evidence exists. A real verifier still needs to expose an uncertainty signal before this becomes an implementable fallback policy.

## Result

| dataset | policy | projected acc | delta | chars/problem | est tokens/problem | fallback share of invoked |
|---|---|---:|---:|---:|---:|---:|
| MATH/Llama | compact only | 0.539 | +0.089 | 1899 | 475 | 0.000 |
| MATH/Llama | full only | 0.546 | +0.096 | 3697 | 924 | 1.000 |
| MATH/Llama | compact then evidence-gap full | 0.546 | +0.096 | 2065 | 516 | 0.045 |
| MATH/Gemma | compact only | 0.332 | +0.093 | 1817 | 454 | 0.000 |
| MATH/Gemma | full only | 0.340 | +0.101 | 3411 | 853 | 1.000 |
| MATH/Gemma | compact then evidence-gap full | 0.340 | +0.101 | 1985 | 496 | 0.049 |

Report: `outputs/cost_aware_verifier_cascade.md`.

## Interpretation

The practical pitch is now cleaner:

```text
Detect unreliable cluster_sum decisions.
Inspect top-20 answer clusters with compact evidence first.
Use full evidence only as fallback when compact evidence appears insufficient.
Report deployed accuracy per average verifier-token budget.
```

The compact policy keeps most of the projected full-prompt gain at roughly half the prompt cost. The oracle evidence-gap cascade nearly matches full-prompt projected accuracy while using about `516` estimated verifier tokens/problem for Llama and `496` for Gemma, versus `924` and `853` for full-only.

This is not a measured verifier result. It is a sharper budget target for the external/local verifier run: the verifier should be evaluated not only by accuracy, but by whether its uncertainty can trigger full-prompt fallback on a small enough fraction of invoked cases.

## Caveat

The fallback row uses trace-key evidence visibility and therefore knows when compact evidence is missing. A real system must learn that signal from verifier confidence, disagreement, or rationale-level diagnostics.
