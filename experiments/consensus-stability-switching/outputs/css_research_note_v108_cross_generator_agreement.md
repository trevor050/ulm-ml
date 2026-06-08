# v108: Cross-Generator Agreement Boundary

## Question

After v105-v107 exhausted several cheap local selector variants, v108 tests a materially different source of evidence:

> If another generator independently samples the same problem, can answer agreement across generator traces rescue selector misses?

This is not another threshold over the same semantic scorer. It uses the existing MATH/Llama and MATH/Gemma traces on the same `128` problems, trains the usual lightweight candidate verifier separately for each generator, then compares target-only `cluster_sum` against policies that use the other generator's answer frontier.

## Policies

For each held-out target trial at `N=128`, the audit samples an independent `N=128` trial from the other generator on the same problem.

It tests:

- `other_cluster_sum`: choose the other generator's `cluster_sum` answer,
- `target_intersection_top{k}`: choose the highest target cluster whose answer also appears in the other generator's top-k answer clusters, otherwise keep target `cluster_sum`,
- `other_intersection_top{k}`: choose the highest other cluster whose answer appears in the target top-k, otherwise keep target `cluster_sum`,
- `union_rank_top{k}`: simple rank/support union over both generators' top-k answer frontiers.

Run config:

- `3` split seeds: `60601,60602,60603`,
- `74` held-out problems per seed,
- `8` trials per problem,
- `592` trials per target/direction/seed,
- problem-bootstrap delta CIs with `250` rounds per seed.

## Result

Cross-generator agreement is real, but asymmetric and not yet a conservative deployed method.

| target | other | policy | mean delta | seeds positive | recoveries | regressions | read |
|---|---|---:|---:|---:|---:|---:|---|
| Gemma | Llama | `other_cluster_sum` | `+0.207` | `3/3` | `463` | `95` | strong but mostly "use the stronger generator" |
| Gemma | Llama | `union_rank_top3` | `+0.151` | `3/3` | `322` | `53` | large ensemble signal, regression-heavy |
| Gemma | Llama | `target_intersection_top10` | `+0.042` | `3/3` | `81` | `6` | low-regression target-only rerank signal |
| Gemma | Llama | `target_intersection_top20` | `+0.034` | `3/3` | `66` | `5` | smaller, lower-regression target-only signal |
| Llama | Gemma | `union_rank_top3` | `-0.040` | `0/3` | `37` | `108` | negative transfer |
| Llama | Gemma | `other_cluster_sum` | `-0.215` | `0/3` | `87` | `468` | choosing weaker generator is bad |

The per-seed CIs sharpen the read. For Gemma target with Llama as the auxiliary trace:

- `target_intersection_top10` deltas are `+0.059`, `+0.044`, `+0.024`; the first two seed CIs have positive lower bounds, the third crosses slightly below zero.
- `target_intersection_top20` deltas are `+0.041`, `+0.042`, `+0.020`; again, the third seed crosses slightly below zero.
- `union_rank_top3` has positive CIs in all three seeds but regresses `53` already-correct Gemma baseline trials.

For Llama target with Gemma as auxiliary, every non-baseline policy is negative on mean. Even the best non-baseline aggregate, `union_rank_top3`, is `-0.040` with `108` regressions against `37` recoveries.

No positive no-regression policy appears; the only no-regression rows are the do-nothing `target_cluster_sum` baselines.

## Read

v108 is a useful boundary, not a solved method.

Positive part:

> A stronger/diverse generator trace can expose missing answer evidence. For Gemma, Llama agreement over target clusters gives a small low-regression rerank signal, and full trace-union policies give large raw gains.

Negative part:

> Cross-generator agreement is directional and regression-prone. It helps when the auxiliary generator is stronger; it hurts when the auxiliary generator is weaker. Without calibration, it is not a verifier replacement.

The reviewer-resistant framing is:

- Diverse generation is a real competing budget axis and should be reported as a control.
- The adaptive-depth verifier story survives because naive trace-union/agreement does not produce a conservative bidirectional deployed policy.
- The most interesting next version would combine phase diagnostics with generator choice: spend on a second generator only when its trace regime is stronger for the target problem family, otherwise spend on depth verification.

## Artifacts

- `outputs/cross_generator_agreement_v108.md`
- `outputs/cross_generator_agreement_v108.csv`
- `outputs/cross_generator_agreement_v108_aggregate.csv`
- `work/cross_generator_agreement_audit.py`
- `outputs/cross_generator_agreement_audit.py`

## Reproduction

```bash
python3 work/cross_generator_agreement_audit.py \
  --n 128 \
  --trials-per-problem 8 \
  --seeds 60601,60602,60603 \
  --verifier-train-problems 30 \
  --audit-holdout-gap 24 \
  --verifier-samples-per-problem 800 \
  --bootstrap-rounds 250 \
  --output-prefix cross_generator_agreement_v108
```
