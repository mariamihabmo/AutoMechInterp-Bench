# Figure Inputs

## Accepted breadth map

### arithmetic_v0

| Model | Lane | Accepted claims |
|---|---|---|
| gpt2-small | canonical_real_repair_v1 | 3 |
| pythia-70m | canonical_real_repair_v1 | 1 |

### country_capital_v0

| Model | Lane | Accepted claims |
|---|---|---|
| gpt2-small | A | 3 |
| gpt2-small | B | 1 |
| gpt2-small | C | 3 |
| gpt2-small | canonical_real | 0 |
| pythia-70m | A | 2 |
| pythia-70m | B | 0 |
| pythia-70m | C | 2 |
| pythia-70m | canonical_real | 0 |

### docstring_v0

| Model | Lane | Accepted claims |
|---|---|---|
| gpt2-small | A | 1 |
| gpt2-small | B | 0 |
| gpt2-small | C | 1 |
| gpt2-small | canonical_real_repair_v1 | 0 |
| pythia-70m | canonical_real_repair_v1 | 0 |

### fact_recall_v0

| Model | Lane | Accepted claims |
|---|---|---|
| gpt2-small | B3 | 0 |
| gpt2-small | canonical_real_repair_v1 | 1 |
| pythia-70m | canonical_real_repair_v1 | 1 |

### gendered_pronoun_v0

| Model | Lane | Accepted claims |
|---|---|---|
| gpt2-small | canonical_real_repair_v1 | 1 |
| pythia-70m | canonical_real_repair_v1 | 0 |

### greater_than_v0

| Model | Lane | Accepted claims |
|---|---|---|
| gpt2-small | canonical_real_repair_v1 | 1 |
| pythia-70m | canonical_real_repair_v1 | 0 |

### ioi_v0

| Model | Lane | Accepted claims |
|---|---|---|
| gpt2-small | A | 1 |
| gpt2-small | B | 0 |
| gpt2-small | B3 | 0 |
| gpt2-small | C | 1 |
| gpt2-small | prompt_variant_repair_v1 | 1 |
| pythia-70m | canonical_real | 0 |

### sentiment_v0

| Model | Lane | Accepted claims |
|---|---|---|
| gpt2-small | A | 0 |
| gpt2-small | B | 0 |
| gpt2-small | C | 2 |
| gpt2-small | canonical_real | 0 |
| pythia-70m | A | 0 |
| pythia-70m | B | 0 |
| pythia-70m | C | 0 |
| pythia-70m | canonical_real | 0 |

## Failure family counts

| Family | Count |
|---|---|
| statistics | 140 |
| robustness | 76 |
| controls | 59 |
| causal | 46 |
| transfer | 28 |
