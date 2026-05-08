# Stage-Gate Report

- Protocol: `multilane_A_country_capital_v0_pythia-70m_prompt_variant_repair_v1`
- Protocol hash: `21b01fd828921efd8238f685234cab4d2d8d34360660325da1006432c10fd75d`
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
| h_sweep_country_capital_v0_001 | ✅ PASS | `cross_model_confirmed` | 2.063 | 7.841 | 0.0001 |
| h_sweep_country_capital_v0_002 | ✅ PASS | `cross_model_confirmed` | 2.008 | 9.143 | 0.0001 |
| h_sweep_country_capital_v0_003 | ❌ FAIL | `rejected` | 1.192 | 3.367 | 0.0001 |

## Failure Analysis

### Core gate failures

| Check | Failure Count | Failure Rate |
|---|---|---|
| baseline_superiority | 1 | 33.3% |
| negative_controls | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `cross_model_confirmed` | 2 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_sweep_country_capital_v0_001
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 1.325028
- Cohen's d: 2.0631
- Confirmatory CI (bootstrap): [1.167068, 1.505085]
- Specificity ratio: 7.841459
- Control abs mean: 0.168977
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.618402
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_country_capital_v0_002
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 1.115357
- Cohen's d: 2.0081
- Confirmatory CI (bootstrap): [0.978552, 1.274036]
- Specificity ratio: 9.142739
- Control abs mean: 0.121994
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.538994
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_country_capital_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: baseline_superiority, negative_controls
- Treatment mean: 0.232868
- Cohen's d: 1.1917
- Confirmatory CI (bootstrap): [0.185016, 0.288612]
- Specificity ratio: 3.367370
- Control abs mean: 0.069154
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.123375
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
