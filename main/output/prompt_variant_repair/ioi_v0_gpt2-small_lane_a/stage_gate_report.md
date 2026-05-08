# Stage-Gate Report

- Protocol: `multilane_A_ioi_v0_gpt2-small_prompt_variant_repair_v1`
- Protocol hash: `56131e795882acbe697a5a0037a0f913d854bcc334ec7dfaf55ca401476f2a04`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.5556
- Cross-model rank τ: -1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sweep_ioi_v0_001 | ✅ PASS | `single_model_confirmed` | -0.587 | 9.501 | 0.0001 |
| h_sweep_ioi_v0_002 | ❌ FAIL | `rejected` | 0.518 | 2.255 | 0.0001 |
| h_sweep_ioi_v0_003 | ❌ FAIL | `rejected` | 0.399 | 3.451 | 0.0046 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| negative_controls | 2 | 66.7% |
| power_adequacy | 2 | 66.7% |
| cross_model_transfer | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_sweep_ioi_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: -0.979966
- Cohen's d: -0.5875
- Confirmatory CI (bootstrap): [-1.429822, -0.548054]
- Specificity ratio: 9.501039
- Control abs mean: 0.103143
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.431846
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_ioi_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, power_adequacy
- Treatment mean: 0.486744
- Cohen's d: 0.5179
- Confirmatory CI (bootstrap): [0.278662, 0.791769]
- Specificity ratio: 2.255457
- Control abs mean: 0.215807
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.421321
- Permutation p-value: 9.999000099990002e-05
- BH q-value: 0.000150
- Holm-adjusted p: 0.00029997000299970003
- Cells: 54

### h_sweep_ioi_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=fail, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, power_adequacy
- Treatment mean: 0.423436
- Cohen's d: 0.3990
- Confirmatory CI (bootstrap): [0.155047, 0.718569]
- Specificity ratio: 3.450708
- Control abs mean: 0.122710
- Robustness (seed/prompt/resample): 1.000 / 0.667 / 1.000
- Method sensitivity std: 0.281213
- Permutation p-value: 0.0058994100589941
- BH q-value: 0.004600
- Holm-adjusted p: 0.0045995400459954
- Cells: 54
