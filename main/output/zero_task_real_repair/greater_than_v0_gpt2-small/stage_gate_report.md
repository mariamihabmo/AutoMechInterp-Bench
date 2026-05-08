# Stage-Gate Report

- Protocol: `real_greater_than_v0_gpt2-small_confirmatory_repair_real`
- Protocol hash: `2c15fdd97f66f77c1126f28193fee5cc9b5dd20984e656a9b381f62fe15b01e9`
- Hypotheses: 3
- Accepted: 1
- Unstable: 2
- Rejected: 0
- All pass: False
- Cross-method rank τ: 1.0000
- Cross-model rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_greater_than_v0_001 | ❌ FAIL | `suggestive` | -0.534 | 5.247 | 0.2773 |
| h_greater_than_v0_002 | ❌ FAIL | `suggestive` | 0.515 | 3.502 | 0.2773 |
| h_greater_than_v0_003 | ✅ PASS | `single_model_confirmed` | 0.940 | 4.684 | 0.0474 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| cross_model_transfer | 3 | 100.0% |
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
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, multiplicity, cross_model_transfer
- Treatment mean: -0.082127
- Cohen's d: -0.5337
- Confirmatory CI (bootstrap): [-0.211729, -0.001083]
- Specificity ratio: 5.246512
- Control abs mean: 0.015654
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.055834
- Permutation p-value: 0.22877712228777122
- BH q-value: 0.277272
- Holm-adjusted p: 0.45655434456554345
- Cells: 8

### h_greater_than_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, confirmatory_ci, multiplicity, cross_model_transfer
- Treatment mean: 0.078161
- Cohen's d: 0.5150
- Confirmatory CI (bootstrap): [-0.003056, 0.200617]
- Specificity ratio: 3.501686
- Control abs mean: 0.022321
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.057665
- Permutation p-value: 0.2832716728327167
- BH q-value: 0.277272
- Holm-adjusted p: 0.45655434456554345
- Cells: 8

### h_greater_than_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.034827
- Cohen's d: 0.9397
- Confirmatory CI (bootstrap): [0.008845, 0.060081]
- Specificity ratio: 4.684246
- Control abs mean: 0.007435
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.034452
- Permutation p-value: 0.0143985601439856
- BH q-value: 0.047395
- Holm-adjusted p: 0.04739526047395261
- Cells: 8
