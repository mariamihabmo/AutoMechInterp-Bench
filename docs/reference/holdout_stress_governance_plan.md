# Holdout Stress Governance Plan

This document describes the intended governance path for stress-test holdouts.

## Why this exists

Evaluator-authored synthetic negatives are useful but insufficient.
Without a holdout policy, benchmark maintainers can gradually overfit stress generators to the released gate taxonomy.

## Planned holdout policy

1. Maintain a hidden stress set outside the public repo.
2. Separate authorship of holdout negatives from gate-maintainer implementation where feasible.
3. Score public releases against the holdout set only at major benchmark versions.
4. Publish aggregate holdout results, not the item-level generators, until a rotation policy exists.

## Current status

This plan is documented, but a fully operational blinded holdout workflow is still open work.
Do not describe the benchmark as holdout-hardened today.

See [`open_item_blinded_holdout.md`](open_item_blinded_holdout.md) for the operational
plan: definition of done, first concrete step (a labeled "rehearsal" closes the
plumbing sub-item without an external collaborator), evidence required to close,
and anti-patterns. The other three open items have parallel one-page operational plans:

- [`open_item_cross_model_transfer.md`](open_item_cross_model_transfer.md)
- [`open_item_third_party_bundle_ecosystem.md`](open_item_third_party_bundle_ecosystem.md)
- [`open_item_broad_external_validity.md`](open_item_broad_external_validity.md)
