# Stage-Gate Report

- Protocol: `ioi_v0_gpt2-small_mock_v1`
- Protocol hash: `a1d5fcfb76794cfb1c47cc046af85a86b883e8a3319d38f1381bef570179d4fb`
- Hypotheses: 3
- Accepted: 3
- Unstable: 0
- Rejected: 0
- All pass: True
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_ioi_v0_001 | ✅ PASS | `causal_plus_robustness` | 6.093 | 11.069 | 0.0000 |
| h_ioi_v0_002 | ✅ PASS | `causal_plus_robustness` | 6.730 | 12.474 | 0.0000 |
| h_ioi_v0_003 | ✅ PASS | `causal_plus_robustness` | 6.753 | 11.780 | 0.0000 |

## Failure Analysis

No failures detected.

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `causal_plus_robustness` | 3 |

## Per-Hypothesis Details

### h_ioi_v0_001
- Passed: True
- Evidence tier: `causal_plus_robustness`
- Failed checks: none
- Treatment mean: 0.075806
- Cohen's d: 6.0925
- Confirmatory CI (bootstrap): [0.070256, 0.081987]
- Specificity ratio: 11.069131
- Control abs mean: 0.006848
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.004094
- Permutation p-value: 0.0001
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 16

### h_ioi_v0_002
- Passed: True
- Evidence tier: `causal_plus_robustness`
- Failed checks: none
- Treatment mean: 0.081394
- Cohen's d: 6.7296
- Confirmatory CI (bootstrap): [0.074912, 0.086500]
- Specificity ratio: 12.474138
- Control abs mean: 0.006525
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.003719
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 16

### h_ioi_v0_003
- Passed: True
- Evidence tier: `causal_plus_robustness`
- Failed checks: none
- Treatment mean: 0.077381
- Cohen's d: 6.7534
- Confirmatory CI (bootstrap): [0.072387, 0.083175]
- Specificity ratio: 11.780209
- Control abs mean: 0.006569
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.007444
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 16
