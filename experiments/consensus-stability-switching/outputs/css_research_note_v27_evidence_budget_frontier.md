# v27 Evidence-Budget Adjusted Frontier

## Question

v21 projected adaptive top-20 verifier gains under assumed verifier success. v25/v26 showed compact prompts are cheaper and usually preserve trace-correct representatives. The remaining question is:

> If compact prompts expose trace-correct evidence only about 90% of the time, does the deployed projection collapse?

## Setup

Script: `work/evidence_budget_frontier.py`.

Inputs:

- `outputs/adaptive_depth_frontier.csv`
- `outputs/packet_representative_visibility.csv`

I take the `depth=20`, `20%` invoke frontier and adjust recoverable invoked cases by observed representative visibility:

- compact: correct-cluster top1 representative is trace-correct,
- full: correct-cluster top2 representative is trace-correct.

This is a conservative sensitivity check, not a measured verifier run.

## Result

| dataset | scenario | evidence rate | projected acc | delta |
|---|---|---:|---:|---:|
| MATH/Llama | compact perfect | 0.926 | 0.563 | +0.113 |
| MATH/Llama | compact 80%, 2% false-regress | 0.926 | 0.539 | +0.089 |
| MATH/Llama | full perfect | 1.000 | 0.572 | +0.122 |
| MATH/Llama | full 80%, 2% false-regress | 1.000 | 0.546 | +0.096 |
| MATH/Gemma | compact perfect | 0.900 | 0.357 | +0.119 |
| MATH/Gemma | compact 80%, 2% false-regress | 0.900 | 0.332 | +0.093 |
| MATH/Gemma | full perfect | 0.975 | 0.367 | +0.128 |
| MATH/Gemma | full 80%, 2% false-regress | 0.975 | 0.340 | +0.101 |

Report: `outputs/evidence_budget_frontier.md`.

## Interpretation

Compact evidence does not collapse the projection. Under the conservative 80% success / 2% false-regression assumption at 20% invoke:

```text
MATH/Llama full -> compact: 0.546 -> 0.539
MATH/Gemma full -> compact: 0.340 -> 0.332
```

That is a small cost for roughly halving prompt size. It strengthens the practical method:

1. run compact diverse top-20 prompts first,
2. rerun full prompts on compact failures,
3. attribute compact-only failures to evidence budget,
4. attribute failures that survive full prompts to verifier weakness or genuinely misleading clusters.

## Caveat

This still assumes verifier success conditional on visible evidence. The next necessary result is a real external/local verifier run on compact diverse prompts.
