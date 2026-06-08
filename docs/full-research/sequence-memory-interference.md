# Sequence-Memory Interference

Status: `full_research`

## Claim

Compact fast-weight memories are useful here as failure objects. They expose how
outer-product, scalar, delta, gated, and orthogonalized update rules degrade as
associative-recall load approaches or exceeds key dimension. The honest result
right now is negative: local nearest-neighbor retrieval is much stronger on this
toy task.

## Research Question

How do compact write-update memories fail under associative-recall load, and
which update rules postpone interference as `pairs/key_dim` increases?

## Current Evidence

Command:

```bash
python experiments/sequence-memory-interference/associative_recall_fast_weights.py --epochs 8 --key-dims 16 32 64 --train-size 2048 --test-size 1024 --output artifacts/hard_push_sequence_memory.json
```

Selected cosine accuracy:

| key dim | pairs | pairs/key_dim | nearest neighbor | scalar fast weights | orthogonalized | delta | gated |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 8 | 0.50 | 0.982 | 0.825 | 0.855 | 0.828 | 0.825 |
| 16 | 64 | 4.00 | 0.982 | 0.430 | 0.146 | 0.236 | 0.429 |
| 32 | 8 | 0.25 | 0.982 | 0.892 | 0.919 | 0.913 | 0.892 |
| 32 | 64 | 2.00 | 0.982 | 0.573 | 0.336 | 0.410 | 0.572 |
| 64 | 8 | 0.12 | 0.982 | 0.930 | 0.948 | 0.946 | 0.930 |
| 64 | 64 | 1.00 | 0.981 | 0.673 | 0.618 | 0.623 | 0.673 |

Orthogonalization helps at low load but collapses once the compact basis
saturates. Delta updates are competitive at low load and degrade more smoothly
than the orthogonalized rule at high load. Gating, as currently learned, mostly
tracks scalar fast weights rather than solving interference.

## Baselines And Controls

- `nearest_neighbor`: non-compact retrieval ceiling for this synthetic task.
- `recency_biased`: verifies that recency is not the main hidden variable.
- `scalar_fast_weights`: minimal compact outer-product baseline.
- `delta_fast_weights`: error-correcting write rule.
- `orthogonalized_fast_weights`: capacity-aware hand-built control.
- `gated_fast_weights`: tiny learned write gate.

## Literature Anchor

This track survives because memory mechanisms are currently live research, and
small failure probes help distinguish claims about "long-term memory" from
interference reality:

- [Titans: Learning to Memorize at Test Time](https://arxiv.org/abs/2501.00663)
- [Gated Delta Networks](https://arxiv.org/abs/2412.06464)

## Failure Conditions

Give up on this track if every compact update rule remains dominated by simple
nearest-neighbor retrieval after adding a task where exact non-compact lookup is
not allowed or not cheap. A benchmark that only proves "attention retrieves
better than compressed memory" is not enough.

## Next Full Experiment

Add a constrained retrieval setting where nearest-neighbor memory must use a
small reservoir or compressed candidate set. Then compare whether delta/gated
rules offer a meaningful accuracy-memory tradeoff instead of losing to a full
lookup table.

