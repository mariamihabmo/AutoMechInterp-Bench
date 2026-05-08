# Stage-Gate Report

- Protocol: `multilane_C_sentiment_v0_gpt2-small_prompt_variant_repair_v1`
- Protocol hash: `04bea5093cb2b82e2101ce02300472233dc515e6e8f82984793f0898459a6aaf`
- Hypotheses: 3
- Accepted: 2
- Unstable: 0
- Rejected: 1
- All pass: False
- Cross-method rank τ: -0.3333
- Cross-model rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_dla_sentiment_v0_001 | ✅ PASS | `single_model_confirmed` | 1.126 | 4.460 | 0.0001 |
| h_dla_sentiment_v0_002 | ❌ FAIL | `rejected` | -0.660 | 2.091 | 0.0001 |
| h_dla_sentiment_v0_003 | ✅ PASS | `cross_model_confirmed` | 0.864 | 3.027 | 0.0001 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| cross_model_transfer | 2 | 66.7% |
| negative_controls | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `cross_model_confirmed` | 1 |
| `single_model_confirmed` | 1 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_dla_sentiment_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.134172
- Cohen's d: 1.1265
- Confirmatory CI (bootstrap): [0.103517, 0.167547]
- Specificity ratio: 4.459873
- Control abs mean: 0.030084
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.095790
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_dla_sentiment_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, cross_model_transfer
- Treatment mean: -0.166566
- Cohen's d: -0.6596
- Confirmatory CI (bootstrap): [-0.243658, -0.107797]
- Specificity ratio: 2.091099
- Control abs mean: 0.079655
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.181397
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_dla_sentiment_v0_003
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.124186
- Cohen's d: 0.8640
- Confirmatory CI (bootstrap): [0.087827, 0.165150]
- Specificity ratio: 3.027418
- Control abs mean: 0.041020
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.090854
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000100
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
