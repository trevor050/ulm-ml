# Prior-Anchored Conservative Entropy for Bias-Only Test-Time Adaptation

Date: 2026-06-01

Portfolio verdict: **given up as standalone research**. Keep PACE only as a
narrow prior-drift diagnostic baseline. See `docs/given-up/pace-bias-tta.md`.

## One-line claim

A class-bias-only test-time adapter with a conservative entropy floor and a weak source-prior anchor is a cheap, auditable way to repair **logit prior drift** without touching model weights; on a 5-seed corrupted/digit-logit benchmark it improved balanced-stream accuracy from **89.2% source** to **90.9% PACE**, while exposing an important negative control: image corruptions are not fixed by bias updates alone.

## Motivation from recent work

Test-time adaptation (TTA) commonly adapts a pretrained classifier on unlabeled target batches. TENT framed this as minimizing prediction entropy at inference time. Recent 2025 work keeps finding the same failure mode: plain entropy minimization can become overconfident or collapse. COME (ICLR 2025) addresses this by conservatively minimizing entropy with uncertainty-aware lower bounds, while Ranked Entropy Minimization (ICML 2025) explicitly targets collapse in continual settings.

Sources checked on 2026-06-01:

- TENT: Wang et al., "Tent: Fully Test-Time Adaptation by Entropy Minimization," ICLR 2021. https://arxiv.org/abs/2006.10726
- COME: Zhang et al., "COME: Test-time Adaption by Conservatively Minimizing Entropy," ICLR 2025. https://proceedings.iclr.cc/paper_files/paper/2025/hash/2ea18fdc667e0ef2ad82b2b4d65147ad-Abstract-Conference.html
- Ranked Entropy Minimization: Han et al., ICML 2025. https://proceedings.mlr.press/v267/han25e.html

The gap pursued here is narrower than those papers: if production constraints forbid backbone updates, can we still get a useful TTA primitive by adapting only the final class-bias vector?

## Method: PACE-bias

Given a frozen classifier's logits `z(x)` and a batch-level bias vector `b`, adapt predictions as:

```text
p_i = softmax(z(x_i) + b)
```

The proposed objective is:

```text
L_PACE = mean_i max(H(p_i), h_floor) + lambda * KL(mean_confident(p_i) || source_prior)
```

Implementation details in this repo:

- `source`: no adaptation.
- `entropy`: direct entropy minimization.
- `conservative`: entropy minimization only for examples above an entropy floor.
- `pace`: conservative entropy plus a KL penalty that keeps the confident subset's mean predicted class distribution near the smoothed source prior.
- The adapter is NumPy-only and updates only one shared class-bias vector per unlabeled batch.

Why this is interesting:

1. It is cheap enough for experimentation and constrained deployments.
2. It is interpretable: the learned vector is a per-class calibration correction.
3. It separates two shift types: label/logit-prior drift, where bias updates are plausible, from feature corruption, where they should not be expected to solve the problem.

## Experiment

Script: `experiments/pace-bias-tta/pace_bias_tta.py`

Dataset and model:

- `sklearn.datasets.load_digits` 8x8 digits.
- Stratified train/test split with 45% test.
- StandardScaler + multinomial logistic regression (`C=0.35`, `max_iter=2000`).
- Five seeds: `0 1 2 3 4`.
- Batch size: `64`.

Shift scenarios:

1. `logit_prior_drift`: clean test images, but a fixed monotone class-bias drift is added to logits. This simulates deployment-time class calibration drift.
2. `image_corruption`: rotated/noisy/dimmed images. This is a negative control because a class-bias vector cannot restore missing or distorted features.

Stream scenarios:

1. `balanced`: class prior approximately matches training.
2. `head_heavy`: low digits are oversampled, creating a target prior that conflicts with the source prior.

Run command:

```bash
PYTHONPATH=src python experiments/pace-bias-tta/pace_bias_tta.py --seeds 0 1 2 3 4 --out-dir artifacts/pace_bias_tta
```

## Results

Mean accuracy over five seeds:

| Shift | Stream | Source | Entropy | Conservative | PACE |
| --- | --- | ---: | ---: | ---: | ---: |
| logit_prior_drift | balanced | 0.892 | 0.903 | 0.907 | **0.909** |
| logit_prior_drift | head_heavy | 0.929 | **0.934** | 0.932 | 0.932 |
| image_corruption | balanced | 0.303 | 0.289 | 0.287 | **0.304** |
| image_corruption | head_heavy | 0.372 | 0.359 | 0.356 | **0.373** |

Mean NLL over five seeds:

| Shift | Stream | Source | Entropy | Conservative | PACE |
| --- | --- | ---: | ---: | ---: | ---: |
| logit_prior_drift | balanced | 0.341 | 0.307 | 0.294 | **0.287** |
| logit_prior_drift | head_heavy | 0.201 | **0.191** | 0.203 | 0.200 |
| image_corruption | balanced | **4.940** | 5.187 | 5.348 | 5.043 |
| image_corruption | head_heavy | **4.461** | 4.633 | 4.700 | 4.469 |

## Interpretation

The positive result is small but real in the targeted setting: when the stream prior is balanced and the shift is an additive logit drift, PACE is best on accuracy and NLL. The class-prior anchor appears to correct class-frequency distortion better than entropy-only adaptation: the predicted-prior L1 distance from the source prior falls from `0.191` for source logits to `0.157` for PACE in the balanced logit-drift setting.

The negative controls are equally useful:

- Under image corruption, none of the bias-only adapters meaningfully improve accuracy or NLL. This is expected and supports the hypothesis that the method is a calibration/prior-drift tool, not a feature-restoration tool.
- Under `head_heavy` target streams, PACE is not best because its source-prior anchor is partially misspecified. This is the right failure mode: source-prior anchoring should be used when target priors are expected to remain close, or replaced by an online prior estimator when class balance can move.

## Research value and next steps

This is not a finished paper result, but it is a clean seed for one:

1. **Theoretical angle:** bias-only adaptation under label/logit-prior shift can be related to intercept correction and black-box label-shift estimation. PACE can be framed as a conservative, regularized online estimator.
2. **Better estimator:** replace the fixed source prior with an EMA prior that moves only when confidence and entropy-rank diagnostics agree.
3. **Realistic benchmark:** test on CIFAR-C or ImageNet-C with a frozen linear probe / CLIP zero-shot logits, where bias-only adaptation is deployment-relevant.
4. **Safety criterion:** abstain from adapting when the batch's corruption signature looks like feature damage rather than class-bias drift. The image-corruption negative control suggests a simple diagnostic: if prior matching requires large bias movement without NLL/entropy-rank consistency, do not adapt.

## Reproducibility notes

The experiment writes CSV outputs to `artifacts/pace_bias_tta/`, which is intentionally gitignored. The committed code and this report contain the runnable recipe and summarized results, but not generated artifacts.
