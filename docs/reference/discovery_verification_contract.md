# Discovery vs Verification Contract

## Discovery side (agent)
Allowed:
1. Propose hypotheses.
2. Suggest intervention targets.
3. Suggest likely failure modes.

Not allowed:
1. Assign final pass/fail verdicts.
2. Edit frozen protocol.
3. Use certainty language reserved for passed claims.

## Verification side (system)
Required:
1. Validate artifact integrity and schema.
2. Execute deterministic gate calculations.
3. Emit transparent pass/fail reasons.

Not allowed:
1. Inject undeclared methods or thresholds.
2. Skip control/robustness/sensitivity checks.
3. Accept claims with missing confirmatory requirements.

## Hand-off boundary
The boundary artifact is `hypothesis.jsonl`.
Everything after that point is system-governed by `protocol.yaml`.

## Acceptance definition
A claim is accepted only when all hard gates pass under the frozen protocol and all artifact integrity checks pass.
