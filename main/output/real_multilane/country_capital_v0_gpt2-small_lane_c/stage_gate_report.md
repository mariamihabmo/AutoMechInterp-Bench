# Stage-Gate Report

- Protocol: `multilane_C_country_capital_v0_gpt2-small`
- Protocol hash: `e0a8a3623f06ac59feb5f202f82db2d9a93066507c794c2ba6ff3cd10a6550f7`
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
| h_dla_country_capital_v0_001 | ✅ PASS | `cross_model_confirmed` | 1.308 | 11.247 | 0.0001 |
| h_dla_country_capital_v0_002 | ✅ PASS | `cross_model_confirmed` | 1.745 | 9.253 | 0.0001 |
| h_dla_country_capital_v0_003 | ✅ PASS | `single_model_confirmed` | 1.141 | 7.416 | 0.0001 |

## Failure Analysis

No failures detected.

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
- Treatment mean: 1.942812
- Cohen's d: 1.3080
- Confirmatory CI (bootstrap): [1.578053, 2.366911]
- Specificity ratio: 11.246834
- Control abs mean: 0.172743
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 1.384936
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_002
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.705375
- Cohen's d: 1.7448
- Confirmatory CI (bootstrap): [0.604046, 0.816820]
- Specificity ratio: 9.253488
- Control abs mean: 0.076228
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.370879
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.839770
- Cohen's d: 1.1409
- Confirmatory CI (bootstrap): [0.672095, 1.067374]
- Specificity ratio: 7.415687
- Control abs mean: 0.113242
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.532771
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
