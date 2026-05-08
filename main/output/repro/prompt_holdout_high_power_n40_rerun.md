# High-Power Prompt-Holdout Rerun

This prospective diagnostic covers every current canonical bundle with accepted claims and multiple prompt variants. It must be reported as a high-power robustness frontier, not as external validation or a silent contract migration.

- Completion status: **complete**
- Examples per cell: **40**
- Planned bundles: **17**
- Bundles rerun: **17**
- Original accepted claims covered: **26**
- Original accepted claims retained: **23**
- Original accepted claims demoted: **3**
- Retained original accepted claims passing all held-out prompts: **19/23**
- Passing held-out prompt checks on retained claims: **59/63**

## Bundle Summary

| Bundle | Task | Model | Accepted before | Retained | Demoted | Retained + all holdouts pass |
|---|---|---|---:|---:|---:|---:|
| `arithmetic_v0_gpt2-small` | `arithmetic_v0` | `gpt2-small` | 3 | 2 | 1 | 1 |
| `arithmetic_v0_pythia-70m` | `arithmetic_v0` | `pythia-70m` | 1 | 0 | 1 | 0 |
| `country_capital_v0_gpt2-small_lane_a` | `country_capital_v0` | `gpt2-small` | 3 | 3 | 0 | 3 |
| `country_capital_v0_gpt2-small_lane_b` | `country_capital_v0` | `gpt2-small` | 1 | 1 | 0 | 1 |
| `country_capital_v0_gpt2-small_lane_c` | `country_capital_v0` | `gpt2-small` | 3 | 3 | 0 | 3 |
| `country_capital_v0_pythia-70m_lane_a` | `country_capital_v0` | `pythia-70m` | 2 | 2 | 0 | 2 |
| `country_capital_v0_pythia-70m_lane_c` | `country_capital_v0` | `pythia-70m` | 2 | 2 | 0 | 2 |
| `docstring_v0_gpt2-small_lane_a` | `docstring_v0` | `gpt2-small` | 1 | 1 | 0 | 1 |
| `docstring_v0_gpt2-small_lane_c` | `docstring_v0` | `gpt2-small` | 1 | 1 | 0 | 1 |
| `fact_recall_v0_gpt2-small` | `fact_recall_v0` | `gpt2-small` | 1 | 1 | 0 | 1 |
| `fact_recall_v0_pythia-70m` | `fact_recall_v0` | `pythia-70m` | 1 | 1 | 0 | 1 |
| `gendered_pronoun_v0_gpt2-small` | `gendered_pronoun_v0` | `gpt2-small` | 1 | 1 | 0 | 1 |
| `greater_than_v0_gpt2-small` | `greater_than_v0` | `gpt2-small` | 1 | 1 | 0 | 1 |
| `ioi_v0_gpt2-small` | `ioi_v0` | `gpt2-small` | 1 | 1 | 0 | 0 |
| `ioi_v0_gpt2-small_lane_a` | `ioi_v0` | `gpt2-small` | 1 | 1 | 0 | 0 |
| `ioi_v0_gpt2-small_lane_c` | `ioi_v0` | `gpt2-small` | 1 | 1 | 0 | 0 |
| `sentiment_v0_gpt2-small_lane_c` | `sentiment_v0` | `gpt2-small` | 2 | 1 | 1 | 1 |

## Failing Or Demoted Original Claims

- `arithmetic_v0_gpt2-small` / `h_arithmetic_v0_001`: demoted under the high-power rerun
- `arithmetic_v0_gpt2-small` / `h_arithmetic_v0_003`: retained but failed holdouts ['worded']
- `arithmetic_v0_pythia-70m` / `h_arithmetic_v0_002`: demoted under the high-power rerun
- `ioi_v0_gpt2-small` / `h_ioi_v0_001`: retained but failed holdouts ['structural']
- `ioi_v0_gpt2-small_lane_a` / `h_sweep_ioi_v0_001`: retained but failed holdouts ['structural']
- `ioi_v0_gpt2-small_lane_c` / `h_dla_ioi_v0_002`: retained but failed holdouts ['structural']
- `sentiment_v0_gpt2-small_lane_c` / `h_dla_sentiment_v0_003`: demoted under the high-power rerun
