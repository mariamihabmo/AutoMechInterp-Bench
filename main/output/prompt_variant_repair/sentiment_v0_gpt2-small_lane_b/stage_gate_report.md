# Stage-Gate Report

- Protocol: `multilane_B_sentiment_v0_gpt2-small_prompt_variant_repair_v1`
- Protocol hash: `050d9a521fac641002f740fe1c184e926df240a9576e5bd2464f63981a3be050`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.1111

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_neuron_sentiment_v0_001 | ❌ FAIL | `rejected` | -0.645 | 24.786 | 0.0001 |
| h_neuron_sentiment_v0_002 | ❌ FAIL | `rejected` | -0.535 | 10.284 | 0.0001 |
| h_neuron_sentiment_v0_003 | ❌ FAIL | `rejected` | -0.170 | 6.987 | 0.2155 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| power_adequacy | 2 | 66.7% |
| confirmatory_ci | 1 | 33.3% |
| multiplicity | 1 | 33.3% |
| effect_size_practical | 1 | 33.3% |

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
- Treatment mean: -0.039069
- Cohen's d: -0.6451
- Confirmatory CI (bootstrap): [-0.057724, -0.025195]
- Specificity ratio: 24.785719
- Control abs mean: 0.001576
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.054997
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_neuron_sentiment_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, power_adequacy
- Treatment mean: -0.008652
- Cohen's d: -0.5351
- Confirmatory CI (bootstrap): [-0.013691, -0.004966]
- Specificity ratio: 10.283891
- Control abs mean: 0.000841
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.013199
- Permutation p-value: 0.00019998000199980003
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_neuron_sentiment_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=fail, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=fail, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, confirmatory_ci, multiplicity, power_adequacy, effect_size_practical
- Treatment mean: -0.007843
- Cohen's d: -0.1696
- Confirmatory CI (bootstrap): [-0.019751, 0.004871]
- Specificity ratio: 6.986561
- Control abs mean: 0.001123
- Robustness (seed/prompt/resample): 0.000 / 0.333 / 0.000
- Method sensitivity std: 0.009664
- Permutation p-value: 0.2151784821517848
- BH q-value: 0.215478
- Holm-adjusted p: 0.21547845215478453
- Cells: 54
