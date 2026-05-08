# Stage-Gate Report

- Protocol: `real_greater_than_v0_gpt2-small`
- Protocol hash: `189d48e71419f76c7081c45effee6255409bf1cadb8df45609dd70baf09dab61`
- Hypotheses: 3
- Accepted: 0
- Unstable: 3
- Rejected: 0
- All pass: False
- Cross-method rank τ: 1.0000
- Cross-model rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_greater_than_v0_001 | ❌ FAIL | `suggestive` | -1.244 | 8.754 | 0.1280 |
| h_greater_than_v0_002 | ❌ FAIL | `suggestive` | 1.236 | 8.202 | 0.1280 |
| h_greater_than_v0_003 | ❌ FAIL | `causal_tested_unstable` | 0.870 | 4.157 | 0.1280 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| multiplicity | 3 | 100.0% |
| cross_model_transfer | 3 | 100.0% |
| method_sensitivity | 2 | 66.7% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `causal_tested_unstable` | 1 |
| `suggestive` | 2 |

## Per-Hypothesis Details

### h_greater_than_v0_001
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, multiplicity, cross_model_transfer
- Treatment mean: -0.199842
- Cohen's d: -1.2436
- Confirmatory CI (bootstrap): [-0.346703, -0.061219]
- Specificity ratio: 8.753950
- Control abs mean: 0.022829
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.138623
- Permutation p-value: 0.125987401259874
- BH q-value: 0.127987
- Holm-adjusted p: 0.37976202379762025
- Cells: 4

### h_greater_than_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, multiplicity, cross_model_transfer
- Treatment mean: 0.187721
- Cohen's d: 1.2355
- Confirmatory CI (bootstrap): [0.054972, 0.318878]
- Specificity ratio: 8.202452
- Control abs mean: 0.022886
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.131157
- Permutation p-value: 0.12488751124887511
- BH q-value: 0.127987
- Holm-adjusted p: 0.37976202379762025
- Cells: 4

### h_greater_than_v0_003
- Passed: False
- Evidence tier: `causal_tested_unstable`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: multiplicity, cross_model_transfer
- Treatment mean: 0.032138
- Cohen's d: 0.8697
- Confirmatory CI (bootstrap): [0.000719, 0.063536]
- Specificity ratio: 4.156867
- Control abs mean: 0.007731
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.031398
- Permutation p-value: 0.12258774122587741
- BH q-value: 0.127987
- Holm-adjusted p: 0.37976202379762025
- Cells: 4
