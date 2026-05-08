# Prompt-Holdout Transfer Control

- Accepted claims with multi-prompt coverage: **26**
- Claims passing all held-out prompt variants: **20 / 26**
- Passing hold-out checks: **63 / 70**

This is a within-model prompt control, not a new evidence tier. It asks whether accepted claims remain causal on held-out prompt variants already present in the release.

> **Prompt-variant repair caveat/status.** Legacy artifacts still contain unsupported nominal variants in bundles that previously held accepted claims, but the current canonical surface has **0** unsupported-prompt files and **0** affected accepted claims after prompt-repair promotion. The promotion frontier retained **19** and demoted **6** of **25** previously accepted affected claims.

## By model

| Model | Claims tested | Claims passing all holdouts |
|---|---|---|
| `gpt2-small` | 20 | 14 |
| `pythia-70m` | 6 | 6 |

## By task

| Task | Claims tested | Claims passing all holdouts |
|---|---|---|
| `arithmetic_v0` | 4 | 2 |
| `country_capital_v0` | 11 | 11 |
| `docstring_v0` | 2 | 2 |
| `fact_recall_v0` | 2 | 2 |
| `gendered_pronoun_v0` | 1 | 1 |
| `greater_than_v0` | 1 | 1 |
| `ioi_v0` | 3 | 0 |
| `sentiment_v0` | 2 | 1 |

## Bundle summary

| Bundle | Task | Model | Accepted claims tested | Passing all holdouts |
|---|---|---|---|---|
| `docstring_v0_gpt2-small_lane_a` | `docstring_v0` | `gpt2-small` | 1 | 1 |
| `docstring_v0_gpt2-small_lane_c` | `docstring_v0` | `gpt2-small` | 1 | 1 |
| `fact_recall_v0_gpt2-small` | `fact_recall_v0` | `gpt2-small` | 1 | 1 |
| `fact_recall_v0_pythia-70m` | `fact_recall_v0` | `pythia-70m` | 1 | 1 |
| `gendered_pronoun_v0_gpt2-small` | `gendered_pronoun_v0` | `gpt2-small` | 1 | 1 |
| `greater_than_v0_gpt2-small` | `greater_than_v0` | `gpt2-small` | 1 | 1 |
| `arithmetic_v0_gpt2-small` | `arithmetic_v0` | `gpt2-small` | 3 | 1 |
| `arithmetic_v0_pythia-70m` | `arithmetic_v0` | `pythia-70m` | 1 | 1 |
| `country_capital_v0_gpt2-small_lane_a` | `country_capital_v0` | `gpt2-small` | 3 | 3 |
| `country_capital_v0_gpt2-small_lane_b` | `country_capital_v0` | `gpt2-small` | 1 | 1 |
| `country_capital_v0_gpt2-small_lane_c` | `country_capital_v0` | `gpt2-small` | 3 | 3 |
| `country_capital_v0_pythia-70m_lane_a` | `country_capital_v0` | `pythia-70m` | 2 | 2 |
| `country_capital_v0_pythia-70m_lane_c` | `country_capital_v0` | `pythia-70m` | 2 | 2 |
| `ioi_v0_gpt2-small` | `ioi_v0` | `gpt2-small` | 1 | 0 |
| `ioi_v0_gpt2-small_lane_a` | `ioi_v0` | `gpt2-small` | 1 | 0 |
| `ioi_v0_gpt2-small_lane_c` | `ioi_v0` | `gpt2-small` | 1 | 0 |
| `sentiment_v0_gpt2-small_lane_c` | `sentiment_v0` | `gpt2-small` | 2 | 1 |

## Failing claims

### `arithmetic_v0_gpt2-small` / `h_arithmetic_v0_001`

- FAIL `base`: holdout_mean=+0.104794, source_mean=-0.008910, same_direction=False, above_floor=True
- FAIL `worded`: holdout_mean=-0.008910, source_mean=+0.104794, same_direction=False, above_floor=False

### `arithmetic_v0_gpt2-small` / `h_arithmetic_v0_003`

- PASS `base`: holdout_mean=+0.077538, source_mean=+0.010824, same_direction=True, above_floor=True
- FAIL `worded`: holdout_mean=+0.010824, source_mean=+0.077538, same_direction=True, above_floor=False

### `ioi_v0_gpt2-small` / `h_ioi_v0_001`

- PASS `base`: holdout_mean=-2.659831, source_mean=-0.178249, same_direction=True, above_floor=True
- PASS `paraphrase`: holdout_mean=-1.349007, source_mean=-0.833661, same_direction=True, above_floor=True
- FAIL `structural`: holdout_mean=+0.992509, source_mean=-2.004419, same_direction=False, above_floor=True

### `ioi_v0_gpt2-small_lane_a` / `h_sweep_ioi_v0_001`

- PASS `base`: holdout_mean=-2.586766, source_mean=-0.176566, same_direction=True, above_floor=True
- PASS `paraphrase`: holdout_mean=-1.358954, source_mean=-0.790472, same_direction=True, above_floor=True
- FAIL `structural`: holdout_mean=+1.005822, source_mean=-1.972860, same_direction=False, above_floor=True

### `ioi_v0_gpt2-small_lane_c` / `h_dla_ioi_v0_002`

- PASS `base`: holdout_mean=-2.530882, source_mean=-0.201039, same_direction=True, above_floor=True
- PASS `paraphrase`: holdout_mean=-1.415997, source_mean=-0.758481, same_direction=True, above_floor=True
- FAIL `structural`: holdout_mean=+1.013919, source_mean=-1.973439, same_direction=False, above_floor=True

### `sentiment_v0_gpt2-small_lane_c` / `h_dla_sentiment_v0_003`

- PASS `base`: holdout_mean=+0.224540, source_mean=+0.074009, same_direction=True, above_floor=True
- FAIL `review`: holdout_mean=+0.014428, source_mean=+0.179065, same_direction=True, above_floor=False
- PASS `statement`: holdout_mean=+0.133590, source_mean=+0.119484, same_direction=True, above_floor=True
