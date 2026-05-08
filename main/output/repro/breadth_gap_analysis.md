# Breadth-Gap Forensics

- Total task-model cells: **16**
- Cells with at least one accepted claim: **11**
- Cells with zero accepted claims: **5**

## Highest-priority breadth targets

These are zero-acceptance task-model cells whose closest-to-pass claim has
the fewest failed gates. They are the cells where a small number of
additional evidence improvements (or evidence collection for currently
not-evaluated gates) could plausibly produce the next accepted claim
*without changing the contract*.

| task | model | closest-to-pass: bundle | failed gates | not-evaluated gates |
|---|---|---|---|---|
| `docstring_v0` | `pythia-70m` | `docstring_v0_pythia-70m` | 1 | 1 |
| `sentiment_v0` | `pythia-70m` | `sentiment_v0_pythia-70m_lane_a` | 1 | 1 |
| `ioi_v0` | `pythia-70m` | `ioi_v0_pythia-70m` | 2 | 1 |
| `greater_than_v0` | `pythia-70m` | `greater_than_v0_pythia-70m` | 3 | 1 |
| `gendered_pronoun_v0` | `pythia-70m` | `gendered_pronoun_v0_pythia-70m` | 4 | 1 |

## Per-cell failure breakdown (zero-acceptance cells)

### `docstring_v0` × `pythia-70m`

- Evaluated claims: **3**, all rejected.
- Top failed gates: `method_sensitivity` (3), `multiplicity` (2), `confirmatory_ci` (1)
- Closest-to-pass: `docstring_v0_pythia-70m` / `h_docstring_v0_003`
  - 1 failed gates: `method_sensitivity`
  - 1 not-evaluated gates: `cross_model_transfer`

### `gendered_pronoun_v0` × `pythia-70m`

- Evaluated claims: **3**, all rejected.
- Top failed gates: `multiplicity` (3), `negative_controls` (3), `causal_effect` (2), `confirmatory_ci` (2), `method_sensitivity` (2), `robustness` (2)
- Closest-to-pass: `gendered_pronoun_v0_pythia-70m` / `h_gendered_pronoun_v0_002`
  - 4 failed gates: `negative_controls`, `method_sensitivity`, `confirmatory_ci`, `multiplicity`
  - 1 not-evaluated gates: `cross_model_transfer`

### `greater_than_v0` × `pythia-70m`

- Evaluated claims: **3**, all rejected.
- Top failed gates: `multiplicity` (3), `negative_controls` (3), `confirmatory_ci` (2), `method_sensitivity` (1)
- Closest-to-pass: `greater_than_v0_pythia-70m` / `h_greater_than_v0_001`
  - 3 failed gates: `negative_controls`, `method_sensitivity`, `multiplicity`
  - 1 not-evaluated gates: `cross_model_transfer`

### `ioi_v0` × `pythia-70m`

- Evaluated claims: **3**, all rejected.
- Top failed gates: `method_sensitivity` (3), `multiplicity` (3), `confirmatory_ci` (2), `causal_effect` (1), `robustness` (1)
- Closest-to-pass: `ioi_v0_pythia-70m` / `h_ioi_v0_002`
  - 2 failed gates: `method_sensitivity`, `multiplicity`
  - 1 not-evaluated gates: `cross_model_transfer`

### `sentiment_v0` × `pythia-70m`

- Evaluated claims: **12**, all rejected.
- Top failed gates: `causal_effect` (9), `robustness` (9), `confirmatory_ci` (7), `multiplicity` (7), `negative_controls` (7), `baseline_superiority` (5)
- Closest-to-pass: `sentiment_v0_pythia-70m_lane_a` / `h_sweep_sentiment_v0_001`
  - 1 failed gates: `negative_controls`
  - 1 not-evaluated gates: `cross_model_transfer`
