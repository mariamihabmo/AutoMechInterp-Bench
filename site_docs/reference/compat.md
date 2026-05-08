# Compatibility Vectors

Compatibility vectors are canonical test cases for evaluator behavior.

## Why they matter

If multiple labs implement evaluators, compatibility vectors let you verify that they agree on gate outcomes and tier classification under the same inputs.

## Generate vectors

```bash
python -m automechinterp_evaluator.cli reference-vectors
```

## What to compare

- `gate_outcomes` values
- `evidence_tier`
- `failed_checks` and `not_evaluated_checks`
- rerun determinism behavior

## When to re-run compatibility checks

- after gate logic changes
- after tier-classification updates
- after protocol migration
- before releasing a third-party compatible evaluator
