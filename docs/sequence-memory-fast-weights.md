# Fast-weight associative recall: a low-compute research probe

Portfolio status: `full_research`. The hardened interference framing is in
`docs/full-research/sequence-memory-interference.md`.

## Motivation

Recent efficient-sequence-model work keeps returning to the same idea in different
clothes: update a compact memory at test time, then read from it later. Linear
Transformers can be viewed as fast-weight programmers; newer test-time memory and
delta-rule variants try to make those memories more useful on long contexts.

This repo now has a deliberately tiny probe for that theme. It asks whether a
compact outer-product memory can recall values associated with random keys when
we train on short sequences and evaluate on longer ones. The point is not to win
a benchmark; it is to make memory failure modes visible quickly.

Useful starting references:

- Schlag et al., 2021, "Linear Transformers Are Secretly Fast Weight Programmers":
  https://arxiv.org/abs/2102.11174
- Behrouz et al., 2024/2025, "Titans: Learning to Memorize at Test Time":
  https://arxiv.org/abs/2501.00663
- Yang et al., 2024, "Gated Delta Networks: Improving Mamba2 with Delta Rule":
  https://arxiv.org/abs/2412.06464

## Task

Each synthetic example contains `N` random unit-norm key/value pairs and a final
query key. The target is the value paired with that key. Training uses `N=8`; the
main extrapolation check evaluates `N in {8, 16, 32, 64}`.

Implemented memories:

1. `nearest_neighbor`: softmax lookup over all keys. This is the non-compact upper
   foil because it keeps the whole sequence.
2. `recency_biased`: the same lookup with a late-token logit bias, included to
   expose pathological recency shortcuts.
3. `delta_fast_weights`: a compact matrix memory updated with an online residual
   delta rule.
4. `scalar_fast_weights`: the same outer-product memory with a fixed global write
   scale. This checks whether a learned gate is doing more than shrinking writes.
5. `orthogonalized_fast_weights`: an online Gram-Schmidt write rule that stores
   only key components not already in the compact basis.
6. `gated_fast_weights`: a compact matrix memory with a tiny learned write gate.

## Current result

Command run on 2026-06-01:

```bash
python experiments/sequence-memory-interference/associative_recall_fast_weights.py --epochs 12 --train-size 4096 --test-size 2048
```

Cosine recall from the generated JSON artifact:

| model | 8 pairs | 16 pairs | 32 pairs | 64 pairs |
| --- | ---: | ---: | ---: | ---: |
| nearest_neighbor | 0.982 | 0.982 | 0.982 | 0.982 |
| recency_biased | 0.982 | 0.982 | 0.982 | 0.982 |
| delta_fast_weights | 0.910 | 0.818 | 0.644 | 0.420 |
| gated_fast_weights | 0.891 | 0.807 | 0.693 | 0.564 |

The current script also supports `--key-dims` and records `pairs_per_key_dim`.
A small smoke sweep with 2 training epochs showed that `gated_fast_weights` and
`scalar_fast_weights` are nearly tied, while both degrade smoothly as
`pairs/key_dim` rises:

| key dim | model | 8 pairs | 16 pairs | 32 pairs | 64 pairs |
| ---: | --- | ---: | ---: | ---: | ---: |
| 16 | scalar_fast_weights | 0.832 | 0.703 | 0.573 | 0.428 |
| 16 | orthogonalized_fast_weights | **0.857** | 0.643 | 0.307 | 0.130 |
| 16 | gated_fast_weights | 0.830 | 0.699 | 0.572 | 0.429 |
| 32 | scalar_fast_weights | 0.890 | 0.806 | 0.686 | 0.582 |
| 32 | orthogonalized_fast_weights | **0.919** | **0.831** | 0.627 | 0.348 |
| 32 | gated_fast_weights | 0.888 | 0.805 | 0.686 | 0.580 |

Interpretation: compact fast-weight memories are clearly interference-limited.
The learned gate may help in some longer training runs, but the scalar baseline
shows that much of the behavior is explained by write scaling. The next idea
should target interference directly, not just add another tiny gate. The
orthogonalized baseline confirms the diagnosis but also exposes a new failure:
once the online basis saturates, additional writes are discarded or mangled, so
long-context recall still collapses.

## Hypotheses worth testing next

1. **Online orthogonalization / whitening:** update keys into a basis with reduced
   cross-talk before the outer-product write. This is the most direct response to
   the observed length degradation.
2. **Feature dimension scaling law:** sweep `key_dim` and fit recall against
   `N / key_dim`. If the curves collapse, this toy task can quantify compact-memory
   capacity independently of model scale.
3. **Surprise-gated delta rule:** combine the residual value error from the delta
   rule with a learned gate that is trained to maximize long-context validation
   recall rather than short-context MSE.
4. **Learned projections:** replace random keys/values with a tiny neural encoder
   and train end-to-end. Only do this after the analytic memory rules look sane.

## Why this might matter

The result is small, but it gives us a cheap falsification harness for a class of
long-context memory claims. A proposed recurrent/linear-attention update can be
ported into this script and judged by whether it preserves recall when context
length grows beyond training length. If it fails here, spending GPU time on a
language-model implementation is probably premature.
