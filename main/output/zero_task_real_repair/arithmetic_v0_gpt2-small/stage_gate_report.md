# Stage-Gate Report

- Protocol: `real_arithmetic_v0_gpt2-small_confirmatory_repair_real`
- Protocol hash: `f7da13489928b8507fd73bd3793b98eca64c9a806b85d7f254ec3a58a209170a`
- Hypotheses: 3
- Accepted: 3
- Unstable: 0
- Rejected: 0
- All pass: True
- Cross-method rank τ: 1.0000
- Cross-model rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_arithmetic_v0_001 | ✅ PASS | `single_model_confirmed` | 1.077 | 6.743 | 0.0242 |
| h_arithmetic_v0_002 | ✅ PASS | `single_model_confirmed` | 1.298 | 5.033 | 0.0229 |
| h_arithmetic_v0_003 | ✅ PASS | `single_model_confirmed` | 1.184 | 3.553 | 0.0216 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| cross_model_transfer | 3 | 100.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 3 |

## Per-Hypothesis Details

### h_arithmetic_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.095194
- Cohen's d: 1.0770
- Confirmatory CI (bootstrap): [0.039100, 0.151948]
- Specificity ratio: 6.742796
- Control abs mean: 0.014118
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.049716
- Permutation p-value: 0.0231976802319768
- BH q-value: 0.024198
- Holm-adjusted p: 0.030596940305969402
- Cells: 8

### h_arithmetic_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.048441
- Cohen's d: 1.2984
- Confirmatory CI (bootstrap): [0.026145, 0.074616]
- Specificity ratio: 5.033067
- Control abs mean: 0.009625
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.019662
- Permutation p-value: 0.013298670132986702
- BH q-value: 0.022948
- Holm-adjusted p: 0.030596940305969402
- Cells: 8

### h_arithmetic_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.061294
- Cohen's d: 1.1838
- Confirmatory CI (bootstrap): [0.033405, 0.102366]
- Specificity ratio: 3.553037
- Control abs mean: 0.017251
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.019220
- Permutation p-value: 0.007999200079992
- BH q-value: 0.021598
- Holm-adjusted p: 0.021597840215978402
- Cells: 8
