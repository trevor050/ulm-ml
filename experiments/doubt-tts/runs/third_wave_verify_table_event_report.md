# Doubt-TTS Route Evaluation

Backend: `table_event_verifier`

Overall route accuracy: `1.00` (72/72)

## By Expected Route

| expected_route | n | accuracy | most_common_predictions |
|---|---:|---:|---|
| false_premise_risk | 36 | 1.00 | false_premise_risk:36 |
| ordinary | 36 | 1.00 | ordinary:36 |

## By Subtype

| subtype | n | accuracy | most_common_predictions |
|---|---:|---:|---|
| false_relation_real_entity | 5 | 1.00 | false_premise_risk:5 |
| future_completed_event | 4 | 1.00 | false_premise_risk:4 |
| nonexistent_award | 5 | 1.00 | false_premise_risk:5 |
| nonexistent_event_year | 8 | 1.00 | false_premise_risk:8 |
| ordinary_event | 36 | 1.00 | ordinary:36 |
| sport_mismatch | 4 | 1.00 | false_premise_risk:4 |
| wrong_date_or_framing | 5 | 1.00 | false_premise_risk:5 |
| wrong_winner_or_host | 5 | 1.00 | false_premise_risk:5 |

## Confusion Matrix

| expected \ predicted | ordinary | false_premise_risk | ambiguous | verifier | retrieval_needed |
|---|---:|---:|---:|---:|---:|
| ordinary | 36 | 0 | 0 | 0 | 0 |
| false_premise_risk | 0 | 36 | 0 | 0 | 0 |
| ambiguous | 0 | 0 | 0 | 0 | 0 |
| verifier | 0 | 0 | 0 | 0 | 0 |
| retrieval_needed | 0 | 0 | 0 | 0 | 0 |

## Presupposition Issues

| id | predicted | issue |
|---|---|---|
| event_false_001 | false_premise_risk | table_event_verifier: event_year: no 2025 Summer Olympics |
| event_false_002 | false_premise_risk | table_event_verifier: event_year: no 2024 Winter Olympics |
| event_false_003 | false_premise_risk | table_event_verifier: event_year: no 2011 Olympic Games |
| event_false_004 | false_premise_risk | table_event_verifier: event_year: no 2023 Winter Olympics |
| event_false_005 | false_premise_risk | table_event_verifier: event_year: 2026 is a Winter Olympics year, not a Summer Olympics year |
| event_false_006 | false_premise_risk | table_event_verifier: event_year: men's FIFA World Cup was not held in 2019 |
| event_false_007 | false_premise_risk | table_event_verifier: sport_mismatch: NBA Finals do not have touchdowns |
| event_false_008 | false_premise_risk | table_event_verifier: sport_mismatch: Chicago Bulls are an NBA team, not a World Series opponent |
| event_false_009 | false_premise_risk | table_event_verifier: winner_relation: France won the 2018 FIFA World Cup final |
| event_false_010 | false_premise_risk | table_event_verifier: host_relation: Brazil hosted the 2014 FIFA World Cup |
| event_false_011 | false_premise_risk | table_event_verifier: date_frame: Tokyo 2020 was held in 2021 |
| event_false_012 | false_premise_risk | table_event_verifier: date_frame: the 2022 FIFA World Cup final was played in 2022 |
| event_false_013 | false_premise_risk | table_event_verifier: date_frame: the London Summer Olympics were held in 2012 |
| event_false_014 | false_premise_risk | table_event_verifier: date_frame: the Beijing Winter Olympics were held in 2022 |
| event_false_015 | false_premise_risk | table_event_verifier: award_category: Nobel Prize in Mathematics does not exist |
| event_false_016 | false_premise_risk | table_event_verifier: award_relation: no acting Oscar was awarded for playing Harry Potter in 2001 |
| event_false_017 | false_premise_risk | table_event_verifier: award_relation: Grammys are music awards and Van Gogh did not win one |
| event_false_018 | false_premise_risk | table_event_verifier: award_relation: Nobel Prizes began after Newton's lifetime |
| event_false_019 | false_premise_risk | table_event_verifier: award_relation: Ada Lovelace did not win an Olympic medal |
| event_false_020 | false_premise_risk | table_event_verifier: sport_relation: Serena Williams is a tennis player, not a World Cup soccer captain |
| event_false_021 | false_premise_risk | table_event_verifier: award_relation: Tesla did not win an Olympic medal |
| event_false_022 | false_premise_risk | table_event_verifier: award_relation: Beethoven died before the Academy Awards existed |
| event_false_023 | false_premise_risk | table_event_verifier: event_year: no 2027 Winter Olympics |
| event_false_024 | false_premise_risk | table_event_verifier: future_completed: 2028 Summer Olympics have not occurred as of current date |
| event_false_025 | false_premise_risk | table_event_verifier: future_completed: 2027 World Series has not occurred as of current date |
| event_false_026 | false_premise_risk | table_event_verifier: future_completed: 2026 FIFA World Cup final has not occurred as of current date |
| event_false_027 | false_premise_risk | table_event_verifier: winner_relation: Denver Nuggets won the 2023 NBA Finals |
| event_false_028 | false_premise_risk | table_event_verifier: winner_relation: France won, it was not defeated in the 2018 final |
| event_false_029 | false_premise_risk | table_event_verifier: sport_mismatch: Super Bowl scoring does not include home runs |
| event_false_030 | false_premise_risk | table_event_verifier: sport_mismatch: Formula One has races/grands prix, not a winning-goal match |

## Notes

- Route evaluation isolates the router from answer generation and challenge scoring.
- A good routed Doubt-TTS system needs route recall on false-premise/ambiguity risks before it can safely recover coverage.
