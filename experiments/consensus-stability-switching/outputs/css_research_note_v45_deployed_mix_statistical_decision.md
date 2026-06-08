# v45 - Deployed-Mix Statistical Decision Protocol

## Why this exists

The deployed-mix verifier run needs a decision rule before any real external/local verifier outputs arrive. A point estimate alone is too easy to overclaim: if a small hand-built packet set shows positive natural-rate weighted delta, a reviewer can reasonably ask whether the gain is robust to which packets happened to be sampled from each deployment category.

v45 adds a conservative statistical gate for that future run.

## Protocol

Given verifier predictions over the deployed-mix packet set:

1. Score each packet under a confidence threshold policy.
2. If verifier confidence is below the threshold, fall back to the baseline answer.
3. Group scored packets by dataset and deployment category.
4. Bootstrap within each dataset/category stratum.
5. For each replicate, recompute natural-rate weighted deployed accuracy and subtract the dataset baseline-correct natural rate.
6. Report a 95% bootstrap confidence interval for deployed delta.

The policy passes only if:

```text
lower_95_ci(deployed_delta) > 0
```

Otherwise the result is reported as `uncertain_or_negative`.

## Implementation

Script:

- [deployed_mix_policy_ci.py](deployed_mix_policy_ci.py)

Test:

- [test_deployed_mix_policy_ci.py](test_deployed_mix_policy_ci.py)

Synthetic smoke output:

- [synthetic_deployed_mix_policy_ci.md](synthetic_deployed_mix_policy_ci.md)
- [synthetic_deployed_mix_policy_ci.csv](synthetic_deployed_mix_policy_ci.csv)

The synthetic smoke validates the scoring, fallback, weighting, bootstrap, and decision machinery. It is not benchmark evidence for the research claim because the predictions are synthetic.

## Smoke result

On synthetic predictions, the low and medium threshold policies pass the lower-bound-positive rule, while the strict `0.90` confidence threshold falls back enough to produce zero deployed delta and is correctly labeled `uncertain_or_negative`.

That matters because the rule is capable of rejecting a superficially safe but non-improving policy.

## Research impact

This does not solve the missing-verifier problem by itself. It does close an important review hole: once real verifier predictions are available, the paper can judge them by a pre-specified, category-stratified, natural-rate weighted criterion rather than by cherry-picked thresholds or raw packet-set averages.
