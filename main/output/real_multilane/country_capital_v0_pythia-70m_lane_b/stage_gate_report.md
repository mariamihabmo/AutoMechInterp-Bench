# Stage-Gate Report

- Protocol: `multilane_B_country_capital_v0_pythia-70m`
- Protocol hash: `0c8a811961207fd05e691eaa949063789497dc636205a763642d0ab194c1f3f2`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.5556
- Cross-model rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_neuron_country_capital_v0_001 | ❌ FAIL | `rejected` | -0.362 | 31.901 | 0.0261 |
| h_neuron_country_capital_v0_002 | ❌ FAIL | `rejected` | -0.167 | 14.891 | 0.3495 |
| h_neuron_country_capital_v0_003 | ❌ FAIL | `rejected` | 0.052 | 4.013 | 0.7260 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| power_adequacy | 3 | 100.0% |
| robustness | 3 | 100.0% |
| confirmatory_ci | 2 | 66.7% |
| effect_size_practical | 2 | 66.7% |
| multiplicity | 2 | 66.7% |
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
- Treatment mean: -0.066927
- Cohen's d: -0.3622
- Confirmatory CI (bootstrap): [-0.124246, -0.025064]
- Specificity ratio: 31.900861
- Control abs mean: 0.002098
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.084115
- Permutation p-value: 0.008399160083991601
- BH q-value: 0.026097
- Holm-adjusted p: 0.0260973902609739
- Cells: 54

### h_neuron_country_capital_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, confirmatory_ci, effect_size_practical, multiplicity, power_adequacy, robustness, cross_model_transfer
- Treatment mean: -0.025575
- Cohen's d: -0.1671
- Confirmatory CI (bootstrap): [-0.071396, 0.009138]
- Specificity ratio: 14.891117
- Control abs mean: 0.001717
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.045550
- Permutation p-value: 0.2313768623137686
- BH q-value: 0.349465
- Holm-adjusted p: 0.46595340465953405
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_country_capital_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, confirmatory_ci, effect_size_practical, multiplicity, power_adequacy, robustness
- Treatment mean: 0.006495
- Cohen's d: 0.0524
- Confirmatory CI (bootstrap): [-0.020288, 0.048572]
- Specificity ratio: 4.013136
- Control abs mean: 0.001618
- Robustness (seed/prompt/resample): 0.500 / 0.333 / 0.000
- Method sensitivity std: 0.003096
- Permutation p-value: 0.7215278472152785
- BH q-value: 0.726027
- Holm-adjusted p: 0.726027397260274
- Cells: 54
