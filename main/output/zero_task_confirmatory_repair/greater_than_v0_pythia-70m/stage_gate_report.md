# Stage-Gate Report

- Protocol: `real_greater_than_v0_pythia-70m_confirmatory_repair_mock`
- Protocol hash: `20fac9d0dcc1278bbf5a704b7ca5fabb3acb17523e35e8cf9bc832381f6621ca`
- Hypotheses: 3
- Accepted: 2
- Unstable: 0
- Rejected: 1
- All pass: False
- Cross-method rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_greater_than_v0_001 | ❌ FAIL | `rejected` | 6.799 | 12.550 | 0.0156 |
| h_greater_than_v0_002 | ✅ PASS | `single_model_confirmed` | 6.884 | 12.460 | 0.0156 |
| h_greater_than_v0_003 | ✅ PASS | `single_model_confirmed` | 7.105 | 12.729 | 0.0156 |

## Failure Analysis

### Core gate failures

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 1 | 33.3% |
| robustness | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 2 |
| `rejected` | 1 |

## Per-Hypothesis Details

### h_greater_than_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness
- Treatment mean: 0.082363
- Cohen's d: 6.7994
- Confirmatory CI (bootstrap): [0.072762, 0.089550]
- Specificity ratio: 12.550476
- Control abs mean: 0.006562
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.008988
- Permutation p-value: 0.019455252918287938
- BH q-value: 0.015564
- Holm-adjusted p: 0.023346303501945526
- Cells: 8

### h_greater_than_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.078925
- Cohen's d: 6.8836
- Confirmatory CI (bootstrap): [0.072737, 0.085925]
- Specificity ratio: 12.459793
- Control abs mean: 0.006334
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.006725
- Permutation p-value: 0.019455252918287938
- BH q-value: 0.015564
- Holm-adjusted p: 0.023346303501945526
- Cells: 8

### h_greater_than_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.086675
- Cohen's d: 7.1055
- Confirmatory CI (bootstrap): [0.077363, 0.092713]
- Specificity ratio: 12.728775
- Control abs mean: 0.006809
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.001250
- Permutation p-value: 0.011673151750972763
- BH q-value: 0.015564
- Holm-adjusted p: 0.023346303501945526
- Cells: 8
