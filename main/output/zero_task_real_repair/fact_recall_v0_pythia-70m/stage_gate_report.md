# Stage-Gate Report

- Protocol: `real_fact_recall_v0_pythia-70m_confirmatory_repair_real`
- Protocol hash: `c0f68ac3cbca39a148e5095a17e825cef367bf4bb1974e14e35e61b6b119727a`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 1.0000
- Cross-model rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_fact_recall_v0_001 | ✅ PASS | `single_model_confirmed` | 2.784 | 11.431 | 0.0123 |
| h_fact_recall_v0_002 | ❌ FAIL | `rejected` | 1.266 | 0.263 | 0.0142 |
| h_fact_recall_v0_003 | ❌ FAIL | `rejected` | 1.059 | 1.435 | 0.0123 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| cross_model_transfer | 3 | 100.0% |
| negative_controls | 2 | 66.7% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_fact_recall_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: cross_model_transfer
- Treatment mean: 0.576693
- Cohen's d: 2.7836
- Confirmatory CI (bootstrap): [0.466133, 0.742722]
- Specificity ratio: 11.430609
- Control abs mean: 0.050452
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.023305
- Permutation p-value: 0.007599240075992401
- BH q-value: 0.012299
- Holm-adjusted p: 0.0221977802219778
- Cells: 8

### h_fact_recall_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, cross_model_transfer
- Treatment mean: 0.062903
- Cohen's d: 1.2659
- Confirmatory CI (bootstrap): [0.029061, 0.094022]
- Specificity ratio: 0.262981
- Control abs mean: 0.239193
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.004360
- Permutation p-value: 0.014598540145985401
- BH q-value: 0.014199
- Holm-adjusted p: 0.0221977802219778
- Cells: 8

### h_fact_recall_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=fail, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls, cross_model_transfer
- Treatment mean: 0.074601
- Cohen's d: 1.0592
- Confirmatory CI (bootstrap): [0.043213, 0.148950]
- Specificity ratio: 1.434593
- Control abs mean: 0.052001
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.030631
- Permutation p-value: 0.006899310068993101
- BH q-value: 0.012299
- Holm-adjusted p: 0.0221977802219778
- Cells: 8
