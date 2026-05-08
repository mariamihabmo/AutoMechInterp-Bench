# Stage-Gate Report

- Protocol: `real_docstring_v0_pythia-70m`
- Protocol hash: `a83fc2e6da30c609a56fb079197d56d4b12e865a979e7d7e4cdd1e4045dae8cd`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_docstring_v0_001 | ❌ FAIL | `rejected` | -0.523 | 6.754 | 0.5105 |
| h_docstring_v0_002 | ❌ FAIL | `rejected` | -0.563 | 5.283 | 0.5105 |
| h_docstring_v0_003 | ❌ FAIL | `rejected` | -0.639 | 11.208 | 0.5105 |

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

### h_docstring_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -1.880402
- Cohen's d: -0.5232
- Confirmatory CI (bootstrap): [-5.454665, 1.000605]
- Specificity ratio: 6.753852
- Control abs mean: 0.278419
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 2.999748
- Permutation p-value: 0.5007499250074993
- BH q-value: 0.510549
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_docstring_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -1.857927
- Cohen's d: -0.5633
- Confirmatory CI (bootstrap): [-5.083014, 0.848707]
- Specificity ratio: 5.282724
- Control abs mean: 0.351699
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 2.786108
- Permutation p-value: 0.5058494150584941
- BH q-value: 0.510549
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_docstring_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -1.959569
- Cohen's d: -0.6389
- Confirmatory CI (bootstrap): [-5.049757, 0.548128]
- Specificity ratio: 11.208157
- Control abs mean: 0.174834
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 2.538923
- Permutation p-value: 0.5038496150384961
- BH q-value: 0.510549
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
