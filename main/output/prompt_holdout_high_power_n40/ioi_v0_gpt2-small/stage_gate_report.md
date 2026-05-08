# Stage-Gate Report

- Protocol: `real_ioi_v0_gpt2-small_prompt_variant_repair_v1_prompt_holdout_high_power_n40`
- Protocol hash: `6dc0a73d3faeaf5948cd08731c132133c0e176b806b50160755956f42d1d3c7f`
- Hypotheses: 4
- Accepted: 1
- Unstable: 2
- Rejected: 1
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_ioi_v0_001 | ✅ PASS | `single_model_confirmed` | -0.573 | 10.289 | 0.0004 |
| h_ioi_v0_002 | ❌ FAIL | `causal_tested_unstable` | 0.528 | 2.380 | 0.0004 |
| h_ioi_v0_003 | ❌ FAIL | `causal_tested_unstable` | 0.408 | 3.350 | 0.0055 |
| h_ioi_v0_mlp_001 | ❌ FAIL | `rejected` | 0.216 | 1.677 | 0.1176 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| power_adequacy | 3 | 75.0% |
| causal_effect | 1 | 25.0% |
| negative_controls | 1 | 25.0% |
| robustness | 1 | 25.0% |
| confirmatory_ci | 1 | 25.0% |
| multiplicity | 1 | 25.0% |
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
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: -1.003906
- Cohen's d: -0.5733
- Confirmatory CI (bootstrap): [-1.465556, -0.540129]
- Specificity ratio: 10.289321
- Control abs mean: 0.097568
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.493256
- Permutation p-value: 0.00029997000299970003
- BH q-value: 0.000400
- Holm-adjusted p: 0.0005999400059994001
- Cells: 54

### h_ioi_v0_002
- Passed: False
- Evidence tier: `causal_tested_unstable`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=pass
- Failed checks: power_adequacy
- Treatment mean: 0.494867
- Cohen's d: 0.5279
- Confirmatory CI (bootstrap): [0.295970, 0.804316]
- Specificity ratio: 2.380119
- Control abs mean: 0.207917
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.425422
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000400
- Holm-adjusted p: 0.00039996000399960006
- Cells: 54

### h_ioi_v0_003
- Passed: False
- Evidence tier: `causal_tested_unstable`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=pass
- Failed checks: power_adequacy
- Treatment mean: 0.450597
- Cohen's d: 0.4083
- Confirmatory CI (bootstrap): [0.164365, 0.749319]
- Specificity ratio: 3.350298
- Control abs mean: 0.134495
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.298298
- Permutation p-value: 0.004199580041995801
- BH q-value: 0.005466
- Holm-adjusted p: 0.0081991800819918
- Cells: 54

### h_ioi_v0_mlp_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, baseline_superiority
- Treatment mean: 0.185798
- Cohen's d: 0.2159
- Confirmatory CI (bootstrap): [-0.021147, 0.439647]
- Specificity ratio: 1.676575
- Control abs mean: 0.110820
- Robustness (seed/prompt/resample): 0.000 / 0.333 / 0.000
- Method sensitivity std: 0.269603
- Permutation p-value: 0.11998800119988001
- BH q-value: 0.117588
- Holm-adjusted p: 0.11758824117588242
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
