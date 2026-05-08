# Stage-Gate Report

- Protocol: `real_docstring_v0_gpt2-small_confirmatory_repair_real_prompt_variant_repair_v1`
- Protocol hash: `f218f174b098b88d31ed4478cf222efeb2a2da76470ea9fbc33d63d2a13992cb`
- Hypotheses: 3
- Accepted: 0
- Unstable: 3
- Rejected: 0
- All pass: False
- Cross-method rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_docstring_v0_001 | ❌ FAIL | `suggestive` | 0.957 | 4.003 | 0.0339 |
| h_docstring_v0_002 | ❌ FAIL | `suggestive` | 1.297 | 5.006 | 0.0123 |
| h_docstring_v0_003 | ❌ FAIL | `suggestive` | 1.128 | 5.494 | 0.0123 |

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
- Treatment mean: 0.592237
- Cohen's d: 0.9566
- Confirmatory CI (bootstrap): [0.212217, 1.017361]
- Specificity ratio: 4.002979
- Control abs mean: 0.147949
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.528713
- Permutation p-value: 0.029397060293970604
- BH q-value: 0.033897
- Holm-adjusted p: 0.033896610338966106
- Cells: 8

### h_docstring_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.460900
- Cohen's d: 1.2966
- Confirmatory CI (bootstrap): [0.222806, 0.704215]
- Specificity ratio: 5.006116
- Control abs mean: 0.092067
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.330414
- Permutation p-value: 0.007699230076992301
- BH q-value: 0.012299
- Holm-adjusted p: 0.021297870212978704
- Cells: 8

### h_docstring_v0_003
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity
- Treatment mean: 0.653529
- Cohen's d: 1.1277
- Confirmatory CI (bootstrap): [0.339345, 1.087609]
- Specificity ratio: 5.494354
- Control abs mean: 0.118946
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.429717
- Permutation p-value: 0.009499050094990502
- BH q-value: 0.012299
- Holm-adjusted p: 0.021297870212978704
- Cells: 8
