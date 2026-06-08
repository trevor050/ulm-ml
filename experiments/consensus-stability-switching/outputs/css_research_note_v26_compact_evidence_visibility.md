# v26 Compact Evidence Visibility Audit

## Question

v25 made compact diverse prompts by keeping all 20 answer clusters but only one truncated representative rationale per cluster. That saves context, but it creates a risk:

> Did compact prompts hide the trace-correct rationale inside the correct cluster?

If yes, poor compact-verifier performance might be an artifact of evidence truncation rather than verifier weakness.

## Audit

Script: `work/audit_packet_representative_visibility.py`.

The audit checks whether a correct cluster's displayed representatives include at least one trace-correct candidate:

- `top1`: one representative per cluster, matching compact/ultracompact prompts.
- `top2`: two representatives per cluster, matching the full diverse packet assets.

Report: `outputs/packet_representative_visibility.md`.

## Result

| set | packets | unique problems | correct rep top1 | correct rep top2 | rank min/median/p90/max |
|---|---:|---:|---:|---:|---|
| Llama diverse | 27 | 27 | 0.926 | 1.000 | 11 / 13 / 19 / 20 |
| Gemma diverse | 40 | 40 | 0.900 | 0.975 | 11 / 13 / 17 / 18 |
| Llama repeated | 30 | 8 | 1.000 | 1.000 | 11 / 13 / 16 / 20 |
| Gemma repeated | 30 | 11 | 0.933 | 1.000 | 11 / 15 / 18 / 20 |

## Interpretation

Compact prompts are not obviously starving the verifier. In the diverse sets, the first shown representative from a correct cluster is itself trace-correct in about 90-93% of packets. The full two-representative prompt recovers nearly all remaining cases.

This supports the v25 protocol:

1. Run compact prompts first.
2. Treat failures as ambiguous between verifier weakness and evidence truncation.
3. Rerun full prompts on failures.
4. Attribute recovered failures to evidence budget; unrecovered failures to verifier weakness or genuinely misleading clusters.

The audit does not prove compact prompts are semantically sufficient. It only shows that, under trace labels, the compact evidence usually includes at least one correct rationale in the correct cluster.
