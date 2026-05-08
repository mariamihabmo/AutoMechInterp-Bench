# Stage-Gate Report

- Protocol: `multilane_C_docstring_v0_gpt2-small`
- Protocol hash: `204a1246e4bf07f8a31701e864cf70c26b0a74eb0fb85ee861d21d7cc08a9090`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.5556
- Cross-model rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_dla_docstring_v0_001 | ❌ FAIL | `rejected` | -0.560 | 0.962 | 0.0001 |
| h_dla_docstring_v0_002 | ❌ FAIL | `rejected` | 0.902 | 2.865 | 0.0001 |
| h_dla_docstring_v0_003 | ✅ PASS | `cross_model_confirmed` | 0.733 | 3.758 | 0.0001 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 2 | 66.7% |
| baseline_superiority | 1 | 33.3% |
| cross_model_transfer | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `cross_model_confirmed` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_dla_docstring_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, baseline_superiority, cross_model_transfer
- Treatment mean: -0.024797
- Cohen's d: -0.5599
- Confirmatory CI (bootstrap): [-0.039768, -0.015281]
- Specificity ratio: 0.961644
- Control abs mean: 0.025786
- Robustness (seed/prompt/resample): 0.833 / 0.667 / 1.000
- Method sensitivity std: 0.033464
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_dla_docstring_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls
- Treatment mean: 0.077726
- Cohen's d: 0.9023
- Confirmatory CI (bootstrap): [0.056806, 0.102296]
- Specificity ratio: 2.864945
- Control abs mean: 0.027130
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.078098
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_docstring_v0_003
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.385166
- Cohen's d: 0.7329
- Confirmatory CI (bootstrap): [0.257192, 0.534785]
- Specificity ratio: 3.758274
- Control abs mean: 0.102485
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.467575
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
