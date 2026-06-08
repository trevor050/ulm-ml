# v54 Cross-Task Transfer Boundary

## Question

v53 weakens the objection that the cheap verifier scorer is just memorizing one trace model's style on MATH. The next boundary is task shift: does a scorer trained on MATH/Llama transfer to GSM8K/Llama, and vice versa?

## Protocol

Run the same three-seed transfer sweep as v53, but replace Gemma with GSM8K/Llama:

- Seeds: `60601`, `60602`, `60603`
- Datasets: `work/MATH_Llama-3-8B-Instruct.json`, `work/GSM8K_Llama-3-8B-Instruct.json`
- N: `128`
- Trials/problem: `12`
- Verifier train problems: `20`
- Holdout gap: `24`
- Verifier training samples/problem: `120`
- Target held-out problems/seed: MATH `84`, GSM8K `83`

This is still the cheap text-feature scorer, not an external verifier.

## Result

Summary artifact: [`cross_task_verifier_transfer_seed_sweep.md`](cross_task_verifier_transfer_seed_sweep.md).

| train | target | transfer | seeds | cluster mean | cluster sd | gap mean | gap sd | AUC gap mean | top20 gap mean |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| GSM8K/Llama | GSM8K/Llama | within | 3 | 0.862 | 0.014 | +0.000 | 0.000 | +0.000 | +0.000 |
| GSM8K/Llama | MATH/Llama | cross | 3 | 0.437 | 0.009 | -0.010 | 0.010 | +0.001 | -0.003 |
| MATH/Llama | GSM8K/Llama | cross | 3 | 0.853 | 0.019 | -0.009 | 0.007 | -0.120 | -0.001 |
| MATH/Llama | MATH/Llama | within | 3 | 0.446 | 0.009 | +0.000 | 0.000 | +0.000 | +0.000 |

Per-seed cross gaps:

| seed | train -> target | cluster gap | AUC gap | top20 gap |
|---:|---|---:|---:|---:|
| 60601 | MATH/Llama -> GSM8K/Llama | -0.004 | -0.121 | -0.001 |
| 60602 | MATH/Llama -> GSM8K/Llama | -0.003 | -0.138 | -0.001 |
| 60603 | MATH/Llama -> GSM8K/Llama | -0.019 | -0.103 | +0.000 |
| 60601 | GSM8K/Llama -> MATH/Llama | +0.002 | +0.007 | -0.007 |
| 60602 | GSM8K/Llama -> MATH/Llama | -0.009 | +0.009 | -0.008 |
| 60603 | GSM8K/Llama -> MATH/Llama | -0.022 | -0.012 | +0.005 |

## Read

Task transfer is slightly worse than same-task model transfer, but not catastrophically worse for realized answer-cluster selection:

- GSM8K-trained scorer on MATH averages `cluster_sum` gap `-0.010 +/- 0.010`.
- MATH-trained scorer on GSM8K averages `cluster_sum` gap `-0.009 +/- 0.007`.

The sharper boundary is candidate-level ranking/calibration. MATH-trained scorer on GSM8K has mean candidate AUC gap `-0.120`, yet the final `cluster_sum` gap is only `-0.009`. So task shift can hurt candidate ranking quality while leaving answer-cluster selection mostly intact at N=128. That is an important caveat for any calibrated-confidence or fallback policy, because confidence transfer may be worse than answer-cluster transfer.

## Updated Claim

The current evidence supports a bounded transfer claim:

- Same-task, cross-model MATH transfer is stable over three seeds.
- Cross-task MATH/GSM8K transfer has small realized `cluster_sum` loss but a visible candidate-AUC shift on GSM8K.

This pushes the paper toward a more precise evaluation recommendation: report scorer transfer at both the final selection level and the candidate calibration/ranking level. A deployed verifier policy cannot assume confidence is portable just because final cluster selection is nearly portable.

## Reproduce

```bash
python3 work/test_cross_model_verifier_transfer_seed_sweep.py
python3 work/cross_model_verifier_transfer_seed_sweep.py \
  --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json GSM8K/Llama=work/GSM8K_Llama-3-8B-Instruct.json \
  --seeds 60601 60602 60603 \
  --n 128 \
  --trials-per-problem 12 \
  --verifier-train-problems 20 \
  --audit-holdout-gap 24 \
  --verifier-samples-per-problem 120 \
  --output-prefix cross_task_verifier_transfer_seed_sweep
```
