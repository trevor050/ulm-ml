# Modular Spectral Split Probe

Portfolio status: part of `full_research` track
`docs/full-research/cyclic-representation-probes.md`.

## One-sentence claim

Before spending long runs on grokking-style modular arithmetic, measure whether the
train split covers the latent Fourier coordinate that the generalizing algorithm will
use. A sum-balanced split can make a closed-form Fourier probe generalize perfectly
from only 3% of the table, while random splits need substantially more examples and
operand-block splits remain badly biased.

## Why this is worth doing now

Recent grokking work keeps pointing at the same pressure point: models first memorize,
then slowly consolidate an algorithmic/Fourier circuit. Grokfast frames the training
trajectory as fast memorizing components plus slow generalizing components and reports
large speedups from amplifying slow gradients (<https://arxiv.org/abs/2405.20233>).
Grokked Transformers are Implicit Reasoners shows that transformers can learn implicit
reasoning only after extended post-overfitting training, and that circuit structure
matters for systematicity (<https://arxiv.org/abs/2405.15071>). The ICML 2024 modular
addition theory paper argues that early kernel-like behavior cannot solve modular
addition from small samples, while later feature-learning dynamics can
(<https://arxiv.org/abs/2407.12332>). A March 2026 ReLU-MLP note reports that latent
Fourier/phase structure can be present even before the validation curve visibly groks
(<https://arxiv.org/abs/2603.23784>).

That suggests a cheap pre-flight question: if the eventual algorithm is Fourier-like,
are we even giving the model a train split that identifies the Fourier coordinate?

## Hypothesis

For modular addition `(a + b) mod p`, many train/test splits with the same number of
examples are not equivalent. The decisive low-compute diagnostic is coverage of the
latent sum residue `s = (a + b) mod p`, not just the headline fraction of the `p^2`
input table.

Predictions:

1. A split with at least one example per latent sum residue should let a Fourier probe
   recover the whole table at extremely small train fractions.
2. Random splits should improve as the coupon-collector probability of missing a sum
   residue falls.
3. Operand-local splits should look deceptively data-rich but generalize poorly because
   they under-cover latent sum residues and condition the Fourier design badly.

## Implemented experiment

The reusable module `src/ulm_ml/modular_spectral.py` implements:

- full modular-addition grid generation;
- three train split families: `random`, `sum_balanced`, and the intentionally bad
  `operand_block` control;
- latent sum coverage diagnostics (`missing_sums`, coefficient of variation, Fourier
  design condition number);
- a closed-form ridge probe over oracle real Fourier features of `(a + b) mod p`;
- a sweep helper for reproducible CPU-only experiments.

Important boundary: this probe explicitly computes the latent sum coordinate.
It is a split/data-geometry diagnostic, not evidence that a neural model learned
the coordinate. The companion character-interaction baseline in
`docs/research-brief-character-timescales.md` is the operand-derived
representation control.

The runnable script is `experiments/modular_spectral_probe.py`.

Command used for the first run:

```bash
PYTHONPATH=src python experiments/modular_spectral_probe.py \
  --modulus 31 \
  --fractions 0.03 0.05 0.08 0.10 0.15 \
  --seeds 0 1 2 3 4 5 6 7 8 9
```

The generated CSV is intentionally kept under ignored `artifacts/` and is not committed.

The script now also prints coverage cards such as:

```text
split=sum_balanced fraction=0.032 train_size=31 missing_sums=0 sum_count_cv=0.000 design_condition=1.41 train_acc=1.000 test_acc=1.000
```

Those cards are the intended pre-flight artifact for future grokking runs.

## First result

Modulus `p=31`, 10 seeds per fraction:

| train fraction | random test acc | sum-balanced test acc | operand-block test acc |
|---:|---:|---:|---:|
| 0.03 | 0.633 ± 0.068 | **1.000 ± 0.000** | 0.300 ± 0.000 |
| 0.05 | 0.783 ± 0.038 | **1.000 ± 0.000** | 0.355 ± 0.000 |
| 0.08 | 0.916 ± 0.039 | **1.000 ± 0.000** | 0.474 ± 0.000 |
| 0.10 | 0.953 ± 0.032 | **1.000 ± 0.000** | 0.534 ± 0.000 |
| 0.15 | 0.996 ± 0.011 | **1.000 ± 0.000** | 0.696 ± 0.000 |

This is not a claim that neural networks will instantly grok under sum-balanced
sampling. It is a sharper screening result: a split can be too weak to identify the
algorithmic coordinate even for the Fourier model that we believe grokked networks
approximate. Therefore, future neural grokking experiments should report latent-coordinate
coverage alongside train fraction.

## Why this may become a publishable thread

A lot of grokking experiments treat the training subset as a random fraction of the
operation table. This probe suggests a complementary experimental axis:

- **data geometry:** balanced vs random vs adversarial coverage of latent algebraic
  coordinates;
- **optimizer geometry:** vanilla AdamW vs Grokfast-like slow-gradient amplification;
- **model geometry:** MLP, one-layer transformer, and small decoder-only transformer;
- **mechanistic readout:** whether Fourier/phase structure appears earlier under
  latent-balanced sampling.

The publishable question is not “can a Fourier probe solve modular addition?” The
question is whether latent-coordinate coverage shortens, removes, or qualitatively
changes the memorization-to-generalization transition in neural models.

## Next experiments

1. Train a tiny MLP on the same three split families and log validation accuracy,
   train accuracy, weight Fourier spectra, and time-to-95% validation accuracy.
2. Cross the split family with a Grokfast-style gradient filter to test whether balanced
   data and slow-gradient amplification are additive or redundant.
3. Replace modular addition with modular multiplication and affine composition tasks;
   define analogous latent-coordinate coverage diagnostics.
4. Build a split generator that targets a desired Fourier design condition number rather
   than a hand-written `sum_balanced` rule.
5. Report a standardized “latent coverage card” for any grokking run: fraction, missing
   latent residues, sum-count CV, and Fourier design condition number.
