# Stage-Gate Report

- Protocol: `multilane_A_country_capital_v0_gpt2-small`
- Protocol hash: `71c2fbc085c868441f30438b315c94dde16519153ff5858fbe3f7ec13422e4ca`
- Hypotheses: 3
- Accepted: 3
- Unstable: 0
- Rejected: 0
- All pass: True
- Cross-method rank τ: 0.5556
- Cross-model rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sweep_country_capital_v0_001 | ✅ PASS | `cross_model_confirmed` | 1.303 | 10.190 | 0.0001 |
| h_sweep_country_capital_v0_002 | ✅ PASS | `cross_model_confirmed` | 1.649 | 10.005 | 0.0001 |
| h_sweep_country_capital_v0_003 | ✅ PASS | `single_model_confirmed` | 1.107 | 7.112 | 0.0001 |

## Failure Analysis

No failures detected.

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `cross_model_confirmed` | 2 |
| `single_model_confirmed` | 1 |

## Per-Hypothesis Details

### h_sweep_country_capital_v0_001
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 2.121018
- Cohen's d: 1.3033
- Confirmatory CI (bootstrap): [1.724474, 2.578904]
- Specificity ratio: 10.190442
- Control abs mean: 0.208138
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 1.520350
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_country_capital_v0_002
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.730114
- Cohen's d: 1.6493
- Confirmatory CI (bootstrap): [0.621370, 0.857976]
- Specificity ratio: 10.005262
- Control abs mean: 0.072973
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.396429
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_country_capital_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.863199
- Cohen's d: 1.1066
- Confirmatory CI (bootstrap): [0.691297, 1.105179]
- Specificity ratio: 7.112395
- Control abs mean: 0.121365
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.542649
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
