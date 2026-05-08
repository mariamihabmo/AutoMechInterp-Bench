# Stage-Gate Report

- Protocol: `multilane_C_ioi_v0_gpt2-small_prompt_variant_repair_v1_prompt_holdout_high_power_n40`
- Protocol hash: `5778bb71d4759cb891f1f5a3c882e8bc7a3233865ee0372fa0a2b87eae022a1d`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.5556

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_dla_ioi_v0_001 | ❌ FAIL | `rejected` | 0.220 | 1.947 | 0.1160 |
| h_dla_ioi_v0_002 | ✅ PASS | `single_model_confirmed` | -0.608 | 11.448 | 0.0006 |
| h_dla_ioi_v0_003 | ❌ FAIL | `rejected` | -0.335 | 0.901 | 0.0264 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 2 | 66.7% |
| robustness | 2 | 66.7% |
| power_adequacy | 2 | 66.7% |
| baseline_superiority | 2 | 66.7% |
| confirmatory_ci | 1 | 33.3% |
| multiplicity | 1 | 33.3% |
| causal_effect | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_dla_ioi_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, baseline_superiority
- Treatment mean: 0.175735
- Cohen's d: 0.2203
- Confirmatory CI (bootstrap): [-0.006943, 0.423382]
- Specificity ratio: 1.947252
- Control abs mean: 0.090248
- Robustness (seed/prompt/resample): 1.000 / 0.333 / 1.000
- Method sensitivity std: 0.395471
- Permutation p-value: 0.11038896110388961
- BH q-value: 0.115988
- Holm-adjusted p: 0.11598840115988401
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_dla_ioi_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: -1.014627
- Cohen's d: -0.6079
- Confirmatory CI (bootstrap): [-1.462945, -0.587326]
- Specificity ratio: 11.448276
- Control abs mean: 0.088627
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.439960
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000600
- Holm-adjusted p: 0.0005999400059994001
- Cells: 54

### h_dla_ioi_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, power_adequacy, baseline_superiority
- Treatment mean: -0.132168
- Cohen's d: -0.3351
- Confirmatory CI (bootstrap): [-0.231936, -0.021130]
- Specificity ratio: 0.901273
- Control abs mean: 0.146645
- Robustness (seed/prompt/resample): 0.000 / 0.333 / 0.000
- Method sensitivity std: 0.065032
- Permutation p-value: 0.0168983101689831
- BH q-value: 0.026397
- Holm-adjusted p: 0.03519648035196481
- Cells: 54
