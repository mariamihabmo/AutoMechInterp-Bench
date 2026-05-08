# Contract Hardening V1 Migration Decision

- Decision: **defer**
- Decision status: **deferred_pending_external_validation**
- Adoptable under pre-registered criteria: **False**

## Stress Tradeoff

| Contract | Status | False accepts | FAR | 95% CI |
|---|---|---:|---:|---|
| Current | `benchmark_authored_rehearsal_not_independent_evidence` | 0/200 | 0.0% | [0.0%, 1.9%] |
| V1 candidate | `benchmark_authored_rehearsal_not_independent_evidence` | 0/200 | 0.0% | [0.0%, 1.9%] |

## Retention Tradeoff

- Accepted claims before: **26**
- Accepted claims after: **1**
- Accepted-claim retention: **3.8%**
- Tasks with accepted claims after: **1** (fact_recall_v0)
- Bundles changed: **16**

## Criteria

- `independent_evidence`: **False**
- `candidate_ci_upper_below_5pct`: **True**
- `current_ci_lower_above_candidate_point`: **False**
- `accepted_claim_retention_at_least_60pct`: **False**
- `accepted_task_retention_documented`: **True**

## Human Rationale

Defer adoption until an externally authored negative set or external custodian run validates the stress reduction under the pre-registered protocol.

## Claim Boundary

V1 is not adopted by this artifact unless decision=adopt_next_major and all pre-registered criteria are met. Rehearsal or benchmark-authored stress is not independent validation.
