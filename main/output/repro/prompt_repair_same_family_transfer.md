# Prompt-Repair Same-Family Transfer

Cached summary of same-family transfer rows for prompt-repaired canonical bundles. This mode performs no live model inference and is suitable for the materialized audit.

- Mode: **summarize_existing**
- Bundles summarized: **11**
- Bundles updated: **0**
- Accepted claims with transfer rows: **20**
- Accepted claims missing transfer rows: **0**
- Examples per transfer run: **n/a**

| Bundle | Source -> target | Filled / missing hypotheses | Rows before -> after |
|---|---|---|---:|
| `arithmetic_v0_gpt2-small` | `gpt2-small` -> `gpt2-medium` | none | 4 -> 4 |
| `arithmetic_v0_pythia-70m` | `pythia-70m` -> `pythia-160m` | none | 4 -> 4 |
| `country_capital_v0_gpt2-small_lane_a` | `gpt2-small` -> `gpt2-medium` | none | 5 -> 5 |
| `country_capital_v0_gpt2-small_lane_b` | `gpt2-small` -> `gpt2-medium` | none | 1 -> 1 |
| `country_capital_v0_gpt2-small_lane_c` | `gpt2-small` -> `gpt2-medium` | none | 5 -> 5 |
| `country_capital_v0_pythia-70m_lane_a` | `pythia-70m` -> `pythia-160m` | none | 5 -> 5 |
| `country_capital_v0_pythia-70m_lane_c` | `pythia-70m` -> `pythia-160m` | none | 5 -> 5 |
| `ioi_v0_gpt2-small` | `gpt2-small` -> `gpt2-medium` | none | 1 -> 1 |
| `ioi_v0_gpt2-small_lane_a` | `gpt2-small` -> `gpt2-medium` | none | 1 -> 1 |
| `ioi_v0_gpt2-small_lane_c` | `gpt2-small` -> `gpt2-medium` | none | 1 -> 1 |
| `sentiment_v0_gpt2-small_lane_c` | `gpt2-small` -> `gpt2-medium` | none | 3 -> 3 |
