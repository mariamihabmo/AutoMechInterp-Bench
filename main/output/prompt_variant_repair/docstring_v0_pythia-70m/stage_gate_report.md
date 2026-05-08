# Stage-Gate Report

- Protocol: `real_docstring_v0_pythia-70m_confirmatory_repair_real_prompt_variant_repair_v1`
- Protocol hash: `ca902f955e0cd51ea100437f944ae666b5ae12c2394cbdad082c85bc467666ef`
- Hypotheses: 3
- Accepted: 0
- Unstable: 3
- Rejected: 0
- All pass: False
- Cross-method rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_docstring_v0_001 | ❌ FAIL | `suggestive` | 0.802 | 2.659 | 0.1346 |
| h_docstring_v0_002 | ❌ FAIL | `suggestive` | 0.598 | 2.156 | 0.1346 |
| h_docstring_v0_003 | ❌ FAIL | `suggestive` | 1.183 | 2.067 | 0.0213 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| method_sensitivity | 3 | 100.0% |
| multiplicity | 2 | 66.7% |
| confirmatory_ci | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `suggestive` | 3 |

## Per-Hypothesis Details

### h_docstring_v0_001
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, multiplicity
- Treatment mean: 0.533204
- Cohen's d: 0.8024
- Confirmatory CI (bootstrap): [0.096381, 0.955665]
- Specificity ratio: 2.659437
- Control abs mean: 0.200495
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.599836
- Permutation p-value: 0.0831916808319168
- BH q-value: 0.134587
- Holm-adjusted p: 0.18138186181381863
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_docstring_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: 0.340175
- Cohen's d: 0.5977
- Confirmatory CI (bootstrap): [-0.018038, 0.709289]
- Specificity ratio: 2.155860
- Control abs mean: 0.157791
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.494051
- Permutation p-value: 0.13928607139286073
- BH q-value: 0.134587
- Holm-adjusted p: 0.18138186181381863
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_docstring_v0_003
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.309845
- Cohen's d: 1.1831
- Confirmatory CI (bootstrap): [0.144736, 0.485621]
- Specificity ratio: 2.067008
- Control abs mean: 0.149900
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.222353
- Permutation p-value: 0.009499050094990502
- BH q-value: 0.021298
- Holm-adjusted p: 0.021297870212978704
- Cells: 8
