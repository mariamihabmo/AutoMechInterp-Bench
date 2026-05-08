# Gates And Suites

## Gate outcome model

Every gate emits one of:

- `pass`
- `fail`
- `not_evaluated`

Tri-state outputs preserve distinction between contradictory evidence and missing evidence.

## Core and optional gates

Core gates determine acceptance eligibility.

Optional gates add extra evidentiary dimensions (for example transfer support).

## Suite-level rationale

| Suite | Primary risk mitigated |
|---|---|
| Causal | spurious correlation mistaken for mechanism |
| Controls | leakage or baseline confounds |
| Robustness | brittle, perturbation-sensitive claims |
| Method sensitivity | method-specific artifacts |
| Statistical rigor | chance-driven acceptance |
| Integrity | invalid or drifting artifacts |

## Reading gate failures

High concentration in one suite usually indicates workflow-level issues rather than isolated claim mistakes.

Example: widespread `method_sensitivity` failures suggest intervention methodology instability.

## Stress testing relationship

Stress scripts estimate how acceptance behavior changes when specific gate protections are weakened.

See [Stress testing overview](stress/index.md).
