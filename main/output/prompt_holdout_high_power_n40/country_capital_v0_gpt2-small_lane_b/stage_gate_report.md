# Stage-Gate Report

- Protocol: `multilane_B_country_capital_v0_gpt2-small_prompt_variant_repair_v1_prompt_holdout_high_power_n40`
- Protocol hash: `8a5dd029ca067c61f98862fe6e7fe55148a0498623410eb7c5ddd44f5b79b3e6`
- Hypotheses: 3
- Accepted: 1
- Unstable: 1
- Rejected: 1
- All pass: False
- Cross-method rank τ: 0.1111

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_neuron_country_capital_v0_001 | ❌ FAIL | `rejected` | -0.064 | 3.920 | 0.6398 |
| h_neuron_country_capital_v0_002 | ✅ PASS | `single_model_confirmed` | 0.631 | 19.494 | 0.0003 |
| h_neuron_country_capital_v0_003 | ❌ FAIL | `causal_tested_unstable` | 0.415 | 72.486 | 0.0003 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| power_adequacy | 2 | 66.7% |
| causal_effect | 1 | 33.3% |
| robustness | 1 | 33.3% |
| confirmatory_ci | 1 | 33.3% |
| multiplicity | 1 | 33.3% |
| effect_size_practical | 1 | 33.3% |

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
- Treatment mean: -0.008568
- Cohen's d: -0.0638
- Confirmatory CI (bootstrap): [-0.041444, 0.030054]
- Specificity ratio: 3.919731
- Control abs mean: 0.002186
- Robustness (seed/prompt/resample): 0.000 / 0.333 / 0.000
- Method sensitivity std: 0.011550
- Permutation p-value: 0.6341365863413658
- BH q-value: 0.639836
- Holm-adjusted p: 0.6398360163983602
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_country_capital_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.044411
- Cohen's d: 0.6312
- Confirmatory CI (bootstrap): [0.028264, 0.065432]
- Specificity ratio: 19.493539
- Control abs mean: 0.002278
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.063643
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
- Treatment mean: 0.069165
- Cohen's d: 0.4148
- Confirmatory CI (bootstrap): [0.033110, 0.124540]
- Specificity ratio: 72.486310
- Control abs mean: 0.000954
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.097925
- Permutation p-value: 0.0005999400059994001
- BH q-value: 0.000300
- Holm-adjusted p: 0.00039996000399960006
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
