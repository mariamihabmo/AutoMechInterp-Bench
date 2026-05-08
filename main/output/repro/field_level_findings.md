# Field-Level Findings

- Claims analyzed: **109**
- Accepted: **26**
- Rejected: **83**
- Acceptance rate: **23.85%** (95% CI: [16.83%, 32.66%])

## Gate-family failure counts

| Gate family | Count |
|---|---|
| causal | 46 |
| controls | 59 |
| robustness | 76 |
| statistics | 140 |
| transfer | 28 |

## Failed gates

| Gate | Count |
|---|---|
| multiplicity | 48 |
| robustness | 47 |
| causal_effect | 46 |
| confirmatory_ci | 41 |
| negative_controls | 40 |
| power_adequacy | 33 |
| method_sensitivity | 29 |
| cross_model_transfer | 28 |
| baseline_superiority | 19 |
| effect_size_practical | 18 |

## Acceptance by task

| Task | Claims | Accepted | Acceptance |
|---|---|---|---|
| arithmetic_v0 | 6 | 4 | 66.67% |
| country_capital_v0 | 24 | 11 | 45.83% |
| docstring_v0 | 15 | 2 | 13.33% |
| fact_recall_v0 | 9 | 2 | 22.22% |
| gendered_pronoun_v0 | 6 | 1 | 16.67% |
| greater_than_v0 | 6 | 1 | 16.67% |
| ioi_v0 | 19 | 3 | 15.79% |
| sentiment_v0 | 24 | 2 | 8.33% |

## Acceptance by model

| Model | Claims | Accepted | Acceptance |
|---|---|---|---|
| gpt2-small | 67 | 20 | 29.85% |
| pythia-70m | 42 | 6 | 14.29% |

## Acceptance by component type

| Component | Claims | Accepted | Acceptance |
|---|---|---|---|
| head | 84 | 25 | 29.76% |
| mlp | 1 | 0 | 0.00% |
| mlp_neuron | 18 | 1 | 5.56% |
| sae_feature | 6 | 0 | 0.00% |

## Directional fragility

- Missing sufficiency claims: 15
- Missing necessity claims: 15
- Claims failing bidirectional gate: 0

## Policy sensitivity

- Full-contract acceptance rate: 23.85%
- Most sensitive counterfactual: no_controls_suite
- Acceptance under that counterfactual: 34.86%
