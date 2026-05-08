# Stage-Gate Report

- Protocol: `multilane_C_country_capital_v0_gpt2-small_prompt_variant_repair_v1`
- Protocol hash: `15ceab5e1ebf7d667d709a83f6d8798123555ca471f8b237843156dedc6ca92b`
- Hypotheses: 3
- Accepted: 3
- Unstable: 0
- Rejected: 0
- All pass: True
- Cross-method rank τ: 1.0000
- Cross-model rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_dla_country_capital_v0_001 | ✅ PASS | `cross_model_confirmed` | 1.437 | 12.811 | 0.0001 |
| h_dla_country_capital_v0_002 | ✅ PASS | `cross_model_confirmed` | 2.203 | 10.305 | 0.0001 |
| h_dla_country_capital_v0_003 | ✅ PASS | `single_model_confirmed` | 1.217 | 8.143 | 0.0001 |

## Failure Analysis

No core gate failures detected.

### Optional transfer diagnostics (tier demotions, not core failures)

| Check | Demotion Count | Demotion Rate |
|---|---|---|
| cross_model_transfer | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `cross_model_confirmed` | 2 |
| `single_model_confirmed` | 1 |

## Per-Hypothesis Details

### h_dla_country_capital_v0_001
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 2.243951
- Cohen's d: 1.4366
- Confirmatory CI (bootstrap): [1.868282, 2.694221]
- Specificity ratio: 12.811050
- Control abs mean: 0.175157
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 1.455499
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_002
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.763718
- Cohen's d: 2.2029
- Confirmatory CI (bootstrap): [0.677224, 0.866078]
- Specificity ratio: 10.305067
- Control abs mean: 0.074111
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.324119
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 1.429684
- Cohen's d: 1.2166
- Confirmatory CI (bootstrap): [1.160144, 1.784572]
- Specificity ratio: 8.142794
- Control abs mean: 0.175577
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.854902
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
