# v100: Split-Trained Semantic Threshold Audit

## Question

v99 found target-threshold headroom for raw semantic scores, but it trained on the full source packet set. v100 asks the sharper question:

> Under the same source fit/calibration split used by v98, does the split-trained scorer still have target-threshold headroom, or did v99 only work because full-source training leaked extra signal into the scorer?

This separates three objects:

1. raw semantic ranking signal,
2. split-trained scorer signal,
3. source-calibrated threshold transfer.

## Harness

New script:

- `work/semantic_split_threshold_audit.py`

The script uses the same source split as `work/semantic_risk_controlled_selector.py`:

1. split source packets by deployed-mix category into fit/calibration,
2. train the hashed semantic scorer on the fit split,
3. choose a v98-style source threshold on the source calibration split,
4. apply that threshold to the target packets,
5. independently choose a target-oracle threshold on the same raw target scores.

Aggregate artifact:

- `outputs/split_threshold_v100_policy_aggregate.csv`

The matrix covers the same three lower-duplication setups as v98/v99:

- balanced Llama -> rebuilt Gemma unique16,
- rebuilt Gemma unique16 -> Llama unique32,
- Llama unique32 -> rebuilt Gemma unique16,

with three feature modes, three seeds, and three score fields, giving `81` rows.

## Results

Target-oracle thresholding over split-trained scorers finds `5/81` lower-CI-positive rows.

Top target-oracle rows:

| setup | feature | score field | seed | oracle delta | CI | oracle recoverable | oracle baseline | source rec | source baseline | decision |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| rebuilt Gemma -> Llama unique32 | numeric | semantic probability | 60601 | +0.065 | +0.007..+0.134 | 7/36 | 27/30 | 6 | 27/30 | pass |
| rebuilt Gemma -> Llama unique32 | both | semantic probability | 60603 | +0.049 | +0.008..+0.098 | 4/36 | 30/30 | 3 | 30/30 | pass |
| balanced Llama -> rebuilt Gemma | numeric | semantic probability | 60601 | +0.044 | +0.011..+0.089 | 4/48 | 16/16 | 2 | 16/16 | pass |
| balanced Llama -> rebuilt Gemma | numeric | confidence | 60603 | +0.040 | +0.011..+0.085 | 4/48 | 16/16 | 6 | 12/16 | pass |
| balanced Llama -> rebuilt Gemma | numeric | semantic margin | 60603 | +0.040 | +0.011..+0.081 | 4/48 | 16/16 | 6 | 12/16 | pass |

Mean by setup:

| setup | rows | oracle mean delta | oracle max | oracle pass rows | source rec mean | oracle rec mean |
|---|---:|---:|---:|---:|---:|---:|
| balanced Llama -> rebuilt Gemma | 27 | +0.009 | +0.044 | 3 | 1.44 | 0.85 |
| rebuilt Gemma -> Llama unique32 | 27 | +0.020 | +0.065 | 2 | 1.26 | 1.89 |
| Llama unique32 -> rebuilt Gemma | 27 | +0.005 | +0.033 | 0 | 0.37 | 0.78 |

Mean by feature:

| feature | oracle mean delta | oracle max | oracle pass rows | source rec mean | oracle rec mean |
|---|---:|---:|---:|---:|---:|
| numeric | +0.020 | +0.065 | 4 | 2.00 | 2.00 |
| text | +0.005 | +0.035 | 0 | 0.52 | 0.59 |
| both | +0.009 | +0.049 | 1 | 0.56 | 0.93 |

There are `11` rows where target-oracle thresholding recovers at least two more target recoverable packets than the source-calibrated threshold. The largest gaps include:

| setup | feature | score field | seed | oracle rec - source rec | oracle delta |
|---|---|---|---:|---:|---:|
| rebuilt Gemma -> Llama unique32 | numeric | confidence | 60601 | 4 | +0.024 |
| rebuilt Gemma -> Llama unique32 | text | confidence | 60603 | 4 | +0.004 |
| rebuilt Gemma -> Llama unique32 | numeric | semantic margin | 60601 | 3 | +0.039 |
| rebuilt Gemma -> Llama unique32 | text | semantic probability | 60603 | 3 | +0.021 |
| Llama unique32 -> rebuilt Gemma | both | semantic probability | 60601 | 3 | +0.019 |

## Read

v100 sharpens v99:

> The lower-duplication raw semantic headroom survives source split training. The deployable failure is threshold transfer and baseline-risk calibration, not just full-source overfitting.

This is clearest in rebuilt Gemma -> Llama unique32. The numeric/probability split-trained row reaches target-oracle `+0.065` with `7/36` recoveries, but the source-threshold application still preserves only `27/30` already-correct target baselines. Another split-trained row (`both`/probability, seed `60603`) gets target-oracle `+0.049` with `4/36` recoveries and `30/30` baseline preservation.

The conclusion is still not a deployable method. The target-oracle threshold is selected on the target packet set. But it is now a precise next-experiment target:

1. learn or calibrate the accept/fallback threshold with more source calibration data,
2. add calibration features that predict target baseline-regression risk,
3. use held-out target-style calibration packets rather than a tiny source split,
4. test whether numeric cluster features alone are the stable semantic-risk core.

## Reproduction

Representative split-trained audit:

```bash
python3 work/semantic_split_threshold_audit.py \
  --train-packets outputs/cluster_packets_math_gemma2b_n128_deployed_mix_top20_unique16_rebuilt_v98.jsonl \
  --test-packets outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32.jsonl \
  --train-label Gemma_unique16_rebuilt_v98 \
  --test-label Llama_unique32 \
  --feature-mode numeric \
  --include-problem \
  --seed 60601 \
  --category-stats outputs/cluster_packets_math_llama_n128_deployed_mix_top20_unique32_category_stats.csv \
  --bootstrap-rounds 500 \
  --output-prefix split_threshold_v100_unique_gemma_rebuilt_to_unique_llama_numeric_seed60601
```
