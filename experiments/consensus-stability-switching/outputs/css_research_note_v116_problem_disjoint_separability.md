# v116 Problem-Disjoint Router Separability Audit

## Question

v115 showed that adding a same-feature candidate-correctness head does not make the problem-disjoint auxiliary router safe. v116 asks a sharper diagnostic question:

> Do the available scores actually separate recovery candidates from regression candidates on held-out problem-disjoint rows?

If the answer were "no," the router family would be dead without new features. If the answer is "partly," the right conclusion is subtler: there is signal, but the tail/regression calibration is not good enough for deployment.

## Setup

This audit uses the same live branch as v115:

- Target: MATH/Gemma.
- Auxiliary: MATH/Llama.
- Scope: `pool_all`.
- Split: v114/v115 problem-disjoint source calibration, held-out seed evaluation.

No policy threshold is selected on the target. The script only computes held-out AUCs for ranking:

- true recovery candidates: `baseline_correct == false` and `policy_correct == true`,
- true regression candidates: `baseline_correct == true` and `policy_correct == false`,
- candidate-correct AUC: `policy_correct` vs not,
- baseline-preservation AUC: among baseline-correct rows, policy-correct vs policy-wrong.

Artifacts:

- [`cross_seed_router_separability_v116.md`](cross_seed_router_separability_v116.md)
- [`cross_seed_router_separability_v116.csv`](cross_seed_router_separability_v116.csv)
- [`cross_seed_router_separability_v116_aggregate.csv`](cross_seed_router_separability_v116_aggregate.csv)
- [`cross_seed_router_separability_audit.py`](cross_seed_router_separability_audit.py)

## Main Result

The same-feature scores are not random, but they are not sharp enough for low-regression problem-disjoint calibration.

Aggregate held-out AUCs:

| score | recovery-vs-regression AUC | candidate-correct AUC | baseline-preservation AUC |
|---|---:|---:|---:|
| `utility_head` | `0.711` | `0.802` | `0.839` |
| `correctness_head` | `0.710` | `0.825` | `0.825` |
| `candidate_ratio_gap` | `0.699` | `0.772` | `0.773` |
| `other_conf` | `0.680` | `0.826` | `0.836` |
| `margin_gap` | `0.623` | `0.599` | `0.646` |

The weak fold matters. Held-out seed `60602` has poor recovery-vs-regression separation:

| score | seed 60602 recovery-vs-regression AUC |
|---|---:|
| `utility_head` | `0.597` |
| `correctness_head` | `0.653` |
| `other_conf` | `0.547` |
| `margin_gap` | `0.549` |
| `candidate_ratio_gap` | `0.680` |

So v115 did not fail because every feature is useless. It failed because moderate average ranking plus a weak held-out fold and overlapping regression tails is not enough to select a source threshold that stays low-regression.

## Interpretation

This narrows the next-step requirement.

The current same-feature router has:

- enough signal to recover many Gemma failures when Llama agrees or is confident,
- enough candidate-correctness signal to rank generally correct candidates,
- but not enough calibrated tail separation to protect already-correct baselines under problem-disjoint held-out evaluation.

That means another threshold sweep is unlikely to be the breakthrough. The next useful experiment needs a new regression-risk signal, especially for already-correct baseline cases:

- generator logprobs or token-level confidence,
- hidden-state / representation agreement,
- stronger answer-equivalence normalization,
- proof/process labels over cluster rationales,
- or a third/fourth generator trace so routing can distinguish "Llama is genuinely rescuing Gemma" from "Llama is confidently dragging Gemma off a correct answer."

## Updated Claim

The auxiliary-generator branch is not dead; the same-feature calibration family is.

> Current surface features rank recoveries above regressions at about AUC `0.70`, but this is insufficient for safe problem-disjoint source-threshold transfer. The frontier now needs new regression-risk evidence, not more threshold surgery.
