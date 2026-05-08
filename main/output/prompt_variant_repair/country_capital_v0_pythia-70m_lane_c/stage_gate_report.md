# Stage-Gate Report

- Protocol: `multilane_C_country_capital_v0_pythia-70m_prompt_variant_repair_v1`
- Protocol hash: `1b43ac89570af8ad30ab8b1ea2a91ac421a762070cd7b17763c968a4fb961d62`
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
| h_dla_country_capital_v0_001 | ✅ PASS | `cross_model_confirmed` | 2.209 | 10.722 | 0.0001 |
| h_dla_country_capital_v0_002 | ✅ PASS | `cross_model_confirmed` | 2.073 | 9.549 | 0.0001 |
| h_dla_country_capital_v0_003 | ❌ FAIL | `rejected` | 0.440 | 0.262 | 0.0014 |

## Failure Analysis

### Core gate failures

| Check | Failure Count | Failure Rate |
|---|---|---|
| baseline_superiority | 1 | 33.3% |
| causal_effect | 1 | 33.3% |
| negative_controls | 1 | 33.3% |
| power_adequacy | 1 | 33.3% |
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
- Treatment mean: 1.349543
- Cohen's d: 2.2092
- Confirmatory CI (bootstrap): [1.202096, 1.526945]
- Specificity ratio: 10.721964
- Control abs mean: 0.125867
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.577824
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_002
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 1.106858
- Cohen's d: 2.0734
- Confirmatory CI (bootstrap): [0.974185, 1.261750]
- Specificity ratio: 9.549441
- Control abs mean: 0.115908
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.517044
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: baseline_superiority, causal_effect, negative_controls, power_adequacy, robustness
- Treatment mean: 0.013148
- Cohen's d: 0.4398
- Confirmatory CI (bootstrap): [0.005170, 0.020971]
- Specificity ratio: 0.261927
- Control abs mean: 0.050198
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.005371
- Permutation p-value: 0.0022997700229977
- BH q-value: 0.001400
- Holm-adjusted p: 0.0013998600139986002
- Cells: 54
