# Runtime And Cost

Evaluator runtime profile generated from reproducibility runs.

- Bundles covered by runtime envelope: **36** (measured: **8 / 36**, estimated: **28 / 36**, measurement coverage: **22.2%**)
- Claims: **109**
- Raw cells: **7452**
- Total mean runtime (s): **11367.644**
- Seconds per claim: **104.290**
- Seconds per 1000 cells: **1525.449**

## Runtime by model

| Model | Bundles | Claims | Mean sec/bundle | Sec/claim | Sec/1000 cells |
|---|---|---|---|---|---|
| gpt2-small | 22 | 67 | 352.077 | 115.607 | 1480.445 |
| pythia-70m | 14 | 42 | 258.711 | 86.237 | 1631.512 |

## Runtime by bundle

| Bundle | Task | Model | Claims | Raw cells | Mean runtime (s) | Sec/claim |
|---|---|---|---|---|---|---|
| docstring_v0_gpt2-small_lane_a | docstring_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| docstring_v0_gpt2-small_lane_b | docstring_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| docstring_v0_gpt2-small_lane_c | docstring_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| country_capital_v0_gpt2-small_lane_a | country_capital_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| country_capital_v0_gpt2-small_lane_b | country_capital_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| country_capital_v0_gpt2-small_lane_c | country_capital_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| country_capital_v0_pythia-70m_lane_a | country_capital_v0 | pythia-70m | 3 | 324 | 494.245 | 164.748 |
| country_capital_v0_pythia-70m_lane_b | country_capital_v0 | pythia-70m | 3 | 324 | 494.245 | 164.748 |
| country_capital_v0_pythia-70m_lane_c | country_capital_v0 | pythia-70m | 3 | 324 | 494.245 | 164.748 |
| fact_recall_v0_gpt2-small_lane_b3 | fact_recall_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| ioi_v0_gpt2-small_lane_a | ioi_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| ioi_v0_gpt2-small_lane_b | ioi_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| ioi_v0_gpt2-small_lane_b3 | ioi_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| ioi_v0_gpt2-small_lane_c | ioi_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| sentiment_v0_gpt2-small_lane_a | sentiment_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| sentiment_v0_gpt2-small_lane_b | sentiment_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| sentiment_v0_gpt2-small_lane_c | sentiment_v0 | gpt2-small | 3 | 324 | 494.245 | 164.748 |
| sentiment_v0_pythia-70m_lane_a | sentiment_v0 | pythia-70m | 3 | 324 | 494.245 | 164.748 |
| sentiment_v0_pythia-70m_lane_b | sentiment_v0 | pythia-70m | 3 | 324 | 494.245 | 164.748 |
| sentiment_v0_pythia-70m_lane_c | sentiment_v0 | pythia-70m | 3 | 324 | 494.245 | 164.748 |
| ioi_v0_gpt2-small | ioi_v0 | gpt2-small | 4 | 432 | 248.066 | 62.016 |
| fact_recall_v0_gpt2-small | fact_recall_v0 | gpt2-small | 3 | 48 | 171.188 | 57.063 |
| docstring_v0_pythia-70m | docstring_v0 | pythia-70m | 3 | 48 | 163.479 | 54.493 |
| greater_than_v0_pythia-70m | greater_than_v0 | pythia-70m | 3 | 48 | 162.442 | 54.147 |
| gendered_pronoun_v0_pythia-70m | gendered_pronoun_v0 | pythia-70m | 3 | 48 | 161.118 | 53.706 |
| docstring_v0_gpt2-small | docstring_v0 | gpt2-small | 3 | 48 | 154.332 | 51.444 |
| greater_than_v0_gpt2-small | greater_than_v0 | gpt2-small | 3 | 48 | 73.222 | 24.407 |
| arithmetic_v0_gpt2-small | arithmetic_v0 | gpt2-small | 3 | 48 | 73.222 | 24.407 |
| arithmetic_v0_pythia-70m | arithmetic_v0 | pythia-70m | 3 | 48 | 73.222 | 24.407 |
| gendered_pronoun_v0_gpt2-small | gendered_pronoun_v0 | gpt2-small | 3 | 48 | 69.612 | 23.204 |
| fact_recall_v0_pythia-70m | fact_recall_v0 | pythia-70m | 3 | 48 | 41.307 | 13.769 |
| country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | 3 | 12 | 18.305 | 6.102 |
| country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | 3 | 12 | 18.305 | 6.102 |
| ioi_v0_pythia-70m | ioi_v0 | pythia-70m | 3 | 12 | 18.305 | 6.102 |
| sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | 3 | 12 | 18.305 | 6.102 |
| sentiment_v0_pythia-70m | sentiment_v0 | pythia-70m | 3 | 12 | 18.305 | 6.102 |

## Data source

- `main/output/repro/runtime_cost_report.json`
