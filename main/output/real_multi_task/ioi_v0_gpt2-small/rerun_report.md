# Stage-Gate Report

- Protocol: `real_ioi_v0_gpt2-small`
- Protocol hash: `2cf9391768fcc170931f8224eb50009edde4e328ae068c6389e398b9f8a15fba`
- Hypotheses: 4
- Accepted: 2
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.5556

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_ioi_v0_001 | ✅ PASS | `single_model_confirmed` | -2.224 | 17.759 | 0.0000 |
| h_ioi_v0_002 | ❌ FAIL | `rejected` | -0.825 | 6.093 | 0.0001 |
| h_ioi_v0_003 | ❌ FAIL | `rejected` | -0.796 | 8.120 | 0.0000 |
| h_ioi_v0_mlp_001 | ✅ PASS | `single_model_confirmed` | -1.136 | 475.863 | 0.0000 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 2 | 50.0% |
| robustness | 2 | 50.0% |
| method_sensitivity | 2 | 50.0% |
| negative_controls | 1 | 25.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 2 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_ioi_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: -6.757727
- Cohen's d: -2.2244
- Confirmatory CI (bootstrap): [-7.772485, -5.770210]
- Specificity ratio: 17.758919
- Control abs mean: 0.380526
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 2.325384
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 36

### h_ioi_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, method_sensitivity
- Treatment mean: -3.397934
- Cohen's d: -0.8252
- Confirmatory CI (bootstrap): [-4.641657, -1.973735]
- Specificity ratio: 6.093381
- Control abs mean: 0.557643
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 3.829283
- Permutation p-value: 0.0002
- BH q-value: 0.000100
- Holm-adjusted p: 0.0001
- Cells: 36
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_ioi_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity
- Treatment mean: -3.308893
- Cohen's d: -0.7961
- Confirmatory CI (bootstrap): [-4.549318, -1.923010]
- Specificity ratio: 8.120489
- Control abs mean: 0.407475
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 3.836483
- Permutation p-value: 0.0001
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 36
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_ioi_v0_mlp_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: -3.722082
- Cohen's d: -1.1359
- Confirmatory CI (bootstrap): [-4.786608, -2.660476]
- Specificity ratio: 475.863031
- Control abs mean: 0.007822
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 2.631697
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 36
