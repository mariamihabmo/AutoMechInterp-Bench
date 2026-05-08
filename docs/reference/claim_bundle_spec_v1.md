# Claim Bundle Spec v1

This document specifies the canonical four-artifact claim bundle:

1. `protocol.yaml`
2. `hypothesis.jsonl`
3. `evaluation_result.json`
4. `manifest.json`

## Required properties

1. `protocol.yaml` defines the frozen unit of work, execution grid, controls, gates, and statistical policy.
2. `hypothesis.jsonl` contains structured claims only; it must not contain verdict fields.
3. `hypothesis.jsonl` must not contain duplicate structured claims under different `hypothesis_id` values.
4. `evaluation_result.json` contains raw cell-level measurements and provenance fields.
5. `manifest.json` binds file contents by SHA-256.

## Compatibility expectations

1. Evidence tiers are canonicalized to `cross_model_confirmed`, `single_model_confirmed`, `causal_plus_robustness`, `causal_tested_unstable`, `suggestive`, and `rejected`.
2. Gate outcomes are emitted as `pass`, `fail`, or `not_evaluated`.
3. Third-party implementations should validate behavior against the repository's reference vectors.

## Non-goals

1. The spec does not define mechanistic truth.
2. The spec does not force any particular discovery lane.
3. The spec does not guarantee immunity to benchmark gaming.
