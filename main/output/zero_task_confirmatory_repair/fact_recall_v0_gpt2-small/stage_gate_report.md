# Stage-Gate Report

- Protocol: `real_fact_recall_v0_gpt2-small_confirmatory_repair_mock`
- Protocol hash: `c82e157a93fb5e6515a5e19620689f78b09329a26435c029455d9d13619246e4`
- Hypotheses: 3
- Accepted: 3
- Unstable: 0
- Rejected: 0
- All pass: True
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_fact_recall_v0_001 | ✅ PASS | `single_model_confirmed` | 7.774 | 11.045 | 0.0117 |
| h_fact_recall_v0_002 | ✅ PASS | `single_model_confirmed` | 9.441 | 12.415 | 0.0117 |
| h_fact_recall_v0_003 | ✅ PASS | `single_model_confirmed` | 9.275 | 10.780 | 0.0117 |

## Failure Analysis

No core gate failures detected.

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 3 |

## Per-Hypothesis Details

### h_fact_recall_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.075900
- Cohen's d: 7.7739
- Confirmatory CI (bootstrap): [0.070050, 0.082837]
- Specificity ratio: 11.045020
- Control abs mean: 0.006872
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.002700
- Permutation p-value: 0.011673151750972763
- BH q-value: 0.011673
- Holm-adjusted p: 0.011673151750972763
- Cells: 8

### h_fact_recall_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.080312
- Cohen's d: 9.4409
- Confirmatory CI (bootstrap): [0.074550, 0.086125]
- Specificity ratio: 12.415459
- Control abs mean: 0.006469
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.001113
- Permutation p-value: 0.0038910505836575876
- BH q-value: 0.011673
- Holm-adjusted p: 0.023346303501945526
- Cells: 8

### h_fact_recall_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.071788
- Cohen's d: 9.2749
- Confirmatory CI (bootstrap): [0.066812, 0.076787]
- Specificity ratio: 10.779916
- Control abs mean: 0.006659
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.000113
- Permutation p-value: 0.0038910505836575876
- BH q-value: 0.011673
- Holm-adjusted p: 0.023346303501945526
- Cells: 8
