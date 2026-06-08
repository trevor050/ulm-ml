# v31 Budgeted Variable-Depth Policy

## Question

v30 reframed adaptive depth as a cost frontier. The next question is stronger:

> Can a learned policy choose skip/top-5/top-10/top-20 per problem under a shared verifier-token budget, or should the method stay framed as a fixed operating-point frontier?

## Setup

New script:

```bash
python3 work/test_budgeted_depth_policy.py
python3 work/budgeted_depth_policy.py --output-prefix budgeted_depth_policy
```

The policy trains separate recoverability detectors for compact top-5, top-10, and top-20 inspection. For each held-out trial, it creates candidate actions and greedily spends the token budget on the highest predicted utility per token. It is compared against:

- the best fixed compact row available under the same token budget from v30,
- an oracle variable-depth policy that uses true recoverability labels to measure headroom.

Assumption is the same conservative projection: `80%` verifier success when recoverable, `2%` false-regression otherwise.

## Result

| dataset | budget | learned variable-depth | best fixed compact | oracle variable-depth |
|---|---:|---:|---:|---:|
| MATH/Llama | 128 | 0.508 | 0.488 | 0.610 |
| MATH/Llama | 256 | 0.558 | 0.537 | 0.705 |
| MATH/Llama | 512 | 0.599 | 0.621 | 0.746 |
| MATH/Llama | 1024 | 0.611 | 0.621 | 0.746 |
| MATH/Gemma | 128 | 0.284 | 0.280 | 0.392 |
| MATH/Gemma | 256 | 0.313 | 0.315 | 0.484 |
| MATH/Gemma | 512 | 0.361 | 0.348 | 0.556 |
| MATH/Gemma | 1024 | 0.371 | 0.395 | 0.556 |

Report: `outputs/budgeted_depth_policy.md`.

## Interpretation

This is a useful negative/positive split.

The learned utility-density policy is only mildly useful at low budgets and loses to the fixed compact frontier at higher budgets. It mostly buys shallow top-5 verification and almost never buys top-20. That means the current cheap detector scores are not good enough to allocate depth, even though they can detect some failures.

The oracle policy shows large remaining headroom. At the same token budgets, oracle variable-depth reaches Llama `0.746` and Gemma `0.556`, far above the learned policy and fixed compact frontier. This says the budgeted depth idea is not dead; the bottleneck is depth-value prediction/calibration.

## Updated Method Claim

The proposal should not claim that the current learned depth policy is solved. The sharper claim is:

```text
Correct clusters are recoverable at multiple depths, and oracle budgeted depth allocation has large headroom, but current cheap set-level features cannot reliably price deeper verification. The next method target is calibrated depth-value prediction, not simply larger top-k prompts.
```

## Caveat

This is still a projected verifier-success experiment, not a measured verifier run. The oracle row uses labels and is an upper bound, not a deployable policy.
