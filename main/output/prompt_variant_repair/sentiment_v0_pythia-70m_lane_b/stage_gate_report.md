# Stage-Gate Report

- Protocol: `multilane_B_sentiment_v0_pythia-70m_prompt_variant_repair_v1`
- Protocol hash: `1bd95f42aeacb7c34527cff4cca938cd50d70baa1443a428efd7752fedf0bd88`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_neuron_sentiment_v0_001 | ❌ FAIL | `rejected` | -0.765 | 41.926 | 0.0003 |
| h_neuron_sentiment_v0_002 | ❌ FAIL | `rejected` | 0.017 | 0.258 | 0.8356 |
| h_neuron_sentiment_v0_003 | ❌ FAIL | `rejected` | -0.010 | 0.235 | 0.8356 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| negative_controls | 2 | 66.7% |
| confirmatory_ci | 2 | 66.7% |
| multiplicity | 2 | 66.7% |
| power_adequacy | 2 | 66.7% |
| effect_size_practical | 2 | 66.7% |
| baseline_superiority | 2 | 66.7% |

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
- Treatment mean: -0.121901
- Cohen's d: -0.7654
- Confirmatory CI (bootstrap): [-0.168994, -0.084836]
- Specificity ratio: 41.926128
- Control abs mean: 0.002908
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.152789
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000300
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_sentiment_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical, baseline_superiority
- Treatment mean: 0.000422
- Cohen's d: 0.0173
- Confirmatory CI (bootstrap): [-0.006191, 0.006484]
- Specificity ratio: 0.258486
- Control abs mean: 0.001631
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.000357
- Permutation p-value: 0.7934206579342066
- BH q-value: 0.835616
- Holm-adjusted p: 1.0
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_sentiment_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, negative_controls, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical, baseline_superiority
- Treatment mean: -0.000193
- Cohen's d: -0.0103
- Confirmatory CI (bootstrap): [-0.005385, 0.004754]
- Specificity ratio: 0.235121
- Control abs mean: 0.000822
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.000523
- Permutation p-value: 0.8356164383561644
- BH q-value: 0.835616
- Holm-adjusted p: 1.0
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
