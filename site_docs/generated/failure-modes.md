# Failure Modes

Auto-generated failure decomposition from the released evaluated bundle set.

- Claims analyzed: **109**
- Passed: **26**
- Failed: **83**

## Failed gate counts

| Gate | Count |
|---|---|
| multiplicity | 48 |
| robustness | 47 |
| causal_effect | 46 |
| confirmatory_ci | 41 |
| negative_controls | 40 |
| power_adequacy | 33 |
| method_sensitivity | 29 |
| cross_model_transfer | 28 |
| baseline_superiority | 19 |
| effect_size_practical | 18 |

## Not-evaluated gate counts

| Gate | Count |
|---|---|
| cross_model_transfer | 63 |

## Tier counts

| Tier | Count |
|---|---|
| rejected | 67 |
| single_model_confirmed | 14 |
| suggestive | 13 |
| cross_model_confirmed | 12 |
| causal_tested_unstable | 3 |

## Top failed-check combinations

| Claims | Failed checks |
|---|---|
| 14 | cross_model_transfer |
| 12 | causal_effect, confirmatory_ci, method_sensitivity, multiplicity, robustness |
| 11 | baseline_superiority, causal_effect, confirmatory_ci, effect_size_practical, multiplicity, negative_controls, power_adequacy, robustness |
| 5 | negative_controls |
| 5 | causal_effect, confirmatory_ci, effect_size_practical, multiplicity, power_adequacy, robustness |
| 4 | cross_model_transfer, negative_controls |
| 4 | causal_effect, power_adequacy, robustness |
| 4 | method_sensitivity |
| 3 | method_sensitivity, multiplicity |
| 3 | power_adequacy |

## Contract sensitivity snapshot

- Full-contract acceptance rate: **23.85%**
- Most sensitive suite removal: **no_controls_suite**
- Acceptance under that counterfactual: **34.86%**
- Tier changes under that counterfactual: **21**

## Data sources

- `main/output/real_multi_task/failure_mode_summary.json`
- `main/output/repro/field_level_findings.json`
