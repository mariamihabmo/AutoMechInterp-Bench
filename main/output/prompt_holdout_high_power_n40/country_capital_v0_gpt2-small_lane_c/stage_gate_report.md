# Stage-Gate Report

- Protocol: `multilane_C_country_capital_v0_gpt2-small_prompt_variant_repair_v1_prompt_holdout_high_power_n40`
- Protocol hash: `a224e4357718716eed4a2827dde2e53fab6ea5e37d9b9d742c25dec2cb3d92e5`
- Hypotheses: 3
- Accepted: 3
- Unstable: 0
- Rejected: 0
- All pass: True
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_dla_country_capital_v0_001 | ✅ PASS | `single_model_confirmed` | 1.443 | 13.365 | 0.0001 |
| h_dla_country_capital_v0_002 | ✅ PASS | `single_model_confirmed` | 2.309 | 10.446 | 0.0001 |
| h_dla_country_capital_v0_003 | ✅ PASS | `single_model_confirmed` | 1.288 | 8.181 | 0.0001 |

## Failure Analysis

No failures detected.

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 3 |

## Per-Hypothesis Details

### h_dla_country_capital_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 2.250408
- Cohen's d: 1.4432
- Confirmatory CI (bootstrap): [1.867725, 2.698265]
- Specificity ratio: 13.364543
- Control abs mean: 0.168386
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 1.463710
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.777305
- Cohen's d: 2.3089
- Confirmatory CI (bootstrap): [0.692687, 0.875981]
- Specificity ratio: 10.446434
- Control abs mean: 0.074409
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.315450
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 1.407819
- Cohen's d: 1.2881
- Confirmatory CI (bootstrap): [1.153375, 1.734494]
- Specificity ratio: 8.181442
- Control abs mean: 0.172075
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.810757
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
