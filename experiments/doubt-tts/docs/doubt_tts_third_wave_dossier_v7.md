# Doubt-TTS Third-Wave Dossier v7

Version: 2026-06-01

## One-Sentence Thesis

**Doubt is not a prompt. Doubt is a controller state in an evidence-gated selective-compute system that must choose validity, compute action, source, verifier, and response policy separately.**

The original "make the model doubt itself" idea is now the wrong headline. The aggressive version is:

> Large language models fail selective QA because they are asked to answer before the system has decided what kind of uncertainty it is facing. A useful test-time reliability system should first route the question into semantic reliability actions, then retrieve or verify only when that action can change the decision.

This is stronger than "add a doubt prompt" and more falsifiable than "use RAG." It predicts that failures decompose into separable bottlenecks:

1. validity recognition: answerable vs false premise vs ambiguous;
2. compute action: direct answer, premise check, retrieval, retrieval-backed premise check, deterministic verification, clarify;
3. source selection: what evidence object should be inspected;
4. verifier execution: whether the selected evidence supports the presupposition;
5. response policy: answer, correct premise, abstain, or ask for clarification.

## Why This Is Now A Real Research Object

Recent work makes the gap clear:

- [AbstentionBench](https://arxiv.org/abs/2506.09038) reports that abstention remains unsolved across unknown, underspecified, false-premise, subjective, and outdated-answer questions, and that system prompting does not solve uncertainty reasoning.
- [Know Your Limits](https://aclanthology.org/2025.tacl-1.26/) frames abstention across query, model, and human-value perspectives, which supports treating refusal as a contextual policy rather than a universal behavior.
- [RefusalBench](https://aclanthology.org/2026.eacl-long.321/) finds grounded refusal is separable into detection and categorization skills, and that static benchmarks invite artifact exploitation.
- [MultiHoax](https://arxiv.org/abs/2506.00264) and [KG-FPQ](https://arxiv.org/abs/2407.05868) make false-premise handling a benchmarked problem, not a novelty claim.
- [Astute RAG](https://arxiv.org/abs/2410.07176) emphasizes that imperfect retrieval and internal-vs-external knowledge conflicts are central RAG failure modes.
- OpenAI's 2025 hallucination analysis argues that accuracy-only scoreboards reward guessing over acknowledging uncertainty, which is exactly why selective QA needs explicit answer, abstain, and correction accounting.

So the contribution cannot be "models should abstain" or "false premises exist" or "RAG helps." The contribution has to be narrower and meaner:

> A negative-controlled selective-compute benchmark and controller scaffold showing that prompt-level doubt fails, while route/source/verifier decomposition exposes where reliability actually breaks.

## Third-Wave Empirical Spine

### 1. Prompt-Level Doubt Failed The Control

The first result is still the most important honesty check.

| condition | result |
|---|---|
| static directed challenge | reduces some confident false-premise errors by abstaining more |
| neutral/random reconsideration | often matches or beats directed challenge at similar budget |
| conclusion | directed doubt wording is not validated as the causal mechanism |

This kills the cute paper. Good. The uncute paper is stronger.

### 2. Routing Beats Uniform Doubt On Small Probes

| route surface | strongest current result | interpretation |
|---|---:|---|
| balanced 48-item route eval | cascade 48/48 | route prompting can solve the toy surface |
| held-out 64-item route probe | cascade 61/64 | modest transfer, not solved |
| response-taxonomy route check | event gate 48/48 | event-aware routing fixes measured accepted-false-premise route failures |
| event-contrast stress | event-gated cascade 66/72 | event gate helps, but misses remain verifier-shaped |

The router evidence is promising, but not publishable as "router solved." Its value is diagnostic: it identifies which items need tools, decomposition, or source-backed checks.

### 3. Event Verification Moves The Bottleneck

Offline verifier reruns on 2026-06-01:

| surface | condition | result | claim allowed |
|---|---|---:|---|
| 72 event-contrast rows | table event verifier | 72/72 | event-gate misses are verifier-shaped on the original table condition |
| 32 held-out event rows | inferred-source retrieval verifier | 32/32 | when a clean event source can be inferred, retrieval-conditioned verification generalizes beyond the original table |
| 24 messy event-reference rows | local cached-source retrieval verifier | 24/24 | source selection can be made explicit and scored on a tiny local evidence corpus |

Verification commands rerun:

```bash
python3 work/probe/doubt_probe.py \
  --data work/probe/event_contrast_route_questions.jsonl \
  --route-only --event-verifier-only \
  --out work/probe/runs/third_wave_verify_table_event_results.jsonl \
  --report work/probe/runs/third_wave_verify_table_event_report.md

python3 work/probe/doubt_probe.py \
  --data work/probe/heldout_event_retrieval_questions.jsonl \
  --route-only --retrieval-event-verifier-only --ignore-event-source-title \
  --out work/probe/runs/third_wave_verify_heldout_retrieval_auto_results.jsonl \
  --report work/probe/runs/third_wave_verify_heldout_retrieval_auto_report.md

python3 work/probe/doubt_probe.py \
  --data work/probe/messy_event_search_questions.jsonl \
  --route-only --retrieval-event-verifier-only --ignore-event-source-title --local-event-source-index \
  --out work/probe/runs/third_wave_verify_messy_local_index_results.jsonl \
  --report work/probe/runs/third_wave_verify_messy_local_index_report.md
```

These are not open-domain proof. They are cleaner than that: they isolate source selection and verifier correctness as separate measurable subproblems.

Live model note: the Windows training PC/Ollama host was checked during this wave and SSH to `pc` failed with `Host is down`, so this pass does not claim new live Qwen/Gemma generations beyond the existing saved traces. The fresh evidence in this wave is the offline verifier rerun set above.

### 4. The Messy Probe Reveals The Real Bottleneck

The key contrast:

| messy 24-item condition | overall | false-premise recall | ordinary specificity |
|---|---:|---:|---:|
| table verifier | 12/24 | 0/12 | 12/12 |
| clean-title inference verifier | 12/24 | 0/12 | 12/12 |
| query-fixture retrieval verifier | 24/24 | 12/12 | 12/12 |
| local cached-source retrieval verifier | 24/24 | 12/12 | 12/12 |

This is the best "aha" in the project:

> The verifier is not the hard part once the right evidence object is selected. The hard part is selecting the evidence object from messy language without letting the benchmark hand it to the system.

That is a paper-grade decomposition. It prevents overclaiming retrieval while giving the next experiment a concrete target.

### 5. Two-Axis Evaluation Exposes Prompt Failure Modes

The single route label is not enough because some rows are both false-premise and retrieval-needed. The repaired target is:

```json
{
  "validity": "answerable | false_premise | ambiguous",
  "compute_action": "direct_answer | premise_check | retrieve_then_answer | retrieve_then_premise_check | deterministic_verify | clarify"
}
```

Current two-axis model evidence:

| split | method | joint | validity | important failure |
|---|---|---:|---:|---|
| 62 automation-supported | deterministic two-axis baseline | 43/62 | 55/62 | strong cheap baseline |
| 62 automation-supported | Qwen base | 12/62 | 59/62 | validity ok, retrieval action collapsed |
| 62 automation-supported | Qwen retrieval-strict | 53/62 | 60/62 | beats baseline, over-retrieves direct-answer rows |
| 62 automation-supported | Gemma4-26B action-discriminating | 44/62 | 53/62 | second-model signal but not dominant |
| 161 evidence-pack | deterministic two-axis baseline | 96/161 | 132/161 | current baseline to beat |
| 161 evidence-pack | Qwen base | 62/161 | 129/161 | validity better than action |
| 161 evidence-pack | Qwen retrieval-strict | 71/161 | 127/161 | retrieves too broadly |
| 161 evidence-pack | Qwen action-discriminating | 89/161 | 128/161 | better action mix, misses retrieval |
| 161 evidence-pack | Qwen overlap-guard | 92/161 | 128/161 | partial overlap repair, still below deterministic |
| 161 evidence-pack | Gemma4-26B action-discriminating | 111/161 | 138/161 | first live 161-row baseline win, still 1/18 retrieval-premise |
| 161 evidence-pack | Gemma4-26B overlap-guard | 104/161 | 138/161 | fixes retrieval-premise, but over-routes direct/premise rows |
| 161 evidence-pack | Gemma4-26B hybrid self-gate | 116/161 | 139/161 | best current non-oracle controller diagnostic |
| 26 counterbalanced cue | deterministic baseline | 13/26 | 18/26 | hard cue-repair split |
| 26 counterbalanced cue | Qwen best | 15/26 | 24/26 | validity transfers better than action |
| 26 counterbalanced cue | Gemma4-26B best | 19/26 | 25/26 | stronger second-model signal, still misses retrieve-then-premise |

The 62-row Qwen retrieval-strict result is the first narrow positive controller result. The 161-row Qwen evidence-pack result is negative, but the Gemma4-26B action-discriminating run changes the status to a strong positive pilot: 111/161 joint versus 96/161 deterministic, paired +15 with exact p=0.11, and +22 over Qwen action-discriminating with exact p=0.00031. The overlap-guard run adds the action-specific clue: 104/161 overall but 17/18 compute accuracy on retrieval-backed premise checks. The non-oracle hybrid self-gate is the current best controller diagnostic at 116/161, paired p=0.0151 versus deterministic. That combination is useful:

> Validity recognition is comparatively easy. Compute-action allocation, especially retrieval vs premise-check vs retrieval-backed premise-check, is the unsolved part.

The first learned overlap gate is negative but informative. Naive Bayes gates fail to beat the simple self/hand gates under family transfer, while oracle delta gates stay much higher. A post-hoc semantic recent-assertion rule reaches 127/161 combined, matching the gold overlap-gate ceiling, but because it was written after failure inspection it is a preregistration target rather than a method claim. So the next method is not "use NB"; it is build a better overlap detector and keep family-transfer reporting as the guardrail.

### 6. Text Baselines Are A Reviewer Trap, And We Have Receipts

The benchmark is full of template shortcuts unless repaired.

| baseline surface | result | interpretation |
|---|---:|---|
| full 300 text baseline, random CV | up to 0.69 route / 0.60 joint | random folds leak template families |
| seed-to-candidate transfer | route about 0.24 on some features | family transfer is much harder |
| candidate-to-seed transfer | route about 0.39 on some features | still weak |
| paraphrase transfer | route about 0.83-0.88 | deterministic paraphrases preserve shortcuts |
| counterbalanced cue CV | route about 0.35-0.39, joint about 0.12-0.15 | cue counterbalancing breaks shallow signals |

The aggressive benchmark requirement is therefore:

> Any claimed controller win must beat text-only baselines under family-held-out, subtype-held-out, human paraphrase, and counterbalanced-cue splits. Random CV is not enough.

### 7. Cost Frontier Turns "More Retrieval" Into A Bad Baseline

On the 161-row evidence-pack split:

| method | joint | wasted retrieval | missed retrieval | reading |
|---|---:|---:|---:|---|
| Gemma4-26B hybrid self-gate | 116/161 | 21 | 12 | best current non-oracle tradeoff |
| Gemma4-26B action-discriminating | 111/161 | 9 | 33 | best live frontier point, but still misses overlap rows |
| Gemma4-26B overlap-guard | 104/161 | 46 | 2 | overlap repair branch, too blunt globally |
| deterministic two-axis | 96/161 | 48 | 9 | strong cheap baseline, now below Gemma |
| Qwen action-discriminating | 89/161 | 3 | 46 | cheap, but misses retrieval rows |
| Qwen retrieval-strict | 71/161 | 62 | 2 | catches retrieval, wastes it everywhere |
| hand retrieval gate | 93/161 | 33 | 16 | closer frontier point, still below deterministic |

This forces the paper away from "retrieve more" and toward:

> A selective-compute controller should move the accuracy/cost frontier by reducing both missed retrieval and wasted retrieval while preserving false-premise recall.

## Proposed System: Evidence-Gated Selective Compute

### Controller Output

```json
{
  "validity": "answerable | false_premise | ambiguous",
  "compute_action": "direct_answer | premise_check | retrieve_then_answer | retrieve_then_premise_check | deterministic_verify | clarify",
  "source_policy": "none | table | web_search | local_index | provided_context | calculator",
  "source_query": "...",
  "response_policy": "answer | correct_premise | abstain | clarify",
  "confidence": 0.0
}
```

### Runtime Policy

1. Predict validity and compute action from the question.
2. If action requires evidence, select source and query.
3. Run source-specific verifier, not a generic "think again" prompt.
4. Score source selection separately from verifier correctness.
5. Return answer, correction, abstention, or clarification.
6. Log accepted false premise, false refusal, and correction coverage.

### Minimal Algorithm Sketch

```text
route = controller(question)

if route.compute_action == clarify:
    return ask_clarifying_question(question)

if route.compute_action == deterministic_verify:
    evidence = run_deterministic_tool(question)
    return answer_or_correct(evidence)

if route.compute_action in {retrieve_then_answer, retrieve_then_premise_check}:
    source = source_selector(question, route)
    evidence = retrieve(source, question)
    verdict = verifier(question, evidence)
    return answer_correct_or_abstain(verdict)

if route.compute_action == premise_check:
    verdict = premise_decomposer(question)
    return correct_or_abstain(verdict)

return direct_answer(question)
```

The method is not "self-correction." It is an inference-time controller over reliability actions.

## Strongest Submission Pitch

**Title option A:** Route, Retrieve, Verify: Evidence-Gated Selective Compute for Question Answering

**Title option B:** Doubt Is Not A Prompt: Negative-Controlled Selective Compute for False-Premise QA

**Title option C:** Routed Doubt: Validity-Aware Test-Time Compute for Selective Question Answering

### Abstract Draft

Selective question answering requires more than deciding whether a model is confident. A system must decide whether the question is answerable, false-premised, ambiguous, or tool-verifiable, and then allocate test-time compute to the action that can change the decision. We study this through a negative-controlled failure of prompt-level self-doubt. On local Qwen pilots, directed disconfirmation reduces some false-premise errors by abstaining, but neutral reconsideration often matches or beats it, showing that doubt wording is not the active ingredient. We therefore introduce an evidence-gated selective-compute scaffold that predicts validity and compute action separately, routes event-shaped claims to source-backed verification, and scores source selection independently from verifier correctness. Small pilots expose the decomposition: an event-gated route prompt improves a 72-item event stress test from 63/72 to 66/72, a table-backed verifier reaches 72/72 in-domain but falls to 21/32 on held-out event rows, while retrieval-backed verification reaches 32/32 when clean source selection is available. A messy-reference probe shows the next bottleneck directly: title inference fails at 12/24, but a local cached-source selector restores 24/24. Finally, two-axis evaluations show that LLM prompts often recognize validity while failing compute-action allocation, especially retrieval-backed premise checks. The result is not a solved controller, but a sharper benchmark and systems target: selective QA should be evaluated as route, source, verifier, and response-policy selection under negative controls, not as generic longer reasoning or self-doubt.

## Reviewer-Proof Claim Ledger

### Allowed

- Static directed doubt is not supported as a general improvement over neutral reconsideration.
- Route-first selective compute is a better abstraction than uniform doubt prompting.
- Event-shaped false premises are often verifier-shaped failures.
- Given the correct evidence source, finite-state retrieval verification can separate true and false event premises on current small held-out probes.
- Messy source selection is the current bottleneck.
- Validity recognition and compute-action allocation should be scored separately.
- Current live model prompts do not solve the 161-row evidence-pack split.
- Text-only and template baselines are dangerous and must be included.

### Forbidden

- "Doubt-TTS improves LLM factuality."
- "Retrieval verifier solves false premises."
- "The router generalizes."
- "The messy local-index result is open-domain web retrieval."
- "Directed disconfirmation is better than neutral reconsideration."
- "Qwen/Gemma results establish model-general behavior."

## Next Experiment: The Actually Ambitious One

Build a 400-600 item locked benchmark around the decomposition, not around prompt vibes.

### Dataset Axes

| axis | target |
|---|---|
| validity | answerable, false_premise, ambiguous |
| compute action | direct, premise_check, retrieve_answer, retrieve_premise_check, deterministic_verify, clarify |
| evidence condition | none, clean source, messy source, conflicting source, insufficient source |
| temporal condition | historical, recent completed, future scheduled, impossible future-completed, stale model-knowledge trap |
| source condition | title-hinted, query-only, local index, open web, distractor-rich |
| wording condition | original, human paraphrase, adversarial paraphrase, counterbalanced cue |

### Models And Policies

Run all of these on the same blinded inputs:

1. always answer;
2. always abstain/correct;
3. always retrieve;
4. deterministic question-only controller;
5. text-only Naive Bayes and char n-gram baselines;
6. prompt-level directed doubt;
7. neutral reconsideration;
8. route prompt only;
9. retrieval-strict prompt;
10. action-discriminating prompt;
11. two-stage validity then action prompt;
12. cheap learned selector over prompt outputs;
13. source-selection oracle;
14. verifier oracle;
15. full oracle.

### Primary Metrics

- joint validity/action accuracy;
- macro validity;
- macro compute action;
- false-premise recall;
- ordinary false-refusal rate;
- accepted false-premise rate;
- correction coverage;
- retrieval-needed recall;
- wasted retrieval;
- missed retrieval;
- source-selection accuracy;
- verifier accuracy conditional on correct source;
- risk/coverage and cost/accuracy frontier;
- family-held-out and subtype-held-out transfer.

### Win Condition

A positive controller claim requires all of:

1. beats deterministic two-axis and text-only baselines on the same split;
2. improves false-premise recall without collapsing ordinary specificity;
3. improves retrieval-backed premise rows specifically;
4. reduces missed retrieval without exploding wasted retrieval;
5. survives family-held-out and human paraphrase;
6. reports source-selection failures separately from verifier failures;
7. beats neutral reconsideration when both are route-fixed and coverage-matched.

If it fails, the negative paper is still useful:

> Prompt-level self-doubt fails as a reliability primitive; selective QA evaluation must decompose validity, action, source selection, verification, and response policy to avoid mistaking template artifacts for robust uncertainty handling.

## Current Bottom Line

The third-wave pitch is no longer "I wonder if making the model doubt itself works."

It is:

> Can we turn selective QA into a measurable controller problem where the system chooses the cheapest reliability action that can change the answer, and can we prove that prompt-level doubt is an inadequate substitute using negative controls?

That is worth pursuing. The current results are small, but the failure analysis is unusually clean, and the next benchmark is now specific enough to be scary in the good way.
