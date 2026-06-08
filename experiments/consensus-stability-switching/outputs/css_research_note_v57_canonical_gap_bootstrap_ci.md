# v57 Canonical Gap Bootstrap CI

## Question

The reviewer-facing pitch now depends on the canonical MATH N=128 selectability gap: `cluster_sum` is far below the answer-cluster oracle, and top-10/top-20 inspection closes meaningful headroom. Until now, that headline was mostly a point estimate. This note adds problem-bootstrap confidence intervals over the canonical held-out problems.

## Protocol

Recompute the canonical MATH N=128 depth audit with the same split shape:

- Datasets: `work/MATH_Llama-3-8B-Instruct.json`, `work/MATH_Gemma-2B.json`
- N: `128`
- Trials/problem: `12`
- Verifier train problems: `30`
- Holdout gap: `24`
- Held-out problems/model: `74`
- Verifier training samples/problem: `800`
- Bootstrap: `2000` resamples over held-out problems

The script uses the same cheap verifier/scorer machinery as the deep top-k audit, but only scores sampled candidate indices for the target problems. This reproduces the canonical point estimates while adding uncertainty intervals.

## Result

Artifact: [`canonical_gap_bootstrap_ci.md`](canonical_gap_bootstrap_ci.md), [`canonical_gap_bootstrap_ci.csv`](canonical_gap_bootstrap_ci.csv).

| dataset | problems | cluster_sum | oracle | headroom | top10 | top20 | top20 gain | top20 closed | miss p50/p75/p90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 74 | 0.448 [0.347, 0.561] | 0.852 [0.778, 0.917] | 0.404 [0.309, 0.501] | 0.748 [0.652, 0.834] | 0.809 [0.729, 0.882] | 0.360 [0.269, 0.455] | 0.891 [0.824, 0.947] | 6 / 11 / 21 |
| MATH/Gemma | 74 | 0.233 [0.146, 0.324] | 0.725 [0.643, 0.803] | 0.492 [0.402, 0.582] | 0.536 [0.440, 0.634] | 0.635 [0.545, 0.723] | 0.402 [0.315, 0.492] | 0.817 [0.750, 0.870] | 8 / 16 / 33 |

## Read

The headline gap is not a knife-edge artifact:

- Llama headroom remains large: `0.404`, CI `[0.309, 0.501]`.
- Gemma headroom remains large: `0.492`, CI `[0.402, 0.582]`.
- Top-20 inspection gain is also robust: Llama `0.360`, CI `[0.269, 0.455]`; Gemma `0.402`, CI `[0.315, 0.492]`.
- Top-20 closes most missed headroom under the scorer's current cluster ordering, with CIs still high: Llama `0.891 [0.824, 0.947]`, Gemma `0.817 [0.750, 0.870]`.

This materially strengthens the reviewer-facing diagnostic. The selectability gap is not just a favorable point estimate from 888 trials; it survives resampling over the 74 held-out source problems per model.

## Updated Claim

The safe wording can now include uncertainty:

> In parser-v2 high-N MATH audits with problem-bootstrap CIs, `cluster_sum` reaches `0.448 [0.347, 0.561]` on Llama and `0.233 [0.146, 0.324]` on Gemma, while the answer-cluster oracle reaches `0.852 [0.778, 0.917]` and `0.725 [0.643, 0.803]`. The resulting headroom is large on both models, and top-20 inspection recovers a robust additional `0.360 [0.269, 0.455]` and `0.402 [0.315, 0.492]` accuracy.

The missing external verifier remains the main blocker, but the diagnostic evidence is now statistically harder to dismiss.

## Reproduce

```bash
python3 work/test_canonical_gap_bootstrap_ci.py
python3 work/canonical_gap_bootstrap_ci.py \
  --dataset MATH/Llama=work/MATH_Llama-3-8B-Instruct.json MATH/Gemma=work/MATH_Gemma-2B.json \
  --n 128 \
  --trials-per-problem 12 \
  --seed 60601 \
  --verifier-train-problems 30 \
  --audit-holdout-gap 24 \
  --verifier-samples-per-problem 800 \
  --bootstrap-rounds 2000 \
  --output-prefix canonical_gap_bootstrap_ci
```
