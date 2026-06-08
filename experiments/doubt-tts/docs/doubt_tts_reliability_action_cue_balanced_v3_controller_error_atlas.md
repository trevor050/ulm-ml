# Reliability-Action v3 Controller Error Atlas

Status: row-level audit over Gemma4-26B v3 action-discriminating, overlap-guard, hybrid, learned policy selector, and cue-stem-heldout selector. This report explains what the controller recovers, where it regresses, and what remains unsolved.

- machine-readable atlas: `work/probe/runs/reliability_action_cue_balanced_v3_controller_error_atlas.json`

## Headline

- action/overlap oracle joint: 257/300
- learned policy selector joint: 246/300
- learned regret to action-or-overlap oracle: 11 rows
- hybrid joint: 245/300
- hybrid regret to action-or-overlap oracle: 12 rows

## Method Summary

| method | joint | validity | compute | selected overlap |
|---|---:|---:|---:|---:|
| `action` | 201/300 | 246/300 | 214/300 | 0/300 |
| `overlap` | 232/300 | 254/300 | 237/300 | 0/300 |
| `hybrid` | 245/300 | 260/300 | 250/300 | 69/300 |
| `learned` | 246/300 | 260/300 | 251/300 | 69/300 |
| `cue_heldout` | 246/300 | 260/300 | 251/300 | 71/300 |

## Bucket Counts

| bucket | rows | expected-action mix | source-required mix |
|---|---:|---|---|
| `learned_recovers_action` | 49 | retrieve_then_premise_check:42, retrieve_then_answer:7 | True:49 |
| `learned_loses_vs_action` | 4 | retrieve_then_answer:2, premise_check:1, retrieve_then_premise_check:1 | True:3, False:1 |
| `learned_recovers_overlap` | 21 | direct_answer:18, deterministic_verify:3 | False:21 |
| `learned_loses_vs_overlap` | 7 | retrieve_then_answer:7 | True:7 |
| `hybrid_recovers_action` | 48 | retrieve_then_premise_check:42, retrieve_then_answer:6 | True:48 |
| `hybrid_loses_vs_action` | 4 | retrieve_then_answer:2, premise_check:1, retrieve_then_premise_check:1 | True:3, False:1 |
| `both_base_wrong_learned_right` | 0 | - | - |
| `both_base_wrong_learned_wrong` | 43 | deterministic_verify:22, retrieve_then_premise_check:12, retrieve_then_answer:9 | False:22, True:21 |
| `oracle_action_or_overlap_gap` | 11 | retrieve_then_answer:9, premise_check:1, retrieve_then_premise_check:1 | True:10, False:1 |
| `learned_beats_both_base` | 0 | - | - |

## Learned Selector Recoveries From Action-Discriminating

| id | question | gold | source family | action | overlap | learned |
|---|---|---|---|---|---|---|
| `rav3_000009` | In a QA benchmark, who won Best Picture at the 97th Academy Awards? | `answerable/retrieve_then_answer` | `academy_97_best_picture` | N: __invalid__/retrieve_then_premise_check | Y: answerable/retrieve_then_answer | Y: answerable/retrieve_then_answer |
| `rav3_000010` | In a QA benchmark, who won Best Picture at the 97th Academy Awards for The Brutalist? | `false_premise/retrieve_then_premise_check` | `academy_97_best_picture` | N: __invalid__/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000015` | For a reliability routing test, who won Best Picture at the 97th Academy Awards? | `answerable/retrieve_then_answer` | `academy_97_best_picture` | N: __invalid__/retrieve_then_premise_check | Y: answerable/retrieve_then_answer | Y: answerable/retrieve_then_answer |
| `rav3_000016` | For a reliability routing test, who won Best Picture at the 97th Academy Awards for The Brutalist? | `false_premise/retrieve_then_premise_check` | `academy_97_best_picture` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000019` | Using the event framing in the question, who won Best Picture at the 97th Academy Awards for The Brutalist? | `false_premise/retrieve_then_premise_check` | `academy_97_best_picture` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000024` | Which team won the 2024 NBA Finals against the Los Angeles Lakers? | `false_premise/retrieve_then_premise_check` | `nba_finals_2024` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000030` | In a QA benchmark, which team won the 2024 NBA Finals against the Los Angeles Lakers? | `false_premise/retrieve_then_premise_check` | `nba_finals_2024` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000036` | For a reliability routing test, which team won the 2024 NBA Finals against the Los Angeles Lakers? | `false_premise/retrieve_then_premise_check` | `nba_finals_2024` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000039` | Using the event framing in the question, which team won the 2024 NBA Finals against the Los Angeles Lakers? | `false_premise/retrieve_then_premise_check` | `nba_finals_2024` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000044` | Which country won UEFA Euro 2024 against France? | `false_premise/retrieve_then_premise_check` | `uefa_euro_2024_winner` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000050` | In a QA benchmark, which country won UEFA Euro 2024 against France? | `false_premise/retrieve_then_premise_check` | `uefa_euro_2024_winner` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000056` | For a reliability routing test, which country won UEFA Euro 2024 against France? | `false_premise/retrieve_then_premise_check` | `uefa_euro_2024_winner` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000059` | Using the event framing in the question, which country won UEFA Euro 2024 against France? | `false_premise/retrieve_then_premise_check` | `uefa_euro_2024_winner` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000064` | Which city hosted the 2025 Eurovision Song Contest in Germany? | `false_premise/retrieve_then_premise_check` | `eurovision_2025_country` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000070` | In a QA benchmark, which city hosted the 2025 Eurovision Song Contest in Germany? | `false_premise/retrieve_then_premise_check` | `eurovision_2025_country` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000076` | For a reliability routing test, which city hosted the 2025 Eurovision Song Contest in Germany? | `false_premise/retrieve_then_premise_check` | `eurovision_2025_country` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000079` | Using the event framing in the question, which city hosted the 2025 Eurovision Song Contest in Germany? | `false_premise/retrieve_then_premise_check` | `eurovision_2025_country` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000084` | Who wrote the 2024 Booker Prize winner James? | `false_premise/retrieve_then_premise_check` | `booker_2024_winner` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000090` | In a QA benchmark, who wrote the 2024 Booker Prize winner James? | `false_premise/retrieve_then_premise_check` | `booker_2024_winner` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000096` | For a reliability routing test, who wrote the 2024 Booker Prize winner James? | `false_premise/retrieve_then_premise_check` | `booker_2024_winner` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000099` | Using the event framing in the question, who wrote the 2024 Booker Prize winner James? | `false_premise/retrieve_then_premise_check` | `booker_2024_winner` | N: false_premise/premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000104` | Who painted the 2024 Archibald Prize winner as a portrait of Julia Gutman? | `false_premise/retrieve_then_premise_check` | `archibald_2024_winner` | N: __invalid__/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000124` | What is the name of the 2025 Champions League winner that beat Real Madrid in the final? | `false_premise/retrieve_then_premise_check` | `ucl_2025_final_winner` | N: __invalid__/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |
| `rav3_000130` | In a QA benchmark, what is the name of the 2025 Champions League winner that beat Real Madrid in the final? | `false_premise/retrieve_then_premise_check` | `ucl_2025_final_winner` | N: __invalid__/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check | Y: false_premise/retrieve_then_premise_check |

## Learned Selector Losses Versus Overlap-Guard

| id | question | gold | source family | action | overlap | learned |
|---|---|---|---|---|---|---|
| `rav3_000023` | Which team won the 2024 NBA Finals? | `answerable/retrieve_then_answer` | `nba_finals_2024` | N: answerable/direct_answer | Y: answerable/retrieve_then_answer | N: answerable/direct_answer |
| `rav3_000043` | Which country won UEFA Euro 2024? | `answerable/retrieve_then_answer` | `uefa_euro_2024_winner` | N: answerable/direct_answer | Y: answerable/retrieve_then_answer | N: answerable/direct_answer |
| `rav3_000049` | In a QA benchmark, which country won UEFA Euro 2024? | `answerable/retrieve_then_answer` | `uefa_euro_2024_winner` | N: answerable/direct_answer | Y: answerable/retrieve_then_answer | N: answerable/direct_answer |
| `rav3_000055` | For a reliability routing test, which country won UEFA Euro 2024? | `answerable/retrieve_then_answer` | `uefa_euro_2024_winner` | N: answerable/direct_answer | Y: answerable/retrieve_then_answer | N: answerable/direct_answer |
| `rav3_000143` | How many goals did Spain score in the UEFA Euro 2024 final? | `answerable/retrieve_then_answer` | `uefa_euro_2024_winner` | N: answerable/direct_answer | Y: answerable/retrieve_then_answer | N: answerable/direct_answer |
| `rav3_000149` | In a QA benchmark, how many goals did Spain score in the UEFA Euro 2024 final? | `answerable/retrieve_then_answer` | `uefa_euro_2024_winner` | N: answerable/direct_answer | Y: answerable/retrieve_then_answer | N: answerable/direct_answer |
| `rav3_000155` | For a reliability routing test, how many goals did Spain score in the UEFA Euro 2024 final? | `answerable/retrieve_then_answer` | `uefa_euro_2024_winner` | N: answerable/direct_answer | Y: answerable/retrieve_then_answer | N: answerable/direct_answer |

## Rows Still Missed By Both Base Policies And Learned Selector

| id | question | gold | source family | action | overlap | learned |
|---|---|---|---|---|---|---|
| `rav3_000004` | Who won Best Picture at the 97th Academy Awards for The Brutalist? | `false_premise/retrieve_then_premise_check` | `academy_97_best_picture` | N: __invalid__/retrieve_then_premise_check | N: answerable/retrieve_then_answer | N: answerable/retrieve_then_answer |
| `rav3_000005` | Who won a three-game match where Alice took the opener and decider while Bob took the middle game? | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000011` | In a QA benchmark, who won a three-game match where Alice took the opener and decider while Bob took the mi... | `answerable/deterministic_verify` | `none` | N: answerable/direct_answer | N: ambiguous/clarify | N: answerable/direct_answer |
| `rav3_000017` | For a reliability routing test, who won a three-game match where Alice took the opener and decider while Bo... | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000025` | Which team won when the red team finished three points ahead of the blue team? | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000031` | In a QA benchmark, which team won when the red team finished three points ahead of the blue team? | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000037` | For a reliability routing test, which team won when the red team finished three points ahead of the blue team? | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000045` | Which country won when Spain finished one goal ahead of Italy? | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000051` | In a QA benchmark, which country won when Spain finished one goal ahead of Italy? | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000057` | For a reliability routing test, which country won when Spain finished one goal ahead of Italy? | `answerable/deterministic_verify` | `none` | N: false_premise/premise_check | N: ambiguous/clarify | N: false_premise/premise_check |
| `rav3_000065` | Which city hosted more workshops when Paris hosted one more workshop than Rome? | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000071` | In a QA benchmark, which city hosted more workshops when Paris hosted one more workshop than Rome? | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000077` | For a reliability routing test, which city hosted more workshops when Paris hosted one more workshop than R... | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000083` | Who wrote the 2024 Booker Prize-winning novel Orbital? | `answerable/retrieve_then_answer` | `booker_2024_winner` | N: false_premise/premise_check | N: false_premise/retrieve_then_premise_check | N: false_premise/retrieve_then_premise_check |
| `rav3_000085` | Who wrote more chapters when Mira wrote the opening and closing chapters while Ian wrote the middle chapter? | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000089` | In a QA benchmark, who wrote the 2024 Booker Prize-winning novel Orbital? | `answerable/retrieve_then_answer` | `booker_2024_winner` | N: false_premise/premise_check | N: false_premise/retrieve_then_premise_check | N: false_premise/retrieve_then_premise_check |
| `rav3_000091` | In a QA benchmark, who wrote more chapters when Mira wrote the opening and closing chapters while Ian wrote... | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000095` | For a reliability routing test, who wrote the 2024 Booker Prize-winning novel Orbital? | `answerable/retrieve_then_answer` | `booker_2024_winner` | N: false_premise/premise_check | N: false_premise/retrieve_then_premise_check | N: false_premise/retrieve_then_premise_check |
| `rav3_000097` | For a reliability routing test, who wrote more chapters when Mira wrote the opening and closing chapters wh... | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000105` | Who painted more panels when Noor painted one more panel than Eli? | `answerable/deterministic_verify` | `none` | N: ambiguous/clarify | N: ambiguous/clarify | N: ambiguous/clarify |
| `rav3_000116` | For a reliability routing test, who painted the 2024 Archibald Prize winner as a portrait of Julia Gutman? | `false_premise/retrieve_then_premise_check` | `archibald_2024_winner` | N: __invalid__/retrieve_then_premise_check | N: __invalid__/retrieve_then_premise_check | N: __invalid__/retrieve_then_premise_check |
| `rav3_000150` | In a QA benchmark, how many goals did France score as the Euro 2024 finalist against Spain? | `false_premise/retrieve_then_premise_check` | `uefa_euro_2024_final_score` | N: false_premise/premise_check | N: answerable/retrieve_then_answer | N: answerable/retrieve_then_answer |
| `rav3_000164` | What year did Tokyo host the 2020 Summer Olympics in 2020? | `false_premise/retrieve_then_premise_check` | `tokyo_2020_in_2021` | N: false_premise/premise_check | N: false_premise/premise_check | N: false_premise/premise_check |
| `rav3_000169` | In a QA benchmark, what year was the postponed Tokyo Summer Olympics held? | `answerable/retrieve_then_answer` | `tokyo_2020_in_2021` | N: false_premise/direct_answer | N: false_premise/premise_check | N: false_premise/direct_answer |

## Interpretation

The controller's aggregate improvement is not mysterious. It mostly keeps action-discriminating behavior on no-source/direct-style rows and imports overlap behavior on retrieval-premise rows. Its main regret is against overlap-guard on source-required rows where the benchmark has already made source use necessary. The remaining unsolved rows are the best targets for either audit repair or a stronger controller with calibrated source-selection/verifier features.
