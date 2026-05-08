# Stage-Gate Report

- Protocol: `multilane_B_sentiment_v0_gpt2-small`
- Protocol hash: `d7dd9f6e2e888f1dcc4ae492db807bb6533e5a0a5d15d4b7c872a0a0d5c79285`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.1111

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_neuron_sentiment_v0_001 | ❌ FAIL | `rejected` | -0.686 | 22.607 | 0.0000 |
| h_neuron_sentiment_v0_002 | ❌ FAIL | `rejected` | -0.706 | 5.121 | 0.0000 |
| h_neuron_sentiment_v0_003 | ❌ FAIL | `rejected` | -0.772 | 16.528 | 0.0000 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_neuron_sentiment_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness
- Treatment mean: -0.033892
- Cohen's d: -0.6859
- Confirmatory CI (bootstrap): [-0.048566, -0.022303]
- Specificity ratio: 22.606755
- Control abs mean: 0.001499
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.047621
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 54

### h_neuron_sentiment_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness
- Treatment mean: -0.004101
- Cohen's d: -0.7055
- Confirmatory CI (bootstrap): [-0.005720, -0.002690]
- Specificity ratio: 5.120704
- Control abs mean: 0.000801
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.005745
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_sentiment_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness
- Treatment mean: -0.022785
- Cohen's d: -0.7720
- Confirmatory CI (bootstrap): [-0.031169, -0.015374]
- Specificity ratio: 16.527991
- Control abs mean: 0.001379
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.028806
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 54
