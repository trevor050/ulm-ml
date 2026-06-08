# Canonical Selectability And Depth Table

**Date:** June 1, 2026
**Purpose:** one script-generated reviewer-facing citation target for the high-N MATH selectability gap and depth-oracle numbers.

The older artifacts report several nearby numbers because they answer slightly different questions: multi-N parser-v2 selectability, deep N=128 top-k visibility, and earlier top-k bounds. For the paper draft, use this table unless intentionally discussing parser/trial sensitivity.

## Source Artifacts

- `MATH/Llama` selectability: `cluster_selectability_math_llama_parser_v2.csv`
- `MATH/Llama` depth: `deep_topk_math_llama_n128.csv`
- `MATH/Gemma` selectability: `cluster_selectability_math_gemma2b_parser_v2.csv`
- `MATH/Gemma` depth: `deep_topk_math_gemma2b_n128.csv`

All canonical rows below use parser-v2 held-out MATH, `N=128`, and top-k windows ranked by `cluster_sum`. The depth rows are the canonical source for top-k/depth claims.

## Canonical High-N Table

| dataset | trials | `cluster_sum` | full cluster oracle | headroom | top-5 oracle | top-10 oracle | top-20 oracle | avg clusters | miss rank p50/p75/p90 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 888 | 0.448 | 0.852 | 0.404 | 0.648 | 0.748 | 0.809 | 30.6 | 6 / 11 / 21 |
| MATH/Gemma | 888 | 0.233 | 0.725 | 0.492 | 0.411 | 0.536 | 0.635 | 55.5 | 8 / 16 / 33 |

## Shallow-Reranking Failure

| dataset | top-2 oracle | top-3 oracle | top-5 oracle | read |
|---|---:|---:|---:|---|
| MATH/Llama | 0.519 | 0.575 | 0.648 | top-3 leaves most headroom untouched |
| MATH/Gemma | 0.300 | 0.334 | 0.411 | top-3 is nowhere near enough |

## Headroom Closed By Inspection Depth

| dataset | top-2 | top-3 | top-5 | top-10 | top-20 | top-50 |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.175 | 0.315 | 0.493 | 0.741 | 0.891 | 0.992 |
| MATH/Gemma | 0.135 | 0.206 | 0.362 | 0.616 | 0.817 | 0.966 |

## Provenance Drift Check

This table intentionally exposes the small difference between the multi-N selectability audit and the deep N=128 depth audit.

| dataset | selectability `cluster_sum` | depth `cluster_sum` | delta | selectability oracle | depth oracle | delta |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.448 | 0.448 | +0.000 | 0.846 | 0.852 | +0.007 |
| MATH/Gemma | 0.222 | 0.233 | +0.011 | 0.723 | 0.725 | +0.002 |

## How To Quote

Safe wording:

> In parser-v2 high-N MATH audits, `cluster_sum` reaches `0.448` on Llama and `0.233` on Gemma, while a full answer-cluster oracle reaches `0.852` and `0.725`. Correct clusters on selector misses are often buried: miss-rank p50/p90 is `6/21` for Llama and `8/33` for Gemma. Top-10/top-20 inspection closes much more headroom than top-2/top-3 reranking.

Avoid wording:

> The exact oracle is `0.846`.

That number comes from the multi-N parser-v2 selectability table for any-correct/oracle cluster. The deep N=128 visibility audit reports `0.852` because it is the direct top-k depth source. The difference is small, but reviewers will notice if the draft pretends all artifacts are one identical run.

CSV: [canonical_selectability_depth_table.csv](canonical_selectability_depth_table.csv).