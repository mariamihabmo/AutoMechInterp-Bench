# Stage-Gate Report

- Protocol: `multilane_A_ioi_v0_gpt2-small_prompt_variant_repair_v1_prompt_holdout_high_power_n40`
- Protocol hash: `a305fdeda0430b7db90532076e03da6d95ba2b3fe9d8b0320c711c4bea7d6d11`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.5556

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sweep_ioi_v0_001 | ✅ PASS | `single_model_confirmed` | -0.597 | 9.862 | 0.0001 |
| h_sweep_ioi_v0_002 | ❌ FAIL | `rejected` | 0.514 | 2.324 | 0.0001 |
| h_sweep_ioi_v0_003 | ❌ FAIL | `rejected` | 0.406 | 3.674 | 0.0034 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 2 | 66.7% |
| power_adequacy | 2 | 66.7% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_sweep_ioi_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: -0.985932
- Cohen's d: -0.5968
- Confirmatory CI (bootstrap): [-1.429901, -0.557140]
- Specificity ratio: 9.862285
- Control abs mean: 0.099970
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.451089
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_ioi_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, power_adequacy
- Treatment mean: 0.501695
- Cohen's d: 0.5139
- Confirmatory CI (bootstrap): [0.283726, 0.816111]
- Specificity ratio: 2.323841
- Control abs mean: 0.215891
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.444142
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_ioi_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, power_adequacy
- Treatment mean: 0.455069
- Cohen's d: 0.4063
- Confirmatory CI (bootstrap): [0.176721, 0.772918]
- Specificity ratio: 3.673611
- Control abs mean: 0.123875
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.305588
- Permutation p-value: 0.004199580041995801
- BH q-value: 0.003400
- Holm-adjusted p: 0.0033996600339966003
- Cells: 54
