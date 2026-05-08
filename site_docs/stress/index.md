# Stress Tests Overview

Stress tests estimate how the verifier behaves under degraded or adversarial conditions.

## Why this matters

A verifier can appear strong on nominal bundles but still leak false accepts under targeted pressure. Stress testing quantifies that risk.

## Three regimes

### 1) Suite-targeted ablations

Deliberately remove selected gate suites and measure acceptance leakage.

### 2) Evaluator-agnostic latent stress

Generate perturbations through latent factors rather than direct gate-aware templates.

### 3) Red-team probes

Use adaptive and near-miss attacks to test whether bundles can bypass contract intent.

## Primary metrics to inspect

- acceptance-rate change relative to baseline
- tier migration counts
- gate-family concentration in bypassed cases
- stability of findings across tasks and models

## Interpretation guidance

- Large uplift under a suite ablation indicates that suite is carrying important anti-leakage load.
- Small uplift does not automatically mean a suite is useless; investigate task/model stratification.
- Red-team bypass success is a signal for hardening priorities, not a reason to discard the whole contract.

## Recommended reporting pattern

For each stress regime report:

- baseline acceptance rate
- stressed acceptance rate
- absolute and relative uplift
- confidence interval where available
- tier-change decomposition

## Related pages

- [Suite-targeted ablations](ablations.md)
- [Evaluator-agnostic latent stress](latent.md)
- [Red-team probes](redteam.md)
