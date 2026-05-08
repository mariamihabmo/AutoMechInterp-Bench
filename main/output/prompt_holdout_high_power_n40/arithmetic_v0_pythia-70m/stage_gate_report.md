# Stage-Gate Report

- Protocol: `real_arithmetic_v0_pythia-70m_confirmatory_repair_real_prompt_variant_repair_v1_prompt_holdout_high_power_n40`
- Protocol hash: `cfd93b5e6a8d404b239ea0f675e72408edcfb3e03d5d2f66e006dc1b7f09f84c`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_arithmetic_v0_001 | ❌ FAIL | `rejected` | -0.378 | 0.771 | 0.3635 |
| h_arithmetic_v0_002 | ❌ FAIL | `rejected` | 0.574 | 1.586 | 0.0900 |
| h_arithmetic_v0_003 | ❌ FAIL | `rejected` | 0.610 | 0.923 | 0.0900 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 3 | 100.0% |
| causal_effect | 2 | 66.7% |
| robustness | 2 | 66.7% |
| confirmatory_ci | 1 | 33.3% |
| multiplicity | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_arithmetic_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity
- Treatment mean: -0.008762
- Cohen's d: -0.3781
- Confirmatory CI (bootstrap): [-0.033157, 0.001158]
- Specificity ratio: 0.770501
- Control abs mean: 0.011372
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.013750
- Permutation p-value: 0.37346265373462656
- BH q-value: 0.363464
- Holm-adjusted p: 0.36346365363463656
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_arithmetic_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls
- Treatment mean: 0.041691
- Cohen's d: 0.5737
- Confirmatory CI (bootstrap): [0.011297, 0.119112]
- Specificity ratio: 1.586263
- Control abs mean: 0.026283
- Robustness (seed/prompt/resample): 0.500 / 0.500 / 1.000
- Method sensitivity std: 0.010856
- Permutation p-value: 0.035896410358964105
- BH q-value: 0.089991
- Holm-adjusted p: 0.11968803119688032
- Cells: 8

### h_arithmetic_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness
- Treatment mean: 0.015065
- Cohen's d: 0.6102
- Confirmatory CI (bootstrap): [0.001998, 0.036247]
- Specificity ratio: 0.922509
- Control abs mean: 0.016331
- Robustness (seed/prompt/resample): 0.000 / 0.500 / 0.000
- Method sensitivity std: 0.013733
- Permutation p-value: 0.06369363063693631
- BH q-value: 0.089991
- Holm-adjusted p: 0.11998800119988001
- Cells: 8
