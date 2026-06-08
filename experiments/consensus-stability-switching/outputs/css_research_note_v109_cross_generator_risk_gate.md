# v109 Cross-Generator Risk-Gate Audit

## Question

v108 showed that a second generator trace is useful but asymmetric: Llama as an auxiliary trace helps Gemma, while Gemma as an auxiliary hurts Llama. This audit asks whether a held-out calibration split can turn that raw signal into a conservative accept/fallback policy.

## Setup

- Target traces: `MATH_Gemma-2B` and `MATH_Llama-3-8B-Instruct`
- Auxiliary traces: the opposite model on the same held-out problem ids
- N: `128`
- Trials/problem: `8`
- Seeds: `60601,60602,60603`
- Verifier train problems: `30`
- Audit holdout gap: `24`
- Candidate-verifier samples/problem: `800`
- Calibration problems: `12,24,36`
- Policies: `target_intersection_top10`, `target_intersection_top20`, `union_rank_top3`

Command:

```bash
python3 -u work/cross_generator_risk_gate_audit.py --n 128 --trials-per-problem 8 --seeds 60601,60602,60603 --policies target_intersection_top10,target_intersection_top20,union_rank_top3 --calibration-problems 12,24,36 --verifier-train-problems 30 --audit-holdout-gap 24 --verifier-samples-per-problem 800 --bootstrap-rounds 250 --output-prefix cross_generator_risk_gate_v109
```

## Result

The strongest result survives calibration only in one direction:

| target | auxiliary | policy | calibration problems | mean delta | positive seeds | CI-positive seeds | accepts | recoveries | regressions |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Gemma | Llama | `union_rank_top3` | 36 | `+0.126` | 3/3 | 3/3 | 225 | 122 | 7 |
| Gemma | Llama | `union_rank_top3` | 24 | `+0.102` | 3/3 | 3/3 | 266 | 134 | 12 |
| Gemma | Llama | `target_intersection_top10` | 36 | `+0.019` | 2/3 | 1/3 | 62 | 18 | 1 |
| Llama | Gemma | best nonzero rows | 12-36 | `<=0.000` | 0/3 | 0/3 | mixed | mixed | mixed |

The corrected no-fit guard matters. Rows with fewer than eight usable changed calibration examples now accept zero target rows; the optimistic small-calibration artifacts from the first draft of this run are invalid and should not be cited.

## Interpretation

This is the first calibrated auxiliary-trace result that produces a robust positive deployed-style movement, but it is not a general verifier replacement. It says:

- Cross-generator evidence is directional. Llama is useful auxiliary evidence for Gemma on hard MATH; Gemma is not useful auxiliary evidence for Llama under these policies.
- Calibration helps, but only when the calibration set is large enough to fit the accept gate. The `24` and `36` problem rows are the citeable ones.
- The best policy is not strict agreement. `union_rank_top3` works better than intersection because it can choose a high-consensus answer from either trace, then let the risk gate decide whether to override the target default.
- Regressions remain nonzero. The result is positive under problem-bootstrap CI, but it is not a no-regression policy.

## Updated Claim

The selector-replacement path has a narrow positive branch: calibrated generator-choice routing can recover many Gemma failures when a stronger auxiliary Llama trace is available. This is a different claim from semantic verification. It uses extra generation traces from another model family and should be treated as an auxiliary-trace routing result, not as evidence that the current local verifier models can solve buried cluster selection.

## Artifacts

- Summary: [cross_generator_risk_gate_v109.md](cross_generator_risk_gate_v109.md)
- CSV: [cross_generator_risk_gate_v109.csv](cross_generator_risk_gate_v109.csv)
- Aggregate CSV: [cross_generator_risk_gate_v109_aggregate.csv](cross_generator_risk_gate_v109_aggregate.csv)
- Row details: [cross_generator_risk_gate_v109_details.jsonl](cross_generator_risk_gate_v109_details.jsonl)
- Script snapshot: [cross_generator_risk_gate_audit.py](cross_generator_risk_gate_audit.py)
