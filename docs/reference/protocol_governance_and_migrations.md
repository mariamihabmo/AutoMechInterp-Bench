# Protocol Governance and Migrations

## Governance principles

1. Protocol changes are benchmark changes.
2. Evidence-tier semantics must not drift silently.
3. Optional gates may be added, but their effect on acceptance must be documented.
4. Generated summaries and papers must be refreshed after governance-relevant changes.

## Migration expectations

1. Bump the protocol or methodology version when gate semantics or thresholds materially change.
2. Record the motivation, expected impact, and compatibility implications.
3. Keep older bundles interpretable; do not rewrite history by silently re-labeling prior tiers.
4. If a migration changes headline counts, regenerate the affected summaries.

## Current release note

The current hardening pass canonicalizes tier names and adds normalized `gate_outcomes`.
Older names such as `causal_confirmed` and `causal_confirmed_transferable` should be treated as historical only.

## Contract-Hardening V1 Decision Status

`main/output/repro/contract_hardening_v1_summary.json` records a candidate
threshold migration that sharply lowers benchmark-authored fresh agnostic
false accepts, but demotes current accepted evidence. The decision record is
`methodology/contract_hardening_v1_migration_decision.md`.

Current status:

1. V1 is **not** the released contract.
2. V1 adoption is deferred because the current evidence is benchmark-authored
   rehearsal/stress evidence, not independent validation.
3. A future adoption decision must score the same externally authored negative
   set under current and V1 contracts and report accepted-claim and
   accepted-task retention before paper claims are upgraded.
