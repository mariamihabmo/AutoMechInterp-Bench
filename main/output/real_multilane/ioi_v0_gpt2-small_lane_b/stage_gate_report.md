# Stage-Gate Report

- Protocol: `multilane_B_ioi_v0_gpt2-small`
- Protocol hash: `0dcd410cda8fd60528ea4c0b30eafbd6977a6ecabb0d926649d2d656d9aa24ac`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: -0.3333
- Cross-model rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_neuron_ioi_v0_001 | ❌ FAIL | `rejected` | -0.485 | 18.613 | 0.0010 |
| h_neuron_ioi_v0_002 | ✅ PASS | `single_model_confirmed` | 0.598 | 18.826 | 0.0003 |
| h_neuron_ioi_v0_003 | ❌ FAIL | `rejected` | 0.146 | 8.190 | 0.2959 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| cross_model_transfer | 3 | 100.0% |
| causal_effect | 2 | 66.7% |
| robustness | 2 | 66.7% |
| power_adequacy | 2 | 66.7% |
| confirmatory_ci | 1 | 33.3% |
| multiplicity | 1 | 33.3% |
| effect_size_practical | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_neuron_ioi_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, power_adequacy, cross_model_transfer
- Treatment mean: -0.040805
- Cohen's d: -0.4849
- Confirmatory CI (bootstrap): [-0.065193, -0.020997]
- Specificity ratio: 18.613382
- Control abs mean: 0.002192
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.075951
- Permutation p-value: 0.0007999200079992001
- BH q-value: 0.001050
- Holm-adjusted p: 0.0013998600139986002
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_ioi_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.032183
- Cohen's d: 0.5984
- Confirmatory CI (bootstrap): [0.019742, 0.048916]
- Specificity ratio: 18.825648
- Control abs mean: 0.001710
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.039247
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000300
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_neuron_ioi_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical, cross_model_transfer
- Treatment mean: 0.007760
- Cohen's d: 0.1465
- Confirmatory CI (bootstrap): [-0.006276, 0.021810]
- Specificity ratio: 8.190185
- Control abs mean: 0.000948
- Robustness (seed/prompt/resample): 0.167 / 0.333 / 0.000
- Method sensitivity std: 0.010965
- Permutation p-value: 0.28987101289871015
- BH q-value: 0.295870
- Holm-adjusted p: 0.29587041295870414
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
