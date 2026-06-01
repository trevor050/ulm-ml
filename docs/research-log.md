# Research Log

Use this as the compact source of truth for experiments that matter.

## 2026-06-01

- Initialized the repository as a Codex-friendly ML research staging ground.
- Started a CPU-only grokking diagnostic project around modular-arithmetic character interactions.
  The first result is documented in `docs/research-brief-character-timescales.md`: full Fourier
  interaction features solve held-out modular-addition pairs from 10% of the table for p=31 and
  p=43, while pair one-hot memorization stays at chance. No external datasets or committed
  artifacts were added.
- Added a CPU-only modular spectral split probe. Initial p=31 sweep shows sum-balanced latent residue coverage gives 1.000 Fourier-probe test accuracy at 3% train fraction, while random splits average 0.633 and operand-block splits 0.300; see `docs/modular-spectral-probe.md`.
