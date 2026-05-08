# The Benchmark Contract

AutoMechInterp enforces a single principle: discovery and acceptance are separate operations.

## Contract principle

Discovery tools may propose hypotheses, but only the deterministic evaluator determines acceptance outcomes.

## Gate families in scope

- causal evidence
- negative controls
- robustness checks
- method sensitivity checks
- statistical rigor checks
- integrity/provenance checks

## Threat model

The contract is designed to reduce:

- cherry-picked evidence that ignores controls
- fragile claims that fail perturbation tests
- method-specific artifacts mistaken for mechanisms
- chance-driven acceptance from weak statistical policy

## Non-goals

- proving universal mechanistic ground truth
- replacing scientific judgment and domain context
- ranking discovery tools independent of evidence contract

## Why this framing is useful

A frozen acceptance contract enables longitudinal comparability: you can track whether claim quality improves without changing what counts as acceptance.
