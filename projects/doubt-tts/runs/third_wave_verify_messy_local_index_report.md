# Doubt-TTS Route Evaluation

Backend: `retrieval_event_verifier`

Overall route accuracy: `1.00` (24/24)

## By Expected Route

| expected_route | n | accuracy | most_common_predictions |
|---|---:|---:|---|
| false_premise_risk | 12 | 1.00 | false_premise_risk:12 |
| ordinary | 12 | 1.00 | ordinary:12 |

## By Subtype

| subtype | n | accuracy | most_common_predictions |
|---|---:|---:|---|
| messy_nonexistent_award_category | 1 | 1.00 | false_premise_risk:1 |
| messy_ordinary_event | 8 | 1.00 | ordinary:8 |
| messy_sport_mismatch | 2 | 1.00 | false_premise_risk:2 |
| messy_true_location | 1 | 1.00 | ordinary:1 |
| messy_true_sport_term | 1 | 1.00 | ordinary:1 |
| messy_true_winner_relation | 2 | 1.00 | ordinary:2 |
| messy_wrong_location | 2 | 1.00 | false_premise_risk:2 |
| messy_wrong_winner_relation | 7 | 1.00 | false_premise_risk:7 |

## Confusion Matrix

| expected \ predicted | ordinary | false_premise_risk | ambiguous | verifier | retrieval_needed |
|---|---:|---:|---:|---:|---:|
| ordinary | 12 | 0 | 0 | 0 | 0 |
| false_premise_risk | 0 | 12 | 0 | 0 | 0 |
| ambiguous | 0 | 0 | 0 | 0 | 0 |
| verifier | 0 | 0 | 0 | 0 | 0 |
| retrieval_needed | 0 | 0 | 0 | 0 | 0 |

## Presupposition Issues

| id | predicted | issue |
|---|---|---|
| messy_event_false_001 | false_premise_risk | retrieval_event_verifier[local_cached_index:2015 Rugby World Cup final]: source says New Zealand was the winner, not the defeated side |
| messy_event_false_002 | false_premise_risk | retrieval_event_verifier[local_cached_index:2007 Rugby World Cup final]: source says South Africa was the winner, not the defeated side |
| messy_event_false_003 | false_premise_risk | retrieval_event_verifier[local_cached_index:Super Bowl XLVII]: source does not support defeating Baltimore Ravens |
| messy_event_false_004 | false_premise_risk | retrieval_event_verifier[local_cached_index:2018 World Series]: source does not support defeating Boston Red Sox |
| messy_event_false_005 | false_premise_risk | retrieval_event_verifier[local_cached_index:2010 UEFA Champions League final]: source says Inter Milan was the winner, not the defeated side |
| messy_event_false_006 | false_premise_risk | retrieval_event_verifier[local_cached_index:2004 Summer Olympics]: source does not support claimed location Sydney |
| messy_event_false_007 | false_premise_risk | retrieval_event_verifier[local_cached_index:2010 Winter Olympics]: source does not support claimed location Toronto |
| messy_event_false_008 | false_premise_risk | retrieval_event_verifier[local_cached_index:Nobel Prize]: source does not support claimed award category Algebra |
| messy_event_false_009 | false_premise_risk | retrieval_event_verifier[local_cached_index:2019 Cricket World Cup final]: cricket source does not support touchdown terminology |
| messy_event_false_010 | false_premise_risk | retrieval_event_verifier[local_cached_index:Super Bowl XLVII]: football source does not support home run terminology |
| messy_event_false_011 | false_premise_risk | retrieval_event_verifier[local_cached_index:2015 FIFA Women's World Cup final]: source says United States was the winner, not the defeated side |
| messy_event_false_012 | false_premise_risk | retrieval_event_verifier[local_cached_index:2022 FIFA World Cup final]: source does not support defeating Argentina |

## Notes

- Route evaluation isolates the router from answer generation and challenge scoring.
- A good routed Doubt-TTS system needs route recall on false-premise/ambiguity risks before it can safely recover coverage.
