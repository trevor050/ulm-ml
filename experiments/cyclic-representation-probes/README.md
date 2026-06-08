# Cyclic Representation Probes

## Question

Can modular arithmetic generalization be explained through cyclic
representations, split coverage, and whether learned models actually discover
the useful latent coordinate?

## Verdict

Yes, keep going.

## Answer So Far

Fourier/spectral probes can solve held-out modular addition when the train split
covers the latent sum coordinate. Learned MLP probes still memorize train splits
and fail held-out addition, so the useful gap is oracle representation versus
learned representation.

## Interesting Bit

The split geometry can look solved to an oracle feature map while still not
being discovered by a learned model.

## Commands

```bash
PYTHONPATH=src python experiments/cyclic-representation-probes/modular_spectral_probe.py --modulus 31 --fractions 0.05 0.10 0.20 --seeds 0 1 2 3
PYTHONPATH=src python experiments/cyclic-representation-probes/modular_mlp_split_probe.py --modulus 31 --fractions 0.10 0.20 0.35 --seeds 0 1 2 --max-iter 400
PYTHONPATH=src python experiments/cyclic-representation-probes/modular_character_timescales.py --moduli 31 43
PYTHONPATH=src python experiments/cyclic-representation-probes/phase_state_tracking.py
```

## Deeper Notes

- `docs/full-research/cyclic-representation-probes.md`
- `docs/modular-spectral-probe.md`
- `docs/research-brief-character-timescales.md`
- `docs/phase-state-tracking.md`
