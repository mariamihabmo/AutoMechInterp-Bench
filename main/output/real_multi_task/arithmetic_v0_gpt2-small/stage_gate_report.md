# Stage-Gate Report

- Protocol: `real_arithmetic_v0_gpt2-small`
- Protocol hash: `68f84fceeb7f5d488a3c00d7844f5755a6023ea3861b23241699e6bb8d957bb4`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: -0.3333
- Cross-model rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_arithmetic_v0_001 | ❌ FAIL | `rejected` | -0.636 | 11.229 | 0.5016 |
| h_arithmetic_v0_002 | ❌ FAIL | `rejected` | -0.551 | 4.152 | 0.5016 |
| h_arithmetic_v0_003 | ❌ FAIL | `rejected` | -0.622 | 9.517 | 0.5016 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| method_sensitivity | 3 | 100.0% |
| confirmatory_ci | 3 | 100.0% |
| multiplicity | 3 | 100.0% |
| cross_model_transfer | 3 | 100.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_arithmetic_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity, cross_model_transfer
- Treatment mean: -0.235768
- Cohen's d: -0.6361
- Confirmatory CI (bootstrap): [-0.557830, 0.073509]
- Specificity ratio: 11.228671
- Control abs mean: 0.020997
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.320569
- Permutation p-value: 0.5012498750124987
- BH q-value: 0.501650
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_arithmetic_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity, cross_model_transfer
- Treatment mean: -0.206630
- Cohen's d: -0.5515
- Confirmatory CI (bootstrap): [-0.549759, 0.116293]
- Specificity ratio: 4.151558
- Control abs mean: 0.049772
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.322923
- Permutation p-value: 0.5000499950005
- BH q-value: 0.501650
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_arithmetic_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity, cross_model_transfer
- Treatment mean: -0.209981
- Cohen's d: -0.6219
- Confirmatory CI (bootstrap): [-0.505800, 0.081814]
- Specificity ratio: 9.516677
- Control abs mean: 0.022065
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.292371
- Permutation p-value: 0.5008499150084992
- BH q-value: 0.501650
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
