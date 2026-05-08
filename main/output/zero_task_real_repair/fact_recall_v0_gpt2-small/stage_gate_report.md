# Stage-Gate Report

- Protocol: `real_fact_recall_v0_gpt2-small_confirmatory_repair_real`
- Protocol hash: `c9cefe72b678f177071510370d8915418ea9ea28b58608c06e7f4973a9ff01ca`
- Hypotheses: 3
- Accepted: 1
- Unstable: 2
- Rejected: 0
- All pass: False
- Cross-method rank τ: 1.0000
- Cross-model rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_fact_recall_v0_001 | ❌ FAIL | `suggestive` | 1.348 | 2.773 | 0.0082 |
| h_fact_recall_v0_002 | ❌ FAIL | `suggestive` | 2.012 | 11.544 | 0.0082 |
| h_fact_recall_v0_003 | ✅ PASS | `single_model_confirmed` | 1.845 | 4.253 | 0.0082 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| cross_model_transfer | 3 | 100.0% |
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
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, cross_model_transfer
- Treatment mean: 0.301640
- Cohen's d: 1.3479
- Confirmatory CI (bootstrap): [0.186292, 0.491029]
- Specificity ratio: 2.772573
- Control abs mean: 0.108794
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.131433
- Permutation p-value: 0.007599240075992401
- BH q-value: 0.008199
- Holm-adjusted p: 0.0221977802219778
- Cells: 8

### h_fact_recall_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, cross_model_transfer
- Treatment mean: 0.360671
- Cohen's d: 2.0124
- Confirmatory CI (bootstrap): [0.251888, 0.481739]
- Specificity ratio: 11.543652
- Control abs mean: 0.031244
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.151522
- Permutation p-value: 0.006899310068993101
- BH q-value: 0.008199
- Holm-adjusted p: 0.0221977802219778
- Cells: 8

### h_fact_recall_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.107968
- Cohen's d: 1.8447
- Confirmatory CI (bootstrap): [0.070499, 0.145739]
- Specificity ratio: 4.253239
- Control abs mean: 0.025385
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.048324
- Permutation p-value: 0.006899310068993101
- BH q-value: 0.008199
- Holm-adjusted p: 0.0221977802219778
- Cells: 8
