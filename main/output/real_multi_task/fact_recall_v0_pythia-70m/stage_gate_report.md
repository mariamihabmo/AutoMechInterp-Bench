# Stage-Gate Report

- Protocol: `real_fact_recall_v0_pythia-70m`
- Protocol hash: `28813a7aab3f933efc060804af453bcf687398f2231b02659c8433aa829ff15a`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.3333
- Cross-model rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_fact_recall_v0_001 | ❌ FAIL | `rejected` | 0.006 | 0.042 | 1.0000 |
| h_fact_recall_v0_002 | ❌ FAIL | `rejected` | -0.727 | 2.297 | 0.7645 |
| h_fact_recall_v0_003 | ❌ FAIL | `rejected` | -0.746 | 10.603 | 0.7645 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| method_sensitivity | 3 | 100.0% |
| confirmatory_ci | 3 | 100.0% |
| multiplicity | 3 | 100.0% |
| cross_model_transfer | 3 | 100.0% |
| negative_controls | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_fact_recall_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, method_sensitivity, confirmatory_ci, multiplicity, cross_model_transfer
- Treatment mean: 0.006421
- Cohen's d: 0.0061
- Confirmatory CI (bootstrap): [-0.949327, 0.911417]
- Specificity ratio: 0.042092
- Control abs mean: 0.152555
- Robustness (seed/prompt/resample): 0.500 / 0.000 / 0.000
- Method sensitivity std: 0.904996
- Permutation p-value: 1.0
- BH q-value: 1.000000
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_fact_recall_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity, cross_model_transfer
- Treatment mean: -0.660624
- Cohen's d: -0.7271
- Confirmatory CI (bootstrap): [-1.560531, 0.073619]
- Specificity ratio: 2.297022
- Control abs mean: 0.287600
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.760960
- Permutation p-value: 0.5027497250274973
- BH q-value: 0.764474
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_fact_recall_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity, cross_model_transfer
- Treatment mean: -0.643457
- Cohen's d: -0.7457
- Confirmatory CI (bootstrap): [-1.496195, 0.043295]
- Specificity ratio: 10.602994
- Control abs mean: 0.060686
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.722455
- Permutation p-value: 0.49065093490650935
- BH q-value: 0.764474
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
