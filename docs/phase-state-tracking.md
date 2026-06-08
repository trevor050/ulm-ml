# Phase Channels for Exact State Tracking in Linear-Time Sequence Models

## Status

Portfolio verdict: **folded into full research track** at
`docs/full-research/cyclic-representation-probes.md`. Phase tracking is no
longer a standalone project.

Evidence level: **constructive oracle/probe**.

The current root-of-unity result is an exact hand-built state update for modular
counting. It proves that a tiny recurrent side channel can represent the target
finite-state variable when the right transition is provided. It does **not**
show that a learned language model, Mamba layer, DeltaNet, or generic recurrent
block will discover that transition from data.

Use this result as a diagnostic boundary: if a learned model fails a modular
state-tracking task that the oracle phase channel solves, the open question is
representation discovery and training pressure, not whether constant-memory
cyclic state exists.

## Motivation

Recent efficient sequence models are good at compressing long context into
recurrent state, but several papers point to a fault line around exact discrete
state tracking. Mamba emphasizes input-selective recurrent parameters for
content-based reasoning (<https://arxiv.org/abs/2312.00752>). Work on negative
eigenvalues argues that constraining diagonal transitions to `[0, 1]` breaks
parity-like languages, while sign changes recover some state tracking
(<https://arxiv.org/abs/2411.12537>). Gated Delta Networks frame recurrent state
as fast-weight memory updated by an online regression rule
(<https://proceedings.iclr.cc/paper_files/paper/2025/hash/4904fad153f6434a7bcf04465d4be2cc-Abstract-Conference.html>).

The small question here is: what does an exact finite-state reserve look like if
we do not force it into a contractive scalar memory?

## Constructive probe

For a binary event stream, the channel

```text
z_t = exp(2*pi*i*x_t/m) * z_{t-1},  z_0 = 1
```

tracks the count of events modulo `m` exactly with constant memory. A real-valued
implementation only needs two channels per modulus: cosine and sine. A linear
prototype decoder recovers the residue by choosing the phase with the largest
dot product.

This is the `root-of-unity` method in `experiments/cyclic-representation-probes/phase_state_tracking.py`.
Because it is given the correct cyclic transition, it should be read as an
oracle side channel rather than a learned baseline.

## Probe design

The experiment trains or evaluates on random binary sequences of lengths 8-64
and tests extrapolation lengths 65-512. The task is to predict `count(ones) mod
m` for `m in {2, 3, 5, 7}`.

Methods:

- `count`: one raw count feature plus a ridge readout. This baseline has exact
  count information but no periodic inductive bias.
- `positive-exp`: positive leaky integrators, `h_t = lambda h_{t-1} + x_t`,
  with a ridge readout. This proxies monotone positive-eigenvalue memory.
- `root-of-unity`: exact cyclic phase state for the target modulus plus a
  prototype decoder.

Command:

```bash
python experiments/cyclic-representation-probes/phase_state_tracking.py
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

The useful distinction is architectural, not empirical dominance. Positive
decays summarize event density; they do not expose cyclic state in a way a
linear readout extrapolates. Root-of-unity channels represent the finite cyclic
group directly, so the same decoder works outside the training length range.

Again, this is not evidence that a learned model will find the root of unity. It
is evidence that the exact update is tiny, bounded, and easy to ablate.

## Next compute-light experiments

1. Train a small recurrent model whose transition can choose positive decays,
   signed scalars, or 2D rotations, then measure whether it learns the cyclic
   transition without being handed the modulus.
2. Initialize a few 2D rotation channels near roots of unity and compare against
   random rotation initialization on parity and modular-count tasks.
3. Add a learned reset gate so document or sequence boundaries can zero phase
   state cleanly.
4. Add bracket-depth, delimiter parity, and indentation probes where the event
   stream must be inferred from tokens instead of supplied as binary input.
5. For any language-model sidecar experiment, report a strict ablation against
   positive-only diagonal state and signed real transitions.

## Why this might matter

If long-context models combine associative memories, recurrent compression, and
local attention, exact low-dimensional state may be a useful control plane. The
phase sidecar is small enough that failure is cheap to measure. The honest
research question is now learnability and usefulness in mixed tasks, not whether
the oracle recurrence can count modulo `m`.
