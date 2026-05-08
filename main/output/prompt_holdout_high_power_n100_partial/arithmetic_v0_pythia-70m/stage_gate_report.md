# Stage-Gate Report

- Protocol: `real_arithmetic_v0_pythia-70m_confirmatory_repair_real_prompt_variant_repair_v1_prompt_holdout_high_power_n100`
- Protocol hash: `6ae22d6c7d63e3a1ce1bd3bd7f313d35a33ee69387fb3d4e6874c962be4c9b37`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_arithmetic_v0_001 | ❌ FAIL | `rejected` | -0.263 | 0.513 | 0.4840 |
| h_arithmetic_v0_002 | ✅ PASS | `single_model_confirmed` | 0.892 | 2.514 | 0.0414 |
| h_arithmetic_v0_003 | ❌ FAIL | `rejected` | 0.723 | 1.572 | 0.0414 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 2 | 66.7% |
| causal_effect | 1 | 33.3% |
| robustness | 1 | 33.3% |
| confirmatory_ci | 1 | 33.3% |
| multiplicity | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_arithmetic_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity
- Treatment mean: -0.008939
- Cohen's d: -0.2633
- Confirmatory CI (bootstrap): [-0.034550, 0.009753]
- Specificity ratio: 0.512893
- Control abs mean: 0.017428
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.015998
- Permutation p-value: 0.4884511548845116
- BH q-value: 0.483952
- Holm-adjusted p: 0.48395160483951605
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_arithmetic_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.043548
- Cohen's d: 0.8921
- Confirmatory CI (bootstrap): [0.015433, 0.079001]
- Specificity ratio: 2.513874
- Control abs mean: 0.017323
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.006422
- Permutation p-value: 0.021397860213978603
- BH q-value: 0.041396
- Holm-adjusted p: 0.065993400659934
- Cells: 8

### h_arithmetic_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls
- Treatment mean: 0.020643
- Cohen's d: 0.7234
- Confirmatory CI (bootstrap): [0.005430, 0.044229]
- Specificity ratio: 1.571571
- Control abs mean: 0.013135
- Robustness (seed/prompt/resample): 0.500 / 0.500 / 1.000
- Method sensitivity std: 0.016484
- Permutation p-value: 0.031796820317968204
- BH q-value: 0.041396
- Holm-adjusted p: 0.065993400659934
- Cells: 8
