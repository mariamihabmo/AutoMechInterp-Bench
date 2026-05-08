# Stage-Gate Report

- Protocol: `real_arithmetic_v0_pythia-70m_confirmatory_repair_real_prompt_variant_repair_v1`
- Protocol hash: `6211a685d3a08d362af377c042daeb55ae066d86dbd250a16dabd98f4dcb73c1`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.3333
- Cross-model rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_arithmetic_v0_001 | ❌ FAIL | `rejected` | -0.221 | 0.890 | 0.8399 |
| h_arithmetic_v0_002 | ✅ PASS | `cross_model_confirmed` | 0.875 | 2.885 | 0.0756 |
| h_arithmetic_v0_003 | ❌ FAIL | `rejected` | 0.234 | 0.515 | 0.8399 |

## Failure Analysis

### Core gate failures

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 2 | 66.7% |
| confirmatory_ci | 2 | 66.7% |
| multiplicity | 2 | 66.7% |
| negative_controls | 2 | 66.7% |
| robustness | 2 | 66.7% |

### Optional transfer diagnostics (tier demotions, not core failures)

| Check | Demotion Count | Demotion Rate |
|---|---|---|
| cross_model_transfer | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `cross_model_confirmed` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_arithmetic_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, confirmatory_ci, multiplicity, negative_controls, robustness, cross_model_transfer
- Treatment mean: -0.013549
- Cohen's d: -0.2211
- Confirmatory CI (bootstrap): [-0.067590, 0.016276]
- Specificity ratio: 0.890124
- Control abs mean: 0.015222
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.021284
- Permutation p-value: 0.676032396760324
- BH q-value: 0.839916
- Holm-adjusted p: 1.0
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_arithmetic_v0_002
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.086254
- Cohen's d: 0.8754
- Confirmatory CI (bootstrap): [0.031763, 0.166167]
- Specificity ratio: 2.885207
- Control abs mean: 0.029895
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.031370
- Permutation p-value: 0.021497850214978503
- BH q-value: 0.075592
- Holm-adjusted p: 0.07559244075592442
- Cells: 8

### h_arithmetic_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=fail, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, confirmatory_ci, multiplicity, negative_controls, robustness
- Treatment mean: 0.010179
- Cohen's d: 0.2339
- Confirmatory CI (bootstrap): [-0.008003, 0.056949]
- Specificity ratio: 0.514513
- Control abs mean: 0.019784
- Robustness (seed/prompt/resample): 0.500 / 0.500 / 0.000
- Method sensitivity std: 0.010197
- Permutation p-value: 0.8469153084691531
- BH q-value: 0.839916
- Holm-adjusted p: 1.0
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
