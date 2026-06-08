# Doubt-TTS Fresh Overlap-Gate Holdout Analysis

Status: fresh locked/blinded 48-row holdout for the preregistered recent-assertion overlap gate.

The semantic gate was frozen from the prior 161-row evidence-pack diagnostic before this fresh split was generated. It may use only blind question text plus the two Gemma policy outputs; labels and source/evidence fields are used only for scoring.

Caveat: this v1 holdout reuses 10 exact questions from earlier candidate/evidence-pack artifacts, mostly stable controls plus a few event anchors. Treat it as a fresh targeted branch test, not a fully independent paper benchmark. The next rerun should use no exact duplicates; an attempted rerun was blocked when the Windows Ollama server became unstable after GPU discovery.

## Accuracy

| method | selected | joint | validity | compute | direct | premise | retrieve-answer | retrieve-premise | p vs deterministic |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| deterministic_two_axis | - | 32/48 | 34/48 | 32/48 | 12/12 | 1/12 | 10/12 | 9/12 | - |
| gemma_action_discriminating | - | 29/48 | 47/48 | 30/48 | 11/12 | 12/12 | 6/12 | 0/12 | 0.7111 |
| gemma_overlap_guard | - | 43/48 | 47/48 | 43/48 | 11/12 | 10/12 | 12/12 | 10/12 | 0.01921 |
| qwen_action_discriminating | - | 22/48 | 39/48 | 22/48 | 11/12 | 11/12 | 0/12 | 0/12 | 0.1102 |
| qwen_overlap_guard | - | 34/48 | 39/48 | 38/48 | 11/12 | 11/12 | 11/12 | 1/12 | 0.8388 |
| self_gate | action:36, overlap:12 | 37/48 | 48/48 | 37/48 | 11/12 | 10/12 | 6/12 | 10/12 | 0.4244 |
| hand_assertion_gate | action:36, overlap:12 | 37/48 | 48/48 | 37/48 | 11/12 | 10/12 | 6/12 | 10/12 | 0.4244 |
| frozen_semantic_recent_assertion_gate | action:38, overlap:10 | 39/48 | 48/48 | 39/48 | 11/12 | 12/12 | 6/12 | 10/12 | 0.2295 |
| oracle_gold_overlap_gate | action:36, overlap:12 | 39/48 | 47/48 | 39/48 | 11/12 | 12/12 | 6/12 | 10/12 | 0.2295 |
| oracle_delta_gate | action:32, overlap:16 | 45/48 | 48/48 | 45/48 | 11/12 | 12/12 | 12/12 | 10/12 | 0.004425 |

## Interpretation

- The decisive row is `frozen_semantic_recent_assertion_gate`: if it clears deterministic and preserves direct/premise controls, the post-hoc gate has survived its first fresh split.
- `oracle_gold_overlap_gate` is the target ceiling for a perfect detector of retrieval-backed premise-check cases; it is not deployable.
- `oracle_delta_gate` is an even looser upper bound that can choose whichever policy happens to be correct row by row.
- A weak result should be treated as a method failure, not patched by editing the gate on this split.

