# v47 - Deployed-Mix Representativeness Audit

## Why this exists

The deployed-mix prompt set is balanced by deployment category, which is exactly what the regression-aware verifier benchmark needs. But category balance is not the same as broad problem coverage.

v47 audits the packet set for source-problem duplication and cross-model overlap so the paper does not overclaim what the current assets prove.

## Implementation

Script:

- [audit_deployed_mix_representativeness.py](audit_deployed_mix_representativeness.py)

Test:

- [test_audit_deployed_mix_representativeness.py](test_audit_deployed_mix_representativeness.py)

Output:

- [deployed_mix_representativeness.md](deployed_mix_representativeness.md)
- [deployed_mix_representativeness.csv](deployed_mix_representativeness.csv)

## Main result

The current deployed-mix sets each contain `72` packets:

- MATH/Llama: `38` unique source problems, max `2` packets/problem.
- MATH/Gemma: `37` unique source problems, max `2` packets/problem.
- Cross-model overlap: `27` shared source problems.

Per-category unique-problem counts range from `6` to `10` for Llama and `7` to `10` for Gemma.

This is acceptable for a regression-aware smoke benchmark, especially because max duplication is capped at `2`. It is not enough for a broad MATH generalization claim.

## Research impact

Together with v46, this makes the deployed-verifier run much less mushy:

- The current `72`-prompt/model set is a smoke test.
- A comfortably positive result can be reported as a strong signal.
- A marginal result should trigger a larger one-packet-per-source or lower-duplication deployed-mix rebuild before any method claim.

That caveat is a strength. It keeps the benchmark honest.
