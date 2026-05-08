# Prompt-Repair Same-Family Transfer

This fills missing same-family transfer rows for prompt-repaired canonical bundles. It preserves existing paired-bundle rows and does not lower the transfer gate.

- Mode: **live_fill**
- Bundles summarized: **6**
- Bundles updated: **6**
- Accepted claims with transfer rows: **n/a**
- Accepted claims missing transfer rows: **n/a**
- Examples per transfer run: **100**

| Bundle | Source -> target | Filled / missing hypotheses | Rows before -> after |
|---|---|---|---:|
| `arithmetic_v0_gpt2-small` | `gpt2-small` -> `gpt2-medium` | `h_arithmetic_v0_002` | 3 -> 4 |
| `arithmetic_v0_pythia-70m` | `pythia-70m` -> `pythia-160m` | `h_arithmetic_v0_002` | 3 -> 4 |
| `country_capital_v0_gpt2-small_lane_a` | `gpt2-small` -> `gpt2-medium` | `h_sweep_country_capital_v0_001`, `h_sweep_country_capital_v0_002` | 3 -> 5 |
| `country_capital_v0_gpt2-small_lane_c` | `gpt2-small` -> `gpt2-medium` | `h_dla_country_capital_v0_001`, `h_dla_country_capital_v0_002` | 3 -> 5 |
| `country_capital_v0_pythia-70m_lane_a` | `pythia-70m` -> `pythia-160m` | `h_sweep_country_capital_v0_001`, `h_sweep_country_capital_v0_002` | 3 -> 5 |
| `country_capital_v0_pythia-70m_lane_c` | `pythia-70m` -> `pythia-160m` | `h_dla_country_capital_v0_001`, `h_dla_country_capital_v0_002` | 3 -> 5 |
