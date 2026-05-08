# Stage-Gate Report

- Protocol: `real_greater_than_v0_gpt2-small_confirmatory_repair_real_prompt_holdout_high_power_n100`
- Protocol hash: `28a695435158baa0b9ac0898495027e1091d27b18ec1af6e8f2edac3d5dd522f`
- Hypotheses: 3
- Accepted: 1
- Unstable: 2
- Rejected: 0
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_greater_than_v0_001 | ❌ FAIL | `suggestive` | -0.532 | 5.313 | 0.2198 |
| h_greater_than_v0_002 | ❌ FAIL | `suggestive` | 0.527 | 3.549 | 0.2198 |
| h_greater_than_v0_003 | ✅ PASS | `single_model_confirmed` | 0.948 | 4.754 | 0.0201 |

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
- Treatment mean: -0.082499
- Cohen's d: -0.5325
- Confirmatory CI (bootstrap): [-0.214840, -0.000672]
- Specificity ratio: 5.312641
- Control abs mean: 0.015529
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.060002
- Permutation p-value: 0.1957804219578042
- BH q-value: 0.219778
- Holm-adjusted p: 0.39376062393760625
- Cells: 8

### h_greater_than_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: 0.080632
- Cohen's d: 0.5271
- Confirmatory CI (bootstrap): [-0.000745, 0.201345]
- Specificity ratio: 3.548674
- Control abs mean: 0.022722
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.057501
- Permutation p-value: 0.22897710228977103
- BH q-value: 0.219778
- Holm-adjusted p: 0.39376062393760625
- Cells: 8

### h_greater_than_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.035247
- Cohen's d: 0.9478
- Confirmatory CI (bootstrap): [0.009670, 0.060802]
- Specificity ratio: 4.754012
- Control abs mean: 0.007414
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.034679
- Permutation p-value: 0.0084991500849915
- BH q-value: 0.020098
- Holm-adjusted p: 0.020097990200979902
- Cells: 8
