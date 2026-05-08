# Stage-Gate Report

- Protocol: `real_arithmetic_v0_gpt2-small_confirmatory_repair_real_prompt_variant_repair_v1`
- Protocol hash: `915997aca820bf1539edfa4f10e2fde1c419ba9f3871444f5bfe42af17625dc9`
- Hypotheses: 3
- Accepted: 3
- Unstable: 0
- Rejected: 0
- All pass: True
- Cross-method rank τ: 0.3333
- Cross-model rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_arithmetic_v0_001 | ✅ PASS | `single_model_confirmed` | 0.684 | 7.316 | 0.0686 |
| h_arithmetic_v0_002 | ✅ PASS | `cross_model_confirmed` | 2.039 | 8.752 | 0.0225 |
| h_arithmetic_v0_003 | ✅ PASS | `single_model_confirmed` | 0.883 | 2.507 | 0.0235 |

## Failure Analysis

No core gate failures detected.

### Optional transfer diagnostics (tier demotions, not core failures)

| Check | Demotion Count | Demotion Rate |
|---|---|---|
| cross_model_transfer | 2 | 66.7% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `cross_model_confirmed` | 1 |
| `single_model_confirmed` | 2 |

## Per-Hypothesis Details

### h_arithmetic_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.047942
- Cohen's d: 0.6844
- Confirmatory CI (bootstrap): [0.005027, 0.096151]
- Specificity ratio: 7.315606
- Control abs mean: 0.006553
- Robustness (seed/prompt/resample): 1.000 / 0.500 / 1.000
- Method sensitivity std: 0.020726
- Permutation p-value: 0.0678932106789321
- BH q-value: 0.068593
- Holm-adjusted p: 0.0685931406859314
- Cells: 8

### h_arithmetic_v0_002
- Passed: True
- Evidence tier: `cross_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=pass, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.139977
- Cohen's d: 2.0391
- Confirmatory CI (bootstrap): [0.101652, 0.191415]
- Specificity ratio: 8.751819
- Control abs mean: 0.015994
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.023910
- Permutation p-value: 0.0058994100589941
- BH q-value: 0.022498
- Holm-adjusted p: 0.022497750224977502
- Cells: 8

### h_arithmetic_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.044181
- Cohen's d: 0.8833
- Confirmatory CI (bootstrap): [0.019358, 0.087659]
- Specificity ratio: 2.507357
- Control abs mean: 0.017620
- Robustness (seed/prompt/resample): 0.500 / 0.500 / 1.000
- Method sensitivity std: 0.005410
- Permutation p-value: 0.015798420157984203
- BH q-value: 0.023548
- Holm-adjusted p: 0.0313968603139686
- Cells: 8
