# Stage-Gate Report

- Protocol: `real_arithmetic_v0_gpt2-small_confirmatory_repair_real_prompt_variant_repair_v1_prompt_holdout_high_power_n100`
- Protocol hash: `5fe2f9ccf34856a03870f8abd4c7dd3975d6a7992ac3f34390cb39077fdd0dcf`
- Hypotheses: 3
- Accepted: 1
- Unstable: 2
- Rejected: 0
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_arithmetic_v0_001 | ❌ FAIL | `causal_tested_unstable` | 0.518 | 4.157 | 0.1638 |
| h_arithmetic_v0_002 | ✅ PASS | `single_model_confirmed` | 1.097 | 6.009 | 0.0225 |
| h_arithmetic_v0_003 | ❌ FAIL | `causal_tested_unstable` | 0.773 | 2.997 | 0.1095 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| multiplicity | 2 | 66.7% |
| confirmatory_ci | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `causal_tested_unstable` | 2 |

## Per-Hypothesis Details

### h_arithmetic_v0_001
- Passed: False
- Evidence tier: `causal_tested_unstable`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: confirmatory_ci, multiplicity
- Treatment mean: 0.021237
- Cohen's d: 0.5176
- Confirmatory CI (bootstrap): [-0.002330, 0.050895]
- Specificity ratio: 4.156528
- Control abs mean: 0.005109
- Robustness (seed/prompt/resample): 0.500 / 0.500 / 1.000
- Method sensitivity std: 0.018566
- Permutation p-value: 0.1680831916808319
- BH q-value: 0.163784
- Holm-adjusted p: 0.16378362163783622
- Cells: 8

### h_arithmetic_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.103531
- Cohen's d: 1.0974
- Confirmatory CI (bootstrap): [0.056368, 0.185967]
- Specificity ratio: 6.009455
- Control abs mean: 0.017228
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.044898
- Permutation p-value: 0.0058994100589941
- BH q-value: 0.022498
- Holm-adjusted p: 0.022497750224977502
- Cells: 8

### h_arithmetic_v0_003
- Passed: False
- Evidence tier: `causal_tested_unstable`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: multiplicity
- Treatment mean: 0.036398
- Cohen's d: 0.7726
- Confirmatory CI (bootstrap): [0.004271, 0.065578]
- Specificity ratio: 2.996786
- Control abs mean: 0.012146
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.018570
- Permutation p-value: 0.0684931506849315
- BH q-value: 0.109489
- Holm-adjusted p: 0.145985401459854
- Cells: 8
