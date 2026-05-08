# Stage-Gate Report

- Protocol: `ioi_known_circuit_real_v1`
- Protocol hash: `15d40990c267e5dc6dbbed224fa0df0a8d022617a730522d141977dec1d009c3`
- Hypotheses: 2
- Accepted: 0
- Unstable: 1
- Rejected: 1
- All pass: False
- Cross-method rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_ioi_name_movers | ❌ FAIL | `suggestive` | 0.556 | 2.575 | 0.1868 |
| h_ioi_random_baseline | ❌ FAIL | `rejected` | 0.688 | 0.146 | 0.1868 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| multiplicity | 2 | 100.0% |
| method_sensitivity | 1 | 50.0% |
| confirmatory_ci | 1 | 50.0% |
| causal_effect | 1 | 50.0% |
| negative_controls | 1 | 50.0% |
| baseline_superiority | 1 | 50.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `suggestive` | 1 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_ioi_name_movers
- Passed: False
- Evidence tier: `suggestive`
- Failed checks: method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: 0.531387
- Cohen's d: 0.5564
- Confirmatory CI (bootstrap): [-0.041781, 1.197466]
- Specificity ratio: 2.574599
- Control abs mean: 0.206396
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.696519
- Permutation p-value: 0.1899
- BH q-value: 0.186800
- Holm-adjusted p: 0.248
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_ioi_random_baseline
- Passed: False
- Evidence tier: `rejected`
- Failed checks: causal_effect, negative_controls, multiplicity, baseline_superiority
- Treatment mean: 0.019467
- Cohen's d: 0.6883
- Confirmatory CI (bootstrap): [0.002929, 0.040127]
- Specificity ratio: 0.145938
- Control abs mean: 0.133395
- Robustness (seed/prompt/resample): 0.500 / 0.500 / 0.000
- Method sensitivity std: 0.020188
- Permutation p-value: 0.1165
- BH q-value: 0.186800
- Holm-adjusted p: 0.248
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
