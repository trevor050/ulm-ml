# v51 - Short-Trace Baseline

## Why this exists

The live literature refresh surfaced First Finish Search as a simple but serious objection: maybe shorter reasoning traces are more likely to be correct, so repeated-sampling selection should prefer the first/shortest completion instead of doing answer-cluster depth work.

v51 tests that objection locally on the MATH repeated-sampling traces.

## Implementation

Script:

- [short_trace_baseline.py](short_trace_baseline.py)

Test:

- [test_short_trace_baseline.py](test_short_trace_baseline.py)

Output:

- [short_trace_baseline.md](short_trace_baseline.md)
- [short_trace_baseline.csv](short_trace_baseline.csv)

## Result

At `N=128`:

| dataset | any-correct | cluster_sum | shortest exact | shortest cluster | shortest answer-cluster | length-weighted cluster |
|---|---:|---:|---:|---:|---:|---:|
| MATH/Llama | 0.861 | 0.454 | 0.247 | 0.264 | 0.279 | 0.452 |
| MATH/Gemma | 0.727 | 0.243 | 0.078 | 0.104 | 0.116 | 0.244 |

The shortest-completion selectors are far below `cluster_sum`. A length-weighted cluster score roughly ties `cluster_sum`, but does not improve it.

## Interpretation

First-finish style heuristics are important enough to test, but they do not explain away the cluster selectability gap in these traces.

The result supports the current framing:

- simple length preference is not enough,
- length-normalized verifier mass is not a new win,
- the remaining opportunity is still better answer-cluster evidence and depth allocation.

## Caveat

This is a proxy for First Finish Search, not a full reproduction. The traces provide completed samples, so the script uses completion word count as the finish-time proxy. A real online decoding benchmark could still behave differently.
