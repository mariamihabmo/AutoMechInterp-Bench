# Stage-Gate Report

- Protocol: `real_arithmetic_v0_pythia-70m_confirmatory_repair_real`
- Protocol hash: `7c9783e8c53e407ade66bba55237188618367d26a5bb55a86fdaec9e86a4485c`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_arithmetic_v0_001 | ❌ FAIL | `rejected` | 0.946 | 1.763 | 0.0258 |
| h_arithmetic_v0_002 | ❌ FAIL | `rejected` | -0.080 | 0.727 | 0.9439 |
| h_arithmetic_v0_003 | ❌ FAIL | `rejected` | 0.038 | 0.102 | 0.9439 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 3 | 100.0% |
| causal_effect | 2 | 66.7% |
| robustness | 2 | 66.7% |
| confirmatory_ci | 2 | 66.7% |
| multiplicity | 2 | 66.7% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_arithmetic_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls
- Treatment mean: 0.044024
- Cohen's d: 0.9455
- Confirmatory CI (bootstrap): [0.019802, 0.082960]
- Specificity ratio: 1.763279
- Control abs mean: 0.024967
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.028161
- Permutation p-value: 0.008899110088991101
- BH q-value: 0.025797
- Holm-adjusted p: 0.025797420257974206
- Cells: 8

### h_arithmetic_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity
- Treatment mean: -0.005703
- Cohen's d: -0.0805
- Confirmatory CI (bootstrap): [-0.056637, 0.035004]
- Specificity ratio: 0.727307
- Control abs mean: 0.007842
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.035901
- Permutation p-value: 0.791920807919208
- BH q-value: 0.943906
- Holm-adjusted p: 1.0
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_arithmetic_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity
- Treatment mean: 0.001444
- Cohen's d: 0.0379
- Confirmatory CI (bootstrap): [-0.039797, 0.017510]
- Specificity ratio: 0.101965
- Control abs mean: 0.014166
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.011833
- Permutation p-value: 0.9434056594340566
- BH q-value: 0.943906
- Holm-adjusted p: 1.0
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
