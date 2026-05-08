# Stage-Gate Report

- Protocol: `multilane_C_ioi_v0_gpt2-small_prompt_variant_repair_v1`
- Protocol hash: `dd6a654732da5278e977efc4abd9d3fcf103a543e9c539540d96b0c3cac49d59`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 1.0000
- Cross-model rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_dla_ioi_v0_001 | ❌ FAIL | `rejected` | 0.211 | 1.820 | 0.1317 |
| h_dla_ioi_v0_002 | ✅ PASS | `single_model_confirmed` | -0.580 | 9.320 | 0.0009 |
| h_dla_ioi_v0_003 | ❌ FAIL | `rejected` | -0.302 | 0.811 | 0.0472 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 2 | 66.7% |
| robustness | 2 | 66.7% |
| power_adequacy | 2 | 66.7% |
| baseline_superiority | 2 | 66.7% |
| confirmatory_ci | 1 | 33.3% |
| multiplicity | 1 | 33.3% |
| cross_model_transfer | 1 | 33.3% |
| causal_effect | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_dla_ioi_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, baseline_superiority
- Treatment mean: 0.167825
- Cohen's d: 0.2109
- Confirmatory CI (bootstrap): [-0.015318, 0.412053]
- Specificity ratio: 1.819504
- Control abs mean: 0.092237
- Robustness (seed/prompt/resample): 1.000 / 0.333 / 1.000
- Method sensitivity std: 0.377070
- Permutation p-value: 0.12388761123887611
- BH q-value: 0.131687
- Holm-adjusted p: 0.1316868313168683
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_dla_ioi_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: -0.977653
- Cohen's d: -0.5797
- Confirmatory CI (bootstrap): [-1.430406, -0.545927]
- Specificity ratio: 9.319875
- Control abs mean: 0.104900
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.446816
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000900
- Holm-adjusted p: 0.0008999100089991002
- Cells: 54

### h_dla_ioi_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, power_adequacy, baseline_superiority
- Treatment mean: -0.121447
- Cohen's d: -0.3019
- Confirmatory CI (bootstrap): [-0.225720, -0.011077]
- Specificity ratio: 0.811080
- Control abs mean: 0.149735
- Robustness (seed/prompt/resample): 0.000 / 0.333 / 0.000
- Method sensitivity std: 0.083090
- Permutation p-value: 0.029397060293970604
- BH q-value: 0.047245
- Holm-adjusted p: 0.062993700629937
- Cells: 54
