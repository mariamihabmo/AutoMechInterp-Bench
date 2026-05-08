# Stage-Gate Report

- Protocol: `real_gendered_pronoun_v0_gpt2-small_confirmatory_repair_real_prompt_holdout_high_power_n40`
- Protocol hash: `10790fd0bfe882960dff56475ae7a30d57cc1648ad40dde64dc8e94e5187b018`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_gendered_pronoun_v0_001 | ❌ FAIL | `rejected` | -0.533 | 2.244 | 0.2602 |
| h_gendered_pronoun_v0_002 | ✅ PASS | `single_model_confirmed` | 1.232 | 3.979 | 0.0948 |
| h_gendered_pronoun_v0_003 | ❌ FAIL | `rejected` | -0.792 | 6.366 | 0.1302 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 2 | 66.7% |
| robustness | 2 | 66.7% |
| multiplicity | 2 | 66.7% |
| confirmatory_ci | 1 | 33.3% |
| method_sensitivity | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_gendered_pronoun_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, confirmatory_ci, multiplicity
- Treatment mean: -0.024610
- Cohen's d: -0.5327
- Confirmatory CI (bootstrap): [-0.063091, 0.000243]
- Specificity ratio: 2.243875
- Control abs mean: 0.010968
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.024197
- Permutation p-value: 0.25447455254474555
- BH q-value: 0.260174
- Holm-adjusted p: 0.26017398260173985
- Cells: 8

### h_gendered_pronoun_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.201134
- Cohen's d: 1.2319
- Confirmatory CI (bootstrap): [0.079646, 0.296333]
- Specificity ratio: 3.979365
- Control abs mean: 0.050544
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.031247
- Permutation p-value: 0.0337966203379662
- BH q-value: 0.094791
- Holm-adjusted p: 0.09479052094790522
- Cells: 8

### h_gendered_pronoun_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, multiplicity
- Treatment mean: -0.341160
- Cohen's d: -0.7918
- Confirmatory CI (bootstrap): [-0.607322, -0.044474]
- Specificity ratio: 6.366200
- Control abs mean: 0.053589
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.374948
- Permutation p-value: 0.0903909609039096
- BH q-value: 0.130187
- Holm-adjusted p: 0.1735826417358264
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
