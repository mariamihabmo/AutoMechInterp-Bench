# Stage-Gate Report

- Protocol: `real_sentiment_v0_gpt2-small`
- Protocol hash: `78e924e5e2324fb916299a3bd26a01f0417a269b5e21354423eb3517fa1e68a0`
- Hypotheses: 3
- Accepted: 0
- Unstable: 1
- Rejected: 2
- All pass: False
- Cross-method rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sentiment_v0_001 | ❌ FAIL | `rejected` | -0.670 | 12.523 | 0.4964 |
| h_sentiment_v0_002 | ❌ FAIL | `suggestive` | -1.000 | 22.636 | 0.3585 |
| h_sentiment_v0_003 | ❌ FAIL | `rejected` | -0.677 | 5.506 | 0.4964 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| method_sensitivity | 3 | 100.0% |
| multiplicity | 3 | 100.0% |
| causal_effect | 2 | 66.7% |
| robustness | 2 | 66.7% |
| confirmatory_ci | 2 | 66.7% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `suggestive` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_sentiment_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -1.229423
- Cohen's d: -0.6705
- Confirmatory CI (bootstrap): [-2.826987, 0.358501]
- Specificity ratio: 12.523128
- Control abs mean: 0.098172
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 1.587924
- Permutation p-value: 0.504049595040496
- BH q-value: 0.496350
- Holm-adjusted p: 0.9875012498750125
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_sentiment_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, multiplicity
- Treatment mean: -1.491935
- Cohen's d: -1.0004
- Confirmatory CI (bootstrap): [-2.791198, -0.200819]
- Specificity ratio: 22.636165
- Control abs mean: 0.065909
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 1.291452
- Permutation p-value: 0.12398760123987601
- BH q-value: 0.358464
- Holm-adjusted p: 0.35846415358464156
- Cells: 4

### h_sentiment_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -1.106022
- Cohen's d: -0.6768
- Confirmatory CI (bootstrap): [-2.531031, 0.306753]
- Specificity ratio: 5.506213
- Control abs mean: 0.200868
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 1.415247
- Permutation p-value: 0.49675032496750327
- BH q-value: 0.496350
- Holm-adjusted p: 0.9875012498750125
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
