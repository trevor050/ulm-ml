# v52 Cross-Model Verifier Transfer

## Question

The live literature refresh made judge and trajectory distribution shift a first-class objection. If the cheap verifier-like scorer behind `cluster_sum` only works on the trace model it was trained on, then the answer-cluster depth story is much weaker. This note tests that objection directly on the existing MATH/Llama and MATH/Gemma repeated-sampling traces.

## Protocol

Train the cheap sample-level candidate verifier from `monkey_css_realbench.py` on one trace model, then evaluate answer-cluster selection on the other trace model. The target split is held out with the same deterministic problem split as the earlier MATH audits.

Config:

- Datasets: `work/MATH_Llama-3-8B-Instruct.json`, `work/MATH_Gemma-2B.json`
- N: `128`
- Trials/problem: `12`
- Seed: `60601`
- Verifier train problems: `20`
- Holdout gap: `24`
- Verifier training samples/problem: `120`
- Target held-out problems/model: `84`
- Target trials/model: `1008`

This is still a cheap text-feature verifier, not a real LLM verifier. It is a scorer-transfer stress test, not the final measured-verifier benchmark.

## Result

| train | target | transfer | target problems | AUC | any | BoN | SC | cluster_sum | top5 oracle | top20 oracle | cluster gap | AUC gap | top20 gap |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MATH/Llama | MATH/Llama | within | 84 | 0.528 | 0.865 | 0.220 | 0.433 | 0.436 | 0.657 | 0.826 | +0.000 | +0.000 | +0.000 |
| MATH/Llama | MATH/Gemma | cross | 84 | 0.575 | 0.723 | 0.071 | 0.198 | 0.238 | 0.413 | 0.631 | +0.002 | -0.008 | -0.007 |
| MATH/Gemma | MATH/Llama | cross | 84 | 0.528 | 0.865 | 0.275 | 0.433 | 0.445 | 0.658 | 0.829 | +0.010 | -0.000 | +0.003 |
| MATH/Gemma | MATH/Gemma | within | 84 | 0.583 | 0.723 | 0.099 | 0.198 | 0.236 | 0.414 | 0.638 | +0.000 | +0.000 | +0.000 |

CSV/table artifact: [`cross_model_verifier_transfer.md`](cross_model_verifier_transfer.md), [`cross_model_verifier_transfer.csv`](cross_model_verifier_transfer.csv).

## Read

The feared failure did not show up here. Cross-training the cheap scorer has almost no negative effect on realized answer-cluster selection:

- Gemma-trained scorer on Llama target: `cluster_sum 0.445`, gap `+0.010` vs Llama-trained scorer.
- Llama-trained scorer on Gemma target: `cluster_sum 0.238`, gap `+0.002` vs Gemma-trained scorer.
- Candidate AUC is also stable: Llama target gap `-0.000`; Gemma target gap `-0.008`.
- Top-20 oracle under scorer ordering is essentially unchanged: Llama `+0.003`, Gemma `-0.007`.

This strengthens the paper pitch in a narrow but useful way: the cluster-depth bottleneck is not obviously an artifact of a scorer memorizing one model's trace style. The depth/oracle gap still dominates. Even when the scorer transfers, `cluster_sum` is far below any-correct coverage (`0.436` vs `0.865` on Llama, `0.236` vs `0.723` on Gemma), while top-20 inspection retains substantial headroom (`0.826`/`0.638`).

## Caveats

- This is not an external verifier result.
- The scorer uses shallow text features and correctness labels from the source trace data.
- It tests Llama/Gemma MATH transfer only; task transfer and stronger model-family transfer remain open.
- The target candidate AUC is computed over the sampled candidate union used by the N=128 trials, not all 10,000 traces per problem.

## Updated Claim

After v51 and v52, two obvious reviewer escapes are weaker:

1. "Maybe a short/first-finish heuristic explains the gap." v51 says no on completed traces.
2. "Maybe the scorer is model-specific." v52 says not materially for Llama/Gemma MATH transfer under this cheap verifier.

The biggest unresolved hole remains the real deployed verifier: run the compact deployed-mix and diverse buried top-20 prompt sets with an external/local LLM judge, then score recovery, false regression, confidence fallback, and bootstrap deployed delta.

## Reproduce

```bash
python3 work/test_cross_model_verifier_transfer.py
python3 work/cross_model_verifier_transfer.py \
  --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json MATH/Gemma=work/MATH_Gemma-2B.json \
  --n 128 \
  --trials-per-problem 12 \
  --seed 60601 \
  --verifier-train-problems 20 \
  --audit-holdout-gap 24 \
  --verifier-samples-per-problem 120 \
  --output-prefix cross_model_verifier_transfer
```
