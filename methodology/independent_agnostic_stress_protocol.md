# Independent Agnostic Stress Protocol

**Status:** protocol draft, not yet evidence-bearing.  
**Purpose:** define how an independent negative author can test the current
AutoMechInterp contract and a candidate hardened contract without seeing or
tuning against the gate implementation.

## Scientific Question

Can an independently authored, evaluator-agnostic negative set distinguish:

1. the current released contract, which on the latest fresh release-grade refresh under the full statistical budget leaks 0/200 benchmark-authored fresh
   negatives (Wilson 95% CI [0.0%, 1.9%]); under a reduced rehearsal
   budget (128 bootstrap / 128 permutation) the same generator family leaks
   49/200 (24.5%, [19.1%, 30.9%]) on a different rotated namespace, so the
   0/200 number should be read as a within-generator floor under full
   statistical rigor and not as an external Goodhart-resistance claim, from
2. contract-hardening V1, which leaks 0/200 in each of two benchmark-authored
   rotated namespaces (parity with the released contract) but retains only
   1/26 accepted claims and accepted claims in 1/8 tasks?

## Roles

1. **Gate maintainer:** maintains evaluator code and does not author the
   independent negative set.
2. **Negative author:** authors negative claims without changing the evaluator.
3. **Runner/custodian:** runs both current and candidate contracts and records
   aggregate outputs.

The same person should not be both gate maintainer and negative author for an
evidence-bearing run.

## Visibility Conditions

The negative author may see:

1. public task/model list,
2. claim-bundle schema,
3. high-level statement that claims are evaluated by causal, controls,
   robustness, statistical, transfer, and integrity requirements,
4. examples of public bundles if the run is explicitly labeled
   "public-aware."

The negative author should not see:

1. exact V1 threshold changes,
2. leaked benchmark-authored negatives,
3. per-gate implementation details beyond public documentation,
4. intermediate scoring results during generation.

If the author does see any of these, record the run as "evaluator-aware" rather
than "evaluator-agnostic."

## Negative Set Requirements

Minimum evidence-bearing set:

1. at least 200 negatives,
2. fixed generator version or signed generation notebook,
3. fixed seed or archive hash,
4. no iterative scoring feedback,
5. JSONL or bundle package conforming to the independent negative spec,
6. author attestation describing what public materials were consulted.

Recommended stronger set:

1. 500+ negatives,
2. stratified across at least three task families,
3. at least two model families,
4. one explicit adaptive slice and one near-miss slice,
5. hidden item IDs until after aggregate scoring.

## Evaluation Conditions

Run both:

1. current released contract,
2. contract-hardening V1 candidate.

For each condition report:

1. false accepts,
2. total negatives,
3. false-accept rate,
4. Wilson 95% CI,
5. gate families responsible for rejected negatives,
6. leaked negative summaries stripped of private generation details,
7. runtime and software environment.

## Pre-Registered V1 Decision Criteria

V1 may be proposed for the next major protocol version only if all are true:

1. V1 false-accept 95% CI upper bound is below 5% on the independent set.
2. Current-contract false-accept rate is meaningfully higher than V1 under the
   same negative set.
3. Accepted-claim retention remains at least 60%.
4. Accepted-task retention loss is explicitly judged acceptable by governance.
5. The decision document reports demoted accepted claims and demoted tasks.

V1 must not be called "strictly better" unless the decision document shows both
stress improvement and acceptable released-claim retention.

## Required Public Artifacts

1. `main/output/repro/independent_agnostic_stress_current_<version>.json`
2. `main/output/repro/independent_agnostic_stress_hardened_<version>.json`
3. `methodology/contract_hardening_v1_migration_decision.md`
4. negative-author attestation or anonymized provenance statement
5. update to `docs/reference/protocol_governance_and_migrations.md`

## Forbidden Moves

1. Do not inspect independent leaks, change V1, and rerun on the same set while
   calling it confirmatory.
2. Do not hide a bad independent result.
3. Do not describe benchmark-authored fresh stress as independent validation.
4. Do not adopt V1 silently inside a paper without a protocol-version decision.
