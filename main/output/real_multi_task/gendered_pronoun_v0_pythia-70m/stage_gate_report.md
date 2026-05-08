# Stage-Gate Report

- Protocol: `real_gendered_pronoun_v0_pythia-70m`
- Protocol hash: `b7244a6c4101708ec76596c0947666e3c599063acadafb054bee5db92079f542`
- Hypotheses: 3
- Accepted: 0
- Unstable: 3
- Rejected: 0
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_gendered_pronoun_v0_001 | ❌ FAIL | `suggestive` | 0.761 | 6.507 | 0.5033 |
| h_gendered_pronoun_v0_002 | ❌ FAIL | `suggestive` | -5.500 | 3.613 | 0.3903 |
| h_gendered_pronoun_v0_003 | ❌ FAIL | `suggestive` | 0.749 | 13.572 | 0.5033 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| method_sensitivity | 3 | 100.0% |
| multiplicity | 3 | 100.0% |
| confirmatory_ci | 2 | 66.7% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `suggestive` | 3 |

## Per-Hypothesis Details

### h_gendered_pronoun_v0_001
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: 0.415308
- Cohen's d: 0.7609
- Confirmatory CI (bootstrap): [-0.058641, 0.867898]
- Specificity ratio: 6.506715
- Control abs mean: 0.063828
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.471897
- Permutation p-value: 0.49275072492750727
- BH q-value: 0.503350
- Holm-adjusted p: 0.7597240275972402
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_gendered_pronoun_v0_002
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, multiplicity
- Treatment mean: -0.976359
- Cohen's d: -5.5002
- Confirmatory CI (bootstrap): [-1.144608, -0.847078]
- Specificity ratio: 3.612792
- Control abs mean: 0.270250
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.083031
- Permutation p-value: 0.126987301269873
- BH q-value: 0.390261
- Holm-adjusted p: 0.3902609739026098
- Cells: 4

### h_gendered_pronoun_v0_003
- Passed: False
- Evidence tier: `suggestive`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: 0.193316
- Cohen's d: 0.7489
- Confirmatory CI (bootstrap): [-0.000129, 0.465970]
- Specificity ratio: 13.571933
- Control abs mean: 0.014244
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.193445
- Permutation p-value: 0.38316168383161686
- BH q-value: 0.503350
- Holm-adjusted p: 0.7597240275972402
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
