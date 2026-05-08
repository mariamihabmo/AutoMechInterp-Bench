# Stage-Gate Report

- Protocol: `real_ioi_v0_gpt2-small_prompt_variant_repair_v1`
- Protocol hash: `607257ae395cfc27e190daf1ac2313d0b62f2d522a8715be2a2ea53977ef8f19`
- Hypotheses: 4
- Accepted: 1
- Unstable: 2
- Rejected: 1
- All pass: False
- Cross-method rank τ: 0.3333
- Cross-model rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_ioi_v0_001 | ✅ PASS | `single_model_confirmed` | -0.588 | 10.802 | 0.0004 |
| h_ioi_v0_002 | ❌ FAIL | `causal_tested_unstable` | 0.526 | 2.413 | 0.0004 |
| h_ioi_v0_003 | ❌ FAIL | `causal_tested_unstable` | 0.404 | 3.352 | 0.0055 |
| h_ioi_v0_mlp_001 | ❌ FAIL | `rejected` | 0.189 | 1.638 | 0.1729 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| power_adequacy | 3 | 75.0% |
| cross_model_transfer | 1 | 25.0% |
| causal_effect | 1 | 25.0% |
| negative_controls | 1 | 25.0% |
| robustness | 1 | 25.0% |
| confirmatory_ci | 1 | 25.0% |
| multiplicity | 1 | 25.0% |
| effect_size_practical | 1 | 25.0% |
| baseline_superiority | 1 | 25.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `causal_tested_unstable` | 2 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_ioi_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: -1.005443
- Cohen's d: -0.5883
- Confirmatory CI (bootstrap): [-1.459887, -0.554283]
- Specificity ratio: 10.802096
- Control abs mean: 0.093079
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.496893
- Permutation p-value: 0.00019998000199980003
- BH q-value: 0.000400
- Holm-adjusted p: 0.0005999400059994001
- Cells: 54

### h_ioi_v0_002
- Passed: False
- Evidence tier: `causal_tested_unstable`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=pass
- Failed checks: power_adequacy
- Treatment mean: 0.482102
- Cohen's d: 0.5256
- Confirmatory CI (bootstrap): [0.286077, 0.780045]
- Specificity ratio: 2.413122
- Control abs mean: 0.199784
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.413869
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000400
- Holm-adjusted p: 0.00039996000399960006
- Cells: 54

### h_ioi_v0_003
- Passed: False
- Evidence tier: `causal_tested_unstable`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=pass
- Failed checks: power_adequacy
- Treatment mean: 0.450576
- Cohen's d: 0.4042
- Confirmatory CI (bootstrap): [0.167933, 0.757511]
- Specificity ratio: 3.351982
- Control abs mean: 0.134421
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.308415
- Permutation p-value: 0.0045995400459954
- BH q-value: 0.005466
- Holm-adjusted p: 0.0081991800819918
- Cells: 54

### h_ioi_v0_mlp_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical, baseline_superiority
- Treatment mean: 0.184433
- Cohen's d: 0.1888
- Confirmatory CI (bootstrap): [-0.064086, 0.455510]
- Specificity ratio: 1.638109
- Control abs mean: 0.112589
- Robustness (seed/prompt/resample): 0.000 / 0.333 / 0.000
- Method sensitivity std: 0.274891
- Permutation p-value: 0.17098290170982902
- BH q-value: 0.172883
- Holm-adjusted p: 0.1728827117288271
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
