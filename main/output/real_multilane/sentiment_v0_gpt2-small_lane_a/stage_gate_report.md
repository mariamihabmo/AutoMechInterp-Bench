# Stage-Gate Report

- Protocol: `multilane_A_sentiment_v0_gpt2-small`
- Protocol hash: `cb33e5ffb799ef1922a40a02e8d6c455b8d3fd4e14c3a150f9a924954815ee2d`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sweep_sentiment_v0_001 | ❌ FAIL | `rejected` | 0.583 | 2.041 | 0.0000 |
| h_sweep_sentiment_v0_002 | ❌ FAIL | `rejected` | -0.661 | 1.579 | 0.0000 |
| h_sweep_sentiment_v0_003 | ❌ FAIL | `rejected` | 1.361 | 2.325 | 0.0000 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 3 | 100.0% |
| baseline_superiority | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_sweep_sentiment_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls
- Treatment mean: 0.106517
- Cohen's d: 0.5833
- Confirmatory CI (bootstrap): [0.062053, 0.157627]
- Specificity ratio: 2.040888
- Control abs mean: 0.052191
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.180544
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_sweep_sentiment_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, baseline_superiority
- Treatment mean: -0.065073
- Cohen's d: -0.6615
- Confirmatory CI (bootstrap): [-0.092543, -0.040731]
- Specificity ratio: 1.579055
- Control abs mean: 0.041210
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.096851
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_sweep_sentiment_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls
- Treatment mean: 0.185340
- Cohen's d: 1.3610
- Confirmatory CI (bootstrap): [0.146437, 0.219417]
- Specificity ratio: 2.325358
- Control abs mean: 0.079704
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.133963
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
