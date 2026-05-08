# Stage-Gate Report

- Protocol: `multilane_B3_ioi_v0_gpt2-small`
- Protocol hash: `0432713deeb78d69da02bbfb770cf7b95d2ff519954b28825dce4238e5093f0e`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sae_ioi_v0_001 | ❌ FAIL | `rejected` | 0.000 | 0.000 | 1.0000 |
| h_sae_ioi_v0_002 | ❌ FAIL | `rejected` | 0.000 | 0.000 | 1.0000 |
| h_sae_ioi_v0_003 | ❌ FAIL | `rejected` | 0.000 | 0.000 | 1.0000 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| negative_controls | 3 | 100.0% |
| robustness | 3 | 100.0% |
| confirmatory_ci | 3 | 100.0% |
| multiplicity | 3 | 100.0% |
| power_adequacy | 3 | 100.0% |
| effect_size_practical | 3 | 100.0% |
| baseline_superiority | 3 | 100.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_sae_ioi_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical, baseline_superiority
- Treatment mean: 0.000000
- Cohen's d: 0.0000
- Confirmatory CI (bootstrap): [0.000000, 0.000000]
- Specificity ratio: 0.000000
- Control abs mean: 0.000000
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.000000
- Permutation p-value: 1.0
- BH q-value: 1.000000
- Holm-adjusted p: 1.0
- Cells: 54

### h_sae_ioi_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical, baseline_superiority
- Treatment mean: 0.000000
- Cohen's d: 0.0000
- Confirmatory CI (bootstrap): [0.000000, 0.000000]
- Specificity ratio: 0.000000
- Control abs mean: 0.000000
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.000000
- Permutation p-value: 1.0
- BH q-value: 1.000000
- Holm-adjusted p: 1.0
- Cells: 54

### h_sae_ioi_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical, baseline_superiority
- Treatment mean: 0.000000
- Cohen's d: 0.0000
- Confirmatory CI (bootstrap): [0.000000, 0.000000]
- Specificity ratio: 0.000000
- Control abs mean: 0.000000
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.000000
- Permutation p-value: 1.0
- BH q-value: 1.000000
- Holm-adjusted p: 1.0
- Cells: 54
