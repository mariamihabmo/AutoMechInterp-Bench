# Stage-Gate Report

- Protocol: `multilane_A_ioi_v0_gpt2-small`
- Protocol hash: `db42026176f8853fc7eb81c84a14845713e63666155c6ace51df25136d8976e2`
- Hypotheses: 3
- Accepted: 2
- Unstable: 0
- Rejected: 1
- All pass: False
- Cross-method rank τ: 1.0000
- Cross-model rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sweep_ioi_v0_001 | ✅ PASS | `single_model_confirmed` | -1.621 | 13.553 | 0.0001 |
| h_sweep_ioi_v0_002 | ❌ FAIL | `rejected` | 0.755 | 2.816 | 0.0001 |
| h_sweep_ioi_v0_003 | ✅ PASS | `single_model_confirmed` | 1.235 | 7.162 | 0.0001 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| cross_model_transfer | 3 | 100.0% |
| negative_controls | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 2 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_sweep_ioi_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: -2.018049
- Cohen's d: -1.6209
- Confirmatory CI (bootstrap): [-2.381839, -1.719435]
- Specificity ratio: 13.552630
- Control abs mean: 0.148905
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 1.003418
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_ioi_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, cross_model_transfer
- Treatment mean: 0.964069
- Cohen's d: 0.7550
- Confirmatory CI (bootstrap): [0.669786, 1.334687]
- Specificity ratio: 2.815713
- Control abs mean: 0.342389
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.882651
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_ioi_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 1.164454
- Cohen's d: 1.2353
- Confirmatory CI (bootstrap): [0.941739, 1.446882]
- Specificity ratio: 7.161537
- Control abs mean: 0.162598
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.710836
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
