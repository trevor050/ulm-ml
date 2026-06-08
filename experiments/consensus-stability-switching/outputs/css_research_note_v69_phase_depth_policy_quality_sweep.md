# v69 Phase Depth Policy Quality Sweep

**Date:** June 1, 2026  
**Question:** Does the v68 depth policy depend on one verifier-quality setting?

## Run

I reran the costed utility frontier over verifier success and false-regression assumptions.

```bash
python3 work/phase_depth_policy_quality_sweep.py \
  --cost-csv outputs/phase_depth_cost_roi.csv \
  --output-prefix phase_depth_policy_quality_sweep \
  --value-grid 4000,8000,16000,32000,64000 \
  --success-grid 0.50,0.80,1.00 \
  --regress-grid 0.00,0.02,0.05
```

Primary artifact: [phase_depth_policy_quality_sweep.md](phase_depth_policy_quality_sweep.md).

## Result

The policy degrades sensibly rather than holding a fixed depth:

- At lower verifier success, the frontier shifts toward no-verifier or top-10.
- Top-20 remains a high-value tail choice, not the ordinary operating point.
- At 80% success / 2% false regression, the v68 thresholds hold: top20 beats top10 above about `20k` tokens per +1.0 accuracy for Gemma and `35k` for Llama.
- At 50% success, those thresholds rise to about `31.7k` for Gemma and `55.6k` for Llama under 2% false regression.

## Read

This is the expected behavior for a deployed policy. If the verifier is worse, the system should not blindly keep paying for deep prompts. It should either run top-10 or abstain from verification under low value settings.

The minor non-obvious detail is false regression: under the projection formula, higher false regression can slightly lower the top20-vs-top10 threshold because deeper recovery leaves fewer non-recovered cases. But absolute utility can still worsen and push low-value settings to no-verifier.

## Caveat

This is still projected from compact prompt costs and assumed verifier quality. The real verifier benchmark needs to measure success and false-regression rates directly, then plug them into this frontier.
