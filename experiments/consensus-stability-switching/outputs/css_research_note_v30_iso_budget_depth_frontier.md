# v30 Iso-Budget Depth Frontier

## Question

v21/v28 make top-20 depth look useful, but a reviewer can still ask:

> Is top-20 actually the right operating point once verifier-token budget is counted, or is this just a cherry-picked depth/invocation row?

## Setup

New compact prompt assets:

- `outputs/cluster_verifier_prompts_math_llama_n128_top5_compact.jsonl`
- `outputs/cluster_verifier_prompts_math_gemma2b_n128_top5_compact.jsonl`
- `outputs/cluster_verifier_prompts_math_llama_n128_top10_strict_compact.jsonl`
- `outputs/cluster_verifier_prompts_math_gemma2b_n128_top10_strict_compact.jsonl`

New frontier script:

```bash
python3 work/test_iso_budget_depth_frontier.py
python3 work/iso_budget_depth_frontier.py --output-prefix iso_budget_depth_frontier
```

Inputs:

- `outputs/adaptive_depth_frontier.csv`
- compact/full prompt files for depths 5, 10, and 20.

Token estimate is `prompt_chars / 4`. The accuracy rows still use the projected `external_80_2pct_false_regress` scenario; no external verifier has been measured.

## Key Result

The cost-aware story is a frontier, not a single depth:

| dataset | low-budget compact row | high-accuracy compact row |
|---|---|---|
| MATH/Llama | depth 5, invoke 0.20: `0.508` at `128` tokens/problem | depth 20, invoke 0.50: `0.653` at `1184` tokens/problem |
| MATH/Gemma | depth 5, invoke 0.10: `0.264` at `65` tokens/problem | depth 20, invoke 0.50: `0.443` at `1133` tokens/problem |

Report: `outputs/iso_budget_depth_frontier.md`.

## Interpretation

This is a useful constraint on the method. Top-20 inspection is not the universal answer. At low budgets, compact top-5/top-10 rows are often better accuracy-per-token operating points. Top-20 becomes attractive when the budget allows a higher invocation rate and the goal is to chase more of the selectability gap.

That gives the proposal a cleaner shape:

```text
adaptive depth is a budgeted policy, not a fixed depth.
low budget: invoke shallow compact verification.
medium budget: invoke compact top-10 more often.
high budget: invoke compact top-20, optionally with full fallback.
```

## Caveat

This is still based on projected verifier success and measured prompt costs. The needed external/local verifier result is now more specific: measure compact verifier accuracy and confidence calibration at multiple depths, then redraw this frontier with measured verifier success and fallback rates.
