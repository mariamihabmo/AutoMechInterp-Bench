# Stage-Gate Report

- Protocol: `multilane_B_sentiment_v0_pythia-70m`
- Protocol hash: `d12f26cfda1188987f14484d76e035bfc1af568a2ebf656c97fe47593cd5c20a`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_neuron_sentiment_v0_001 | ❌ FAIL | `rejected` | -0.798 | 43.769 | 0.0000 |
| h_neuron_sentiment_v0_002 | ❌ FAIL | `rejected` | 0.483 | 2.013 | 0.0005 |
| h_neuron_sentiment_v0_003 | ❌ FAIL | `rejected` | 0.595 | 0.675 | 0.0000 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| baseline_superiority | 2 | 66.7% |
| power_adequacy | 1 | 33.3% |
| negative_controls | 1 | 33.3% |

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
- Treatment mean: -0.157450
- Cohen's d: -0.7980
- Confirmatory CI (bootstrap): [-0.214820, -0.110474]
- Specificity ratio: 43.769498
- Control abs mean: 0.003597
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.195444
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_sentiment_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, power_adequacy, baseline_superiority
- Treatment mean: 0.001187
- Cohen's d: 0.4833
- Confirmatory CI (bootstrap): [0.000551, 0.001859]
- Specificity ratio: 2.012911
- Control abs mean: 0.000590
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.001883
- Permutation p-value: 0.0004
- BH q-value: 0.000500
- Holm-adjusted p: 0.0005
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_sentiment_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, baseline_superiority
- Treatment mean: 0.000730
- Cohen's d: 0.5948
- Confirmatory CI (bootstrap): [0.000401, 0.001058]
- Specificity ratio: 0.675056
- Control abs mean: 0.001082
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.000836
- Permutation p-value: 0.0001
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
