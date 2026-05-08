# Benchmark Breadth Summary

- Evaluated bundles: **36**
- Evaluated claims: **109**
- Tasks covered: **8**
- Models covered: **2**
- Discovery lanes represented: **7**
- Providers represented: **7**

## Claims by task

| Task | Claims |
|---|---|
| arithmetic_v0 | 6 |
| country_capital_v0 | 24 |
| docstring_v0 | 15 |
| fact_recall_v0 | 9 |
| gendered_pronoun_v0 | 6 |
| greater_than_v0 | 6 |
| ioi_v0 | 19 |
| sentiment_v0 | 24 |

## Claims by model

| Model | Claims |
|---|---|
| gpt2-small | 67 |
| pythia-70m | 42 |

## Claims by discovery lane

| Lane | Claims |
|---|---|
| A | 18 |
| B | 18 |
| B3 | 6 |
| C | 18 |
| canonical_real | 15 |
| canonical_real_repair_v1 | 30 |
| prompt_variant_repair_v1 | 4 |

## Evaluated bundles

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
| ioi_v0_gpt2-small | ioi_v0 | gpt2-small | 4 | prompt_variant_repair_v1:4 |
| ioi_v0_gpt2-small_lane_a | ioi_v0 | gpt2-small | 3 | A:3 |
| ioi_v0_gpt2-small_lane_b | ioi_v0 | gpt2-small | 3 | B:3 |
| ioi_v0_gpt2-small_lane_b3 | ioi_v0 | gpt2-small | 3 | B3:3 |
| ioi_v0_gpt2-small_lane_c | ioi_v0 | gpt2-small | 3 | C:3 |
| sentiment_v0_gpt2-small_lane_a | sentiment_v0 | gpt2-small | 3 | A:3 |
| sentiment_v0_gpt2-small_lane_b | sentiment_v0 | gpt2-small | 3 | B:3 |
| sentiment_v0_gpt2-small_lane_c | sentiment_v0 | gpt2-small | 3 | C:3 |
| sentiment_v0_pythia-70m_lane_a | sentiment_v0 | pythia-70m | 3 | A:3 |
| sentiment_v0_pythia-70m_lane_b | sentiment_v0 | pythia-70m | 3 | B:3 |
| sentiment_v0_pythia-70m_lane_c | sentiment_v0 | pythia-70m | 3 | C:3 |

## Auxiliary lane artifacts

These artifacts exist locally but are not counted as evaluated bundles unless Stage-2 and Stage-1 were run on them.

| Source dir | Task | Model | Lane | Provider | Hypothesis |
|---|---|---|---|---|---|
| lanes_country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_country_capital_v0_001 |
| lanes_country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_country_capital_v0_002 |
| lanes_country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_country_capital_v0_003 |
| lanes_country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | B | neuron_dla_real | h_neuron_country_capital_v0_001 |
| lanes_country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | B | neuron_dla_real | h_neuron_country_capital_v0_002 |
| lanes_country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | B | neuron_dla_real | h_neuron_country_capital_v0_003 |
| lanes_country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | C | behavioral_dla_real | h_dla_country_capital_v0_001 |
| lanes_country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | C | behavioral_dla_real | h_dla_country_capital_v0_002 |
| lanes_country_capital_v0_gpt2-small | country_capital_v0 | gpt2-small | C | behavioral_dla_real | h_dla_country_capital_v0_003 |
| lanes_country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | A | circuit_sweep_real | h_sweep_country_capital_v0_001 |
| lanes_country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | A | circuit_sweep_real | h_sweep_country_capital_v0_002 |
| lanes_country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | A | circuit_sweep_real | h_sweep_country_capital_v0_003 |
| lanes_country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | B | neuron_dla_real | h_neuron_country_capital_v0_001 |
| lanes_country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | B | neuron_dla_real | h_neuron_country_capital_v0_002 |
| lanes_country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | B | neuron_dla_real | h_neuron_country_capital_v0_003 |
| lanes_country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | C | behavioral_dla_real | h_dla_country_capital_v0_001 |
| lanes_country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | C | behavioral_dla_real | h_dla_country_capital_v0_002 |
| lanes_country_capital_v0_pythia-70m | country_capital_v0 | pythia-70m | C | behavioral_dla_real | h_dla_country_capital_v0_003 |
| lanes_docstring_v0_gpt2-small | docstring_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_docstring_v0_001 |
| lanes_docstring_v0_gpt2-small | docstring_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_docstring_v0_002 |
| lanes_docstring_v0_gpt2-small | docstring_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_docstring_v0_003 |
| lanes_docstring_v0_gpt2-small | docstring_v0 | gpt2-small | B | neuron_dla_real | h_neuron_docstring_v0_001 |
| lanes_docstring_v0_gpt2-small | docstring_v0 | gpt2-small | B | neuron_dla_real | h_neuron_docstring_v0_002 |
| lanes_docstring_v0_gpt2-small | docstring_v0 | gpt2-small | B | neuron_dla_real | h_neuron_docstring_v0_003 |
| lanes_docstring_v0_gpt2-small | docstring_v0 | gpt2-small | C | behavioral_dla_real | h_dla_docstring_v0_001 |
| lanes_docstring_v0_gpt2-small | docstring_v0 | gpt2-small | C | behavioral_dla_real | h_dla_docstring_v0_002 |
| lanes_docstring_v0_gpt2-small | docstring_v0 | gpt2-small | C | behavioral_dla_real | h_dla_docstring_v0_003 |
| lanes_ioi_v0_gpt2-small | ioi_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_ioi_v0_001 |
| lanes_ioi_v0_gpt2-small | ioi_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_ioi_v0_002 |
| lanes_ioi_v0_gpt2-small | ioi_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_ioi_v0_003 |
| lanes_ioi_v0_gpt2-small | ioi_v0 | gpt2-small | B | neuron_dla_real | h_neuron_ioi_v0_001 |
| lanes_ioi_v0_gpt2-small | ioi_v0 | gpt2-small | B | neuron_dla_real | h_neuron_ioi_v0_002 |
| lanes_ioi_v0_gpt2-small | ioi_v0 | gpt2-small | B | neuron_dla_real | h_neuron_ioi_v0_003 |
| lanes_ioi_v0_gpt2-small | ioi_v0 | gpt2-small | C | behavioral_dla_real | h_dla_ioi_v0_001 |
| lanes_ioi_v0_gpt2-small | ioi_v0 | gpt2-small | C | behavioral_dla_real | h_dla_ioi_v0_002 |
| lanes_ioi_v0_gpt2-small | ioi_v0 | gpt2-small | C | behavioral_dla_real | h_dla_ioi_v0_003 |
| lanes_sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_sentiment_v0_001 |
| lanes_sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_sentiment_v0_002 |
| lanes_sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | A | circuit_sweep_real | h_sweep_sentiment_v0_003 |
| lanes_sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | B | neuron_dla_real | h_neuron_sentiment_v0_001 |
| lanes_sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | B | neuron_dla_real | h_neuron_sentiment_v0_002 |
| lanes_sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | B | neuron_dla_real | h_neuron_sentiment_v0_003 |
| lanes_sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | C | behavioral_dla_real | h_dla_sentiment_v0_001 |
| lanes_sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | C | behavioral_dla_real | h_dla_sentiment_v0_002 |
| lanes_sentiment_v0_gpt2-small | sentiment_v0 | gpt2-small | C | behavioral_dla_real | h_dla_sentiment_v0_003 |
| lanes_sentiment_v0_pythia-70m | sentiment_v0 | pythia-70m | A | circuit_sweep_real | h_sweep_sentiment_v0_001 |
| lanes_sentiment_v0_pythia-70m | sentiment_v0 | pythia-70m | A | circuit_sweep_real | h_sweep_sentiment_v0_002 |
| lanes_sentiment_v0_pythia-70m | sentiment_v0 | pythia-70m | A | circuit_sweep_real | h_sweep_sentiment_v0_003 |
| lanes_sentiment_v0_pythia-70m | sentiment_v0 | pythia-70m | B | neuron_dla_real | h_neuron_sentiment_v0_001 |
| lanes_sentiment_v0_pythia-70m | sentiment_v0 | pythia-70m | B | neuron_dla_real | h_neuron_sentiment_v0_002 |
