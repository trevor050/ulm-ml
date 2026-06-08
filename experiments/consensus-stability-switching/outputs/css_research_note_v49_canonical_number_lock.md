# v49 - Canonical Number Lock

## Why this exists

The reviewer checklist had one avoidable weakness: the draft quoted several nearby high-N MATH gap numbers from different artifacts. The differences were small, but small numerical drift looks sloppy when the central claim is measurement.

v49 makes the canonical selectability/depth table script-generated.

## Implementation

Script:

- [make_canonical_selectability_depth_table.py](make_canonical_selectability_depth_table.py)

Test:

- [test_make_canonical_selectability_depth_table.py](test_make_canonical_selectability_depth_table.py)

Generated outputs:

- [canonical_selectability_depth_table.md](canonical_selectability_depth_table.md)
- [canonical_selectability_depth_table.csv](canonical_selectability_depth_table.csv)

## What changed

The canonical table now reads directly from:

- `cluster_selectability_math_llama_parser_v2.csv`
- `cluster_selectability_math_gemma2b_parser_v2.csv`
- `deep_topk_math_llama_n128.csv`
- `deep_topk_math_gemma2b_n128.csv`

It uses the deep N=128 top-k audit as the canonical source for depth claims and explicitly reports the small drift relative to the multi-N selectability audit:

- Llama oracle: selectability `0.846`, depth `0.852`.
- Gemma selector: selectability `0.222`, depth `0.233`.

## Safe quote

> In parser-v2 high-N MATH audits, `cluster_sum` reaches `0.448` on Llama and `0.233` on Gemma, while a full answer-cluster oracle reaches `0.852` and `0.725`. Correct clusters on selector misses are often buried: miss-rank p50/p90 is `6/21` for Llama and `8/33` for Gemma.

## Research impact

This does not add a new method result. It removes a preventable credibility leak. The paper now has one reproducible source of truth for the core diagnostic numbers.
