# v107: Process-Feature Cluster Scorer Boundary

## Question

v106 closed the dependency-light symbolic/answer-shape escape hatch after v105. v107 tests a related but more representative-process-specific signal family:

> Do low-dimensional process/proof-hygiene features make cluster selection or fallback calibration deployable?

The trace schema check found no stored logprobs or hidden-state metadata in the local Monkey Business JSONs. Raw traces expose `question`, `samples`, `is_corrects`, `gt_answer`, and source index fields; deployed packet JSONL files expose cluster support/score aggregates plus representative rationales. v107 therefore uses process signatures available from packet representatives rather than more hashed text.

## Harness

New script:

- `work/process_cluster_scorer.py`

The scorer trains a logistic cluster-correctness model over compact, interpretable features:

- cluster support/rank/verifier-score aggregates,
- baseline-answer match,
- representative length/line/number counts,
- arithmetic equation validity/invalidity via the existing `equation_stats`,
- boxed/final-answer hygiene,
- answer occurrence counts,
- simple process markers such as checking/substitution, guessing/trying, `therefore`, `however`, and repeated "I hope it is correct",
- the existing cheap candidate verifier surface features, aggregated over representatives.

It then selects the highest process-probability cluster and applies the same conservative source-calibrated fallback idea: choose a source calibration threshold with zero baseline-correct regressions, deploy to the target, and score natural-rate weighted `deployed_delta` with the v45 stratified bootstrap rule.

## Result

No process-feature policy clears the lower-CI-positive deployed rule.

| regime | direction | seed | accept | delta | 95% CI | decision |
|---|---|---:|---:|---:|---:|---|
| overlap_allowed | Gemma->Llama | 60601 | 0.132 | +0.000 | +0.000..+0.000 | uncertain_or_negative |
| overlap_allowed | Gemma->Llama | 60602 | 0.718 | -0.051 | -0.105..+0.002 | uncertain_or_negative |
| overlap_allowed | Gemma->Llama | 60603 | 0.306 | -0.045 | -0.090..+0.000 | uncertain_or_negative |
| overlap_allowed | Llama->Gemma | 60601 | 0.135 | +0.007 | +0.000..+0.021 | uncertain_or_negative |
| overlap_allowed | Llama->Gemma | 60602 | 0.109 | +0.007 | +0.000..+0.028 | uncertain_or_negative |
| overlap_allowed | Llama->Gemma | 60603 | 0.569 | +0.008 | -0.043..+0.054 | uncertain_or_negative |
| problem_disjoint | Gemma->Llama | 60601 | 0.242 | +0.000 | +0.000..+0.000 | uncertain_or_negative |
| problem_disjoint | Gemma->Llama | 60602 | 0.241 | -0.016 | -0.061..+0.027 | uncertain_or_negative |
| problem_disjoint | Gemma->Llama | 60603 | 0.892 | -0.033 | -0.105..+0.036 | uncertain_or_negative |
| problem_disjoint | Llama->Gemma | 60601 | 1.000 | +0.027 | +0.000..+0.059 | uncertain_or_negative |
| problem_disjoint | Llama->Gemma | 60602 | 0.118 | -0.017 | -0.060..+0.027 | uncertain_or_negative |
| problem_disjoint | Llama->Gemma | 60603 | 0.057 | +0.000 | +0.000..+0.000 | uncertain_or_negative |

The most encouraging row is problem-disjoint Llama->Gemma seed `60601`: it accepts all target packets and gets a point estimate `+0.027`, but the lower CI is exactly zero. The other Llama->Gemma rows are no-op, tiny point-positive, or negative; Gemma->Llama is flat or negative.

## Read

v107 is a useful negative boundary:

> Process/proof-hygiene features available in the current packet representatives show at most small, unstable point-positive signal. They do not produce a conservative, seed-stable, cross-model deployed policy.

This narrows the next viable local route again. The failure is no longer only "hashed semantic text is too weak." A low-dimensional symbolic/process proxy over representative rationales also fails the same deployed regression-control rule. The remaining material routes are:

- a stronger measured verifier endpoint,
- trace generation with stored token logprobs/hidden states/process rewards,
- richer symbolic equivalence/proof checking outside the current representative-only packet format,
- or a larger lower-duplication labeled panel if pursuing target-style calibration.

## Caveats

- Problem-disjoint overlap filtering leaves small source fit/calibration splits in the cross-model unique-source setting, especially because many source problem IDs overlap across Llama and Gemma assets.
- The script uses packet representatives, not every member sample in each answer cluster. The current packet files do not retain sample indices for reconstructing full cluster-member process statistics.
- This is a compact boundary test, not a proof that all process signals are useless. It says the process signals currently available from packet representatives are not enough.

## Reproduction

Problem-disjoint Llama->Gemma representative command:

```bash
python3 work/process_cluster_scorer.py \
  --train-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl \
  --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl \
  --category-stats outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98_category_stats.csv \
  --train-label Llama_unique32 \
  --test-label Gemma_unique16_rebuilt \
  --output-prefix process_cluster_v107_llama_to_gemma_seed60601 \
  --exclude-test-problems-from-train \
  --seed 60601 \
  --bootstrap-rounds 250
```

Reverse direction swaps source/target packet files and uses:

```bash
--category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32_category_stats.csv
```
