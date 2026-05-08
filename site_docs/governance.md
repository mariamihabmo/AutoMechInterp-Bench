# Governance And Migrations

## Versioning principle

Any change that can alter acceptance outcomes should be versioned and documented.

## What must be documented for protocol changes

- rationale for the change
- expected impact on historical comparability
- migration guidance for bundle authors
- compatibility implications for third-party evaluators

## Migration workflow

1. propose change and rationale
2. implement with tests
3. update docs and changelog
4. run compatibility vectors
5. communicate migration notes

## Determinism commitment

Protocol evolution should preserve deterministic behavior for fixed artifacts and pinned environments.

## Supporting docs

- `docs/reference/protocol_governance_and_migrations.md`
- `docs/reference/holdout_stress_governance_plan.md`
