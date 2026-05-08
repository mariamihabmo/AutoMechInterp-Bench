# Evidence Tiers

## Tier taxonomy

### Accepted tiers

- `single_model_confirmed`
- `cross_model_confirmed`

### Intermediate tiers

- `causal_plus_robustness`
- `causal_tested_unstable`
- `suggestive`

### Rejected tier

- `rejected`

## How tiers are produced

Tiers are derived from gate outcomes, slice requirements, and optional transfer evidence.

They are not manual labels.

## Interpretation guidance

- Use tiers to summarize evidence quality.
- Use gate diagnostics to determine next experiments.
- Treat intermediate tiers as prioritized follow-up states, not terminal outcomes.

## Reporting recommendation

When publishing any tier summary, include:

- failed gate decomposition
- not-evaluated decomposition
- protocol version/hash
- deterministic rerun status
