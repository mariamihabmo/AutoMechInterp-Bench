# Stage-Gate Report

- Protocol: `real_docstring_v0_pythia-70m_confirmatory_repair_real`
- Protocol hash: `600653bd7c47670315971f4af02dacf387d9c95ebad79eda1a87dd7b76de86d5`
- Hypotheses: 3
- Accepted: 0
- Unstable: 3
- Rejected: 0
- All pass: False
- Cross-method rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_docstring_v0_001 | ❌ FAIL | `suggestive` | 0.656 | 2.670 | 0.1048 |
| h_docstring_v0_002 | ❌ FAIL | `suggestive` | 0.938 | 2.902 | 0.0570 |
| h_docstring_v0_003 | ❌ FAIL | `suggestive` | 1.180 | 2.102 | 0.0213 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| method_sensitivity | 3 | 100.0% |
| confirmatory_ci | 1 | 33.3% |
| multiplicity | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `suggestive` | 3 |

## Per-Hypothesis Details

### h_docstring_v0_001
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: 0.463171
- Cohen's d: 0.6559
- Confirmatory CI (bootstrap): [-0.002624, 0.909744]
- Specificity ratio: 2.669592
- Control abs mean: 0.173499
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.633084
- Permutation p-value: 0.09759024097590241
- BH q-value: 0.104790
- Holm-adjusted p: 0.10478952104789521
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_docstring_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.459191
- Cohen's d: 0.9384
- Confirmatory CI (bootstrap): [0.171351, 0.801556]
- Specificity ratio: 2.902395
- Control abs mean: 0.158211
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.426944
- Permutation p-value: 0.0400959904009599
- BH q-value: 0.056994
- Holm-adjusted p: 0.07599240075992401
- Cells: 8

### h_docstring_v0_003
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.338072
- Cohen's d: 1.1801
- Confirmatory CI (bootstrap): [0.152739, 0.524572]
- Specificity ratio: 2.101838
- Control abs mean: 0.160846
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.258861
- Permutation p-value: 0.009499050094990502
- BH q-value: 0.021298
- Holm-adjusted p: 0.021297870212978704
- Cells: 8
