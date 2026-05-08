# Cross-Model Transfer Near-Miss Forensics

- Cross-model floor (`CROSS_MODEL_EFFECT_FLOOR`): **0.02**
- Accepted claims with transfer evidence: **26**
- Cross-model confirmed: **12**
- Same-direction near-misses (below floor): **8**
- Opposite-direction subthreshold: **3**
- Opposite-direction above floor: **3**

## Closest near-miss

- Bundle: `sentiment_v0_gpt2-small_lane_c`
- Hypothesis: `h_dla_sentiment_v0_001`
- Source → transfer effect: **+0.013992**
- Transfer examples: **200**
- Floor fraction: **70.0%** of the 0.02 floor
- Same direction as source: **True**

This is the unresolved accepted released claim that is closest to satisfying the cross-model transfer gate. It has already been preregistered and rerun at n=200, where it stayed same-direction but below the frozen floor. The current interpretation is therefore not "missing run" or obvious sampling noise; it is a persistent below-floor tail case under the released mapping and threshold. Further reruns should require a new preregistered rationale rather than being repeated until lucky.

## Top 5 same-direction near-misses

| bundle | hypothesis | effect | floor fraction |
|---|---|---|---|
| `sentiment_v0_gpt2-small_lane_c` | `h_dla_sentiment_v0_001` | +0.013992 | 70.0% |
| `country_capital_v0_gpt2-small_lane_a` | `h_sweep_country_capital_v0_003` | +0.010134 | 50.7% |
| `country_capital_v0_gpt2-small_lane_c` | `h_dla_country_capital_v0_003` | +0.010134 | 50.7% |
| `docstring_v0_gpt2-small_lane_a` | `h_sweep_docstring_v0_002` | +0.007126 | 35.6% |
| `fact_recall_v0_pythia-70m` | `h_fact_recall_v0_001` | +0.006474 | 32.4% |

## Direction-and-magnitude asymmetry by (source, target)

| source | target | n | correct dir | median floor frac | max floor frac |
|---|---|---|---|---|---|
| gpt2-small | gpt2-medium | 20 | 14/20 | 86.5% | 6747.7% |
| pythia-70m | pythia-160m | 6 | 6/6 | 3830.4% | 11245.2% |

## Most consistent transfer direction

- pythia-70m → pythia-160m: 6/6 accepted claims share the source direction; median floor fraction 3830.4% (max 11245.2%).

This pair is where the unresolved data most plausibly extrapolates to an additional cross-model-confirmed result. This should not be generalized beyond the paired-bundle country-capital-heavy evidence currently in the release; it means future discovery-side work targeted at this pair has the highest a-priori chance of crossing the floor without changing the contract.

## All accepted-claim transfer evidence

| bundle | hypothesis | effect | same dir | above floor | status |
|---|---|---|---|---|---|
| `country_capital_v0_pythia-70m_lane_a` | `h_sweep_country_capital_v0_001` | +2.249044 | True | True | `confirmed` |
| `country_capital_v0_pythia-70m_lane_c` | `h_dla_country_capital_v0_001` | +2.243951 | True | True | `confirmed` |
| `country_capital_v0_gpt2-small_lane_c` | `h_dla_country_capital_v0_001` | +1.349543 | True | True | `confirmed` |
| `country_capital_v0_gpt2-small_lane_a` | `h_sweep_country_capital_v0_001` | +1.325028 | True | True | `confirmed` |
| `country_capital_v0_gpt2-small_lane_a` | `h_sweep_country_capital_v0_002` | +1.115357 | True | True | `confirmed` |
| `country_capital_v0_gpt2-small_lane_c` | `h_dla_country_capital_v0_002` | +1.106858 | True | True | `confirmed` |
| `country_capital_v0_pythia-70m_lane_a` | `h_sweep_country_capital_v0_002` | +0.768435 | True | True | `confirmed` |
| `country_capital_v0_pythia-70m_lane_c` | `h_dla_country_capital_v0_002` | +0.763718 | True | True | `confirmed` |
| `arithmetic_v0_pythia-70m` | `h_arithmetic_v0_002` | +0.139977 | True | True | `confirmed` |
| `sentiment_v0_gpt2-small_lane_c` | `h_dla_sentiment_v0_003` | +0.126121 | True | True | `confirmed` |
| `arithmetic_v0_gpt2-small` | `h_arithmetic_v0_002` | +0.086254 | True | True | `confirmed` |
| `docstring_v0_gpt2-small_lane_c` | `h_dla_docstring_v0_003` | +0.020598 | True | True | `confirmed` |
| `sentiment_v0_gpt2-small_lane_c` | `h_dla_sentiment_v0_001` | +0.013992 | True | False | `near_miss_below_floor` |
| `country_capital_v0_gpt2-small_lane_a` | `h_sweep_country_capital_v0_003` | +0.010134 | True | False | `near_miss_below_floor` |
| `country_capital_v0_gpt2-small_lane_c` | `h_dla_country_capital_v0_003` | +0.010134 | True | False | `near_miss_below_floor` |
| `docstring_v0_gpt2-small_lane_a` | `h_sweep_docstring_v0_002` | +0.007126 | True | False | `near_miss_below_floor` |
| `fact_recall_v0_pythia-70m` | `h_fact_recall_v0_001` | +0.006474 | True | False | `near_miss_below_floor` |
| `country_capital_v0_gpt2-small_lane_b` | `h_neuron_country_capital_v0_002` | +0.000146 | True | False | `near_miss_below_floor` |
| `arithmetic_v0_gpt2-small` | `h_arithmetic_v0_001` | +0.000069 | True | False | `near_miss_below_floor` |
| `arithmetic_v0_gpt2-small` | `h_arithmetic_v0_003` | +0.000026 | True | False | `near_miss_below_floor` |
| `ioi_v0_gpt2-small` | `h_ioi_v0_001` | +0.137648 | False | True | `opposite_direction_above_floor` |
| `ioi_v0_gpt2-small_lane_a` | `h_sweep_ioi_v0_001` | +0.137648 | False | True | `opposite_direction_above_floor` |
| `ioi_v0_gpt2-small_lane_c` | `h_dla_ioi_v0_002` | +0.137648 | False | True | `opposite_direction_above_floor` |
| `greater_than_v0_gpt2-small` | `h_greater_than_v0_003` | -0.003674 | False | False | `opposite_direction_subthreshold` |
| `fact_recall_v0_gpt2-small` | `h_fact_recall_v0_003` | -0.001599 | False | False | `opposite_direction_subthreshold` |
| `gendered_pronoun_v0_gpt2-small` | `h_gendered_pronoun_v0_002` | -0.000708 | False | False | `opposite_direction_subthreshold` |
