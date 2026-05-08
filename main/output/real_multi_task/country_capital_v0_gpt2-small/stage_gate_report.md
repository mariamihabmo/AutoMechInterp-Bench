# Stage-Gate Report

- Protocol: `real_country_capital_v0_gpt2-small`
- Protocol hash: `b3a34fd6fa0c65a4d240cde0b14ae4240759c2308088f0a225c569795c2d1966`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_country_capital_v0_001 | ❌ FAIL | `rejected` | -0.227 | 3.030 | 0.7459 |
| h_country_capital_v0_002 | ❌ FAIL | `rejected` | -0.654 | 23.400 | 0.7459 |
| h_country_capital_v0_003 | ❌ FAIL | `rejected` | -0.674 | 25.684 | 0.7459 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| method_sensitivity | 3 | 100.0% |
| confirmatory_ci | 3 | 100.0% |
| multiplicity | 3 | 100.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_country_capital_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -1.425705
- Cohen's d: -0.2274
- Confirmatory CI (bootstrap): [-7.025489, 3.994102]
- Specificity ratio: 3.029922
- Control abs mean: 0.470542
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 5.419807
- Permutation p-value: 0.7516248375162484
- BH q-value: 0.745925
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_country_capital_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -3.219190
- Cohen's d: -0.6541
- Confirmatory CI (bootstrap): [-7.685971, 1.015863]
- Specificity ratio: 23.400320
- Control abs mean: 0.137570
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 4.251076
- Permutation p-value: 0.5028497150284972
- BH q-value: 0.745925
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_country_capital_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -3.339360
- Cohen's d: -0.6744
- Confirmatory CI (bootstrap): [-7.806382, 0.925022]
- Specificity ratio: 25.683639
- Control abs mean: 0.130019
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 4.280202
- Permutation p-value: 0.49455054494550543
- BH q-value: 0.745925
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
