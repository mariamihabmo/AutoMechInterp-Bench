# Stage-Gate Report

- Protocol: `real_arithmetic_v0_pythia-70m_confirmatory_repair_mock`
- Protocol hash: `a87225226be8f272e5c27ebd4da24d9c6de53c44fd9e268361e578e96dea6c60`
- Hypotheses: 3
- Accepted: 3
- Unstable: 0
- Rejected: 0
- All pass: True
- Cross-method rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_arithmetic_v0_001 | ✅ PASS | `single_model_confirmed` | 5.845 | 11.615 | 0.0117 |
| h_arithmetic_v0_002 | ✅ PASS | `single_model_confirmed` | 7.488 | 12.824 | 0.0156 |
| h_arithmetic_v0_003 | ✅ PASS | `single_model_confirmed` | 5.705 | 11.916 | 0.0117 |

## Failure Analysis

No core gate failures detected.

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 3 |

## Per-Hypothesis Details

### h_arithmetic_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.077750
- Cohen's d: 5.8452
- Confirmatory CI (bootstrap): [0.070400, 0.087225]
- Specificity ratio: 11.615313
- Control abs mean: 0.006694
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.006925
- Permutation p-value: 0.011673151750972763
- BH q-value: 0.011673
- Holm-adjusted p: 0.023346303501945526
- Cells: 8

### h_arithmetic_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.084600
- Cohen's d: 7.4876
- Confirmatory CI (bootstrap): [0.077625, 0.091950]
- Specificity ratio: 12.824254
- Control abs mean: 0.006597
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.008200
- Permutation p-value: 0.0038910505836575876
- BH q-value: 0.015564
- Holm-adjusted p: 0.023346303501945526
- Cells: 8

### h_arithmetic_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.079575
- Cohen's d: 5.7046
- Confirmatory CI (bootstrap): [0.070813, 0.087938]
- Specificity ratio: 11.915770
- Control abs mean: 0.006678
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.001825
- Permutation p-value: 0.023346303501945526
- BH q-value: 0.011673
- Holm-adjusted p: 0.023346303501945526
- Cells: 8
