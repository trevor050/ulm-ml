# v46 - Deployed-Mix Power Plan

## Why this exists

v45 defined the decision rule for the missing deployed verifier run: the policy only passes if the lower 95% bootstrap confidence bound on natural-rate weighted deployed delta is positive.

v46 asks the next practical question: how large does the deployed-mix packet set need to be for that conservative rule to have a reasonable chance of passing?

## Implementation

Script:

- [deployed_mix_power_plan.py](deployed_mix_power_plan.py)

Test:

- [test_deployed_mix_power_plan.py](test_deployed_mix_power_plan.py)

Output:

- [deployed_mix_power_plan.md](deployed_mix_power_plan.md)
- [deployed_mix_power_plan.csv](deployed_mix_power_plan.csv)

The simulation uses the natural deployed-mix category rates from the existing Llama/Gemma packet stats. For each verifier scenario, it simulates balanced packet sets with `12`, `24`, `48`, and `96` packets per category, then applies the v45 lower-CI-positive bootstrap gate.

## Main result

The current assets have `12` packets per category per model, `72` prompts per model.

That is enough for a useful verifier smoke:

- Under the weak scenario, Llama has expected deployed delta `+0.123` and passes the v45 rule in `0.842` of simulations at `12` packets/category.
- Under the weak scenario, Gemma has expected deployed delta `+0.105` and passes in `0.925` of simulations at `12` packets/category.
- Medium/strong scenarios pass essentially always at the current size.

But the current set is not enough to certify a tiny break-even effect:

- Under the marginal scenario, Llama expected delta is only `+0.018`; pass rate is `0.225` at `12` packets/category and only `0.517` at `96`.
- Under the marginal scenario, Gemma expected delta is `+0.016`; pass rate is `0.158` at `12` and `0.650` at `96`.

## Decision implication

The next verifier run should be treated as a two-stage evaluation:

1. Run the existing `72`-prompt-per-model deployed-mix assets as a smoke benchmark.
2. If the point estimate is medium/large, the current set may already pass the v45 rule.
3. If the point estimate is marginal, do not overinterpret it. Build a larger deployed-mix packet set before claiming a positive method result.

This turns the missing external/local verifier run into a concrete go/no-go protocol rather than another open-ended benchmark wish.

## Caveat

This is a simulation over assumed category-level verifier behavior. It does not replace measured verifier predictions. Its value is experimental design: it says how to interpret the first real verifier smoke and when to scale the packet set.
