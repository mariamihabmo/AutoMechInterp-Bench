# Stage-Gate Report

- Protocol: `real_gendered_pronoun_v0_pythia-70m_confirmatory_repair_real`
- Protocol hash: `b00d9ec93026daf6ceabb9a31f24394d9b7f09bf57ebe1f93416c10d69bb57cd`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_gendered_pronoun_v0_001 | ❌ FAIL | `rejected` | -0.097 | 0.188 | 0.7405 |
| h_gendered_pronoun_v0_002 | ❌ FAIL | `rejected` | -0.152 | 0.624 | 0.7405 |
| h_gendered_pronoun_v0_003 | ❌ FAIL | `rejected` | -0.688 | 1.488 | 0.1722 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 3 | 100.0% |
| multiplicity | 3 | 100.0% |
| causal_effect | 2 | 66.7% |
| robustness | 2 | 66.7% |
| confirmatory_ci | 2 | 66.7% |
| method_sensitivity | 2 | 66.7% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_gendered_pronoun_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity
- Treatment mean: -0.014210
- Cohen's d: -0.0974
- Confirmatory CI (bootstrap): [-0.100848, 0.087838]
- Specificity ratio: 0.187630
- Control abs mean: 0.075734
- Robustness (seed/prompt/resample): 0.000 / 0.500 / 0.000
- Method sensitivity std: 0.011789
- Permutation p-value: 0.758024197580242
- BH q-value: 0.740526
- Holm-adjusted p: 1.0
- Cells: 8

### h_gendered_pronoun_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -0.190695
- Cohen's d: -0.1522
- Confirmatory CI (bootstrap): [-1.017801, 0.612498]
- Specificity ratio: 0.624225
- Control abs mean: 0.305490
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.315514
- Permutation p-value: 0.6913308669133087
- BH q-value: 0.740526
- Holm-adjusted p: 1.0
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_gendered_pronoun_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, method_sensitivity, multiplicity
- Treatment mean: -0.106591
- Cohen's d: -0.6876
- Confirmatory CI (bootstrap): [-0.238213, -0.023394]
- Specificity ratio: 1.488413
- Control abs mean: 0.071614
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.106574
- Permutation p-value: 0.0570942905709429
- BH q-value: 0.172183
- Holm-adjusted p: 0.17218278172182783
- Cells: 8
