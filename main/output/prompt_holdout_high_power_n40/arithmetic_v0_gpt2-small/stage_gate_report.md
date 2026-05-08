# Stage-Gate Report

- Protocol: `real_arithmetic_v0_gpt2-small_confirmatory_repair_real_prompt_variant_repair_v1_prompt_holdout_high_power_n40`
- Protocol hash: `69f0a9b7c017d341b2ceba36b1542a1b6cb597a9bf4971b1780d6cb2a5dbb7cb`
- Hypotheses: 3
- Accepted: 2
- Unstable: 0
- Rejected: 1
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_arithmetic_v0_001 | ❌ FAIL | `rejected` | 0.426 | 2.901 | 0.2829 |
| h_arithmetic_v0_002 | ✅ PASS | `single_model_confirmed` | 1.102 | 8.948 | 0.0112 |
| h_arithmetic_v0_003 | ✅ PASS | `single_model_confirmed` | 1.328 | 2.719 | 0.0112 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 1 | 33.3% |
| robustness | 1 | 33.3% |
| confirmatory_ci | 1 | 33.3% |
| multiplicity | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 2 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_arithmetic_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, confirmatory_ci, multiplicity
- Treatment mean: 0.019455
- Cohen's d: 0.4264
- Confirmatory CI (bootstrap): [-0.006737, 0.053187]
- Specificity ratio: 2.900668
- Control abs mean: 0.006707
- Robustness (seed/prompt/resample): 0.000 / 0.500 / 0.000
- Method sensitivity std: 0.024569
- Permutation p-value: 0.2786721327867213
- BH q-value: 0.282872
- Holm-adjusted p: 0.28287171282871715
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_arithmetic_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.092556
- Cohen's d: 1.1022
- Confirmatory CI (bootstrap): [0.044309, 0.153648]
- Specificity ratio: 8.947570
- Control abs mean: 0.010344
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.023501
- Permutation p-value: 0.0058994100589941
- BH q-value: 0.011249
- Holm-adjusted p: 0.021597840215978402
- Cells: 8

### h_arithmetic_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.035163
- Cohen's d: 1.3278
- Confirmatory CI (bootstrap): [0.018015, 0.052445]
- Specificity ratio: 2.719111
- Control abs mean: 0.012932
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.000999
- Permutation p-value: 0.007999200079992
- BH q-value: 0.011249
- Holm-adjusted p: 0.021597840215978402
- Cells: 8
