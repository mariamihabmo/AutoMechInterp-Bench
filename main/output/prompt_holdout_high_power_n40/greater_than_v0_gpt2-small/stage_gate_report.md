# Stage-Gate Report

- Protocol: `real_greater_than_v0_gpt2-small_confirmatory_repair_real_prompt_holdout_high_power_n40`
- Protocol hash: `55cbaf291d905e88b4e4d2d94c49cf0e3197fb4164b0ceeb1fd59be0b3c1727e`
- Hypotheses: 3
- Accepted: 1
- Unstable: 2
- Rejected: 0
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_greater_than_v0_001 | ❌ FAIL | `suggestive` | -0.538 | 5.213 | 0.2842 |
| h_greater_than_v0_002 | ❌ FAIL | `suggestive` | 0.508 | 3.372 | 0.3422 |
| h_greater_than_v0_003 | ✅ PASS | `single_model_confirmed` | 0.947 | 4.746 | 0.0201 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| method_sensitivity | 2 | 66.7% |
| multiplicity | 2 | 66.7% |
| confirmatory_ci | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `suggestive` | 2 |

## Per-Hypothesis Details

### h_greater_than_v0_001
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, multiplicity
- Treatment mean: -0.083185
- Cohen's d: -0.5384
- Confirmatory CI (bootstrap): [-0.216054, -0.001877]
- Specificity ratio: 5.213167
- Control abs mean: 0.015957
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.057417
- Permutation p-value: 0.18788121187881213
- BH q-value: 0.284222
- Holm-adjusted p: 0.37896210378962103
- Cells: 8

### h_greater_than_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: 0.078831
- Cohen's d: 0.5081
- Confirmatory CI (bootstrap): [-0.003835, 0.202766]
- Specificity ratio: 3.371880
- Control abs mean: 0.023379
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.060108
- Permutation p-value: 0.34756524347565243
- BH q-value: 0.342166
- Holm-adjusted p: 0.37896210378962103
- Cells: 8

### h_greater_than_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.035093
- Cohen's d: 0.9466
- Confirmatory CI (bootstrap): [0.009623, 0.060538]
- Specificity ratio: 4.745685
- Control abs mean: 0.007395
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.034545
- Permutation p-value: 0.0084991500849915
- BH q-value: 0.020098
- Holm-adjusted p: 0.020097990200979902
- Cells: 8
