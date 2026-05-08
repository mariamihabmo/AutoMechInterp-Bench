# Stage-Gate Report

- Protocol: `multilane_C_sentiment_v0_pythia-70m_prompt_variant_repair_v1`
- Protocol hash: `a77fb6278106d20f2b73d3dde7519a1c8c9889c17633d2c5d4262287a64d46de`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.5556
- Cross-model rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_dla_sentiment_v0_001 | ❌ FAIL | `rejected` | 0.115 | 0.336 | 0.5944 |
| h_dla_sentiment_v0_002 | ❌ FAIL | `rejected` | 0.798 | 4.301 | 0.0003 |
| h_dla_sentiment_v0_003 | ❌ FAIL | `rejected` | -0.029 | 0.007 | 0.8328 |

## Failure Analysis

### Core gate failures

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| baseline_superiority | 2 | 66.7% |
| confirmatory_ci | 2 | 66.7% |
| effect_size_practical | 2 | 66.7% |
| multiplicity | 2 | 66.7% |
| negative_controls | 2 | 66.7% |
| power_adequacy | 2 | 66.7% |

### Optional transfer diagnostics (tier demotions, not core failures)

| Check | Demotion Count | Demotion Rate |
|---|---|---|
| cross_model_transfer | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_dla_sentiment_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: baseline_superiority, causal_effect, confirmatory_ci, effect_size_practical, multiplicity, negative_controls, power_adequacy, robustness
- Treatment mean: 0.010225
- Cohen's d: 0.1152
- Confirmatory CI (bootstrap): [-0.013620, 0.033466]
- Specificity ratio: 0.335926
- Control abs mean: 0.030439
- Robustness (seed/prompt/resample): 0.000 / 0.333 / 0.000
- Method sensitivity std: 0.010716
- Permutation p-value: 0.41025897410258977
- BH q-value: 0.594391
- Holm-adjusted p: 0.7925207479252074
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_dla_sentiment_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness
- Treatment mean: 0.156533
- Cohen's d: 0.7979
- Confirmatory CI (bootstrap): [0.110685, 0.214618]
- Specificity ratio: 4.301321
- Control abs mean: 0.036392
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.163173
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000300
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_dla_sentiment_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: baseline_superiority, causal_effect, confirmatory_ci, effect_size_practical, multiplicity, negative_controls, power_adequacy, robustness, cross_model_transfer
- Treatment mean: -0.000553
- Cohen's d: -0.0289
- Confirmatory CI (bootstrap): [-0.005317, 0.004850]
- Specificity ratio: 0.007316
- Control abs mean: 0.075586
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.003497
- Permutation p-value: 0.8427157284271573
- BH q-value: 0.832817
- Holm-adjusted p: 0.8328167183281672
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
