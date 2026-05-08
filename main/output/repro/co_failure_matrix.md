# Gate Co-Failure Matrix

- Claims analyzed: **109**
- Rejected: **83**
- Claims with at least one failed gate: **97**

## Dominant fragility cluster

- Pattern size: **1 gates**
- Claims with this exact failure pattern: **14**
- Fraction of claims with failed gates: **14.4%**
- Fraction of all evaluated claims: **12.8%**
- Failed gates: `cross_model_transfer`

## Marginal failed-gate counts

| Gate | Claims failing |
|---|---|
| `multiplicity` | 48 |
| `robustness` | 47 |
| `causal_effect` | 46 |
| `confirmatory_ci` | 41 |
| `negative_controls` | 40 |
| `power_adequacy` | 33 |
| `method_sensitivity` | 29 |
| `cross_model_transfer` | 28 |
| `baseline_superiority` | 19 |
| `effect_size_practical` | 18 |

## Co-failure matrix (claims failing both gates)

| gate | baseline_superiority | causal_effect | confirmatory_ci | cross_model_transfer | effect_size_practical | method_sensitivity | multiplicity | negative_controls | power_adequacy | robustness |
|---|---|---|---|---|---|---|---|---|---|---|
| `baseline_superiority` | 19 | 14 | 13 | 2 | 12 | 0 | 13 | 19 | 16 | 15 |
| `causal_effect` | 14 | 46 | 34 | 5 | 18 | 14 | 36 | 19 | 25 | 46 |
| `confirmatory_ci` | 13 | 34 | 41 | 4 | 18 | 16 | 41 | 20 | 19 | 35 |
| `cross_model_transfer` | 2 | 5 | 4 | 28 | 1 | 5 | 6 | 7 | 2 | 5 |
| `effect_size_practical` | 12 | 18 | 18 | 1 | 18 | 0 | 18 | 13 | 18 | 18 |
| `method_sensitivity` | 0 | 14 | 16 | 5 | 0 | 29 | 23 | 3 | 0 | 14 |
| `multiplicity` | 13 | 36 | 41 | 6 | 18 | 23 | 48 | 22 | 19 | 37 |
| `negative_controls` | 19 | 19 | 20 | 7 | 13 | 3 | 22 | 40 | 20 | 20 |
| `power_adequacy` | 16 | 25 | 19 | 2 | 18 | 0 | 19 | 20 | 33 | 26 |
| `robustness` | 15 | 46 | 35 | 5 | 18 | 14 | 37 | 20 | 26 | 47 |
