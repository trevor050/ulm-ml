# Reliability-Action Routing for Selective Question Answering

Version: 2026-06-02 v8 Gemma transfer-v4 draft

Status: current paper-style draft aligned with the v29 evidence packet. This is a development-paper draft, not a final paper claim. The 300-row v3 scaffold and transfer stress sets are generated and manual-audit-required.

## Abstract

Selective question answering is usually evaluated as a scalar decision: answer or abstain, retrieve or skip retrieval, spend more or less test-time compute. That framing hides a practical reliability failure: a model can recognize that a question is risky while still choosing the wrong safety action. We introduce reliability-action routing, a two-axis protocol that separately labels answer validity and the computation required before response. The compute-action space distinguishes direct answering, premise checking, retrieval to answer, retrieval to check a premise, deterministic verification, and clarification.

On a 300-row cue-balanced development scaffold, Gemma4-26B action-discriminating routing reaches 201/300 joint accuracy and preserves direct-answer controls, 45/45 direct compute, but nearly misses retrieval-backed premise checks, 6/60 joint. A Gemma4-26B overlap-guard prompt repairs that branch, 47/60 joint, but damages direct controls, 27/45 direct compute. A policy-output selector recovers a mixed-distribution frontier: 246/300 joint, 260/300 validity, 251/300 compute, 45/45 direct compute, and 47/60 retrieval-premise joint.

A development-only verifier/source overlay reaches 269/300 on generated v3, but stress tests prevent overclaiming it. Lexical gates miss 11/12 deterministic paraphrase positives. A qwen3.5:9b overlap-guard live stress run reaches 13/30 joint. An after-inspection phrase module reaches 30/30 on original stress but collapses to 8/38 on transfer-v1. Module-general-v1 reaches 38/38 transfer-v1 but only 23/38 transfer-v2. Source-role module v3 reaches 41/42 on source-role transfer-v3 and 50/50 on fresh transfer-v4. Live transfer-v4 baselines show the target is not trivial: qwen3:14b reaches 34/50, while Gemma4-26B reaches 44/50. Gemma solves ambiguity on this split, 16/16, but still misses source false-premise/premise-check rows, 5/8, and local deterministic verification, 6/8. The current contribution is therefore a sharper benchmark and falsifiable method target, not a solved controller.

## 1. Thesis

The original Doubt-TTS hypothesis, asking the model to doubt or challenge itself, failed as a robust method. The useful object is action selection.

Reliability-action routing labels two axes:

```json
{
  "validity": "answerable | false_premise | ambiguous",
  "compute_action": "direct_answer | premise_check | retrieve_then_answer | retrieve_then_premise_check | deterministic_verify | clarify"
}
```

Primary score is joint validity/action correctness. This penalizes a model that knows a row is risky but chooses the wrong reliability operation.

## 2. Prior-Art Boundary

The contribution is not generic adaptive retrieval. Selective QA and abstention already evaluate when systems should answer ([Jurayj et al., 2025](https://arxiv.org/abs/2502.13962); [Kirichenko et al., 2025](https://arxiv.org/abs/2506.09038)). Adaptive RAG and reasoning-time retrieval already decide when to retrieve ([Wu et al., 2025](https://arxiv.org/abs/2504.01018); [Guo et al., 2026](https://arxiv.org/abs/2604.26649)). Retrieval-as-generation and retriever routing make controller architecture itself non-novel ([Li et al., 2026](https://arxiv.org/abs/2604.11407); [Zhao et al., 2026](https://arxiv.org/abs/2604.22849)). Confidence-aware reranking and premise verification are direct adjacent components ([Song et al., 2026](https://arxiv.org/abs/2605.04495); [Qin et al., 2025](https://arxiv.org/abs/2504.06438)).

The remaining wedge is typed reliability-action evaluation. Retrieval can answer a fact or check a premise. Verification can be local deterministic computation or source-backed premise validation. Clarification is not abstention.

## 3. Development Scaffold

The current v3 scaffold has 300 rows:

| compute action | count |
|---|---:|
| `direct_answer` | 45 |
| `premise_check` | 45 |
| `retrieve_then_answer` | 45 |
| `retrieve_then_premise_check` | 60 |
| `deterministic_verify` | 45 |
| `clarify` | 60 |

Validity counts are 135 answerable, 105 false-premise, and 60 ambiguous. The blind export uses opaque IDs and passes blind-field leakage checks. Shortcut baselines are low enough for development use: oracle template-family majority reaches 60/300 and legacy keyword routing reaches 87/300.

The caveat is central: v3 is generated scaffolding. It is not locked evidence.

## 4. Development Frontier

| method | joint | validity | compute | mean cost |
|---|---:|---:|---:|---:|
| Gemma4-26B action-discriminating | 201/300 | 246/300 | 214/300 | 1.78 |
| Gemma4-26B overlap-guard | 232/300 | 254/300 | 237/300 | 2.38 |
| Gemma4-26B learned policy selector | 246/300 | 260/300 | 251/300 | 2.17 |
| deterministic-verifier overlay only | 262/300 | 275/300 | 267/300 | 2.22 |
| source-confidence overlay only | 253/300 | 260/300 | 258/300 | 2.25 |
| verifier/source overlay full | 269/300 | 275/300 | 274/300 | 2.30 |

Branch/cost read:

| method | direct compute | retrieval-premise joint | source-required joint | no-source joint | wasted retrieval | missed retrieval |
|---|---:|---:|---:|---:|---:|---:|
| action-discriminating | 45/45 | 6/60 | 28/105 | 173/195 | 0 | 54 |
| overlap-guard | 27/45 | 47/60 | 81/105 | 151/195 | 17 | 9 |
| learned selector | 45/45 | 47/60 | 74/105 | 172/195 | 1 | 15 |
| verifier/source overlay | 45/45 | 47/60 | 81/105 | 188/195 | 1 | 7 |

The controller claim is mixed-distribution cost-aware routing, not source-slice dominance.

## 5. Stress Ladder

### 5.1 Lexical Overlay Failure

| gate | TP | FP | FN | TN |
|---|---:|---:|---:|---:|
| deterministic-verifier lexical gate | 1 | 1 | 11 | 17 |
| source-confidence raw lexical gate | 6 | 5 | 0 | 19 |

This is 17/30 static trigger failures, 11/12 missed deterministic positives, and 5/24 raw source false positives.

Qwen3.5-9B overlap-guard on the same stress split gets 13/30 joint, 24/30 validity, 14/30 compute, 1/12 deterministic-verify compute, 6/6 retrieve-answer compute, and 0/2 false-premise validity.

### 5.2 Module Ladder

| diagnostic | joint | validity | compute |
|---|---:|---:|---:|
| phrase module, original stress | 30/30 | 30/30 | 30/30 |
| phrase module, transfer-v1 | 8/38 | 26/38 | 8/38 |
| module-general-v1, original stress | 28/30 | 29/30 | 28/30 |
| module-general-v1, transfer-v1 | 38/38 | 38/38 | 38/38 |
| module-general-v1, transfer-v2 | 23/38 | 26/38 | 23/38 |
| source-role v2, transfer-v2 | 38/38 | 38/38 | 38/38 |
| source-role v2, transfer-v3 | 38/42 | 39/42 | 38/42 |
| source-role v3, transfer-v3 | 41/42 | 41/42 | 41/42 |
| source-role v3, transfer-v4 | 50/50 | 50/50 | 50/50 |

The source-role v2 transfer-v3 failure is concentrated in source ambiguity, 3/6, which is why source-role v3 adds a separate under-named source-context branch.

### 5.3 Live Transfer-v4 Baselines

| model/policy | joint | validity | compute |
|---|---:|---:|---:|
| qwen3:14b overlap-guard | 34/50 | 42/50 | 34/50 |
| Gemma4-26B overlap-guard | 44/50 | 47/50 | 44/50 |

Compute-action slices:

| model/policy | direct answer | retrieve answer | retrieve premise check | deterministic verify | clarify |
|---|---:|---:|---:|---:|---:|
| qwen3:14b overlap-guard | 10/10 | 8/8 | 8/8 | 0/8 | 8/16 |
| Gemma4-26B overlap-guard | 9/10 | 8/8 | 5/8 | 6/8 | 16/16 |

Validity slices:

| model/policy | answerable | false premise | ambiguous |
|---|---:|---:|---:|
| qwen3:14b overlap-guard | 26/26 | 8/8 | 8/16 |
| Gemma4-26B overlap-guard | 26/26 | 5/8 | 16/16 |

Source-role v3 itself keeps the source stable-direct transfer-v4 controls at 4/4. Earlier transfer-v3 live baselines are weaker: qwen3.5:9b reaches 20/42 joint, 31/42 validity, and 20/42 compute, with clarify 6/10, deterministic verify 2/8, retrieve-answer 7/8, retrieve-premise-check 0/8, and false-premise validity 3/8. qwen3:14b reaches 27/42 joint, 34/42 validity, and 27/42 compute, with clarify 4/10, deterministic verify 0/8, retrieve-answer 8/8, retrieve-premise-check 7/8, and false-premise validity 7/8.

The shape matters. Qwen3:14b handles named source answer and source premise-check rows but fails deterministic verification and under-named ambiguity. Gemma4-26B handles ambiguity and most local verification but accepts three named recent-event false premises as answerable. Scalar retrieval or abstention scores hide that distinction.

A transfer-v4 disagreement atlas shows the same point more sharply. The qwen/Gemma two-policy oracle reaches 48/50 joint. Both prompts are correct on 30 rows; Gemma alone repairs 14 qwen misses, mostly deterministic-positive and under-named ambiguity rows; qwen alone repairs 4 Gemma misses, mostly source false-premise and stable-direct rows; both prompts miss only 2 rows, both local deterministic verification rows. Source-role v3 reaches 50/50 on the same generated split.

## 6. Locked Method Target

The next frozen controller should combine:

1. Local-operation detector/executor: structural counts, comparisons, inventories, ledgers, schedules, lists, route distances, and simple arithmetic.
2. Generic underspecification detector: missing referents in local questions and missing source context in recent-looking questions.
3. Source-role router: `retrieve_then_answer` versus `retrieve_then_premise_check`, with stable year-token facts kept direct.
4. Source-confidence layer: retrieval availability, source agreement, reranker confidence, generator confidence change, and premise consistency.

Gemma transfer-v4 makes the source-confidence layer central: the model can answer and clarify many rows but still accepts false winner premises.

## 7. Locked Experiment

The next credible experiment is:

1. Human-audit the v3 scaffold and source-role transfer rows.
2. Require complete human source packs for locked source-required rows.
3. Freeze prompts, parser repair, model list, source format, controller features, module thresholds, and scoring.
4. Evaluate once on locked blind rows plus source-role transfer slices.

Support requires:

- controller beats the learned selector on audited locked rows;
- direct-answer compute remains high;
- deterministic-verify and clarify rows are reported separately;
- retrieval-premise joint remains near overlap-guard;
- source false-premise rows route to `retrieve_then_premise_check`;
- source answerable rows route to `retrieve_then_answer`;
- source ambiguous rows route to `clarify`;
- stable year-token facts stay direct.

Kill criteria:

- source-role v3 only wins by enumerating role nouns;
- source ambiguous collapses under human-authored transfer;
- direct controls over-verify;
- source-confidence or reranking baselines erase the margin;
- final answer audit shows route-correct but answer-wrong behavior.

## 8. Claim Ledger

Allowed:

1. Doubt prompting failed as the main method and is now a negative control.
2. Reliability-action routing is a useful evaluation target because validity and compute action diverge.
3. `retrieve_then_premise_check` is distinct from ordinary retrieve-to-answer.
4. Development evidence shows a real mixed-distribution cost frontier.
5. Module diagnostics expose concrete components but are not locked evidence.
6. Source-role v3 is the best current method-shaped diagnostic, with fresh transfer-v4 support and live qwen/Gemma baselines that do not erase the target.

Forbidden:

1. "Doubt prompting works."
2. "We solve false-premise QA."
3. "Reliability-action routing is proven on a final benchmark."
4. "The learned controller generalizes semantically."
5. "The verifier/source overlay is validated."
6. "Source-role v3 solves semantic transfer."
7. "Gemma solves the transfer-v4 stress."

## 9. Reproducibility Pointers

Current pitch and audits:

- `outputs/doubt_tts_aggressive_submission_blueprint_v29.md`
- `outputs/doubt_tts_aggressive_submission_blueprint_v29_numeric_audit.md`
- `outputs/doubt_tts_paper_draft_v8.md`
- `outputs/doubt_tts_paper_draft_v8_numeric_audit.md`
- `outputs/doubt_tts_current_evidence_manifest.md`

Current source-role stress artifacts:

- `outputs/doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_protocol.md`
- `outputs/doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_module_source_role_v3.md`
- `outputs/doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_qwen3_14b_overlap_guard_report.md`
- `outputs/doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_gemma4_26b_overlap_guard_report.md`
- `outputs/doubt_tts_reliability_action_v3_overlay_source_role_transfer_stress_v4_model_atlas.md`

## References

- William Jurayj, Jeffrey Cheng, Benjamin Van Durme. "Is That Your Final Answer? Test-Time Scaling Improves Selective Question Answering." arXiv:2502.13962. <https://arxiv.org/abs/2502.13962>
- Polina Kirichenko, Mark Ibrahim, Kamalika Chaudhuri, Samuel J. Bell. "AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions." arXiv:2506.09038. <https://arxiv.org/abs/2506.09038>
- Di Wu, Jia-Chen Gu, Kai-Wei Chang, Nanyun Peng. "Self-Routing RAG: Binding Selective Retrieval with Knowledge Verbalization." arXiv:2504.01018. <https://arxiv.org/abs/2504.01018>
- Dongxin Guo, Jikun Wu, Siu Ming Yiu. "When to Retrieve During Reasoning: Adaptive Retrieval for Large Reasoning Models." arXiv:2604.26649. <https://arxiv.org/abs/2604.26649>
- Bo Li, Mingda Wang, Gexiang Fang, Shikun Zhang, Wei Ye. "Retrieval as Generation: A Unified Framework with Self-Triggered Information Planning." arXiv:2604.11407. <https://arxiv.org/abs/2604.11407>
- Tong Zhao, Yutao Zhu, Yucheng Tian, Zhicheng Dou. "R3AG: Retriever Routing for Retrieval-Augmented Generation." arXiv:2604.22849. <https://arxiv.org/abs/2604.22849>
- Zhipeng Song, Yizhi Zhou, Xiangyu Kong, Jiulong Jiao, Xuezhou Ye, Chunqi Gao, Xueqing Shi, Yuhang Zhou, Heng Qi. "CAR: Query-Guided Confidence-Aware Reranking for Retrieval-Augmented Generation." arXiv:2605.04495. <https://arxiv.org/abs/2605.04495>
- Yuehan Qin, Shawn Li, Yi Nian, Xinyan Velocity Yu, Yue Zhao, Xuezhe Ma. "Don't Let It Hallucinate: Premise Verification via Retrieval-Augmented Logical Reasoning." arXiv:2504.06438. <https://arxiv.org/abs/2504.06438>
