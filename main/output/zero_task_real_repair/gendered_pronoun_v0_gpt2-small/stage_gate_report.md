# Stage-Gate Report

- Protocol: `real_gendered_pronoun_v0_gpt2-small_confirmatory_repair_real`
- Protocol hash: `b976424f281592d198ea7318295910976e85abe96a232ebe9f9ae0f912dc4aa0`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.3333
- Cross-model rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_gendered_pronoun_v0_001 | ❌ FAIL | `rejected` | -0.525 | 2.263 | 0.2602 |
| h_gendered_pronoun_v0_002 | ✅ PASS | `single_model_confirmed` | 1.198 | 3.967 | 0.0948 |
| h_gendered_pronoun_v0_003 | ❌ FAIL | `rejected` | -0.763 | 6.153 | 0.1302 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| cross_model_transfer | 3 | 100.0% |
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
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, confirmatory_ci, multiplicity, cross_model_transfer
- Treatment mean: -0.025144
- Cohen's d: -0.5247
- Confirmatory CI (bootstrap): [-0.065141, 0.000659]
- Specificity ratio: 2.263213
- Control abs mean: 0.011110
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.024857
- Permutation p-value: 0.25447455254474555
- BH q-value: 0.260174
- Holm-adjusted p: 0.26017398260173985
- Cells: 8

### h_gendered_pronoun_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.206248
- Cohen's d: 1.1983
- Confirmatory CI (bootstrap): [0.074012, 0.303691]
- Specificity ratio: 3.966760
- Control abs mean: 0.051994
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.039345
- Permutation p-value: 0.0337966203379662
- BH q-value: 0.094791
- Holm-adjusted p: 0.09479052094790522
- Cells: 8

### h_gendered_pronoun_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, multiplicity, cross_model_transfer
- Treatment mean: -0.332893
- Cohen's d: -0.7634
- Confirmatory CI (bootstrap): [-0.595975, -0.028071]
- Specificity ratio: 6.152593
- Control abs mean: 0.054106
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.378354
- Permutation p-value: 0.0903909609039096
- BH q-value: 0.130187
- Holm-adjusted p: 0.1735826417358264
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
