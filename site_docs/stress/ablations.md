# Suite-Targeted Ablations

## Goal

Estimate false-accept leakage when specific protection suites are disabled.

## Command

```bash
python main/stress_test_ablation.py \
  --bundle-dir main/output/real_multi_task/ioi_v0_gpt2-small
```

## What is ablated

Typical ablation settings remove one suite at a time, for example:

- controls suite
- robustness suite
- statistical rigor suite

## Output artifact

- `stress_test_ablation.json`

## How to read results

Focus on:

- baseline acceptance rate
- ablated acceptance rate
- acceptance uplift (absolute and percentage points)
- number of tier changes

## Interpretation caveats

- Ablations are counterfactual diagnostics, not production policy proposals.
- A suite with low uplift in one lane may still be critical in other tasks/models.
- Always interpret with task/model stratification when available.
