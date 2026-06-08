# v55 Transfer Calibration Audit

## Question

v53 and v54 show that final answer-cluster selection transfers better than expected. But deployed verifier policies usually need confidence thresholds, fallback rules, and calibrated uncertainty. Does confidence/ranking transfer as well as final `cluster_sum`?

## Protocol

Summarize the raw rows from:

- [`cross_model_verifier_transfer_seed_sweep.csv`](cross_model_verifier_transfer_seed_sweep.csv)
- [`cross_task_verifier_transfer_seed_sweep.csv`](cross_task_verifier_transfer_seed_sweep.csv)

For each cross-transfer row, compute mean/std gap versus the within-target scorer over:

- final selection: `cluster_sum_gap_vs_within`
- candidate ranking: `candidate_auc_gap_vs_within`
- candidate calibration: `target_candidate_brier` gap versus within-target brier
- scorer-induced depth ordering: `oracle_top20_gap_vs_within`

## Result

Summary artifact: [`transfer_calibration_summary.md`](transfer_calibration_summary.md).

| suite | train -> target | seeds | cluster gap | AUC gap | Brier gap | top20 gap |
|---|---|---:|---:|---:|---:|---:|
| model | MATH/Gemma -> MATH/Llama | 3 | +0.005 +/- 0.005 | +0.003 +/- 0.004 | -0.004 +/- 0.003 | +0.000 +/- 0.004 |
| model | MATH/Llama -> MATH/Gemma | 3 | +0.000 +/- 0.005 | -0.013 +/- 0.004 | +0.011 +/- 0.011 | -0.005 +/- 0.005 |
| task | GSM8K/Llama -> MATH/Llama | 3 | -0.010 +/- 0.010 | +0.001 +/- 0.009 | +0.026 +/- 0.015 | -0.003 +/- 0.006 |
| task | MATH/Llama -> GSM8K/Llama | 3 | -0.009 +/- 0.007 | -0.120 +/- 0.014 | +0.003 +/- 0.049 | -0.001 +/- 0.000 |

## Read

There are two different transfer stories:

1. Final answer-cluster selection is fairly portable in these cheap-scorer sweeps. All cross-transfer `cluster_sum` gaps are between about `-0.010` and `+0.005`.
2. Candidate ranking/calibration is less portable. The clearest case is MATH-trained scorer on GSM8K: candidate AUC drops `-0.120 +/- 0.014` while final `cluster_sum` drops only `-0.009 +/- 0.007`.

This is exactly the nuance the paper should keep. The cluster-depth diagnostic is not obviously a trace-style artifact, but a deployed confidence-threshold policy should not assume scorer probabilities or candidate-level ranking transfer cleanly across tasks.

## Updated Evaluation Recommendation

Report transfer at two levels:

- selection transfer: `cluster_sum`, top-k oracle/depth ordering, deployed answer accuracy,
- calibration transfer: candidate AUC, Brier score, confidence-threshold fallback curves, regression under thresholded deployment.

The next real verifier run should therefore include target-domain calibration or threshold sweeps, not only raw judge accuracy.

## Reproduce

```bash
python3 work/test_transfer_calibration_summary.py
python3 work/transfer_calibration_summary.py \
  --input model=outputs/cross_model_verifier_transfer_seed_sweep.csv task=outputs/cross_task_verifier_transfer_seed_sweep.csv \
  --output-prefix transfer_calibration_summary
```
