# v38 Deployed-Mix Break-Even Analysis

**Date:** June 1, 2026  
**Question:** given the v37 deployed-mix rates, how good does a verifier need to be before adaptive cluster-depth verification beats `cluster_sum`?

## Result

The deployed-mix categories give a simple expected-delta equation for an always-invoked depth-k verifier:

```text
delta = recoverable_rate(depth k) * recovery_success
        - baseline_correct_rate * false_regression

false_regression = 1 - baseline_preservation_on_baseline_correct
```

Unhelpful invocations (`no_visible_top20`, `no_correct_generated`) have no top-k gain under this packet key. They matter for token cost and confidence/abstention, but direct accuracy loss is concentrated in already-correct defaults.

## Natural Rates

| dataset | baseline_correct | recoverable top5 | recoverable top10 | recoverable top20 | no visible top20 | no correct generated | compact prompt tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.428 | 0.216 | 0.315 | 0.389 | 0.038 | 0.145 | 2157 |
| MATH/Gemma | 0.299 | 0.159 | 0.263 | 0.342 | 0.100 | 0.259 | 2244 |

## Break-Even Highlights

At `98%` baseline preservation:

| dataset | depth | recovery success needed to break even |
|---|---:|---:|
| MATH/Llama | 5 | 0.040 |
| MATH/Llama | 10 | 0.027 |
| MATH/Llama | 20 | 0.022 |
| MATH/Gemma | 5 | 0.038 |
| MATH/Gemma | 10 | 0.023 |
| MATH/Gemma | 20 | 0.017 |

At `80%` recovery success:

| dataset | depth | max false regression tolerated |
|---|---:|---:|
| MATH/Llama | 5 | 0.405 |
| MATH/Llama | 10 | 0.590 |
| MATH/Llama | 20 | 0.729 |
| MATH/Gemma | 5 | 0.427 |
| MATH/Gemma | 10 | 0.703 |
| MATH/Gemma | 20 | 0.916 |

Projected deltas under the old conservative `80%` recovery / `2%` false-regression assumption:

| dataset | depth 5 | depth 10 | depth 20 |
|---|---:|---:|---:|
| MATH/Llama | +0.165 | +0.244 | +0.303 |
| MATH/Gemma | +0.122 | +0.204 | +0.268 |

These are not new measured verifier results. They are the break-even math implied by the deployed-mix category rates.

## Interpretation

The result is favorable because high-N MATH has lots of visible recoverable mistakes. If the verifier preserves already-correct defaults, it does not need heroic recovery rates to become useful.

This reframes the next external-verifier benchmark:

```text
Measure baseline preservation first.
Then measure recovery by depth.
Then use the v38 formula to convert those category rates into deployed delta.
```

If baseline preservation is poor, the method can still fail even with good hard-packet recovery. If preservation is high, the visible recoverable mass is large enough that modest recovery can matter.

## Commands

```bash
python3 work/test_deployed_mix_break_even.py
python3 work/deployed_mix_break_even.py --output-prefix deployed_mix_break_even
```

Artifacts:

- [deployed-mix break-even report](deployed_mix_break_even.md)
- [deployed-mix break-even CSV](deployed_mix_break_even.csv)
- `work/deployed_mix_break_even.py`
- `work/test_deployed_mix_break_even.py`
