# Stage-Gate Report

- Protocol: `multilane_C_country_capital_v0_pythia-70m_prompt_variant_repair_v1_prompt_holdout_high_power_n40`
- Protocol hash: `c0ab4ff01a2bc636c0ace2265ebe4eefb268bd88747a9f1d2cc053b0a682ed37`
- Hypotheses: 3
- Accepted: 2
- Unstable: 0
- Rejected: 1
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_dla_country_capital_v0_001 | ✅ PASS | `single_model_confirmed` | 2.230 | 11.039 | 0.0001 |
| h_dla_country_capital_v0_002 | ✅ PASS | `single_model_confirmed` | 2.162 | 9.922 | 0.0001 |
| h_dla_country_capital_v0_003 | ❌ FAIL | `rejected` | 0.419 | 0.266 | 0.0025 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 1 | 33.3% |
| negative_controls | 1 | 33.3% |
| robustness | 1 | 33.3% |
| power_adequacy | 1 | 33.3% |
| baseline_superiority | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 2 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_dla_country_capital_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 1.349954
- Cohen's d: 2.2303
- Confirmatory CI (bootstrap): [1.205024, 1.526535]
- Specificity ratio: 11.038796
- Control abs mean: 0.122292
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.572426
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 1.129877
- Cohen's d: 2.1621
- Confirmatory CI (bootstrap): [1.000982, 1.282554]
- Specificity ratio: 9.922217
- Control abs mean: 0.113873
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.504276
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_country_capital_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, power_adequacy, baseline_superiority
- Treatment mean: 0.012181
- Cohen's d: 0.4189
- Confirmatory CI (bootstrap): [0.004187, 0.019607]
- Specificity ratio: 0.266264
- Control abs mean: 0.045746
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.004238
- Permutation p-value: 0.0030996900309969004
- BH q-value: 0.002500
- Holm-adjusted p: 0.0024997500249975004
- Cells: 54
