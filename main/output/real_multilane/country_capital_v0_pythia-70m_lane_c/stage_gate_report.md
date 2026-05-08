# Stage-Gate Report

- Protocol: `multilane_C_country_capital_v0_pythia-70m`
- Protocol hash: `e63c56024a53e7086afdc1bd9d2af218bfd56e76615058a2787e7ccacba3319c`
- Hypotheses: 3
- Accepted: 2
- Unstable: 0
- Rejected: 1
- All pass: False
- Cross-method rank τ: 1.0000
- Cross-model rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_dla_country_capital_v0_001 | ✅ PASS | `cross_model_confirmed` | 1.604 | 8.767 | 0.0001 |
| h_dla_country_capital_v0_002 | ✅ PASS | `cross_model_confirmed` | 1.513 | 8.256 | 0.0001 |
| h_dla_country_capital_v0_003 | ❌ FAIL | `rejected` | 0.544 | 0.482 | 0.0001 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| baseline_superiority | 1 | 33.3% |
| causal_effect | 1 | 33.3% |
| negative_controls | 1 | 33.3% |
| robustness | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `cross_model_confirmed` | 2 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_dla_country_capital_v0_001
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 1.311132
- Cohen's d: 1.6039
- Confirmatory CI (bootstrap): [1.112652, 1.546711]
- Specificity ratio: 8.767236
- Control abs mean: 0.149549
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.736840
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_002
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 1.106588
- Cohen's d: 1.5126
- Confirmatory CI (bootstrap): [0.927813, 1.315696]
- Specificity ratio: 8.255896
- Control abs mean: 0.134036
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.672251
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: baseline_superiority, causal_effect, negative_controls, robustness
- Treatment mean: 0.025108
- Cohen's d: 0.5436
- Confirmatory CI (bootstrap): [0.013525, 0.037799]
- Specificity ratio: 0.481847
- Control abs mean: 0.052109
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.013578
- Permutation p-value: 0.00019998000199980003
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
