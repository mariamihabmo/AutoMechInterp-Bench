# Stage-Gate Report

- Protocol: `real_fact_recall_v0_gpt2-small_confirmatory_repair_real_prompt_holdout_high_power_n40`
- Protocol hash: `54e8595edeb9526976b62bbd81e10091f0c90c55168e5be1509e426bed6090cc`
- Hypotheses: 3
- Accepted: 1
- Unstable: 2
- Rejected: 0
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_fact_recall_v0_001 | ❌ FAIL | `suggestive` | 1.317 | 2.531 | 0.0082 |
| h_fact_recall_v0_002 | ❌ FAIL | `suggestive` | 1.653 | 11.589 | 0.0082 |
| h_fact_recall_v0_003 | ✅ PASS | `single_model_confirmed` | 1.758 | 3.330 | 0.0082 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| method_sensitivity | 2 | 66.7% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `suggestive` | 2 |

## Per-Hypothesis Details

### h_fact_recall_v0_001
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.280731
- Cohen's d: 1.3175
- Confirmatory CI (bootstrap): [0.172748, 0.468464]
- Specificity ratio: 2.530858
- Control abs mean: 0.110923
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.121216
- Permutation p-value: 0.007599240075992401
- BH q-value: 0.008199
- Holm-adjusted p: 0.0221977802219778
- Cells: 8

### h_fact_recall_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.374066
- Cohen's d: 1.6532
- Confirmatory CI (bootstrap): [0.249138, 0.542162]
- Specificity ratio: 11.589417
- Control abs mean: 0.032277
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.179687
- Permutation p-value: 0.006899310068993101
- BH q-value: 0.008199
- Holm-adjusted p: 0.0221977802219778
- Cells: 8

### h_fact_recall_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.098419
- Cohen's d: 1.7579
- Confirmatory CI (bootstrap): [0.059638, 0.131974]
- Specificity ratio: 3.330175
- Control abs mean: 0.029554
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.047653
- Permutation p-value: 0.006899310068993101
- BH q-value: 0.008199
- Holm-adjusted p: 0.0221977802219778
- Cells: 8
