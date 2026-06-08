# Cluster Selectability v13: Answer Extraction Audit

**Status:** v13 research note, June 1, 2026  
**Question:** are the final-answer clusters trustworthy enough to support the selectability analysis?

## Why This Matters

The whole project depends on final-answer clustering. If the extractor maps correct rationales to the wrong final answer, or maps flawed rationales to the ground-truth answer too often, then cluster selectability tables become suspect.

I audited the local answer extractor against dataset-provided correctness labels and normalized ground-truth answers.

## Parser Fix

The first audit exposed two parser issues:

1. GSM8K ground-truth answers are full rationales ending in `#### answer`, not bare answers. The audit normalized them incorrectly.
2. MATH samples often use simple LaTeX fractions like `\frac{3}{2}`. The extractor sometimes fell back to the last numeric token, e.g. `2`, instead of the fraction.

I patched the extractor to:

- normalize ground-truth rationales through the same answer extractor,
- handle `\frac{a}{b}` and `\dfrac{a}{b}`,
- prefer normalized final-answer text before falling back to raw numeric tokens.

## Extraction Audit After Patch

Sample: 1,200 candidates per problem.

| dataset | samples | correct labels | correct extraction matches GT | correct mismatch | incorrect extraction matches GT | null rate |
|---|---:|---:|---:|---:|---:|---:|
| GSM8K/Llama | 152400 | 117155 | 1.000 | 13 | 0.000 | 0.000 |
| MATH/Llama | 153600 | 41273 | 0.905 | 3922 | 0.005 | 0.000 |
| MATH/Gemma-2B | 153600 | 14331 | 0.856 | 2067 | 0.008 | 0.001 |
| MATH/Pythia-1B | 153600 | 1301 | 0.744 | 333 | 0.013 | 0.023 |

## Spot-Review Read

The low `incorrect extraction matches GT` rate is reassuring. Some examples are flawed rationales that land on the correct final answer string. That is not necessarily an extraction bug; it is a difference between answer-only correctness and rationale correctness.

The remaining correct-label mismatches on MATH are still a real limitation. They likely include:

- equivalent forms not normalized by the parser,
- interval/set/expression answers,
- LaTeX forms beyond simple fractions,
- samples that the dataset evaluator accepts but the string normalizer does not.

Pythia is especially noisy because the model often emits malformed text and the null rate is higher.

## Parser Sensitivity Rerun

I reran the key MATH selectability audits with the patched extractor.

### MATH/Llama at N=128

| metric | original | parser-v2 |
|---|---:|---:|
| any-correct / oracle cluster | 0.846 | 0.846 |
| self-consistency | 0.445 | 0.448 |
| cluster_sum | 0.445 | 0.448 |
| top-2 oracle by cluster_sum | 0.518 | 0.516 |
| top-3 oracle by cluster_sum | 0.572 | 0.569 |

### MATH/Gemma-2B at N=128

| metric | original | parser-v2 |
|---|---:|---:|
| any-correct / oracle cluster | 0.725 | 0.723 |
| self-consistency | 0.243 | 0.215 |
| cluster_sum | 0.240 | 0.222 |
| top-2 oracle by cluster_sum | 0.301 | 0.283 |
| top-3 oracle by cluster_sum | 0.363 | 0.339 |

## Interpretation

The parser fix does **not** erase the main result.

For MATH/Llama, the high-N selectability gap is essentially unchanged. For MATH/Gemma, the patched parser makes the selected-accuracy story slightly worse, not better: `cluster_sum` drops from about `0.240` to `0.222` at `N=128`, while any-correct coverage remains about `0.723`.

This strengthens the core diagnostic:

> The cluster selectability gap survives a targeted answer-extraction fix.

But the audit also justifies caution. MATH string normalization remains imperfect, so exact absolute numbers should be treated as trace-and-parser-specific. The qualitative result is more robust than the third decimal place.

## Artifacts

Scripts:

- [answer_extraction_audit.py](answer_extraction_audit.py)
- [monkey_css_realbench.py](monkey_css_realbench.py)

Reports:

- [answer extraction audit v2](answer_extraction_audit_v2.md)
- [MATH/Llama parser-v2 selectability audit](cluster_selectability_math_llama_parser_v2.md)
- [MATH/Gemma parser-v2 selectability audit](cluster_selectability_math_gemma2b_parser_v2.md)
