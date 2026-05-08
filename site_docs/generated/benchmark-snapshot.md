# Benchmark Snapshot

Latest auto-generated summary from benchmark artifacts.

- Bundles: **36**
- Claims evaluated: **109**
- Tasks covered: **8**
- Models covered: **2**
- Discovery lanes represented: **7**
- Providers represented: **7**
- Acceptance rate: **23.85%** (95% CI: [16.83%, 32.66%])

## Claims by task

| Task | Claims |
|---|---|
| country_capital_v0 | 24 |
| sentiment_v0 | 24 |
| ioi_v0 | 19 |
| docstring_v0 | 15 |
| fact_recall_v0 | 9 |
| arithmetic_v0 | 6 |
| gendered_pronoun_v0 | 6 |
| greater_than_v0 | 6 |

## Claims by model

| Model | Claims |
|---|---|
| gpt2-small | 67 |
| pythia-70m | 42 |

## Claims by discovery lane

| Lane | Claims |
|---|---|
| canonical_real_repair_v1 | 30 |
| A | 18 |
| B | 18 |
| C | 18 |
| canonical_real | 15 |
| B3 | 6 |
| prompt_variant_repair_v1 | 4 |

## Bundle inventory

| Bundle | Task | Model | Claims | Lane counts |
|---|---|---|---|---|
| country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | 3 | canonical_real:3 |
| country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | 3 | canonical_real:3 |
| ioi_v0_pythia-70m | ioi_v0 | pythia-70m | 3 | canonical_real:3 |
| sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | 3 | canonical_real:3 |
| sentiment_v0_pythia-70m | sentiment_v0 | pythia-70m | 3 | canonical_real:3 |
| docstring_v0_gpt2-small_lane_a | docstring_v0 | gpt2-small | 3 | A:3 |
| docstring_v0_gpt2-small_lane_b | docstring_v0 | gpt2-small | 3 | B:3 |
| docstring_v0_gpt2-small_lane_c | docstring_v0 | gpt2-small | 3 | C:3 |
| fact_recall_v0_gpt2-small | fact_recall_v0 | gpt2-small | 3 | canonical_real_repair_v1:3 |
| fact_recall_v0_pythia-70m | fact_recall_v0 | pythia-70m | 3 | canonical_real_repair_v1:3 |
| gendered_pronoun_v0_gpt2-small | gendered_pronoun_v0 | gpt2-small | 3 | canonical_real_repair_v1:3 |
| gendered_pronoun_v0_pythia-70m | gendered_pronoun_v0 | pythia-70m | 3 | canonical_real_repair_v1:3 |
| greater_than_v0_gpt2-small | greater_than_v0 | gpt2-small | 3 | canonical_real_repair_v1:3 |
| greater_than_v0_pythia-70m | greater_than_v0 | pythia-70m | 3 | canonical_real_repair_v1:3 |
| arithmetic_v0_gpt2-small | arithmetic_v0 | gpt2-small | 3 | canonical_real_repair_v1:3 |
| arithmetic_v0_pythia-70m | arithmetic_v0 | pythia-70m | 3 | canonical_real_repair_v1:3 |
| country_capital_v0_gpt2-small_lane_a | country_capital_v0 | gpt2-small | 3 | A:3 |
| country_capital_v0_gpt2-small_lane_b | country_capital_v0 | gpt2-small | 3 | B:3 |
| country_capital_v0_gpt2-small_lane_c | country_capital_v0 | gpt2-small | 3 | C:3 |
| country_capital_v0_pythia-70m_lane_a | country_capital_v0 | pythia-70m | 3 | A:3 |
| country_capital_v0_pythia-70m_lane_b | country_capital_v0 | pythia-70m | 3 | B:3 |
| country_capital_v0_pythia-70m_lane_c | country_capital_v0 | pythia-70m | 3 | C:3 |
| docstring_v0_gpt2-small | docstring_v0 | gpt2-small | 3 | canonical_real_repair_v1:3 |
| docstring_v0_pythia-70m | docstring_v0 | pythia-70m | 3 | canonical_real_repair_v1:3 |
| fact_recall_v0_gpt2-small_lane_b3 | fact_recall_v0 | gpt2-small | 3 | B3:3 |

## Data sources

- `main/output/repro/benchmark_breadth_summary.json`
- `main/output/repro/field_level_findings.json`
