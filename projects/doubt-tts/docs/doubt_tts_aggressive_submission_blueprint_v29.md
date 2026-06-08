# Doubt-TTS Aggressive Submission Blueprint v29

Date: 2026-06-02

Status: current strongest aggressive packet after the completed remote-PC Gemma4-26B transfer-v4 baseline. This supersedes v28 for pitch framing. V28 remains the clean qwen-live source-role-v3 packet.

## Title

Reliability-Action Routing for Selective Question Answering

Sharper subtitle:

Typed Reliability Actions Expose What Retrieve/Skip Scores Hide

## Current Best Claim

Use this wording:

> We introduce reliability-action routing, a two-axis selective-QA protocol that separates answer validity from the computation required before response. Development evidence on a 300-row cue-balanced scaffold shows a prompt/controller frontier: Gemma4-26B action-discriminating routing preserves cheap direct-answer controls but nearly misses retrieval-backed premise checks (`6/60` joint), while overlap-guard repairs that branch (`47/60`) but damages direct controls (`27/45`). A policy-output selector recovers the mixed-distribution frontier (`246/300` joint, `45/45` direct compute, `47/60` retrieval-premise joint). A development-only verifier/source overlay reaches `269/300`, but stress tests prevent overclaiming it. The v0 lexical overlay misses `11/12` deterministic paraphrase positives; qwen3.5:9b overlap-guard gets `13/30` joint on the original stress split; an after-inspection phrase module gets `30/30` original stress and `8/38` transfer-v1; broader module-general-v1 gets `38/38` transfer-v1 but only `23/38` transfer-v2. Source-role module v3 gets `41/42` on source-role transfer-v3 and `50/50` on fresh transfer-v4. Live prompt baselines on transfer-v4 do not erase the target: qwen3:14b overlap-guard gets `34/50`, while Gemma4-26B overlap-guard gets `44/50`. Gemma solves the under-named ambiguity rows (`16/16`) and source-answer rows (`8/8`), but still misses source false-premise/premise-check rows (`5/8`) and local deterministic verification (`6/8`). The locked paper claim is now concrete: freeze typed local-operation, source-role, underspecification, and source-confidence modules, then test them once on audited blind rows with deterministic verification, source answer, source premise-check, source ambiguity, and stable-direct controls reported separately.

Do not claim:

- the generated v3 scaffold is locked evidence;
- transfer-v4 is paper-locked;
- source-role v3 is semantic generalization;
- Gemma solves the transfer-v4 stress;
- the verifier/source overlay is validated;
- Doubt prompting works.

## Why v29 Is Stronger Than v28

V28 showed that qwen prompts do not erase the source-role target:

| split | model/policy | joint | validity | compute |
|---|---|---:|---:|---:|
| transfer-v3 | qwen3.5:9b overlap-guard | 20/42 | 31/42 | 20/42 |
| transfer-v3 | qwen3:14b overlap-guard | 27/42 | 34/42 | 27/42 |
| transfer-v4 | qwen3:14b overlap-guard | 34/50 | 42/50 | 34/50 |

V29 adds the stronger remote-PC Gemma4-26B run:

| split | model/policy | joint | validity | compute |
|---|---|---:|---:|---:|
| transfer-v4 | source-role v3 module | 50/50 | 50/50 | 50/50 |
| transfer-v4 | qwen3:14b overlap-guard | 34/50 | 42/50 | 34/50 |
| transfer-v4 | Gemma4-26B overlap-guard | 44/50 | 47/50 | 44/50 |

The Gemma result makes the pitch stronger because it is not a trivial negative baseline. A capable model handles ambiguity perfectly on this split, yet still fails the typed action distinction for source false premises and local deterministic verification.

## Fresh Transfer-v4 Slices

Source-role ladder immediately before v4:

- source-role v2 gets 38/42 on transfer-v3, with source ambiguous at 3/6.
- source-role v3 gets 26/30 on original stress and 37/38 on transfer-v1 before reaching 38/38 on transfer-v2, 41/42 on transfer-v3, and 50/50 on transfer-v4.

Source-role v3 module:

| category | joint |
|---|---:|
| deterministic positive transfer-v4 | 8/8 |
| deterministic ambiguous transfer-v4 | 6/6 |
| deterministic direct transfer-v4 | 6/6 |
| source positive transfer-v4 | 8/8 |
| source false-premise transfer-v4 | 8/8 |
| source ambiguous transfer-v4 | 10/10 |
| source stable direct transfer-v4 | 4/4 |

Live transfer-v4 compute slices:

| model/policy | direct answer | retrieve answer | retrieve premise check | deterministic verify | clarify |
|---|---:|---:|---:|---:|---:|
| qwen3:14b overlap-guard | 10/10 | 8/8 | 8/8 | 0/8 | 8/16 |
| Gemma4-26B overlap-guard | 9/10 | 8/8 | 5/8 | 6/8 | 16/16 |

Live transfer-v4 validity slices:

| model/policy | answerable | false premise | ambiguous |
|---|---:|---:|---:|
| qwen3:14b overlap-guard | 26/26 | 8/8 | 8/16 |
| Gemma4-26B overlap-guard | 26/26 | 5/8 | 16/16 |

Earlier live transfer-v3 baselines are weaker and differently shaped: qwen3.5:9b reaches 20/42 joint, 31/42 validity, and 20/42 compute, with clarify 6/10, retrieve-premise-check 0/8, and false-premise validity 3/8. qwen3:14b reaches 27/42 joint, 34/42 validity, and 27/42 compute, with clarify 4/10 and retrieve-premise-check 7/8.

The failure modes are complementary:

- qwen3:14b treats many under-named source questions as retrievable facts and routes all deterministic comparisons to direct answer.
- Gemma4-26B correctly clarifies all under-named source/local ambiguous rows but accepts three named recent-event false premises as answerable.

The transfer-v4 disagreement atlas makes the complementarity explicit: qwen/Gemma two-policy oracle joint is 48/50; they share 30 correct rows, Gemma-only repairs 14 qwen misses, qwen-only repairs 4 Gemma misses, and both prompts miss only 2 rows, both local deterministic verification cases. Source-role v3 still reaches 50/50 on the same generated split.

That is the paper wedge: validity and compute action are not a scalar "retrieve or do not retrieve" decision.

## Development Frontier Still Holds

| method | joint | validity | compute | mean cost |
|---|---:|---:|---:|---:|
| Gemma action-discriminating | 201/300 | 246/300 | 214/300 | 1.78 |
| Gemma overlap-guard | 232/300 | 254/300 | 237/300 | 2.38 |
| Gemma learned policy selector | 246/300 | 260/300 | 251/300 | 2.17 |
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

The claim is mixed-distribution cost-aware routing, not source-slice dominance.

## Locked Method Target

The next frozen controller needs four components:

1. Local-operation detector/executor.
2. Generic local underspecification detector.
3. Source-role underspecification and premise-role router.
4. Source-confidence layer using retrieval availability, source agreement, reranker confidence, generator confidence change, and premise consistency.

Gemma transfer-v4 makes the fourth component more important, not less. The model knows enough to answer named events and clarify under-named questions, but it still accepts some false winner premises.

## Locked Acceptance Gates

A locked result supports the main claim only if:

- the frozen controller beats the learned selector on audited locked rows;
- direct-answer compute remains high;
- deterministic-verify controls are reported separately;
- retrieval-premise joint remains near overlap-guard;
- source false-premise rows route to `retrieve_then_premise_check`;
- source answerable rows route to `retrieve_then_answer`;
- source ambiguous rows route to `clarify`;
- stable year-token facts stay direct;
- response-quality audit does not show correct routes still accepting false premises.

## Kill Criteria

Demote the method if:

- source-role v3 only wins by enumerating role nouns;
- source ambiguous collapses under human-authored transfer;
- direct controls over-verify;
- source-confidence/reranking baselines erase the margin;
- final response audit shows route-correct but answer-wrong behavior.

## Bottom Line

V29 is the strongest current packet because it adds a serious positive live baseline, not just a weak one. Gemma4-26B gets `44/50` on fresh transfer-v4, but the remaining failures are exactly the typed reliability-action failures the benchmark was built to expose: source false-premise premise checking and local deterministic verification. That makes the proposal more credible and more falsifiable.
