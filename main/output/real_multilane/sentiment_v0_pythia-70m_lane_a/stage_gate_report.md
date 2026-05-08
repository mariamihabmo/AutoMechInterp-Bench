# Stage-Gate Report

- Protocol: `multilane_A_sentiment_v0_pythia-70m`
- Protocol hash: `4f3316f25d7d56184805a779137623057db9ed7e58a35f9ab7318f9783bc1dcc`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.1111

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sweep_sentiment_v0_001 | ❌ FAIL | `rejected` | 1.042 | 4.356 | 0.0000 |
| h_sweep_sentiment_v0_002 | ❌ FAIL | `rejected` | 0.914 | 2.475 | 0.0000 |
| h_sweep_sentiment_v0_003 | ❌ FAIL | `rejected` | 0.858 | 0.790 | 0.0000 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 3 | 100.0% |
| baseline_superiority | 2 | 66.7% |

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
- Treatment mean: 0.427840
- Cohen's d: 1.0420
- Confirmatory CI (bootstrap): [0.319685, 0.535409]
- Specificity ratio: 4.355565
- Control abs mean: 0.098228
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.404260
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
- Treatment mean: 0.070271
- Cohen's d: 0.9143
- Confirmatory CI (bootstrap): [0.051822, 0.093001]
- Specificity ratio: 2.475474
- Control abs mean: 0.028387
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.060595
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 54

### h_sweep_sentiment_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=fail, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, baseline_superiority
- Treatment mean: 0.034892
- Cohen's d: 0.8581
- Confirmatory CI (bootstrap): [0.025016, 0.046477]
- Specificity ratio: 0.790182
- Control abs mean: 0.044157
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.039975
- Permutation p-value: 0.0
- BH q-value: 0.000000
- Holm-adjusted p: 0.0
- Cells: 54
