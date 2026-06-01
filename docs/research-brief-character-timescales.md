# Spectral Character Baselines for Grokking Timescale Experiments

_Date:_ 2026-06-01

Portfolio status: part of `full_research` track
`docs/full-research/cyclic-representation-probes.md`.

## Abstract

Recent grokking work increasingly frames delayed generalization as competition between a fast
memorizing solution and a slower, more structured generalizing circuit. This note turns that framing
into a cheap diagnostic baseline for modular arithmetic: before spending GPU time waiting for a
network to discover a cyclic representation, fit explicit cyclic-character interaction features and
ask how much of the apparent difficulty remains once the correct feature family is available.

On modular addition tables for primes 31 and 43, a ridge linear classifier on all real Fourier
interaction channels reaches perfect held-out-pair accuracy from only 10% of the operation table.
A pair one-hot memorizer gets perfect training accuracy but chance held-out accuracy, and a
separable one-hot model cannot solve the task. Truncated character bases produce smooth partial
accuracy curves. The result is not meant to beat neural grokking; it is a control that separates
three factors that are otherwise entangled in neural training curves:

1. whether the sample contains enough information to determine the group operation;
2. whether the representation family contains the cyclic characters that solve the operation; and
3. how long gradient descent takes to find and amplify those characters.

## Literature hook

This project was selected because it is small enough to run on CPU but touches a current open
question in grokking research.

- Liu et al. (2022) describe grokking as delayed generalization and map phase diagrams over
  hyperparameters: <https://arxiv.org/abs/2205.10343>.
- Gromov (2023) gives analytic modular-arithmetic solutions and evidence that neural networks
  discover structured feature maps: <https://arxiv.org/abs/2301.02679>.
- Varma et al. (2023) frame grokking as competition between memorizing and generalizing circuits:
  <https://arxiv.org/abs/2309.02390>.
- Song and Ye (2026) explicitly model capacity-dependent memorization and generalization
  timescales: <https://arxiv.org/abs/2605.09724>.

The proposed baseline complements those lines: it gives the generalizing circuit family to a linear
readout and measures the residual sample/generalization behavior with no optimizer search.

## Core idea

For a prime modulus `p`, the ordered pair `(x, y)` is encoded with real cyclic-character product
features. For each frequency `k`, the feature block is:

```text
cos(kx)cos(ky), cos(kx)sin(ky), sin(kx)cos(ky), sin(kx)sin(ky)
```

where phases are scaled by `2π / p`. A linear readout can combine these products into
`cos(k(x+y))` and `sin(k(x+y))`, so the full basis contains an explicit low-dimensional addition
circuit. It still receives only input pairs and labels; it is not handed the target label as a feature.

The experiment compares this representation with two controls:

- `pair_onehot`: exact-pair indicators, an intentionally high-capacity memorizer;
- `separable_onehot`: separate indicators for left and right operands, which lacks pairwise
  interaction terms.

All models are the same one-vs-all ridge classifier. The only moving part is the representation.

## Reproducible command

```bash
PYTHONPATH=src python experiments/modular_character_timescales.py \
  --moduli 31 43 \
  --train-fractions 0.10 0.20 0.35 \
  --seeds 0 1 2 3 4 \
  --output /tmp/modular_character_timescales.csv
```

This writes only a CSV artifact, which should remain uncommitted.

## Results

Mean held-out-pair accuracy over five stratified random splits:

| modulus | train fraction | encoder | k/full | features | mean test acc | min test acc |
|---:|---:|---|---:|---:|---:|---:|
| 31 | 0.10 | character interactions | 1 | 5 | 0.148 | 0.116 |
| 31 | 0.10 | character interactions | 2 | 9 | 0.229 | 0.210 |
| 31 | 0.10 | character interactions | 4 | 17 | 0.460 | 0.440 |
| 31 | 0.10 | character interactions | full | 61 | 1.000 | 1.000 |
| 31 | 0.10 | pair one-hot | full | 961 | 0.032 | 0.032 |
| 31 | 0.10 | separable one-hot | full | 62 | 0.000 | 0.000 |
| 31 | 0.20 | character interactions | 4 | 17 | 0.580 | 0.564 |
| 31 | 0.20 | character interactions | full | 61 | 1.000 | 1.000 |
| 31 | 0.35 | character interactions | 4 | 17 | 0.736 | 0.692 |
| 31 | 0.35 | character interactions | full | 61 | 1.000 | 1.000 |
| 43 | 0.10 | character interactions | 1 | 5 | 0.115 | 0.108 |
| 43 | 0.10 | character interactions | 2 | 9 | 0.186 | 0.174 |
| 43 | 0.10 | character interactions | 4 | 17 | 0.364 | 0.341 |
| 43 | 0.10 | character interactions | full | 85 | 1.000 | 1.000 |
| 43 | 0.10 | pair one-hot | full | 1849 | 0.023 | 0.023 |
| 43 | 0.10 | separable one-hot | full | 86 | 0.000 | 0.000 |
| 43 | 0.20 | character interactions | 4 | 17 | 0.473 | 0.460 |
| 43 | 0.20 | character interactions | full | 85 | 1.000 | 1.000 |
| 43 | 0.35 | character interactions | 4 | 17 | 0.548 | 0.498 |
| 43 | 0.35 | character interactions | full | 85 | 1.000 | 1.000 |

Chance accuracy is `1 / p`: about 0.032 for `p=31` and 0.023 for `p=43`. Thus, the pair one-hot
model is behaving exactly like a memorizer on unseen pairs despite having far more features than
the full character model.

## Interpretation

This note is the **operand-derived representation baseline**. It differs from
`docs/modular-spectral-probe.md`, whose `addition_fourier_features()` diagnostic
explicitly computes the latent sum coordinate and should be treated as an oracle
split/data-geometry probe. Use them together: first ask whether the split covers
the latent coordinate, then ask whether an operand-derived character family can
solve the task from that split.

The striking result is not that Fourier characters can solve modular addition; that is expected.
The useful part is the diagnostic contrast:

- **Memorization capacity is not the bottleneck.** Pair one-hot has `p²` features, fits training
  pairs perfectly, and still has chance held-out accuracy.
- **A compact interaction basis is sufficient.** Full character interactions use `2p - 1` real
  features and generalize perfectly from sparse stratified observations.
- **Partial character availability gives a graded signal.** Low-frequency truncations do not solve
  the task but rise smoothly with frequency budget and train coverage. This suggests a cheap
  scalar proxy for "how much of the cyclic circuit has emerged" in neural representations.

A concrete next experiment is therefore to train a tiny MLP/transformer on the same splits and,
at checkpoints, regress its hidden states onto these character-interaction channels. If held-out
accuracy jumps only after the hidden state becomes linearly predictive of high-frequency character
blocks, that would connect optimizer-time grokking to explicit spectral circuit acquisition.

## Falsifiable hypotheses

1. **Spectral coverage predicts grokking onset.** In a neural modular-addition run, the number of
   character-interaction channels linearly decodable from hidden activations should rise before or
   during the delayed held-out accuracy transition.
2. **Regularizers that penalize pair memorization should accelerate character coverage.** Weight
   decay or feature-noise interventions should reduce the gap between training accuracy saturation
   and spectral coverage saturation.
3. **Capacity sweeps should cross over when memorizer speed beats character discovery speed.** This
   mirrors the 2026 timescale framing, but the character baseline gives an explicit target for the
   generalization timescale.

## Why this is worth keeping

This is a low-cost research scaffold rather than a finished paper result. It gives future agents or
humans a fast sanity check before launching expensive grokking sweeps: if a proposed task split is
not solved by the character baseline, the issue is probably the data/task design; if it is solved by
the baseline but not by the network, the issue is representation discovery and optimizer dynamics.
