# Stage-Gate Report

- Protocol: `multilane_A_country_capital_v0_pythia-70m_prompt_variant_repair_v1_prompt_holdout_high_power_n40`
- Protocol hash: `6b4f99cf959b7e5ae2f812c911ccebae56dfd9613f4e7360c05ad86b63f78fe9`
- Hypotheses: 3
- Accepted: 2
- Unstable: 0
- Rejected: 1
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sweep_country_capital_v0_001 | ✅ PASS | `single_model_confirmed` | 2.150 | 7.856 | 0.0001 |
| h_sweep_country_capital_v0_002 | ✅ PASS | `single_model_confirmed` | 2.026 | 8.906 | 0.0001 |
| h_sweep_country_capital_v0_003 | ❌ FAIL | `rejected` | 1.246 | 3.217 | 0.0001 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 1 | 33.3% |
| baseline_superiority | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 2 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_sweep_country_capital_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 1.361582
- Cohen's d: 2.1502
- Confirmatory CI (bootstrap): [1.205199, 1.537739]
- Specificity ratio: 7.856444
- Control abs mean: 0.173308
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.611336
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_country_capital_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 1.142255
- Cohen's d: 2.0262
- Confirmatory CI (bootstrap): [1.002862, 1.301469]
- Specificity ratio: 8.905819
- Control abs mean: 0.128259
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.550700
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_country_capital_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, baseline_superiority
- Treatment mean: 0.223046
- Cohen's d: 1.2461
- Confirmatory CI (bootstrap): [0.177827, 0.272303]
- Specificity ratio: 3.217069
- Control abs mean: 0.069332
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.110271
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
