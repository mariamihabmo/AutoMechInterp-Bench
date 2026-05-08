# Artifact Spec Overview

This page summarizes what each bundle file is responsible for.

## `protocol.yaml`

Defines the contract for an evaluation run:

- task and model metadata
- execution grid and controls
- gate policy and thresholds
- statistical policy
- claim budget and constraints

## `hypothesis.jsonl`

Registers submitted claims:

- unique hypothesis IDs
- component type and location
- claim statement and direction
- lane/provider metadata

## `evaluation_result.json`

Contains raw intervention cells consumed by gate logic.

Typical fields include intervention mode, slice identity, effects, controls, and statistics inputs.

## `manifest.json`

Binds artifact integrity using SHA-256 hashes.

If bundle files change, manifest hashes must be regenerated.

## Full schema references

- [File formats and schemas](reference/schemas.md)
- `docs/reference/claim_bundle_spec_v1.md`
