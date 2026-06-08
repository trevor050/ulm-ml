# Local Data

The raw trace files required for many reruns are intentionally not committed.

Expected local files:

- `work/GSM8K_Llama-3-8B-Instruct.json`
- `work/MATH_Llama-3-8B-Instruct.json`
- `work/MATH_Gemma-2B.json`
- `work/MATH_Pythia-1B.json`

Also omitted:

- `outputs/cross_seed_router_frontier_v113_details.jsonl`

These files were excluded because they are large generated/source artifacts, not monorepo source. Restore them locally or pass explicit alternate paths when rerunning older scripts.

