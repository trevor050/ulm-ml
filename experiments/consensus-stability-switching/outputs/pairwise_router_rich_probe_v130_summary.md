# Pairwise Rich Probe Summary

Manifest: `pairwise_router_rich_probe_v130_manifest.csv`.

## By Prompt Variant

| model | variant | rows | choice acc | accepts | rec/reg | A | B | BOTH | NEITHER | invalid |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gemma4 | solve_first | 12 | 0.000 | 0 | 0/0 | 0 | 0 | 0 | 0 | 12 |
| gemma4 | type_check | 12 | 0.000 | 0 | 0/0 | 0 | 0 | 0 | 0 | 12 |
| mathstral | solve_first | 12 | 0.417 | 3 | 0/3 | 0 | 1 | 2 | 9 | 0 |
| mathstral | type_check | 12 | 0.417 | 1 | 0/1 | 0 | 1 | 0 | 11 | 0 |
| qwen14b | solve_first | 12 | 0.250 | 6 | 2/4 | 6 | 5 | 1 | 0 | 0 |
| qwen14b | type_check | 12 | 0.417 | 4 | 2/2 | 8 | 4 | 0 | 0 | 0 |

## By Variant And Category

| model | variant | category | rows | choice acc | accepts | rec/reg | A | B | BOTH | NEITHER | invalid |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gemma4 | solve_first | neither_correct | 5 | 0.000 | 0 | 0/0 | 0 | 0 | 0 | 0 | 5 |
| gemma4 | solve_first | recovery | 2 | 0.000 | 0 | 0/0 | 0 | 0 | 0 | 0 | 2 |
| gemma4 | solve_first | regression | 5 | 0.000 | 0 | 0/0 | 0 | 0 | 0 | 0 | 5 |
| gemma4 | type_check | neither_correct | 5 | 0.000 | 0 | 0/0 | 0 | 0 | 0 | 0 | 5 |
| gemma4 | type_check | recovery | 2 | 0.000 | 0 | 0/0 | 0 | 0 | 0 | 0 | 2 |
| gemma4 | type_check | regression | 5 | 0.000 | 0 | 0/0 | 0 | 0 | 0 | 0 | 5 |
| mathstral | solve_first | neither_correct | 5 | 1.000 | 0 | 0/0 | 0 | 0 | 0 | 5 | 0 |
| mathstral | solve_first | recovery | 2 | 0.000 | 0 | 0/0 | 0 | 0 | 0 | 2 | 0 |
| mathstral | solve_first | regression | 5 | 0.000 | 3 | 0/3 | 0 | 1 | 2 | 2 | 0 |
| mathstral | type_check | neither_correct | 5 | 1.000 | 0 | 0/0 | 0 | 0 | 0 | 5 | 0 |
| mathstral | type_check | recovery | 2 | 0.000 | 0 | 0/0 | 0 | 0 | 0 | 2 | 0 |
| mathstral | type_check | regression | 5 | 0.000 | 1 | 0/1 | 0 | 1 | 0 | 4 | 0 |
| qwen14b | solve_first | neither_correct | 5 | 0.000 | 0 | 0/0 | 5 | 0 | 0 | 0 | 0 |
| qwen14b | solve_first | recovery | 2 | 1.000 | 2 | 2/0 | 0 | 2 | 0 | 0 | 0 |
| qwen14b | solve_first | regression | 5 | 0.200 | 4 | 0/4 | 1 | 3 | 1 | 0 | 0 |
| qwen14b | type_check | neither_correct | 5 | 0.000 | 0 | 0/0 | 5 | 0 | 0 | 0 | 0 |
| qwen14b | type_check | recovery | 2 | 1.000 | 2 | 2/0 | 0 | 2 | 0 | 0 | 0 |
| qwen14b | type_check | regression | 5 | 0.600 | 2 | 0/2 | 3 | 2 | 0 | 0 | 0 |

## Read

This is a targeted stress panel, not a natural-rate benchmark. It is designed to test whether richer answer-only pairwise prompts repair known qwen/union regressions while preserving matched recoveries and safe fallback behavior.

Variant CSV: [pairwise_router_rich_probe_v130_summary.csv](pairwise_router_rich_probe_v130_summary.csv). Category CSV: [pairwise_router_rich_probe_v130_summary_categories.csv](pairwise_router_rich_probe_v130_summary_categories.csv). Details: [pairwise_router_rich_probe_v130_summary_details.csv](pairwise_router_rich_probe_v130_summary_details.csv).