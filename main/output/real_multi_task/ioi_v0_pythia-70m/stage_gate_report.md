# Stage-Gate Report

- Protocol: `real_ioi_v0_pythia-70m`
- Protocol hash: `6980afcb553155bbb599b5ba637e051bdfc9102cb603a27b51efe6426e6d01b4`
- Hypotheses: 3
- Accepted: 0
- Unstable: 2
- Rejected: 1
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_ioi_v0_001 | ❌ FAIL | `suggestive` | -0.458 | 2.203 | 0.5002 |
| h_ioi_v0_002 | ❌ FAIL | `suggestive` | 5.144 | 7.133 | 0.3885 |
| h_ioi_v0_003 | ❌ FAIL | `rejected` | 0.550 | 12.153 | 0.5002 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| method_sensitivity | 3 | 100.0% |
| multiplicity | 3 | 100.0% |
| confirmatory_ci | 2 | 66.7% |
| causal_effect | 1 | 33.3% |
| robustness | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `suggestive` | 2 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_ioi_v0_001
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -0.528736
- Cohen's d: -0.4584
- Confirmatory CI (bootstrap): [-1.536850, 0.469755]
- Specificity ratio: 2.202934
- Control abs mean: 0.240014
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.998491
- Permutation p-value: 0.5047495250474953
- BH q-value: 0.500250
- Holm-adjusted p: 0.9993000699930007
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_ioi_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, multiplicity
- Treatment mean: 1.538453
- Cohen's d: 5.1444
- Confirmatory CI (bootstrap): [1.248442, 1.770688]
- Specificity ratio: 7.133300
- Control abs mean: 0.215672
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.251770
- Permutation p-value: 0.1287871212878712
- BH q-value: 0.388461
- Holm-adjusted p: 0.38846115388461155
- Cells: 4

### h_ioi_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: 0.438226
- Cohen's d: 0.5498
- Confirmatory CI (bootstrap): [-0.271130, 1.127973]
- Specificity ratio: 12.152638
- Control abs mean: 0.036060
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.689746
- Permutation p-value: 0.5003499650034996
- BH q-value: 0.500250
- Holm-adjusted p: 0.9993000699930007
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
