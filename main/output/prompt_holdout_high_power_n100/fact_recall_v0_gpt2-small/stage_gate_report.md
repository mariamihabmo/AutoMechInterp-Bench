# Stage-Gate Report

- Protocol: `real_fact_recall_v0_gpt2-small_confirmatory_repair_real_prompt_holdout_high_power_n100`
- Protocol hash: `2d3343e0f66cefad8936df69e802fecf9329175570a1c81eacb2c3b4ce472d2f`
- Hypotheses: 3
- Accepted: 1
- Unstable: 2
- Rejected: 0
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_fact_recall_v0_001 | ❌ FAIL | `suggestive` | 2.165 | 3.107 | 0.0082 |
| h_fact_recall_v0_002 | ❌ FAIL | `suggestive` | 1.562 | 11.552 | 0.0082 |
| h_fact_recall_v0_003 | ✅ PASS | `single_model_confirmed` | 1.998 | 3.358 | 0.0082 |

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
- Treatment mean: 0.296525
- Cohen's d: 2.1651
- Confirmatory CI (bootstrap): [0.203340, 0.382305]
- Specificity ratio: 3.106799
- Control abs mean: 0.095444
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.119265
- Permutation p-value: 0.007599240075992401
- BH q-value: 0.008199
- Holm-adjusted p: 0.0221977802219778
- Cells: 8

### h_fact_recall_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.333943
- Cohen's d: 1.5618
- Confirmatory CI (bootstrap): [0.213337, 0.490898]
- Specificity ratio: 11.552259
- Control abs mean: 0.028907
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.171614
- Permutation p-value: 0.006899310068993101
- BH q-value: 0.008199
- Holm-adjusted p: 0.0221977802219778
- Cells: 8

### h_fact_recall_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.099543
- Cohen's d: 1.9977
- Confirmatory CI (bootstrap): [0.067925, 0.132178]
- Specificity ratio: 3.357749
- Control abs mean: 0.029646
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.044125
- Permutation p-value: 0.006899310068993101
- BH q-value: 0.008199
- Holm-adjusted p: 0.0221977802219778
- Cells: 8
