# v118 Answer-Symbolic Guard Audit

## Question

v114 showed that the Gemma-with-Llama auxiliary-generator router keeps substantial recovery signal under problem-disjoint source calibration, but low-regression control breaks on held-out problems. v115 showed that a same-feature correctness head does not fix this. v117 showed there are no hidden logprob/state fields in the local traces.

This audit asks whether the remaining cheap local signal, the text/shape of the selected answer itself, can guard regressions.

## Setup

I rebuilt the v109/v114 Gemma-with-Llama candidate rows with answer-level metadata:

- baseline answer and auxiliary candidate answer
- numeric parseability, answer length, fraction/decimal/radical/set/matrix flags
- numeric equality/sign/ratio/difference features between candidate and baseline
- the original v109 base router features

Then I reran the v114 problem-disjoint held-out seed protocol with four score families:

- `base_utility`: original v114 learned utility score
- `symbolic_utility`: answer-symbolic features only
- `base_symbolic_utility`: original features plus answer-symbolic features
- `base_symbolic_correctness`: original plus answer-symbolic features trained for candidate correctness

Scripts and outputs:

- `work/cross_seed_router_symbolic_guard_audit.py`
- `outputs/cross_seed_router_symbolic_guard_v118.md`
- `outputs/cross_seed_router_symbolic_guard_v118_aggregate.csv`
- `outputs/cross_seed_router_symbolic_guard_v118_separability_aggregate.csv`
- `outputs/cross_seed_router_symbolic_guard_v118_answer_rows.jsonl`

Command:

```bash
python3 work/cross_seed_router_symbolic_guard_audit.py --rebuild-cache --output-prefix cross_seed_router_symbolic_guard_v118 --answer-rows-cache outputs/cross_seed_router_symbolic_guard_v118_answer_rows.jsonl
```

## Result

Answer-symbolic features do not fix the problem-disjoint regression-control failure.

Recovery-vs-regression separability:

| score | recovery/regression AUC | candidate-correct AUC |
|---|---:|---:|
| `base_utility` | `0.711` | `0.802` |
| `base_symbolic_correctness` | `0.652` | `0.765` |
| `base_symbolic_utility` | `0.608` | `0.669` |
| `symbolic_utility` | `0.509` | `0.648` |

No score family produced an aggregate row with `<=5` held-out regressions.

Best mean deltas still came from the original base utility score:

| score | source budget | mean delta | recoveries | regressions |
|---|---:|---:|---:|---:|
| `base_utility` | `20` | `+0.147` | `306` | `45` |
| `base_utility` | `10` | `+0.138` | `288` | `43` |
| `base_utility` | `5` | `+0.131` | `271` | `39` |
| `base_utility` | `2` | `+0.118` | `240` | `30` |
| `base_utility` | `0` | `+0.097` | `192` | `20` |

## Read

The answer text contains some weak structure, but not the missing regression-risk signal. Adding numeric/shape features either trails the original router score or increases held-out regressions. This makes the v116/v117 boundary sharper: the current trace-only route is running out of cheap guard signals.

The next credible signal should come from a different source:

- a live verifier over a smaller pairwise decision
- regenerated traces with decoder telemetry
- more diverse generator traces
- a stronger symbolic equivalence checker with problem semantics, not just answer shape

