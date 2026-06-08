# Doubt-TTS Route Evaluation

Backend: `retrieval_event_verifier`

Overall route accuracy: `1.00` (32/32)

## By Expected Route

| expected_route | n | accuracy | most_common_predictions |
|---|---:|---:|---|
| false_premise_risk | 12 | 1.00 | false_premise_risk:12 |
| ordinary | 20 | 1.00 | ordinary:20 |

## By Subtype

| subtype | n | accuracy | most_common_predictions |
|---|---:|---:|---|
| heldout_nonexistent_award_category | 1 | 1.00 | false_premise_risk:1 |
| heldout_ordinary_event | 12 | 1.00 | ordinary:12 |
| heldout_sport_mismatch | 2 | 1.00 | false_premise_risk:2 |
| heldout_true_location | 2 | 1.00 | ordinary:2 |
| heldout_true_sport_term | 1 | 1.00 | ordinary:1 |
| heldout_true_winner_relation | 5 | 1.00 | ordinary:5 |
| heldout_wrong_location | 2 | 1.00 | false_premise_risk:2 |
| heldout_wrong_winner_relation | 7 | 1.00 | false_premise_risk:7 |

## Confusion Matrix

| expected \ predicted | ordinary | false_premise_risk | ambiguous | verifier | retrieval_needed |
|---|---:|---:|---:|---:|---:|
| ordinary | 20 | 0 | 0 | 0 | 0 |
| false_premise_risk | 0 | 12 | 0 | 0 | 0 |
| ambiguous | 0 | 0 | 0 | 0 | 0 |
| verifier | 0 | 0 | 0 | 0 | 0 |
| retrieval_needed | 0 | 0 | 0 | 0 | 0 |

## Presupposition Issues

| id | predicted | issue |
|---|---|---|
| heldout_event_false_001 | false_premise_risk | retrieval_event_verifier[inferred_source:2015 Rugby World Cup final]: source says New Zealand was the winner, not the defeated side |
| heldout_event_false_002 | false_premise_risk | retrieval_event_verifier[inferred_source:2007 Rugby World Cup final]: source says South Africa was the winner, not the defeated side |
| heldout_event_false_003 | false_premise_risk | retrieval_event_verifier[inferred_source:2011 Rugby World Cup final]: source says New Zealand was the winner, not the defeated side |
| heldout_event_false_004 | false_premise_risk | retrieval_event_verifier[inferred_source:2015 FIFA Women's World Cup final]: source says United States was the winner, not the defeated side |
| heldout_event_false_005 | false_premise_risk | retrieval_event_verifier[inferred_source:Super Bowl XLVII]: source does not support defeating Baltimore Ravens |
| heldout_event_false_006 | false_premise_risk | retrieval_event_verifier[inferred_source:2018 World Series]: source does not support defeating Boston Red Sox |
| heldout_event_false_007 | false_premise_risk | retrieval_event_verifier[inferred_source:2010 UEFA Champions League final]: source says Inter Milan was the winner, not the defeated side |
| heldout_event_false_008 | false_premise_risk | retrieval_event_verifier[inferred_source:2004 Summer Olympics]: source does not support claimed location Sydney |
| heldout_event_false_009 | false_premise_risk | retrieval_event_verifier[inferred_source:2010 Winter Olympics]: source does not support claimed location Toronto |
| heldout_event_false_010 | false_premise_risk | retrieval_event_verifier[inferred_source:Nobel Prize]: source does not support claimed award category Algebra |
| heldout_event_false_011 | false_premise_risk | retrieval_event_verifier[inferred_source:2019 Cricket World Cup final]: cricket source does not support touchdown terminology |
| heldout_event_false_012 | false_premise_risk | retrieval_event_verifier[inferred_source:Super Bowl XLVII]: football source does not support home run terminology |

## Notes

- Route evaluation isolates the router from answer generation and challenge scoring.
- A good routed Doubt-TTS system needs route recall on false-premise/ambiguity risks before it can safely recover coverage.
