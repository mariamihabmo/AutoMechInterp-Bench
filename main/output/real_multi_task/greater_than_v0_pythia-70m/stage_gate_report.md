# Stage-Gate Report

- Protocol: `real_greater_than_v0_pythia-70m`
- Protocol hash: `06f99d91efb0299bb92b25793f806d09e6814cbecd1f0e06aa9993e6e9aacaa8`
- Hypotheses: 3
- Accepted: 0
- Unstable: 1
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_greater_than_v0_001 | ❌ FAIL | `suggestive` | -1.496 | 8.771 | 0.1908 |
| h_greater_than_v0_002 | ❌ FAIL | `rejected` | -0.985 | 12.821 | 0.1908 |
| h_greater_than_v0_003 | ❌ FAIL | `rejected` | -0.494 | 4.544 | 0.4998 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| confirmatory_present | 3 | 100.0% |
| confirmatory_ci | 3 | 100.0% |
| multiplicity | 3 | 100.0% |
| method_sensitivity | 2 | 66.7% |
| causal_effect | 2 | 66.7% |
| robustness | 2 | 66.7% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `suggestive` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_greater_than_v0_001
- Passed: False
- Evidence tier: `suggestive`
- Failed checks: confirmatory_present, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -0.133302
- Cohen's d: -1.4964
- Confirmatory CI (bootstrap): [-0.212356, -0.057471]
- Specificity ratio: 8.770677
- Control abs mean: 0.015199
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.075831
- Permutation p-value: 0.1259
- BH q-value: 0.190800
- Holm-adjusted p: 0.3795
- Cells: 4

### h_greater_than_v0_002
- Passed: False
- Evidence tier: `rejected`
- Failed checks: confirmatory_present, causal_effect, robustness, confirmatory_ci, multiplicity
- Treatment mean: -0.017963
- Cohen's d: -0.9846
- Confirmatory CI (bootstrap): [-0.035366, -0.002507]
- Specificity ratio: 12.820542
- Control abs mean: 0.001401
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.015589
- Permutation p-value: 0.1248
- BH q-value: 0.190800
- Holm-adjusted p: 0.3795
- Cells: 4

### h_greater_than_v0_003
- Passed: False
- Evidence tier: `rejected`
- Failed checks: confirmatory_present, causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -0.031803
- Cohen's d: -0.4938
- Confirmatory CI (bootstrap): [-0.091002, 0.021615]
- Specificity ratio: 4.543561
- Control abs mean: 0.007000
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.055452
- Permutation p-value: 0.498
- BH q-value: 0.499800
- Holm-adjusted p: 0.4998
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
