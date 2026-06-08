# Cyclic Representation Probes

Status: `full_research`

## Claim

Modular arithmetic grokking runs should not be launched blind. Cheap cyclic
probes can separate data coverage, representation family, and learned discovery.

This track absorbs three earlier threads:

- Modular spectral split probe.
- Modular character baseline.
- Phase-state tracking.

Phase-state tracking is no longer a standalone project. It is a constructive
cyclic-state boundary condition inside this track.

## Research Question

For modular addition and modular counting tasks, when does the training split
contain enough cyclic structure for an explicit readout to generalize, and when
does a learned model still choose memorization despite the data being sufficient
for the cyclic solution?

## Current Evidence

Oracle split command:

```bash
python experiments/cyclic-representation-probes/modular_spectral_probe.py --modulus 31 --fractions 0.05 0.10 0.20 --seeds 0 1 2 3 --output artifacts/hard_push_modular_spectral.csv
```

Oracle Fourier-probe result:

| fraction | split | mean test accuracy |
| ---: | --- | ---: |
| 0.05 | sum_balanced | 1.000 |
| 0.05 | random | 0.788 |
| 0.05 | operand_block | 0.355 |
| 0.10 | sum_balanced | 1.000 |
| 0.10 | random | 0.946 |
| 0.10 | operand_block | 0.534 |
| 0.20 | sum_balanced | 1.000 |
| 0.20 | random | 1.000 |
| 0.20 | operand_block | 0.798 |

At 5 percent train coverage, sum-balanced splits cover every latent sum and the
oracle Fourier ridge probe generalizes perfectly. Operand-block splits miss 19
of 31 sums and fail hard despite perfect train accuracy. This distinguishes
representation-identifiable splits from splits where the cyclic coordinate is
underdetermined.

Learned-model sanity command:

```bash
python experiments/cyclic-representation-probes/modular_mlp_split_probe.py --modulus 31 --fractions 0.10 0.20 0.35 --seeds 0 1 2 --max-iter 400 --output artifacts/hard_push_modular_mlp_split_probe.csv
```

Tiny ReLU MLP result:

| fraction | split | mean test accuracy | mean missing sums |
| ---: | --- | ---: | ---: |
| 0.10 | random | 0.000 | 1.33 |
| 0.10 | sum_balanced | 0.000 | 0.00 |
| 0.10 | operand_block | 0.024 | 13.00 |
| 0.20 | random | 0.000 | 0.00 |
| 0.20 | sum_balanced | 0.000 | 0.00 |
| 0.20 | operand_block | 0.022 | 5.00 |
| 0.35 | random | 0.000 | 0.00 |
| 0.35 | sum_balanced | 0.000 | 0.00 |
| 0.35 | operand_block | 0.019 | 0.00 |

The MLP reaches 1.000 train accuracy but essentially zero held-out accuracy on
random and sum-balanced splits. That is the useful research gap: latent-sum
coverage is enough for the supplied Fourier representation, but vanilla learned
features still find a memorizing solution.

Phase-state command:

```bash
python experiments/cyclic-representation-probes/phase_state_tracking.py
```

Root-of-unity channels get 1.000 extrapolation accuracy for count mod 2, 3, 5,
and 7, while raw counts and positive exponential features stay near chance on
lengths 65-512. This is not learned recurrence evidence. It says exactly what a
cyclic state channel can represent if supplied.

## Baselines And Controls

- `operand_block`: deliberately bad split with missing latent sums.
- `random`: realistic small split that may miss sums.
- `sum_balanced`: data-geometry control with equal latent-sum coverage.
- `pair_onehot`, `separable_onehot`, and `character_interactions`: memorizing
  vs cyclic feature controls.
- `count` and `positive-exp`: weak non-periodic recurrent-state controls.
- `modular_mlp_split_probe.py`: learned memorization control.

## Literature Anchor

This track is worth keeping because current modular-grokking work is explicitly
about Fourier features, phase alignment, and algorithmic structure:

- [Grokking modular arithmetic](https://arxiv.org/abs/2301.02679)
- [On the Mechanism and Dynamics of Modular Addition](https://arxiv.org/abs/2602.16849)
- [Latent Algorithmic Structure Precedes Grokking](https://arxiv.org/abs/2603.23784)
- [Grokfast](https://arxiv.org/abs/2405.20233)

## Failure Conditions

Give up on this track if checkpointed learned-model sweeps show no relationship
between coverage-card diagnostics, hidden-state character readouts, and learned
generalization across multiple moduli, split families, and seeds.

Do not call it a grokking result until a learned model discovers the relevant
features. Oracle Fourier features and root-of-unity channels are controls.

## Next Full Experiment

Turn `experiments/cyclic-representation-probes/modular_mlp_split_probe.py` into a checkpointed dynamics
study. Log Fourier readout alignment and slow-feature amplification during
training, then compare ordinary training against Grokfast-style slow-gradient
amplification. The question is now sharper: when the data split identifies the
cyclic solution, what optimization pressure makes a learned model choose it
instead of memorization?

