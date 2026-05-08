# Stage-Gate Report

- Protocol: `real_docstring_v0_pythia-70m_confirmatory_repair_real_distributed_repair_v1`
- Protocol hash: `2c0668895d68028c58cef2b1025e85e59484b34795c5d509d59cfebee765c3ab`
- Hypotheses: 4
- Accepted: 0
- Unstable: 3
- Rejected: 1
- All pass: False
- Cross-method rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_docstring_distributed_001 | ❌ FAIL | `suggestive` | 0.825 | 2.969 | 0.0976 |
| h_docstring_distributed_002 | ❌ FAIL | `suggestive` | 1.003 | 2.803 | 0.0656 |
| h_docstring_distributed_003 | ❌ FAIL | `suggestive` | 1.008 | 3.047 | 0.0628 |
| h_docstring_distributed_004 | ❌ FAIL | `rejected` | 0.878 | 2.481 | 0.0976 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| method_sensitivity | 4 | 100.0% |
| negative_controls | 1 | 25.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `suggestive` | 3 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_docstring_distributed_001
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 1.024067
- Cohen's d: 0.8251
- Confirmatory CI (bootstrap): [0.178498, 1.835417]
- Specificity ratio: 2.968532
- Control abs mean: 0.344974
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 1.140256
- Permutation p-value: 0.09619038096190381
- BH q-value: 0.097590
- Holm-adjusted p: 0.18018198180181982
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_docstring_distributed_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.884357
- Cohen's d: 1.0026
- Confirmatory CI (bootstrap): [0.316457, 1.472341]
- Specificity ratio: 2.803066
- Control abs mean: 0.315496
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.806757
- Permutation p-value: 0.032296770322967704
- BH q-value: 0.065593
- Holm-adjusted p: 0.0983901609839016
- Cells: 8

### h_docstring_distributed_003
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.771643
- Cohen's d: 1.0078
- Confirmatory CI (bootstrap): [0.267321, 1.260068]
- Specificity ratio: 3.046534
- Control abs mean: 0.253285
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.699927
- Permutation p-value: 0.015598440155984402
- BH q-value: 0.062794
- Holm-adjusted p: 0.0627937206279372
- Cells: 8

### h_docstring_distributed_004
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, method_sensitivity
- Treatment mean: 1.307159
- Cohen's d: 0.8782
- Confirmatory CI (bootstrap): [0.337989, 2.308982]
- Specificity ratio: 2.480523
- Control abs mean: 0.526969
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 1.369217
- Permutation p-value: 0.09409059094090591
- BH q-value: 0.097590
- Holm-adjusted p: 0.18018198180181982
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
