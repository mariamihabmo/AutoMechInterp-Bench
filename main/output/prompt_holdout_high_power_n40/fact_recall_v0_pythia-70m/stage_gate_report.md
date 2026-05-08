# Stage-Gate Report

- Protocol: `real_fact_recall_v0_pythia-70m_confirmatory_repair_real_prompt_holdout_high_power_n40`
- Protocol hash: `7746cba6f63c71fd53f6ad6d65f66af59e64f670a922b5f9f9e6b9550d3b4b6a`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_fact_recall_v0_001 | ✅ PASS | `single_model_confirmed` | 5.663 | 17.587 | 0.0123 |
| h_fact_recall_v0_002 | ❌ FAIL | `rejected` | 0.997 | 0.193 | 0.0440 |
| h_fact_recall_v0_003 | ❌ FAIL | `rejected` | 1.813 | 1.277 | 0.0123 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
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
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.589601
- Cohen's d: 5.6629
- Confirmatory CI (bootstrap): [0.530826, 0.666417]
- Specificity ratio: 17.586857
- Control abs mean: 0.033525
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.009816
- Permutation p-value: 0.007599240075992401
- BH q-value: 0.012299
- Holm-adjusted p: 0.0221977802219778
- Cells: 8

### h_fact_recall_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls
- Treatment mean: 0.038896
- Cohen's d: 0.9973
- Confirmatory CI (bootstrap): [0.014860, 0.064572]
- Specificity ratio: 0.193183
- Control abs mean: 0.201343
- Robustness (seed/prompt/resample): 0.500 / 1.000 / 1.000
- Method sensitivity std: 0.021584
- Permutation p-value: 0.0458954104589541
- BH q-value: 0.043996
- Holm-adjusted p: 0.043995600439956005
- Cells: 8

### h_fact_recall_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=fail, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: negative_controls
- Treatment mean: 0.059787
- Cohen's d: 1.8131
- Confirmatory CI (bootstrap): [0.043452, 0.088935]
- Specificity ratio: 1.277121
- Control abs mean: 0.046814
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.007475
- Permutation p-value: 0.006899310068993101
- BH q-value: 0.012299
- Holm-adjusted p: 0.0221977802219778
- Cells: 8
