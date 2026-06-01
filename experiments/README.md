# Experiments

Put runnable experiment scripts and configs here. Keep stable reusable logic in `src/ulm_ml/`.

## Modular character timescales

`modular_character_timescales.py` is a CPU-only diagnostic for modular-arithmetic grokking
experiments. It compares memorizing pair one-hot features, separable one-hot features, and
cyclic-character interaction features under the same ridge readout. Example:

```bash
PYTHONPATH=src python experiments/modular_character_timescales.py --moduli 31 43
```

Results and interpretation are summarized in `docs/research-brief-character-timescales.md`.

## Portfolio commands

Representative active research commands:

```bash
python experiments/modular_spectral_probe.py --modulus 31 --fractions 0.05 0.10 0.20 --seeds 0 1 2 3
python experiments/modular_mlp_split_probe.py --modulus 31 --fractions 0.10 0.20 0.35 --seeds 0 1 2 --max-iter 400
python experiments/symmetry_augmented_sparse_recovery.py
python experiments/sequence_memory/associative_recall_fast_weights.py --epochs 8 --key-dims 16 32 64 --train-size 2048 --test-size 1024
```

The current binary project map is in `docs/research-portfolio.md`.
