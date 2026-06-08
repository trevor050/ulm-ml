# v68 Phase Depth Policy Frontier

**Date:** June 1, 2026  
**Question:** Once verifier quality and prompt cost are both explicit, which depth should the policy actually choose?

## Run

I turned v67's cost-normalized depth table into a simple utility frontier. For each dataset, sample count, and value setting, the policy chooses no verifier, top-5, top-10, or top-20 by maximizing:

```text
projected_delta - avg_prompt_tokens / value_tokens_per_point
```

Command:

```bash
python3 work/phase_depth_policy_frontier.py \
  --cost-csv outputs/phase_depth_cost_roi.csv \
  --output-prefix phase_depth_policy_frontier \
  --value-grid 4000,8000,16000,32000,64000 \
  --verifier-success 0.80 \
  --false-regress 0.02
```

Primary artifact: [phase_depth_policy_frontier.md](phase_depth_policy_frontier.md).

## Result

At `N=128`, using 80% verifier success and 2% false regression:

| dataset | value tokens / +1.0 | chosen depth | projected delta | avg prompt tok | utility |
|---|---:|---:|---:|---:|---:|
| MATH/Gemma | `4k` | no verifier | `0.000` | `0` | `0.000` |
| MATH/Gemma | `8k` | top10 | `0.228` | `1116` | `0.088` |
| MATH/Gemma | `16k` | top10 | `0.228` | `1116` | `0.158` |
| MATH/Gemma | `32k` | top20 | `0.285` | `2266` | `0.214` |
| MATH/Gemma | `64k` | top20 | `0.285` | `2266` | `0.250` |
| MATH/Llama | `4k` | no verifier | `0.000` | `0` | `0.000` |
| MATH/Llama | `8k` | top10 | `0.223` | `1011` | `0.096` |
| MATH/Llama | `16k` | top10 | `0.223` | `1011` | `0.159` |
| MATH/Llama | `32k` | top10 | `0.223` | `1011` | `0.191` |
| MATH/Llama | `64k` | top20 | `0.261` | `2369` | `0.224` |

Top-20 beats top-10 only when the value of a +1.0 accuracy improvement crosses the tail threshold:

| dataset | top20 extra delta | top20 extra tok | value threshold |
|---|---:|---:|---:|
| MATH/Gemma | `0.057` | `1150` | `20082` |
| MATH/Llama | `0.038` | `1357` | `35279` |

## Read

This turns the adaptive-depth claim into an actual decision frontier:

1. If verifier tokens are cheap relative to accuracy, top-20 is justified on high-N depth-limited MATH.
2. If tokens are moderately priced, top-10 is the stable operating point.
3. If tokens are expensive, the policy should skip verification rather than run a shallow but still net-negative prompt.

The important result is not that top-10 always wins. It is that the method now has an explicit value knob and a measurable top20 threshold. That is much closer to a deployable policy than saying "inspect top20" or "inspect top10" in isolation.

## Caveat

This still depends on the v67 compact prompt cost proxy and the v65-style verifier success / false-regression projection. It is a policy frontier for prioritizing the real verifier benchmark, not a measured deployed verifier result.
