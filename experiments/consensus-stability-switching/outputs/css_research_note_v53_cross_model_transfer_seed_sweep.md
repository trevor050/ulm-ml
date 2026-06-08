# v53 Cross-Model Transfer Seed Sweep

## Question

v52 found that the cheap verifier scorer transfers across MATH/Llama and MATH/Gemma with almost no realized `cluster_sum` loss. This note checks whether that was a lucky split/sampling seed.

## Protocol

Repeat the v52 transfer test over three deterministic seeds:

- Seeds: `60601`, `60602`, `60603`
- Datasets: `work/MATH_Llama-3-8B-Instruct.json`, `work/MATH_Gemma-2B.json`
- N: `128`
- Trials/problem: `12`
- Verifier train problems: `20`
- Holdout gap: `24`
- Verifier training samples/problem: `120`
- Target held-out problems/model/seed: `84`
- Target trials/model/seed: `1008`

This uses the same cheap text-feature scorer as v52. It is still not the external/local LLM verifier benchmark.

## Result

Summary artifact: [`cross_model_verifier_transfer_seed_sweep.md`](cross_model_verifier_transfer_seed_sweep.md).

| train | target | transfer | seeds | cluster mean | cluster sd | gap mean | gap sd | AUC gap mean | top20 gap mean |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MATH/Gemma | MATH/Gemma | within | 3 | 0.231 | 0.015 | +0.000 | 0.000 | +0.000 | +0.000 |
| MATH/Gemma | MATH/Llama | cross | 3 | 0.451 | 0.004 | +0.005 | 0.005 | +0.003 | +0.000 |
| MATH/Llama | MATH/Gemma | cross | 3 | 0.231 | 0.020 | +0.000 | 0.005 | -0.013 | -0.005 |
| MATH/Llama | MATH/Llama | within | 3 | 0.446 | 0.009 | +0.000 | 0.000 | +0.000 | +0.000 |

Per-seed cross gaps:

| seed | train -> target | cluster gap | AUC gap | top20 gap |
|---:|---|---:|---:|---:|
| 60601 | Llama -> Gemma | +0.002 | -0.008 | -0.007 |
| 60602 | Llama -> Gemma | -0.007 | -0.018 | +0.002 |
| 60603 | Llama -> Gemma | +0.006 | -0.013 | -0.010 |
| 60601 | Gemma -> Llama | +0.010 | -0.000 | +0.003 |
| 60602 | Gemma -> Llama | -0.002 | +0.001 | -0.005 |
| 60603 | Gemma -> Llama | +0.007 | +0.009 | +0.003 |

## Read

The v52 transfer result survives the small seed sweep. Mean cross-model `cluster_sum` gaps are:

- Gemma-trained scorer on Llama: `+0.005 +/- 0.005`.
- Llama-trained scorer on Gemma: `+0.000 +/- 0.005`.

The AUC and top-20 scorer-order gaps are also small. Gemma target AUC is the one mildly negative row (`-0.013` mean), but it does not translate into realized `cluster_sum` loss. That matters because the paper's bottleneck is answer-cluster selection under a fixed candidate set, not calibrated probability estimation for every candidate.

## Updated Claim

The scorer-specificity objection is now weaker than in v52: not only does cross transfer look stable on one split, it remains stable over three deterministic split/sampling seeds. This strengthens the narrow claim that the MATH answer-cluster depth gap is not obviously an artifact of one cheap scorer overfitting one trace model's style.

The unresolved bottleneck is unchanged: the method still needs a real external/local LLM verifier run on deployed-mix and buried-depth prompts, scored with false-regression accounting.

## Reproduce

```bash
python3 work/test_cross_model_verifier_transfer_seed_sweep.py
python3 work/cross_model_verifier_transfer_seed_sweep.py \
  --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json MATH/Gemma=work/MATH_Gemma-2B.json \
  --seeds 60601 60602 60603 \
  --n 128 \
  --trials-per-problem 12 \
  --verifier-train-problems 20 \
  --audit-holdout-gap 24 \
  --verifier-samples-per-problem 120 \
  --output-prefix cross_model_verifier_transfer_seed_sweep
```
