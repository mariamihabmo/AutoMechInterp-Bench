# Stage-Gate Report

- Protocol: `real_gendered_pronoun_v0_gpt2-small`
- Protocol hash: `576292ef00e7ff406c388f76f0cfb86677e58efc84aea347761ef7c6dfb90be8`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 0.3333
- Cross-model rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_gendered_pronoun_v0_001 | ❌ FAIL | `rejected` | -0.857 | 339.982 | 0.5033 |
| h_gendered_pronoun_v0_002 | ❌ FAIL | `rejected` | -0.418 | 3.751 | 0.5033 |
| h_gendered_pronoun_v0_003 | ❌ FAIL | `rejected` | -0.662 | 14.071 | 0.5033 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| method_sensitivity | 3 | 100.0% |
| confirmatory_ci | 3 | 100.0% |
| multiplicity | 3 | 100.0% |
| cross_model_transfer | 3 | 100.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_gendered_pronoun_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity, cross_model_transfer
- Treatment mean: -0.671634
- Cohen's d: -0.8570
- Confirmatory CI (bootstrap): [-1.357786, 0.007010]
- Specificity ratio: 339.981615
- Control abs mean: 0.001976
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.678644
- Permutation p-value: 0.49275072492750727
- BH q-value: 0.503350
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_gendered_pronoun_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity, cross_model_transfer
- Treatment mean: -0.354077
- Cohen's d: -0.4176
- Confirmatory CI (bootstrap): [-1.091254, 0.380095]
- Specificity ratio: 3.751107
- Control abs mean: 0.094393
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.734172
- Permutation p-value: 0.5065493450654934
- BH q-value: 0.503350
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_gendered_pronoun_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity, cross_model_transfer
- Treatment mean: -0.915241
- Cohen's d: -0.6617
- Confirmatory CI (bootstrap): [-2.122539, 0.282501]
- Specificity ratio: 14.071167
- Control abs mean: 0.065044
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 1.197741
- Permutation p-value: 0.5044495550444955
- BH q-value: 0.503350
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
