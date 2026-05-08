# Stage-Gate Report

- Protocol: `real_fact_recall_v0_gpt2-small_confirmatory_repair_real`
- Protocol hash: `c9cefe72b678f177071510370d8915418ea9ea28b58608c06e7f4973a9ff01ca`
- Hypotheses: 3
- Accepted: 0
- Unstable: 3
- Rejected: 0
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_fact_recall_v0_001 | ❌ FAIL | `suggestive` | 1.522 | 2.780 | 0.0123 |
| h_fact_recall_v0_002 | ❌ FAIL | `suggestive` | 1.465 | 10.005 | 0.0123 |
| h_fact_recall_v0_003 | ❌ FAIL | `suggestive` | 1.373 | 3.141 | 0.0175 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| method_sensitivity | 3 | 100.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `suggestive` | 3 |

## Per-Hypothesis Details

### h_fact_recall_v0_001
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.330973
- Cohen's d: 1.5216
- Confirmatory CI (bootstrap): [0.214577, 0.503598]
- Specificity ratio: 2.780311
- Control abs mean: 0.119042
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.154829
- Permutation p-value: 0.007599240075992401
- BH q-value: 0.012299
- Holm-adjusted p: 0.0245975402459754
- Cells: 8

### h_fact_recall_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.389546
- Cohen's d: 1.4650
- Confirmatory CI (bootstrap): [0.248677, 0.602595]
- Specificity ratio: 10.005275
- Control abs mean: 0.038934
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.196879
- Permutation p-value: 0.006899310068993101
- BH q-value: 0.012299
- Holm-adjusted p: 0.0245975402459754
- Cells: 8

### h_fact_recall_v0_003
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.104331
- Cohen's d: 1.3733
- Confirmatory CI (bootstrap): [0.053412, 0.152359]
- Specificity ratio: 3.141116
- Control abs mean: 0.033215
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.063172
- Permutation p-value: 0.014898510148985102
- BH q-value: 0.017498
- Holm-adjusted p: 0.0245975402459754
- Cells: 8
