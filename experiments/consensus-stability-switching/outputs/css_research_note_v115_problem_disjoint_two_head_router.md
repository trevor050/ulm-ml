# v115 Problem-Disjoint Two-Head Router Control

## Question

v114 showed a sharp split:

- The Gemma-with-Llama auxiliary-generator router still recovers many failures after excluding source rows whose problem ids appear in the held-out seed.
- But the learned source threshold no longer controls held-out regressions. The v114 learned `pool_all` row has `+0.097` delta at source budget 0, but already has `20` held-out regressions.

v115 asks whether a simple second head can fix that.

## Setup

The v115 router uses the same problem-disjoint source split as v114. For each held-out seed:

- Test rows are all rows from the held-out seed.
- Source rows are the other two seeds.
- Training/threshold rows remove every source row whose `pid` appears in the held-out seed.

The live branch is Gemma target with Llama auxiliary, `pool_all`, because that is the only branch v109-v114 kept alive.

Modes:

- `utility_only`: v114 learned utility head, reproduced as a control.
- `correctness_only`: a new logistic head trained on all changed source rows to predict whether the candidate policy answer is correct.
- `two_head`: require both utility score and correctness score to pass source-selected thresholds; select by utility.
- `two_head_correctness_tiebreak`: same thresholds, but select by correctness first.

Thresholds are selected on problem-disjoint source rows under source regression budgets `0,1,2,5,10,20`. No target thresholds or target labels are used.

Artifacts:

- [`cross_seed_router_two_head_control_v115.md`](cross_seed_router_two_head_control_v115.md)
- [`cross_seed_router_two_head_control_v115.csv`](cross_seed_router_two_head_control_v115.csv)
- [`cross_seed_router_two_head_control_v115_aggregate.csv`](cross_seed_router_two_head_control_v115_aggregate.csv)
- [`cross_seed_router_two_head_control.py`](cross_seed_router_two_head_control.py)

## Main Result

The correctness head does not repair problem-disjoint regression control.

For Gemma with Llama auxiliary:

| mode | source budget | mean delta | v114 learned | recoveries | held-out regressions |
|---|---:|---:|---:|---:|---:|
| `utility_only` | 0 | `+0.097` | `+0.097` | 192 | 20 |
| `correctness_only` | 0 | `+0.102` | `+0.097` | 204 | 23 |
| `two_head` | 0 | `+0.098` | `+0.097` | 194 | 20 |
| `two_head_correctness_tiebreak` | 0 | `+0.098` | `+0.097` | 194 | 20 |
| `utility_only` | 2 | `+0.118` | `+0.118` | 240 | 30 |
| `correctness_only` | 2 | `+0.106` | `+0.118` | 216 | 27 |
| `two_head` | 2 | `+0.108` | `+0.118` | 217 | 26 |
| `two_head_correctness_tiebreak` | 2 | `+0.112` | `+0.118` | 223 | 24 |
| `utility_only` | 5 | `+0.131` | `+0.131` | 271 | 39 |
| `two_head_correctness_tiebreak` | 5 | `+0.137` | `+0.131` | 280 | 36 |

No v115 row has at most five held-out regressions. The two-head rows sometimes improve mean delta slightly at moderate budgets, but they do so while staying deep in the same regression-heavy regime.

## Interpretation

This is a negative result, but a useful one.

The failure is now narrower:

1. v109-v111 show the Gemma-with-Llama auxiliary signal is real under cross-seed transfer and not reproduced by source-label placebo.
2. v112 shows tie-safe simple heuristics do not explain that signal.
3. v113 shows learned routing is the best overlap-allowed low-regression frontier.
4. v114 shows problem-disjoint source calibration preserves recovery but breaks low-regression safety.
5. v115 shows a same-feature candidate-correctness head does not fix the safety break.

So the next router should not be another same-feature threshold variant. It needs new information about regression risk:

- candidate logprobs or confidence from the original generator,
- hidden-state or verifier embeddings,
- symbolic equivalence / answer-normalization features,
- process/proof labels over the actual cluster rationales,
- or additional generator traces beyond this two-model pair.

## Claim Boundary

v115 does not kill auxiliary-generator routing. It kills the easy rescue where a second same-feature correctness head makes v114 deployably safe.

The current honest claim is:

> Auxiliary-generator routing has real recovery signal on hard MATH/Gemma failures, but current surface features cannot calibrate low-regression problem-disjoint deployment. The method needs a new regression-risk signal, not more threshold surgery.
