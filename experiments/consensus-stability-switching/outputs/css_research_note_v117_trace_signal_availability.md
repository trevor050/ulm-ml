# v117 Trace Signal Availability Audit

## Question

v116 says the current auxiliary-router features have real but insufficient recovery-vs-regression separation. The obvious next ask is:

> Can we mine better regression-risk evidence from the local traces, such as logprobs, token metadata, hidden states, model confidence, or finish reasons?

v117 checks the actual local Monkey Business JSON schema.

## Setup

The audit loads the four local trace files:

- `work/MATH_Llama-3-8B-Instruct.json`
- `work/MATH_Gemma-2B.json`
- `work/GSM8K_Llama-3-8B-Instruct.json`
- `work/MATH_Pythia-1B.json`

It reports problem count, sample count, sample type, correctness-label count, and whether any rich decoder/representation fields are present.

Artifacts:

- [`trace_signal_availability_v117.md`](trace_signal_availability_v117.md)
- [`trace_signal_availability_v117.csv`](trace_signal_availability_v117.csv)
- [`trace_signal_availability_audit.py`](trace_signal_availability_audit.py)

## Result

All four traces have the same usable schema:

| file | problems | samples/problem | sample type | labels | rich signal keys |
|---|---:|---:|---|---:|---|
| `MATH_Llama-3-8B-Instruct.json` | 128 | 10000 | `str` | 10000 | none |
| `MATH_Gemma-2B.json` | 128 | 10000 | `str` | 10000 | none |
| `GSM8K_Llama-3-8B-Instruct.json` | 127 | 10000 | `str` | 10000 | none |
| `MATH_Pythia-1B.json` | 128 | 10000 | `str` | 10000 | none |

Available fields are limited to:

- `question`,
- `prompt`,
- `samples`,
- `is_corrects`,
- `gt_answer`,
- `orig_dset_idx`,
- `orig_dset_split`.

There are no local logprobs, token logprobs, hidden states, embeddings, model confidence, usage fields, finish reasons, or sampling metadata.

## Interpretation

This matters for the next method.

The v116 frontier cannot be improved locally by simply "using logprobs" from the existing traces. Those fields are absent. The available local evidence is:

- sampled solution text,
- correctness labels,
- answer-cluster statistics,
- extracted final answers,
- text-derived process/symbolic features.

The next genuinely new regression-risk signal must come from one of four routes:

1. regenerate or obtain traces with logprobs/hidden states,
2. run a live verifier or embedding model over candidate clusters,
3. add stronger symbolic/equivalence checking from the text,
4. add more generator traces so auxiliary routing has more than a two-model choice.

## Claim Boundary

v117 turns the "new signal needed" line from advice into evidence:

> The current local trace files do not contain decoder telemetry. Same-feature calibration is exhausted; improving problem-disjoint regression control requires new data, new model calls, stronger symbolic processing, or additional generator traces.
