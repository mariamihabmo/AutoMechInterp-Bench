# Stage-Gate Report

- Protocol: `multilane_A_country_capital_v0_gpt2-small_prompt_variant_repair_v1_prompt_holdout_high_power_n40`
- Protocol hash: `51fee84d2376fd262daa1f35fd34bc9a62dd5fe0dcc4d9a8f52627ba4a833be6`
- Hypotheses: 3
- Accepted: 3
- Unstable: 0
- Rejected: 0
- All pass: True
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sweep_country_capital_v0_001 | ✅ PASS | `single_model_confirmed` | 1.397 | 12.849 | 0.0001 |
| h_sweep_country_capital_v0_002 | ✅ PASS | `single_model_confirmed` | 2.152 | 9.215 | 0.0001 |
| h_sweep_country_capital_v0_003 | ✅ PASS | `single_model_confirmed` | 1.306 | 8.452 | 0.0001 |

## Failure Analysis

No failures detected.

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 3 |

## Per-Hypothesis Details

### h_sweep_country_capital_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 2.312266
- Cohen's d: 1.3970
- Confirmatory CI (bootstrap): [1.910068, 2.794662]
- Specificity ratio: 12.848694
- Control abs mean: 0.179961
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 1.530724
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_country_capital_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.772430
- Cohen's d: 2.1525
- Confirmatory CI (bootstrap): [0.682821, 0.873188]
- Specificity ratio: 9.215241
- Control abs mean: 0.083821
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.338064
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_country_capital_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 1.397717
- Cohen's d: 1.3061
- Confirmatory CI (bootstrap): [1.145547, 1.708234]
- Specificity ratio: 8.452280
- Control abs mean: 0.165366
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.765856
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
