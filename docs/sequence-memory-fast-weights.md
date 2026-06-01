# Fast-weight associative recall: a low-compute research probe

## Motivation

Recent efficient-sequence-model work keeps returning to the same idea in different
clothes: update a compact memory at test time, then read from it later. Linear
Transformers can be viewed as fast-weight programmers; newer test-time memory and
delta-rule variants try to make those memories more useful on long contexts.

This repo now has a deliberately tiny probe for that theme. It asks whether a
compact outer-product memory can recall values associated with random keys when
we train on short sequences and evaluate on longer ones. The point is not to win
a benchmark; it is to make memory failure modes visible in seconds on CPU.

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
4. `gated_fast_weights`: a compact matrix memory with a tiny learned write gate.

## Current result

Command run on 2026-06-01:

```bash
python experiments/sequence_memory/associative_recall_fast_weights.py --epochs 12 --train-size 4096 --test-size 2048
```

Cosine recall from the generated JSON artifact:

| model | 8 pairs | 16 pairs | 32 pairs | 64 pairs |
| --- | ---: | ---: | ---: | ---: |
| nearest_neighbor | 0.982 | 0.982 | 0.982 | 0.982 |
| recency_biased | 0.982 | 0.982 | 0.982 | 0.982 |
| delta_fast_weights | 0.910 | 0.818 | 0.644 | 0.420 |
| gated_fast_weights | 0.891 | 0.807 | 0.693 | 0.564 |

Interpretation: the compact fast-weight memories are clearly capacity-limited.
The learned scalar/vector gate helps at the longest tested contexts relative to
the residual delta rule, but it does not close the gap to explicit key storage.
This is a useful negative result because it says a tiny surprise/write gate alone
is not enough; the next idea should target interference directly.

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
