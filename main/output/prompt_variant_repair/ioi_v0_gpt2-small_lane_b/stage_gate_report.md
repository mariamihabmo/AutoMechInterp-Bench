# Stage-Gate Report

- Protocol: `multilane_B_ioi_v0_gpt2-small_prompt_variant_repair_v1`
- Protocol hash: `2b8d26952c7888cdccc6529bd24927556e6fd95f6b133be7bca0839d9e97a2cc`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.1111

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_neuron_ioi_v0_001 | ❌ FAIL | `rejected` | -0.145 | 5.630 | 0.4440 |
| h_neuron_ioi_v0_002 | ❌ FAIL | `rejected` | 0.068 | 3.665 | 0.6212 |
| h_neuron_ioi_v0_003 | ❌ FAIL | `rejected` | -0.300 | 13.101 | 0.0885 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| power_adequacy | 3 | 100.0% |
| confirmatory_ci | 2 | 66.7% |
| multiplicity | 2 | 66.7% |
| effect_size_practical | 2 | 66.7% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_neuron_ioi_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical
- Treatment mean: -0.012859
- Cohen's d: -0.1447
- Confirmatory CI (bootstrap): [-0.036731, 0.010015]
- Specificity ratio: 5.629865
- Control abs mean: 0.002284
- Robustness (seed/prompt/resample): 0.000 / 0.333 / 0.000
- Method sensitivity std: 0.027986
- Permutation p-value: 0.29527047295270475
- BH q-value: 0.443956
- Holm-adjusted p: 0.591940805919408
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_ioi_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical
- Treatment mean: 0.004018
- Cohen's d: 0.0684
- Confirmatory CI (bootstrap): [-0.011889, 0.018857]
- Specificity ratio: 3.665057
- Control abs mean: 0.001096
- Robustness (seed/prompt/resample): 0.000 / 0.333 / 0.000
- Method sensitivity std: 0.003926
- Permutation p-value: 0.6222377762223777
- BH q-value: 0.621238
- Holm-adjusted p: 0.6212378762123788
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_ioi_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, power_adequacy
- Treatment mean: -0.014259
- Cohen's d: -0.2996
- Confirmatory CI (bootstrap): [-0.030235, -0.003883]
- Specificity ratio: 13.101046
- Control abs mean: 0.001088
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.017665
- Permutation p-value: 0.028197180281971802
- BH q-value: 0.088491
- Holm-adjusted p: 0.08849115088491151
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
