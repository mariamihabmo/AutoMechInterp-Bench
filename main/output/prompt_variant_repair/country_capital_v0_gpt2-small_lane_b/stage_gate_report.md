# Stage-Gate Report

- Protocol: `multilane_B_country_capital_v0_gpt2-small_prompt_variant_repair_v1`
- Protocol hash: `0b00fcb3a92e3c1d4fd7aead19c8604cc1d85e39072980f72ad45b99cd813860`
- Hypotheses: 3
- Accepted: 1
- Unstable: 1
- Rejected: 1
- All pass: False
- Cross-method rank τ: 0.1111
- Cross-model rank τ: 0.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_neuron_country_capital_v0_001 | ❌ FAIL | `rejected` | -0.101 | 6.071 | 0.4616 |
| h_neuron_country_capital_v0_002 | ✅ PASS | `single_model_confirmed` | 0.623 | 16.757 | 0.0003 |
| h_neuron_country_capital_v0_003 | ❌ FAIL | `causal_tested_unstable` | 0.413 | 71.373 | 0.0003 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| power_adequacy | 2 | 66.7% |
| causal_effect | 1 | 33.3% |
| robustness | 1 | 33.3% |
| confirmatory_ci | 1 | 33.3% |
| multiplicity | 1 | 33.3% |
| effect_size_practical | 1 | 33.3% |
| cross_model_transfer | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `causal_tested_unstable` | 1 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_neuron_country_capital_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical
- Treatment mean: -0.013575
- Cohen's d: -0.1006
- Confirmatory CI (bootstrap): [-0.047443, 0.023616]
- Specificity ratio: 6.071316
- Control abs mean: 0.002236
- Robustness (seed/prompt/resample): 0.000 / 0.333 / 0.000
- Method sensitivity std: 0.019233
- Permutation p-value: 0.4587541245875412
- BH q-value: 0.461554
- Holm-adjusted p: 0.46155384461553844
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_country_capital_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.045865
- Cohen's d: 0.6235
- Confirmatory CI (bootstrap): [0.029134, 0.067888]
- Specificity ratio: 16.756657
- Control abs mean: 0.002737
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.066203
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000300
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_country_capital_v0_003
- Passed: False
- Evidence tier: `causal_tested_unstable`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=pass
- Failed checks: power_adequacy
- Treatment mean: 0.071063
- Cohen's d: 0.4131
- Confirmatory CI (bootstrap): [0.034040, 0.128773]
- Specificity ratio: 71.372551
- Control abs mean: 0.000996
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.100674
- Permutation p-value: 0.0005999400059994001
- BH q-value: 0.000300
- Holm-adjusted p: 0.00039996000399960006
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
