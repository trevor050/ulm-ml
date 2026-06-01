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
