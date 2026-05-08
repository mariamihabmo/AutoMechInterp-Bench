# Stage-Gate Report

- Protocol: `multilane_B_docstring_v0_gpt2-small`
- Protocol hash: `394fd339aa513c2b5e86343506faa7263b550828c41e0432b7816260ebcfdc51`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_neuron_docstring_v0_001 | ❌ FAIL | `rejected` | 0.022 | 0.363 | 0.8655 |
| h_neuron_docstring_v0_002 | ❌ FAIL | `rejected` | -0.460 | 16.596 | 0.0006 |
| h_neuron_docstring_v0_003 | ❌ FAIL | `rejected` | 0.178 | 1.634 | 0.2928 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| power_adequacy | 3 | 100.0% |
| negative_controls | 2 | 66.7% |
| confirmatory_ci | 2 | 66.7% |
| multiplicity | 2 | 66.7% |
| effect_size_practical | 2 | 66.7% |
| baseline_superiority | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_neuron_docstring_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical, baseline_superiority
- Treatment mean: 0.000572
- Cohen's d: 0.0224
- Confirmatory CI (bootstrap): [-0.005597, 0.008163]
- Specificity ratio: 0.362684
- Control abs mean: 0.001578
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.000896
- Permutation p-value: 0.8763123687631237
- BH q-value: 0.865513
- Holm-adjusted p: 0.8655134486551345
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_docstring_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, power_adequacy
- Treatment mean: -0.029871
- Cohen's d: -0.4596
- Confirmatory CI (bootstrap): [-0.051483, -0.015569]
- Specificity ratio: 16.595989
- Control abs mean: 0.001800
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.045697
- Permutation p-value: 0.00029997000299970003
- BH q-value: 0.000600
- Holm-adjusted p: 0.0005999400059994001
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_docstring_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical
- Treatment mean: 0.003578
- Cohen's d: 0.1785
- Confirmatory CI (bootstrap): [-0.001766, 0.008879]
- Specificity ratio: 1.634086
- Control abs mean: 0.002190
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.007130
- Permutation p-value: 0.20677932206779323
- BH q-value: 0.292771
- Holm-adjusted p: 0.39036096390360964
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
