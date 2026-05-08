# Stage-Gate Report

- Protocol: `multilane_B_country_capital_v0_pythia-70m_prompt_variant_repair_v1`
- Protocol hash: `6f673448f7eb1e42ad59c083e33e17ebf1b4821330d54e672ea18e238dd2bdd0`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.5556

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_neuron_country_capital_v0_001 | ❌ FAIL | `rejected` | -0.507 | 44.580 | 0.0006 |
| h_neuron_country_capital_v0_002 | ❌ FAIL | `rejected` | -0.447 | 40.125 | 0.0012 |
| h_neuron_country_capital_v0_003 | ❌ FAIL | `rejected` | -0.149 | 9.133 | 0.2911 |

## Failure Analysis

### Core gate failures

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| power_adequacy | 3 | 100.0% |
| robustness | 3 | 100.0% |
| confirmatory_ci | 1 | 33.3% |
| effect_size_practical | 1 | 33.3% |
| multiplicity | 1 | 33.3% |

### Optional transfer diagnostics (tier demotions, not core failures)

| Check | Demotion Count | Demotion Rate |
|---|---|---|
| cross_model_transfer | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_neuron_country_capital_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, power_adequacy, robustness
- Treatment mean: -0.065397
- Cohen's d: -0.5068
- Confirmatory CI (bootstrap): [-0.101775, -0.033896]
- Specificity ratio: 44.580304
- Control abs mean: 0.001467
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.079886
- Permutation p-value: 0.00029997000299970003
- BH q-value: 0.000600
- Holm-adjusted p: 0.0005999400059994001
- Cells: 54

### h_neuron_country_capital_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, power_adequacy, robustness, cross_model_transfer
- Treatment mean: -0.041913
- Cohen's d: -0.4474
- Confirmatory CI (bootstrap): [-0.071493, -0.021864]
- Specificity ratio: 40.124792
- Control abs mean: 0.001045
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.073064
- Permutation p-value: 0.000999900009999
- BH q-value: 0.001200
- Holm-adjusted p: 0.0015998400159984002
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_country_capital_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, confirmatory_ci, effect_size_practical, multiplicity, power_adequacy, robustness
- Treatment mean: -0.015371
- Cohen's d: -0.1493
- Confirmatory CI (bootstrap): [-0.051726, 0.005311]
- Specificity ratio: 9.132786
- Control abs mean: 0.001683
- Robustness (seed/prompt/resample): 0.167 / 0.000 / 0.000
- Method sensitivity std: 0.042263
- Permutation p-value: 0.2950704929507049
- BH q-value: 0.291071
- Holm-adjusted p: 0.2910708929107089
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
