# Docstring Method-Sensitivity Explorer

diagnostic_queue_only_not_new_model_evidence

- Method-sensitivity failed docstring claims: **0**
- Single-gate-only method-sensitivity failures: **0**
- Distributed-head repair accepted claims: **0**
- Distributed-head residual gates: **{'method_sensitivity': 8, 'negative_controls': 1}**
- Diagnosis counts: **{}**

## Ranked repair candidates

| Rank | Bundle | Hypothesis | Model | Diagnosis | Ratio | Margin | Single gate | Next experiment |
|---:|---|---|---|---|---:|---:|---|---|

## Recommended program

- Do not relax method_sensitivity for docstring_v0 post hoc.
- Start with single-gate-only method_sensitivity failures whose zero-ablation effect has the same sign as activation patching.
- Use pilot cells to search for components or positions that increase the zero-ablation/activation-patching absolute ratio before running full Stage-2.
- Treat direction-reversal cases as metric/intervention-mapping failures until proven otherwise.
- If no necessity-aligned pilot exists, propose a versioned sufficiency-only docstring claim type rather than accepting current claims under the existing tier.
