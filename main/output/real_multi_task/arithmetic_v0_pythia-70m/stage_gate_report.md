# Stage-Gate Report

- Protocol: `real_arithmetic_v0_pythia-70m`
- Protocol hash: `6d476701a3d5db2ab5694c6687e2b1d8cd2cba09a620eda268f5ffa89b3acb14`
- Hypotheses: 3
- Accepted: 0
- Unstable: 1
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_arithmetic_v0_001 | ❌ FAIL | `rejected` | -0.433 | 5.289 | 0.6244 |
| h_arithmetic_v0_002 | ❌ FAIL | `causal_tested_unstable` | 3.799 | 2.802 | 0.3705 |
| h_arithmetic_v0_003 | ❌ FAIL | `rejected` | -0.575 | 4.974 | 0.6244 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| multiplicity | 3 | 100.0% |
| causal_effect | 2 | 66.7% |
| robustness | 2 | 66.7% |
| confirmatory_ci | 2 | 66.7% |
| method_sensitivity | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `causal_tested_unstable` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_arithmetic_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -0.050289
- Cohen's d: -0.4330
- Confirmatory CI (bootstrap): [-0.209019, 0.011561]
- Specificity ratio: 5.289292
- Control abs mean: 0.009508
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.086712
- Permutation p-value: 0.6293370662933707
- BH q-value: 0.624438
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_arithmetic_v0_002
- Passed: False
- Evidence tier: `causal_tested_unstable`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: multiplicity
- Treatment mean: 0.051029
- Cohen's d: 3.7989
- Confirmatory CI (bootstrap): [0.039662, 0.062136]
- Specificity ratio: 2.802146
- Control abs mean: 0.018211
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.011106
- Permutation p-value: 0.12458754124587541
- BH q-value: 0.370463
- Holm-adjusted p: 0.37046295370462956
- Cells: 4

### h_arithmetic_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, confirmatory_ci, multiplicity
- Treatment mean: -0.027354
- Cohen's d: -0.5752
- Confirmatory CI (bootstrap): [-0.068879, 0.009588]
- Specificity ratio: 4.974092
- Control abs mean: 0.005499
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.040807
- Permutation p-value: 0.5008499150084992
- BH q-value: 0.624438
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
