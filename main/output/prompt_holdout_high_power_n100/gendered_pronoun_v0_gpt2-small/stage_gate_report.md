# Stage-Gate Report

- Protocol: `real_gendered_pronoun_v0_gpt2-small_confirmatory_repair_real_prompt_holdout_high_power_n100`
- Protocol hash: `7c586d108a06536769e0f06a3d30525f75db12c807e3ac3dbae9827c5a6f0c29`
- Hypotheses: 3
- Accepted: 1
- Unstable: 0
- Rejected: 2
- All pass: False
- Cross-method rank τ: 0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_gendered_pronoun_v0_001 | ❌ FAIL | `rejected` | -0.537 | 2.353 | 0.2348 |
| h_gendered_pronoun_v0_002 | ✅ PASS | `single_model_confirmed` | 1.259 | 4.110 | 0.0948 |
| h_gendered_pronoun_v0_003 | ❌ FAIL | `rejected` | -0.769 | 6.141 | 0.1302 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| causal_effect | 2 | 66.7% |
| robustness | 2 | 66.7% |
| multiplicity | 2 | 66.7% |
| method_sensitivity | 1 | 33.3% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `single_model_confirmed` | 1 |
| `rejected` | 2 |

## Per-Hypothesis Details

### h_gendered_pronoun_v0_001
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, multiplicity
- Treatment mean: -0.026175
- Cohen's d: -0.5374
- Confirmatory CI (bootstrap): [-0.066802, -0.000006]
- Specificity ratio: 2.353113
- Control abs mean: 0.011124
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.024957
- Permutation p-value: 0.23217678232176783
- BH q-value: 0.234777
- Holm-adjusted p: 0.23477652234776522
- Cells: 8

### h_gendered_pronoun_v0_002
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.211028
- Cohen's d: 1.2593
- Confirmatory CI (bootstrap): [0.086764, 0.306892]
- Specificity ratio: 4.110178
- Control abs mean: 0.051343
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.034994
- Permutation p-value: 0.0337966203379662
- BH q-value: 0.094791
- Holm-adjusted p: 0.09479052094790522
- Cells: 8

### h_gendered_pronoun_v0_003
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=fail, multiplicity=fail, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness, method_sensitivity, multiplicity
- Treatment mean: -0.330840
- Cohen's d: -0.7685
- Confirmatory CI (bootstrap): [-0.596835, -0.036520]
- Specificity ratio: 6.141124
- Control abs mean: 0.053873
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.374200
- Permutation p-value: 0.0903909609039096
- BH q-value: 0.130187
- Holm-adjusted p: 0.1735826417358264
- Cells: 8
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
