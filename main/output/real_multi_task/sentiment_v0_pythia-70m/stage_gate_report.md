# Stage-Gate Report

- Protocol: `real_sentiment_v0_pythia-70m`
- Protocol hash: `1f450c4086eff700610f0481a054a79a801e9195945a82911dc4af9f8574304b`
- Hypotheses: 3
- Accepted: 0
- Unstable: 0
- Rejected: 3
- All pass: False
- Cross-method rank τ: 1.0000

## Summary Table

| Hypothesis | Verdict | Tier | Cohen's d | Spec. Ratio | q-value |
|---|---|---|---|---|---|
| h_sentiment_v0_001 | ❌ FAIL | `rejected` | -0.383 | 2.990 | 0.5007 |
| h_sentiment_v0_002 | ❌ FAIL | `rejected` | -0.828 | 53.940 | 0.5007 |
| h_sentiment_v0_003 | ❌ FAIL | `rejected` | -0.857 | 77.107 | 0.5007 |

## Failure Analysis

| Check | Failure Count | Failure Rate |
|---|---|---|
| confirmatory_present | 3 | 100.0% |
| causal_effect | 3 | 100.0% |
| robustness | 3 | 100.0% |
| method_sensitivity | 3 | 100.0% |
| confirmatory_ci | 3 | 100.0% |
| multiplicity | 3 | 100.0% |

## Evidence Tier Breakdown

| Tier | Count |
|---|---|
| `rejected` | 3 |

## Per-Hypothesis Details

### h_sentiment_v0_001
- Passed: False
- Evidence tier: `rejected`
- Failed checks: confirmatory_present, causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -0.751997
- Cohen's d: -0.3834
- Confirmatory CI (bootstrap): [-2.485096, 0.945764]
- Specificity ratio: 2.990476
- Control abs mean: 0.251464
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 1.697761
- Permutation p-value: 0.504
- BH q-value: 0.500700
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_sentiment_v0_002
- Passed: False
- Evidence tier: `rejected`
- Failed checks: confirmatory_present, causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -1.347091
- Cohen's d: -0.8277
- Confirmatory CI (bootstrap): [-2.807713, 0.060381]
- Specificity ratio: 53.939626
- Control abs mean: 0.024974
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 1.407473
- Permutation p-value: 0.4957
- BH q-value: 0.500700
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected

### h_sentiment_v0_003
- Passed: False
- Evidence tier: `rejected`
- Failed checks: confirmatory_present, causal_effect, robustness, method_sensitivity, confirmatory_ci, multiplicity
- Treatment mean: -1.395547
- Cohen's d: -0.8575
- Confirmatory CI (bootstrap): [-2.843220, 0.012784]
- Specificity ratio: 77.106837
- Control abs mean: 0.018099
- Robustness (seed/prompt/resample): 0.000 / 0.000 / 0.000
- Method sensitivity std: 1.408331
- Permutation p-value: 0.4967
- BH q-value: 0.500700
- Holm-adjusted p: 1.0
- Cells: 4
- ⚠️ **Compensation warning**: Treatment effect reverses direction across methods — possible compensatory circuit detected
