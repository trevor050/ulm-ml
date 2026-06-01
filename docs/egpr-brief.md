# Entropy-Gated Prototype Replay (EGPR)

## One-line idea

When adapting a classifier to unlabeled shifted test data, keep the source model frozen and update only a small prototype memory with low-entropy, high-confidence target examples; then interpolate frozen source logits with prototype-similarity logits at prediction time.

## Why this is worth trying

Recent test-time adaptation work keeps returning to the same tension: entropy minimization and pseudo-label updates can recover from covariate shift, but updating too aggressively can amplify wrong predictions and collapse. A May 2026 arXiv paper on autoregressive test-time entropy minimization frames entropy objectives as a unified combination of token-level policy-gradient and entropy terms, emphasizing that heuristic partial objectives can behave differently from the exact objective. A 2026 Pattern Recognition article on CLIP-guided entropy dynamics also highlights overconfident collapse as a central failure mode for entropy-minimization TTA in harsh visual conditions.

EGPR is a deliberately small alternative for low-compute research:

1. **Do not update the classifier.** Keep the source decision boundary intact.
2. **Adapt memory, not weights.** Maintain one feature-space prototype per class.
3. **Gate replay by source entropy.** Only examples below a source-calibrated entropy quantile and above a confidence floor can move prototypes.
4. **Use interpolation.** Final logits are a convex combination of frozen source logits and cosine-similarity prototype logits.

This makes the method cheap, auditable, and resistant to catastrophic online drift. It is not meant to beat deep TTA systems immediately; it is meant to be a fast probe for whether target-domain confidence geometry contains enough information to adapt safely.

## Minimal experiment in this repo

The runnable scaffold uses `sklearn.datasets.load_digits` as a source task, creates target-domain shifts with deterministic corruptions, trains a fixed PCA + logistic-regression source model, and compares:

- **Source-only:** no target adaptation.
- **Prototype no-adapt:** source/prototype logit interpolation with frozen source prototypes, isolating the prototype head from online adaptation.
- **All replay:** prototype updates from every target example, bypassing the entropy gate.
- **EGPR:** entropy/confidence-gated prototype updates.

Command:

```bash
python experiments/egpr_digits_tta.py --seeds 0 1 2 3 4 --output artifacts/egpr_digits_tta.json
```

Five-seed accuracy mean +/- std on 2026-06-01:

| Corruption | Source-only | Prototype no-adapt | All replay | EGPR |
|---|---:|---:|---:|---:|
| Gaussian noise | 0.372 +/- 0.054 | **0.377 +/- 0.054** | 0.353 +/- 0.051 | 0.339 +/- 0.052 |
| Top-left occlusion | **0.948 +/- 0.010** | 0.946 +/- 0.009 | 0.947 +/- 0.009 | 0.947 +/- 0.010 |
| Brightness shift | 0.461 +/- 0.227 | **0.466 +/- 0.224** | 0.459 +/- 0.227 | 0.406 +/- 0.183 |
| Mixed shift | 0.299 +/- 0.065 | **0.301 +/- 0.065** | 0.285 +/- 0.063 | 0.278 +/- 0.059 |

The result is intentionally humbling: online prototype adaptation usually hurts
on this toy benchmark, and a frozen prototype head is often as good as or better
than replay. That makes EGPR more valuable as a scaffold for **predicting when
online adaptation is unsafe without labels** than as an accuracy method.

## Research hypotheses opened by the first run

1. **Prototype trust should be shift-aware.** The fixed `source_logit_weight=0.65` is too blunt. A per-batch trust coefficient based on entropy drift or class-balance drift may prevent EGPR from hurting on mixed/noisy shifts.
2. **Acceptance needs class-balance regularization.** Current gating can accept many samples from already-easy classes. A Dirichlet-smoothed quota or inverse-source-frequency replay may reduce prototype over-specialization.
3. **Feature whitening may be the bottleneck.** PCA whitening makes cosine prototypes convenient but may also magnify corruption artifacts. Compare whitened PCA, unwhitened PCA, random projections, and raw scaled pixels.
4. **Replay should model covariance.** One centroid per class is fragile for multimodal digits. A tiny diagonal covariance or top-k exemplar buffer could preserve the low-compute spirit while improving robustness.
5. **Failure prediction may be the publishable core.** Even when EGPR does not improve accuracy, its acceptance histogram and entropy drift could predict when online adaptation is unsafe.

## Next concrete experiments

- Sweep `entropy_quantile`, `confidence_floor`, `source_logit_weight`, and `prototype_logit_scale` over 5 seeds and report mean +/- std.
- Add a `--feature-space` flag for whitened PCA, unwhitened PCA, random projection, and scaled raw pixels.
- Log accepted-class histograms and compare them with target predictions to quantify class-collapse risk.
- Add a no-label online safety score: if target entropy drift is high and accepted-class effective number is low, fall back to source-only.

## References checked

- Rethinking Entropy Minimization in Test-Time Adaptation for Autoregressive Models, arXiv:2605.08186, published May 2026.
- CED: CLIP-guided entropy dynamics for robust test-time adaptation in harsh visual conditions, Pattern Recognition, volume 177, September 2026 article metadata.
