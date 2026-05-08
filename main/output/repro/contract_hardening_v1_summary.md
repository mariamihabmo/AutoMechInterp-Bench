# Contract Hardening V1 Summary

- Overrides: **min_causal_effect=0.15, min_effect_floor=0.15, min_specificity_ratio=5.0**
- Accepted claims before: **26**
- Accepted claims after: **1**
- Accepted-claim retention: **3.8%**
- Tasks with accepted claims after: **1** (fact_recall_v0)
- Cross-model-confirmed claims after: **0**
- Primary fresh agnostic hardened FAR: **0.0%** with 95% CI **[0.0%, 1.9%]**
- Worst agnostic replicate 95% upper bound: **1.9%**

## Which release-quality blockers this closes under V1

- `second_cross_model_confirmed_claim`: **no**
- `agnostic_far_upper_bound_below_5pct`: **yes**

## Agnostic stress replicates

| Seed namespace | Leaked | FAR | 95% CI |
|---|---:|---:|---|
| `rotated_2026q2` | 0/200 | 0.0% | [0.0%, 1.9%] |
| `rotated_2026q3` | 0/200 | 0.0% | [0.0%, 1.9%] |

This is a versioned protocol-migration candidate, not the current released contract. The retention and stress results should be read as a tradeoff analysis.

## Bundles with changed accepted counts

| Bundle | Accepted before | Accepted after | Cross-model confirmed after | Demoted hypotheses |
|---|---:|---:|---:|---|
| docstring_v0_gpt2-small_lane_a | 1 | 0 | 0 | `h_sweep_docstring_v0_002` |
| docstring_v0_gpt2-small_lane_c | 1 | 0 | 0 | `h_dla_docstring_v0_003` |
| fact_recall_v0_gpt2-small | 1 | 0 | 0 | `h_fact_recall_v0_003` |
| gendered_pronoun_v0_gpt2-small | 1 | 0 | 0 | `h_gendered_pronoun_v0_002` |
| greater_than_v0_gpt2-small | 1 | 0 | 0 | `h_greater_than_v0_003` |
| arithmetic_v0_gpt2-small | 3 | 0 | 0 | `h_arithmetic_v0_001`, `h_arithmetic_v0_002`, `h_arithmetic_v0_003` |
| arithmetic_v0_pythia-70m | 1 | 0 | 0 | `h_arithmetic_v0_002` |
| country_capital_v0_gpt2-small_lane_a | 3 | 0 | 0 | `h_sweep_country_capital_v0_001`, `h_sweep_country_capital_v0_002`, `h_sweep_country_capital_v0_003` |
| country_capital_v0_gpt2-small_lane_b | 1 | 0 | 0 | `h_neuron_country_capital_v0_002` |
| country_capital_v0_gpt2-small_lane_c | 3 | 0 | 0 | `h_dla_country_capital_v0_001`, `h_dla_country_capital_v0_002`, `h_dla_country_capital_v0_003` |
| country_capital_v0_pythia-70m_lane_a | 2 | 0 | 0 | `h_sweep_country_capital_v0_001`, `h_sweep_country_capital_v0_002` |
| country_capital_v0_pythia-70m_lane_c | 2 | 0 | 0 | `h_dla_country_capital_v0_001`, `h_dla_country_capital_v0_002` |
| ioi_v0_gpt2-small | 1 | 0 | 0 | `h_ioi_v0_001` |
| ioi_v0_gpt2-small_lane_a | 1 | 0 | 0 | `h_sweep_ioi_v0_001` |
| ioi_v0_gpt2-small_lane_c | 1 | 0 | 0 | `h_dla_ioi_v0_002` |
| sentiment_v0_gpt2-small_lane_c | 2 | 0 | 0 | `h_dla_sentiment_v0_001`, `h_dla_sentiment_v0_003` |
