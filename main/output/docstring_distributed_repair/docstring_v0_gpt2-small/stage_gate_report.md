# Stage-Gate Report

- Protocol: `real_docstring_v0_gpt2-small_confirmatory_repair_real_distributed_repair_v1`
- Protocol hash: `8bd6194801a9318d49d78dca6091eae8c85f35529aa6503631863ef235565180`
- Hypotheses: 4
- Accepted: 0
- Unstable: 4
- Rejected: 0
- All pass: False
- Cross-method rank τ: 0.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_docstring_distributed_001 | ❌ FAIL | `suggestive` | 1.177 | 4.520 | 0.0088 |
| h_docstring_distributed_002 | ❌ FAIL | `suggestive` | 1.364 | 5.345 | 0.0088 |
| h_docstring_distributed_003 | ❌ FAIL | `suggestive` | 1.394 | 5.437 | 0.0088 |
| h_docstring_distributed_004 | ❌ FAIL | `suggestive` | 1.216 | 3.825 | 0.0088 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| method_sensitivity | 4 | 100.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `suggestive` | 4 |

## Per-Hypothesis Details

### h_docstring_distributed_001
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 1.189617
- Cohen's d: 1.1773
- Confirmatory CI (bootstrap): [0.492594, 1.856196]
- Specificity ratio: 4.520480
- Control abs mean: 0.263162
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.937029
- Permutation p-value: 0.006399360063993601
- BH q-value: 0.008799
- Holm-adjusted p: 0.028397160283971604
- Cells: 8

### h_docstring_distributed_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 1.274658
- Cohen's d: 1.3643
- Confirmatory CI (bootstrap): [0.635047, 1.903848]
- Specificity ratio: 5.344887
- Control abs mean: 0.238482
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.867335
- Permutation p-value: 0.0072992700729927005
- BH q-value: 0.008799
- Holm-adjusted p: 0.028397160283971604
- Cells: 8

### h_docstring_distributed_003
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 1.094914
- Cohen's d: 1.3939
- Confirmatory CI (bootstrap): [0.570935, 1.615280]
- Specificity ratio: 5.437171
- Control abs mean: 0.201376
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.728463
- Permutation p-value: 0.008099190080991902
- BH q-value: 0.008799
- Holm-adjusted p: 0.028397160283971604
- Cells: 8

### h_docstring_distributed_004
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 1.738114
- Cohen's d: 1.2155
- Confirmatory CI (bootstrap): [0.757348, 2.709515]
- Specificity ratio: 3.825262
- Control abs mean: 0.454378
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 1.330068
- Permutation p-value: 0.006399360063993601
- BH q-value: 0.008799
- Holm-adjusted p: 0.028397160283971604
- Cells: 8
