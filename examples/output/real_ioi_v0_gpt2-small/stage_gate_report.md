# Stage-Gate Report

- Protocol: `ioi_v0_gpt2-small_real_v1`
- Protocol hash: `d837bdf21051f5e6e4d772966c6c8b47c5a474c77bd93938a48f63a315a05b30`
- Hypotheses: 2
- Accepted: 0
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_ioi_v0_001 | ❌ FAIL | `rejected` | -1.750 | 1.368 | 0.0150 |
| h_ioi_v0_002 | ❌ FAIL | `rejected` | -1.103 | 1.247 | 0.0164 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 2 | 100.0% |
| negative_controls | 2 | 100.0% |
| robustness | 2 | 100.0% |
| baseline_superiority | 2 | 100.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 2 |

## Per-Hypothesis Details

### h_ioi_v0_001
- Passed: False
- Evidence tier: `rejected`
- Failed checks: causal_effect, negative_controls, robustness, baseline_superiority
- Treatment mean: -0.114465
- Cohen's d: -1.7502
- Confirmatory CI (bootstrap): [-0.154491, -0.071007]
- Specificity ratio: 1.367575
- Control abs mean: 0.083699
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.008318
- Permutation p-value: 0.0088
- BH q-value: 0.015000
- Holm-adjusted p: 0.015
- Cells: 8

### h_ioi_v0_002
- Passed: False
- Evidence tier: `rejected`
- Failed checks: causal_effect, negative_controls, robustness, baseline_superiority
- Treatment mean: -0.066611
- Cohen's d: -1.1026
- Confirmatory CI (bootstrap): [-0.104977, -0.028111]
- Specificity ratio: 1.246535
- Control abs mean: 0.053437
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.005039
- Permutation p-value: 0.0175
- BH q-value: 0.016400
- Holm-adjusted p: 0.0164
- Cells: 8
