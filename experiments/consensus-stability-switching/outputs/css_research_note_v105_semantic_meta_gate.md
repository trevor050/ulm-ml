# v105: Semantic Meta-Gate Boundary

## Question

v103 and v104 left one remaining cheap-semantic objection:

> Maybe the scorer is not doomed; maybe one-dimensional threshold fallback is too weak.

v105 tests a richer policy class without changing the underlying scorer. It trains a multifeature target-style accept/fallback gate over existing v103/v104 raw predictions, then evaluates on held-out expanded Gemma packets under the same natural-rate deployed delta and lower-CI-positive decision rule.

## Gate

For each target calibration split, the gate sees semantic prediction features:

- confidence, semantic probability, semantic margin,
- selected rank/support,
- rank/support interactions,
- whether the semantic answer matches the baseline answer,
- top-3/top-5/top-10 selected-rank indicators.

The training label is utility-style: accept semantic prediction when it improves over baseline fallback, reject when it would regress a baseline-correct packet. Neutral rows are ignored for fitting. The chosen calibration threshold must have zero calibration regressions.

## Harness

Generated artifacts:

- `outputs/semantic_meta_gate_v105.md`
- `outputs/semantic_meta_gate_v105.csv`
- `work/semantic_meta_gate_audit.py`
- `outputs/semantic_meta_gate_audit.py`

Inputs:

- 6 matched v103 skinny raw prediction files,
- 6 v104 rich raw prediction files,
- expanded Gemma target packet set from v103,
- target calibration sizes: `1,2,4,8,16,24,all`,
- bootstrap rounds: `250`.

## Result

The multifeature meta-gate still does not produce a conservative held-out deployed policy.

| family | source | rows | target-cal CI+ | point+ | clean point+ | oracle CI+ | best clean | best oracle |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v103 skinny | pooled | 21 | 0 | 11 | 11 | 0 | +0.007, baseline 24/24 | +0.007, baseline 24/24 |
| v103 skinny | unique | 21 | 0 | 14 | 13 | 0 | +0.008, baseline 40/40 | +0.011, baseline 24/24 |
| v104 rich | pooled | 21 | 0 | 10 | 5 | 2 | +0.004, baseline 46/46 | +0.029, baseline 22/24 |
| v104 rich | unique | 21 | 0 | 9 | 6 | 0 | +0.004, baseline 40/40 | +0.014, baseline 24/24 |

The best target-calibrated point estimate is not clean: v104 pooled seed `60602`, `all` calibration gives `+0.023`, but preserves only `23/24` baseline-correct packets and has CI low `-0.005`. The best clean calibrated estimate is tiny: v103 unique seed `60603`, calibration `8/category`, `+0.008`, CI low `0.000`, `2/120` recoverable correctness, baseline `40/40`.

Diagnostic oracle gates can be more active, especially on v104 pooled predictions, but still do not give a clean deployed story. Best oracle is `+0.029` with CI low `-0.007`, `9` recoveries, and baseline `22/24`.

## Read

v105 closes the obvious "use a better gate" objection for the current cheap semantic family:

> A multifeature target-calibrated accept/fallback gate can find small point-positive rows, but it still cannot estimate a held-out lower-CI-positive deployed policy.

This matters because the negative stack is now not just:

- not enough source calibration,
- not enough small target calibration,
- not enough expanded duplicated target calibration,
- not enough local hashed text,
- not enough one-dimensional thresholding.

It is a broader boundary: the current cheap hashed semantic scorer plus conservative regression control is too weak. The next semantic route needs a material new signal source or verifier class: logprobs, hidden states, symbolic equivalence checks, proof/process features, a stronger model endpoint, or a genuinely different policy family.

## Caveats

- v105 is still target-style calibration, not a zero-label deployable method.
- The gate is a compact pilot over the matched expanded-Gemma setup, not every source/target direction.
- The oracle rows are diagnostic only because thresholds are selected on held-out target labels.
- Metrics intentionally reuse the existing deployed-mix scoring semantics for consistency with v45/v74/v103/v104.

## Reproduction

```bash
python3 work/semantic_meta_gate_audit.py \
  --raw-predictions \
    outputs/semantic_target_calibration_v103_problem_unique_llama_to_expanded_gemma_both_seed60601_raw_target_predictions.jsonl \
    outputs/semantic_target_calibration_v103_problem_unique_llama_to_expanded_gemma_both_seed60602_raw_target_predictions.jsonl \
    outputs/semantic_target_calibration_v103_problem_unique_llama_to_expanded_gemma_both_seed60603_raw_target_predictions.jsonl \
    outputs/semantic_target_calibration_v103_problem_pooled_llama_to_expanded_gemma_both_seed60601_raw_target_predictions.jsonl \
    outputs/semantic_target_calibration_v103_problem_pooled_llama_to_expanded_gemma_both_seed60602_raw_target_predictions.jsonl \
    outputs/semantic_target_calibration_v103_problem_pooled_llama_to_expanded_gemma_both_seed60603_raw_target_predictions.jsonl \
    outputs/semantic_target_calibration_v104_problem_unique_llama_to_expanded_gemma_rich_both_seed60601_raw_target_predictions.jsonl \
    outputs/semantic_target_calibration_v104_problem_unique_llama_to_expanded_gemma_rich_both_seed60602_raw_target_predictions.jsonl \
    outputs/semantic_target_calibration_v104_problem_unique_llama_to_expanded_gemma_rich_both_seed60603_raw_target_predictions.jsonl \
    outputs/semantic_target_calibration_v104_problem_pooled_llama_to_expanded_gemma_rich_both_seed60601_raw_target_predictions.jsonl \
    outputs/semantic_target_calibration_v104_problem_pooled_llama_to_expanded_gemma_rich_both_seed60602_raw_target_predictions.jsonl \
    outputs/semantic_target_calibration_v104_problem_pooled_llama_to_expanded_gemma_rich_both_seed60603_raw_target_predictions.jsonl \
  --test-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103.jsonl \
  --category-stats outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_expanded48_v103_category_stats.csv \
  --calibration-per-category 1,2,4,8,16,24,all \
  --bootstrap-rounds 250 \
  --output-prefix semantic_meta_gate_v105
```
