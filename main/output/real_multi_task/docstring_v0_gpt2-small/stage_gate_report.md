# Stage-Gate Report

- Protocol: `real_docstring_v0_gpt2-small`
- Protocol hash: `74dab079a56d028d9c5f7d20b62052faf91909107824a675643b62fb0b7c4a8b`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_docstring_v0_001 | ❌ FAIL | `rejected` | -0.614 | 4.597 | 0.5105 |
| h_docstring_v0_002 | ❌ FAIL | `rejected` | -0.658 | 7.193 | 0.5105 |
| h_docstring_v0_003 | ❌ FAIL | `rejected` | -0.616 | 5.748 | 0.5105 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| confirmatory_present | 3 | 100.0% |
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| method_sensitivity | 3 | 100.0% |
| confirmatory_ci | 3 | 100.0% |
| multiplicity | 3 | 100.0% |
| negative_controls | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_docstring_v0_001
- Passed: False
- Evidence tier: `rejected`
- Failed checks: confirmatory_present, causal_effect, negative_controls, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -2.438159
- Cohen's d: -0.6136
- Confirmatory CI (bootstrap): [-6.218883, 0.869828]
- Specificity ratio: 4.596786
- Control abs mean: 0.530405
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 3.395676
- Permutation p-value: 0.5007
- BH q-value: 0.510500
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_docstring_v0_002
- Passed: False
- Evidence tier: `rejected`
- Failed checks: confirmatory_present, causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -2.556516
- Cohen's d: -0.6581
- Confirmatory CI (bootstrap): [-6.261425, 0.762508]
- Specificity ratio: 7.193462
- Control abs mean: 0.355394
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 3.319024
- Permutation p-value: 0.5058
- BH q-value: 0.510500
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_docstring_v0_003
- Passed: False
- Evidence tier: `rejected`
- Failed checks: confirmatory_present, causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -2.409735
- Cohen's d: -0.6161
- Confirmatory CI (bootstrap): [-6.113921, 0.745299]
- Specificity ratio: 5.748300
- Control abs mean: 0.419208
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 3.337271
- Permutation p-value: 0.5038
- BH q-value: 0.510500
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
