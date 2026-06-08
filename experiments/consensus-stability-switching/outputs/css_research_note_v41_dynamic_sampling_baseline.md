# v41 - Dynamic Extra-Sampling Baseline

**Status:** June 1, 2026. Trace-only baseline against the "just sample more, but adaptively" objection.

## Question

v36 already showed that fixed N=128 -> 1024 mostly increases hidden coverage while barely moving `cluster_sum`.

The stronger objection is:

> Fixed extra sampling is dumb. What if we allocate extra samples only to problems that look uncertain after N=128?

v41 tests that without a model endpoint by using the already-downloaded Monkey Business traces.

## Setup

Script:

```text
work/dynamic_sampling_baseline.py
```

Outputs:

```text
outputs/dynamic_sampling_baseline.md
outputs/dynamic_sampling_baseline.csv
```

For each MATH trace:

1. Train the same cheap candidate verifier used by the local `cluster_sum` selector.
2. Start every held-out problem at N=128.
3. Use base-N cluster statistics to decide where extra generation chunks should go.
4. Allocate extra samples in 128-sample chunks up to max N=1024.
5. Recompute deployed `cluster_sum`, not just any-correct coverage.

Policies:

- `fixed_uniform`: arbitrary/uniform chunk allocation at the same chunk budget.
- `dynamic_entropy`: prioritize high answer entropy at N=128.
- `dynamic_low_margin`: prioritize low normalized cluster-score margin.
- `dynamic_low_top_share`: prioritize low top-cluster score share.
- `learned_hidden_gain`: train a tiny logistic policy on calibration problems to predict whether max-N sampling fixes a base `cluster_sum` miss.
- `oracle_hidden_gain`: upper bound that knows which problems become `cluster_sum`-correct at max N.

## Results

The important read is that uncertainty-targeted extra generation mostly increases coverage, not deployed selection.

### MATH/Llama

Base `cluster_sum` is `0.446`, base any-correct is `0.851`.

| target extra samples/problem | best non-oracle policy by `cluster_sum` | `cluster_sum` delta | best any-correct delta | extra sample tokens/problem |
|---:|---|---:|---:|---:|
| 32 | entropy / low top share | +0.000 | +0.027 | about 5.2k |
| 64 | none | -0.014 | +0.054 | about 9.8k |
| 128 | all tied | +0.000 | +0.054 | about 16.0k |
| 384 | all tied | +0.000 | +0.068 | about 48.8k |
| 896 | all tied | +0.000 | +0.095 | about 114.4k |

The learned hidden-gain policy does not help on Llama; it behaves like arbitrary allocation because calibration has no useful positive signal. Even the `oracle_hidden_gain` allocation cannot improve deployed `cluster_sum` here because the extra samples add correct coverage without moving the cheap selected cluster.

### MATH/Gemma

Base `cluster_sum` is `0.216`, base any-correct is `0.730`.

| target extra samples/problem | best non-oracle policy by `cluster_sum` | `cluster_sum` delta | best any-correct delta | extra sample tokens/problem |
|---:|---|---:|---:|---:|
| 32 | low margin | +0.027 | +0.041 | about 4.5k |
| 64 | entropy / low margin / low top share | +0.027 | +0.041 | about 9.4k |
| 128 | all tied | +0.041 | +0.054 | about 17.2k |
| 192 | entropy | +0.041 | +0.081 | about 27.1k |
| 384 | all tied | +0.027 | +0.149 | about 53.9k |
| 896 | all tied | +0.041 | +0.149 | about 126.4k |

The learned hidden-gain policy ties or trails the simple uncertainty heuristics. Gemma gets small deployed-selector improvements, but they remain far below the projected rank-bucket verification deltas from v33 (`+0.194 +/- 0.024` at 1024 verifier tokens/problem).

## Interpretation

This is a real strengthening of the budget argument.

The dynamic-sampling objection says early uncertainty should tell us where to generate more. In these traces, early uncertainty can buy more any-correct coverage, but the selected `cluster_sum` answer barely improves. That supports the central claim: the bottleneck is not only coverage, it is selectability.

This still does not prove adaptive verification end-to-end. The rank-bucket gains are projected until the external/local verifier run exists. But v41 makes the alternative baseline work harder:

```text
extra generation has to improve realized selection, not just create hidden correct answers
```

## Caveats

- The baseline uses fixed trace prefixes rather than fresh random generations.
- Extra generation is allocated in coarse 128-sample chunks.
- Heuristic dynamic scores are simple answer-cluster uncertainty features, not a learned dynamic-SC model.
- The learned hidden-gain policy is tiny and trained on only 24 calibration problems per dataset; it is a pressure test, not a tuned dynamic-SC baseline.
- The candidate verifier is still the cheap text-feature verifier.
- This is held-out trace evidence, not a model-runtime benchmark.

## Verification

```bash
python3 work/test_dynamic_sampling_baseline.py
python3 work/dynamic_sampling_baseline.py \
  --output-prefix dynamic_sampling_baseline \
  --avg-extra-samples 32,64,128,192,384,896
```

Both commands passed locally.
