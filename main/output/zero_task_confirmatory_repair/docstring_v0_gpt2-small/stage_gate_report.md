# Stage-Gate Report

- Protocol: `real_docstring_v0_gpt2-small_confirmatory_repair_mock`
- Protocol hash: `0553ab5eca92072685d861045cc88241f52a7def059c1af2a6c507f86c5c911b`
- Hypotheses: 3
- Accepted: 3
- Unstable: 0
- Rejected: 0
- All pass: True
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_docstring_v0_001 | ✅ PASS | `single_model_confirmed` | 6.926 | 11.426 | 0.0117 |
| h_docstring_v0_002 | ✅ PASS | `single_model_confirmed` | 11.860 | 11.433 | 0.0156 |
| h_docstring_v0_003 | ✅ PASS | `single_model_confirmed` | 11.886 | 13.031 | 0.0117 |

## Failure Analysis

No core gate failures detected.

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 3 |

## Per-Hypothesis Details

### h_docstring_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.077338
- Cohen's d: 6.9257
- Confirmatory CI (bootstrap): [0.071788, 0.085938]
- Specificity ratio: 11.425669
- Control abs mean: 0.006769
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.003287
- Permutation p-value: 0.01556420233463035
- BH q-value: 0.011673
- Holm-adjusted p: 0.01556420233463035
- Cells: 8

### h_docstring_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.077137
- Cohen's d: 11.8603
- Confirmatory CI (bootstrap): [0.072650, 0.081613]
- Specificity ratio: 11.433071
- Control abs mean: 0.006747
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.000662
- Permutation p-value: 0.0038910505836575876
- BH q-value: 0.015564
- Holm-adjusted p: 0.01556420233463035
- Cells: 8

### h_docstring_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.089100
- Cohen's d: 11.8856
- Confirmatory CI (bootstrap): [0.084788, 0.094787]
- Specificity ratio: 13.031079
- Control abs mean: 0.006837
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.003175
- Permutation p-value: 0.01556420233463035
- BH q-value: 0.011673
- Holm-adjusted p: 0.011673151750972763
- Cells: 8
