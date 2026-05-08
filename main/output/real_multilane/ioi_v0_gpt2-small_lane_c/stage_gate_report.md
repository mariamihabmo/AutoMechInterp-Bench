# Stage-Gate Report

- Protocol: `multilane_C_ioi_v0_gpt2-small`
- Protocol hash: `202f6d10f223424c249417a39b957f56d8d61d6acfca7d956862411b50cdb126`
- Hypotheses: 3
- Accepted: 2
- Unstable: 0
- Rejected: 1
- All pass: False
- Cross-method rank τ: 1.0000
- Cross-model rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_dla_ioi_v0_001 | ✅ PASS | `single_model_confirmed` | 0.623 | 5.384 | 0.0001 |
| h_dla_ioi_v0_002 | ✅ PASS | `single_model_confirmed` | -1.662 | 19.277 | 0.0001 |
| h_dla_ioi_v0_003 | ❌ FAIL | `rejected` | -1.308 | 2.551 | 0.0001 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| cross_model_transfer | 3 | 100.0% |
| causal_effect | 1 | 33.3% |
| negative_controls | 1 | 33.3% |
| robustness | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 2 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_dla_ioi_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.579624
- Cohen's d: 0.6234
- Confirmatory CI (bootstrap): [0.357467, 0.845580]
- Specificity ratio: 5.384321
- Control abs mean: 0.107650
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.721266
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_dla_ioi_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: -2.021739
- Cohen's d: -1.6616
- Confirmatory CI (bootstrap): [-2.365313, -1.716014]
- Specificity ratio: 19.277368
- Control abs mean: 0.104876
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.955964
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_ioi_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, cross_model_transfer
- Treatment mean: -0.428066
- Cohen's d: -1.3081
- Confirmatory CI (bootstrap): [-0.518106, -0.346345]
- Specificity ratio: 2.551170
- Control abs mean: 0.167792
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.218098
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
