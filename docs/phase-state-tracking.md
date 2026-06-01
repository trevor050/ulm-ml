# Phase Channels for Exact State Tracking in Linear-Time Sequence Models

## Executive summary

Recent efficient sequence models have become very good at compressing long context into recurrent state, but several papers point to the same fault line: fixed, mostly contractive state can store fuzzy summaries while still struggling with discrete state tracking. Mamba made the case that input-selective recurrent parameters are central for content-based reasoning (<https://arxiv.org/abs/2312.00752>). Follow-up work on negative eigenvalues argues that constraining diagonal transitions to `[0, 1]` is enough to break parity-like languages, and that allowing sign changes recovers state tracking (<https://arxiv.org/abs/2411.12537>). Gated Delta Networks frame the recurrent state as a fast-weight memory updated by an online regression/delta rule, which is powerful for associative recall but still shares the broader question of what tiny recurrent state should be reserved for exact symbolic state (<https://proceedings.iclr.cc/paper_files/paper/2025/hash/4904fad153f6434a7bcf04465d4be2cc-Abstract-Conference.html>).

This note turns that fault line into a small, reproducible probe: add a few bounded phase-valued state channels whose transition is a root of unity. For a binary event stream, the channel

```text
z_t = exp(2*pi*i*x_t/m) * z_{t-1},  z_0 = 1
```

tracks the count of events modulo `m` exactly with constant memory. Real-valued implementation only needs two channels per modulus: cosine and sine. A linear readout recovers the residue by choosing the prototype phase with the largest dot product.

## Hypothesis

A small bank of learned or initialized root-of-unity channels could be a useful sidecar for linear-time language models:

1. **Exact finite-state reserve:** dedicate tiny state to automaton-like facts that should not be represented as decaying magnitude.
2. **No unbounded cache:** state cost is `2 * number_of_moduli` scalars and update cost is constant per token.
3. **Compatibility:** phase channels can sit next to Mamba-style selective SSM state or DeltaNet-style associative memory; they do not replace high-capacity semantic memory.
4. **Learnable relaxation:** roots of unity are the clean probe; a production layer could parameterize stable rotations/reflections and let training decide which channels remain near exact cycles.

## Probe design

The experiment trains on random binary sequences of lengths 8-64 and tests both in-distribution and extrapolation lengths 65-512. The task is to predict `count(ones) mod m` for `m in {2, 3, 5, 7}`.

Methods:

- `count`: one raw count feature plus a ridge readout. This baseline has the count but lacks periodic inductive bias.
- `positive-exp`: 32 positive leaky integrators, `h_t = lambda h_{t-1} + x_t`, with a ridge readout. This proxies monotone positive-eigenvalue memory.
- `root-of-unity`: exact phase state for the target modulus and a prototype linear decoder.

Command:

```bash
python experiments/phase_state_tracking.py
```

Observed output on 2026-06-01:

| task | method | train/test lengths 8-64 | extrapolate lengths 65-512 | seeds |
| --- | --- | ---: | ---: | ---: |
| count mod 2 | count | 0.485 | 0.496 | 5 |
| count mod 2 | positive-exp | 0.502 | 0.500 | 5 |
| count mod 2 | root-of-unity | 1.000 | 1.000 | 5 |
| count mod 3 | count | 0.329 | 0.336 | 5 |
| count mod 3 | positive-exp | 0.331 | 0.335 | 5 |
| count mod 3 | root-of-unity | 1.000 | 1.000 | 5 |
| count mod 5 | count | 0.185 | 0.196 | 5 |
| count mod 5 | positive-exp | 0.201 | 0.199 | 5 |
| count mod 5 | root-of-unity | 1.000 | 1.000 | 5 |
| count mod 7 | count | 0.143 | 0.138 | 5 |
| count mod 7 | positive-exp | 0.152 | 0.150 | 5 |
| count mod 7 | root-of-unity | 1.000 | 1.000 | 5 |

## Interpretation

The result is deliberately simple, but it isolates a useful architectural distinction. Positive decays summarize event density; they do not represent cyclic state in a way a linear readout can extrapolate. Phase channels represent finite cyclic groups directly, so the same decoder works far outside the training length range.

This does **not** prove that root-of-unity channels improve language modeling. It does suggest a cheap next experiment: add 8-32 phase/reflection channels to a tiny selective SSM on algorithmic mixtures and natural text with bracket depth, indentation, parity, or repeated delimiter probes. The ablation should compare:

1. positive-only diagonal transitions,
2. signed real transitions,
3. complex/2D rotation transitions,
4. learned rotations initialized near roots of unity, and
5. phase channels with a small learned reset gate so document boundaries can zero state.

## Why this might matter

If long-context models increasingly combine associative memories, recurrent compression, and local attention, exact low-dimensional state may become the missing “control plane.” A phase sidecar is tiny enough that the downside is measurable: if it does not help, it costs almost nothing to ablate. If it helps, it gives linear-time models a principled mechanism for state machines that are awkward to emulate with positive decay.
