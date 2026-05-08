# Stage-Gate Report

- Protocol: `multilane_A_sentiment_v0_gpt2-small_prompt_variant_repair_v1`
- Protocol hash: `7c971406eddc439dc68206125970824197109643cb10d55d327a2a6319df0de2`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sweep_sentiment_v0_001 | ❌ FAIL | `rejected` | 0.465 | 2.102 | 0.0003 |
| h_sweep_sentiment_v0_002 | ❌ FAIL | `rejected` | -0.441 | 0.705 | 0.0009 |
| h_sweep_sentiment_v0_003 | ❌ FAIL | `rejected` | 0.716 | 2.370 | 0.0003 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 3 | 100.0% |
| power_adequacy | 2 | 66.7% |
| baseline_superiority | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_sweep_sentiment_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, power_adequacy
- Treatment mean: 0.054921
- Cohen's d: 0.4649
- Confirmatory CI (bootstrap): [0.028836, 0.093232]
- Specificity ratio: 2.102296
- Control abs mean: 0.026124
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.083705
- Permutation p-value: 0.0004999500049995
- BH q-value: 0.000300
- Holm-adjusted p: 0.00039996000399960006
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_sweep_sentiment_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, power_adequacy, baseline_superiority
- Treatment mean: -0.036019
- Cohen's d: -0.4408
- Confirmatory CI (bootstrap): [-0.059640, -0.016012]
- Specificity ratio: 0.705017
- Control abs mean: 0.051089
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.071770
- Permutation p-value: 0.001999800019998
- BH q-value: 0.000900
- Holm-adjusted p: 0.0008999100089991
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_sweep_sentiment_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls
- Treatment mean: 0.275487
- Cohen's d: 0.7156
- Confirmatory CI (bootstrap): [0.190978, 0.401774]
- Specificity ratio: 2.369830
- Control abs mean: 0.116247
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.266292
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000300
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
