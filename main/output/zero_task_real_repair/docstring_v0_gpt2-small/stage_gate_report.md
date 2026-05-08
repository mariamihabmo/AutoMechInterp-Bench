# Stage-Gate Report

- Protocol: `real_docstring_v0_gpt2-small_confirmatory_repair_real`
- Protocol hash: `349a909250ca597f296449ed15eee3a3a91b26e6cefc2e05e136fc3216a50686`
- Hypotheses: 3
- Accepted: 0
- Unstable: 3
- Rejected: 0
- All pass: False
- Cross-method rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_docstring_v0_001 | ❌ FAIL | `suggestive` | 1.045 | 3.871 | 0.0247 |
| h_docstring_v0_002 | ❌ FAIL | `suggestive` | 1.152 | 4.266 | 0.0123 |
| h_docstring_v0_003 | ❌ FAIL | `suggestive` | 1.334 | 5.792 | 0.0123 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| method_sensitivity | 3 | 100.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `suggestive` | 3 |

## Per-Hypothesis Details

### h_docstring_v0_001
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.570246
- Cohen's d: 1.0446
- Confirmatory CI (bootstrap): [0.201308, 0.935283]
- Specificity ratio: 3.871346
- Control abs mean: 0.147299
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.505093
- Permutation p-value: 0.0217978202179782
- BH q-value: 0.024698
- Holm-adjusted p: 0.024697530246975304
- Cells: 8

### h_docstring_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.448391
- Cohen's d: 1.1524
- Confirmatory CI (bootstrap): [0.182070, 0.716117]
- Specificity ratio: 4.265780
- Control abs mean: 0.105113
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.362553
- Permutation p-value: 0.007699230076992301
- BH q-value: 0.012299
- Holm-adjusted p: 0.021297870212978704
- Cells: 8

### h_docstring_v0_003
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.616101
- Cohen's d: 1.3337
- Confirmatory CI (bootstrap): [0.318574, 0.913965]
- Specificity ratio: 5.792295
- Control abs mean: 0.106366
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.415014
- Permutation p-value: 0.009499050094990502
- BH q-value: 0.012299
- Holm-adjusted p: 0.021297870212978704
- Cells: 8
