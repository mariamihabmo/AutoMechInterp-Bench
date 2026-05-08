# Stage-Gate Report

- Protocol: `real_greater_than_v0_pythia-70m_confirmatory_repair_real`
- Protocol hash: `490cca76b31be20708f145b74c02844ad0c67282b5d8cb6f63790895767709e7`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_greater_than_v0_001 | ❌ FAIL | `rejected` | -0.684 | 1.421 | 0.1899 |
| h_greater_than_v0_002 | ❌ FAIL | `rejected` | 0.349 | 1.492 | 0.4692 |
| h_greater_than_v0_003 | ❌ FAIL | `rejected` | 0.336 | 0.918 | 0.4380 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 3 | 100.0% |
| multiplicity | 3 | 100.0% |
| confirmatory_ci | 2 | 66.7% |
| method_sensitivity | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_greater_than_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, method_sensitivity, multiplicity
- Treatment mean: -0.069150
- Cohen's d: -0.6844
- Confirmatory CI (bootstrap): [-0.153379, -0.014834]
- Specificity ratio: 1.421072
- Control abs mean: 0.048661
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.055055
- Permutation p-value: 0.0665933406659334
- BH q-value: 0.189881
- Holm-adjusted p: 0.18988101189881013
- Cells: 8

### h_greater_than_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, confirmatory_ci, multiplicity
- Treatment mean: 0.040458
- Cohen's d: 0.3486
- Confirmatory CI (bootstrap): [-0.022668, 0.137183]
- Specificity ratio: 1.491660
- Control abs mean: 0.027123
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.041174
- Permutation p-value: 0.46835316468353166
- BH q-value: 0.469153
- Holm-adjusted p: 0.583941605839416
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_greater_than_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, confirmatory_ci, multiplicity
- Treatment mean: 0.035136
- Cohen's d: 0.3358
- Confirmatory CI (bootstrap): [-0.042416, 0.092163]
- Specificity ratio: 0.917767
- Control abs mean: 0.038285
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.035993
- Permutation p-value: 0.2900709929007099
- BH q-value: 0.437956
- Holm-adjusted p: 0.583941605839416
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
