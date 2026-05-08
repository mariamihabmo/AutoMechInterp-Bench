# Stage-Gate Report

- Protocol: `multilane_C_sentiment_v0_pythia-70m`
- Protocol hash: `0fc0cfa7e5d716a65b9de37d0965f1932e1b3c6679aeb723bdfa182e1294608d`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.5556
- Cross-model rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_dla_sentiment_v0_001 | ❌ FAIL | `rejected` | 0.534 | 1.615 | 0.0001 |
| h_dla_sentiment_v0_002 | ❌ FAIL | `rejected` | 0.848 | 4.630 | 0.0001 |
| h_dla_sentiment_v0_003 | ❌ FAIL | `rejected` | -0.257 | 0.087 | 0.0646 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| baseline_superiority | 2 | 66.7% |
| negative_controls | 2 | 66.7% |
| power_adequacy | 2 | 66.7% |
| cross_model_transfer | 2 | 66.7% |
| confirmatory_ci | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_dla_sentiment_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: baseline_superiority, causal_effect, negative_controls, power_adequacy, robustness
- Treatment mean: 0.030972
- Cohen's d: 0.5337
- Confirmatory CI (bootstrap): [0.017145, 0.047930]
- Specificity ratio: 1.615316
- Control abs mean: 0.019174
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.043613
- Permutation p-value: 0.00019998000199980003
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_dla_sentiment_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, cross_model_transfer
- Treatment mean: 0.187630
- Cohen's d: 0.8481
- Confirmatory CI (bootstrap): [0.133990, 0.251366]
- Specificity ratio: 4.630010
- Control abs mean: 0.040525
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.215651
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_sentiment_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: baseline_superiority, causal_effect, confirmatory_ci, negative_controls, power_adequacy, robustness, cross_model_transfer
- Treatment mean: -0.004395
- Cohen's d: -0.2566
- Confirmatory CI (bootstrap): [-0.008857, 0.000105]
- Specificity ratio: 0.087188
- Control abs mean: 0.050412
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.005428
- Permutation p-value: 0.0663933606639336
- BH q-value: 0.064594
- Holm-adjusted p: 0.06459354064593541
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
