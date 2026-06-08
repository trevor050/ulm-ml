# Reliability-Action v3 Cost Frontier

Status: diagnostic cost/accuracy accounting over the 300-row cue-balanced v3 scaffold. Costs are hand-set diagnostic units, not measured latency or dollars.

Cost map: direct/clarify=1, premise-check=1.5, deterministic verify=2, retrieve-answer=4, retrieve-premise=4.5.

| method | joint | validity | compute | mean cost | excess cost | joint/cost | wasted retrieval | missed retrieval | direct compute | retrieval-premise joint | retrieval-premise compute | invalid actions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `legacy_keyword_question_only_router` | 87/300 (0.290) | 150/300 (0.500) | 87/300 (0.290) | 2.28 | -0.10 | 0.127 | 52 | 38 | 30/45 | 12/60 | 12/60 | 0 |
| `oracle_template_family_majority` | 60/300 (0.200) | 60/300 (0.200) | 60/300 (0.200) | 1.00 | -1.38 | 0.200 | 0 | 105 | 0/45 | 0/60 | 0/60 | 0 |
| `always_retrieve_premise` | 60/300 (0.200) | 105/300 (0.350) | 60/300 (0.200) | 4.50 | +2.12 | 0.044 | 195 | 0 | 0/45 | 60/60 | 60/60 | 0 |
| `always_retrieve_answer` | 45/300 (0.150) | 135/300 (0.450) | 45/300 (0.150) | 4.00 | +1.62 | 0.037 | 195 | 0 | 0/45 | 0/60 | 0/60 | 0 |
| `qwen3.5:9b:action_discriminating` | 167/300 (0.557) | 226/300 (0.753) | 178/300 (0.593) | 1.51 | -0.87 | 0.369 | 2 | 72 | 45/45 | 0/60 | 11/60 | 0 |
| `qwen3.5:9b:overlap_guard` | 192/300 (0.640) | 236/300 (0.787) | 206/300 (0.687) | 1.97 | -0.40 | 0.324 | 8 | 42 | 41/45 | 11/60 | 25/60 | 0 |
| `qwen3.5:9b:hybrid_overlap_if_either_rtp` | 170/300 (0.567) | 232/300 (0.773) | 184/300 (0.613) | 1.70 | -0.68 | 0.334 | 5 | 60 | 45/45 | 11/60 | 25/60 | 0 |
| `qwen3.5:9b:family_heldout_rule_selector` | 192/300 (0.640) | 236/300 (0.787) | 206/300 (0.687) | 1.97 | -0.40 | 0.324 | 8 | 42 | 41/45 | 11/60 | 25/60 | 0 |
| `qwen3.5:9b:learned_policy_joint_selector` | 193/300 (0.643) | 230/300 (0.767) | 208/300 (0.693) | 1.98 | -0.40 | 0.325 | 8 | 41 | 41/45 | 10/60 | 25/60 | 0 |
| `qwen3.5:9b:cue_stem_heldout_learned_policy_joint_selector` | 193/300 (0.643) | 233/300 (0.777) | 208/300 (0.693) | 1.98 | -0.39 | 0.324 | 8 | 41 | 41/45 | 10/60 | 25/60 | 0 |
| `gemma4:26b:action_discriminating` | 201/300 (0.670) | 246/300 (0.820) | 214/300 (0.713) | 1.78 | -0.60 | 0.377 | 0 | 54 | 45/45 | 6/60 | 19/60 | 0 |
| `gemma4:26b:overlap_guard` | 232/300 (0.773) | 254/300 (0.847) | 237/300 (0.790) | 2.38 | +0.01 | 0.324 | 17 | 9 | 27/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:hybrid_overlap_if_either_rtp` | 245/300 (0.817) | 260/300 (0.867) | 250/300 (0.833) | 2.13 | -0.24 | 0.383 | 1 | 19 | 45/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:family_heldout_rule_selector` | 245/300 (0.817) | 260/300 (0.867) | 250/300 (0.833) | 2.13 | -0.24 | 0.383 | 1 | 19 | 45/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:learned_policy_joint_selector` | 246/300 (0.820) | 260/300 (0.867) | 251/300 (0.837) | 2.17 | -0.20 | 0.378 | 1 | 15 | 45/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:cue_stem_heldout_learned_policy_joint_selector` | 246/300 (0.820) | 260/300 (0.867) | 251/300 (0.837) | 2.15 | -0.23 | 0.382 | 1 | 17 | 45/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:learned_policy_reason_question_joint_selector` | 252/300 (0.840) | 258/300 (0.860) | 257/300 (0.857) | 2.21 | -0.16 | 0.380 | 0 | 10 | 45/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:cue_stem_heldout_learned_policy_reason_question_joint_selector` | 250/300 (0.833) | 259/300 (0.863) | 255/300 (0.850) | 2.21 | -0.17 | 0.377 | 1 | 11 | 45/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:learned_policy_question_joint_selector` | 251/300 (0.837) | 259/300 (0.863) | 256/300 (0.853) | 2.21 | -0.17 | 0.379 | 1 | 11 | 45/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:learned_policy_reason_joint_selector` | 250/300 (0.833) | 258/300 (0.860) | 255/300 (0.850) | 2.19 | -0.18 | 0.380 | 0 | 12 | 45/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:cue_stem_heldout_learned_policy_reason_joint_selector` | 246/300 (0.820) | 260/300 (0.867) | 251/300 (0.837) | 2.16 | -0.21 | 0.379 | 1 | 16 | 45/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:cue_stem_heldout_learned_policy_question_joint_selector` | 243/300 (0.810) | 259/300 (0.863) | 248/300 (0.827) | 2.26 | -0.12 | 0.359 | 7 | 12 | 39/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:hybrid_overlap_if_overlap_rtp` | 239/300 (0.797) | 254/300 (0.847) | 245/300 (0.817) | 2.17 | -0.21 | 0.368 | 1 | 17 | 45/45 | 47/60 | 53/60 | 0 |
| `gemma4:26b:hybrid_overlap_if_overlap_any_retrieval` | 237/300 (0.790) | 260/300 (0.867) | 242/300 (0.807) | 2.41 | +0.04 | 0.328 | 17 | 7 | 29/45 | 47/60 | 52/60 | 0 |
| `gemma4:26b:hybrid_overlap_if_both_rtp` | 208/300 (0.693) | 254/300 (0.847) | 214/300 (0.713) | 1.78 | -0.60 | 0.390 | 0 | 54 | 45/45 | 13/60 | 19/60 | 0 |
| `qwen3.5:9b:learned_policy_reason_question_joint_selector` | 203/300 (0.677) | 232/300 (0.773) | 219/300 (0.730) | 1.98 | -0.40 | 0.343 | 5 | 35 | 44/45 | 10/60 | 26/60 | 0 |
| `qwen3.5:9b:learned_policy_reason_joint_selector` | 202/300 (0.673) | 232/300 (0.773) | 218/300 (0.727) | 1.99 | -0.39 | 0.339 | 6 | 35 | 44/45 | 10/60 | 26/60 | 0 |
| `qwen3.5:9b:learned_policy_question_joint_selector` | 202/300 (0.673) | 231/300 (0.770) | 220/300 (0.733) | 2.00 | -0.38 | 0.337 | 7 | 35 | 44/45 | 10/60 | 28/60 | 0 |
| `qwen3.5:9b:cue_stem_heldout_learned_policy_reason_question_joint_selector` | 196/300 (0.653) | 236/300 (0.787) | 211/300 (0.703) | 1.99 | -0.39 | 0.329 | 7 | 38 | 42/45 | 10/60 | 25/60 | 0 |
| `qwen3.5:9b:cue_stem_heldout_learned_policy_reason_joint_selector` | 196/300 (0.653) | 235/300 (0.783) | 213/300 (0.710) | 2.00 | -0.37 | 0.326 | 7 | 36 | 43/45 | 10/60 | 27/60 | 0 |
| `qwen3.5:9b:cue_stem_heldout_learned_policy_question_joint_selector` | 193/300 (0.643) | 232/300 (0.773) | 208/300 (0.693) | 1.97 | -0.40 | 0.326 | 8 | 41 | 41/45 | 9/60 | 24/60 | 0 |
| `qwen3.5:9b:hybrid_overlap_if_overlap_any_retrieval` | 185/300 (0.617) | 230/300 (0.767) | 202/300 (0.673) | 1.97 | -0.41 | 0.313 | 8 | 35 | 44/45 | 11/60 | 28/60 | 0 |
| `qwen3.5:9b:hybrid_overlap_if_overlap_rtp` | 170/300 (0.567) | 231/300 (0.770) | 187/300 (0.623) | 1.75 | -0.62 | 0.324 | 5 | 54 | 45/45 | 11/60 | 28/60 | 0 |
| `qwen3.5:9b:hybrid_overlap_if_both_rtp` | 168/300 (0.560) | 227/300 (0.757) | 178/300 (0.593) | 1.51 | -0.87 | 0.371 | 2 | 72 | 45/45 | 1/60 | 11/60 | 0 |
| `always_clarify` | 60/300 (0.200) | 60/300 (0.200) | 60/300 (0.200) | 1.00 | -1.38 | 0.200 | 0 | 105 | 0/45 | 0/60 | 0/60 | 0 |
| `always_answerable_direct` | 45/300 (0.150) | 135/300 (0.450) | 45/300 (0.150) | 1.00 | -1.38 | 0.150 | 0 | 105 | 45/45 | 0/60 | 0/60 | 0 |
| `cue_family_only_router` | 45/300 (0.150) | 135/300 (0.450) | 45/300 (0.150) | 1.00 | -1.38 | 0.150 | 0 | 105 | 45/45 | 0/60 | 0/60 | 0 |
| `always_false_premise_check` | 45/300 (0.150) | 105/300 (0.350) | 45/300 (0.150) | 1.50 | -0.88 | 0.100 | 0 | 105 | 0/45 | 0/60 | 0/60 | 0 |
| `always_verify` | 45/300 (0.150) | 135/300 (0.450) | 45/300 (0.150) | 2.00 | -0.38 | 0.075 | 0 | 105 | 0/45 | 0/60 | 0/60 | 0 |

## Interpretation

- Gemma action-discriminating is cheap and preserves direct controls, but misses many required retrieval actions.
- Gemma overlap-guard greatly reduces missed retrieval and repairs retrieval-premise rows, but wastes retrieval on direct/control rows.
- The Gemma policy-output controllers recover the overlap-guard hard-branch gain while restoring direct-answer specificity and lowering mean diagnostic cost.
- Always-retrieval baselines are included to show why the result is not reducible to spending more retrieval everywhere.
- This remains development evidence. The same cost accounting should be part of the locked manually audited benchmark.
