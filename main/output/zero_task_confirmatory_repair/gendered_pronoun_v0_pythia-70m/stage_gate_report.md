# Stage-Gate Report

- Protocol: `real_gendered_pronoun_v0_pythia-70m_confirmatory_repair_mock`
- Protocol hash: `4448729f5e42bea1f584138c11626f3913cffaf43cbae73030e27f51fa48d34d`
- Hypotheses: 3
- Accepted: 2
- Unstable: 0
- Rejected: 1
- All pass: False
- Cross-method rank τ: -0.3333

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_gendered_pronoun_v0_001 | ✅ PASS | `single_model_confirmed` | 5.342 | 11.492 | 0.0175 |
| h_gendered_pronoun_v0_002 | ❌ FAIL | `rejected` | 8.349 | 12.935 | 0.0195 |
| h_gendered_pronoun_v0_003 | ✅ PASS | `single_model_confirmed` | 6.401 | 13.742 | 0.0175 |

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

### h_gendered_pronoun_v0_001
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.080513
- Cohen's d: 5.3417
- Confirmatory CI (bootstrap): [0.069100, 0.089050]
- Specificity ratio: 11.491525
- Control abs mean: 0.007006
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.010113
- Permutation p-value: 0.0038910505836575876
- BH q-value: 0.017510
- Holm-adjusted p: 0.03501945525291829
- Cells: 8

### h_gendered_pronoun_v0_002
- Passed: False
- Evidence tier: `rejected`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=fail, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=fail
- Failed checks: causal_effect, robustness
- Treatment mean: 0.087025
- Cohen's d: 8.3491
- Confirmatory CI (bootstrap): [0.080088, 0.092375]
- Specificity ratio: 12.934510
- Control abs mean: 0.006728
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 0.000825
- Permutation p-value: 0.007782101167315175
- BH q-value: 0.019455
- Holm-adjusted p: 0.03501945525291829
- Cells: 8

### h_gendered_pronoun_v0_003
- Passed: True
- Evidence tier: `single_model_confirmed`
- Gate outcomes: baseline_superiority=pass, bidirectional=pass, causal_effect=pass, confirmatory_ci=pass, confirmatory_firewall=pass, confirmatory_present=pass, cross_model_transfer=not_evaluated, effect_size_practical=pass, execution_coverage=pass, governance_valid=pass, method_sensitivity=pass, multiplicity=pass, negative_controls=pass, power_adequacy=pass, rank_stability=pass, robustness=pass
- Failed checks: none
- Treatment mean: 0.088938
- Cohen's d: 6.4013
- Confirmatory CI (bootstrap): [0.074975, 0.095925]
- Specificity ratio: 13.742154
- Control abs mean: 0.006472
- Robustness (seed/prompt/resample): 1.000 / 1.000 / 1.000
- Method sensitivity std: 0.003813
- Permutation p-value: 0.007782101167315175
- BH q-value: 0.017510
- Holm-adjusted p: 0.03501945525291829
- Cells: 8
