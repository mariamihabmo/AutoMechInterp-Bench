# Determinism And Integrity

## Operational definition

For fixed code, artifacts, seeds, and environment versions, evaluator outcomes should match across reruns.

## Integrity mechanism

`manifest.json` binds required artifacts by SHA-256 hash.

If any required file changes, the bundle must be re-hashed.

## Typical determinism breakers

- artifact bytes changed after manifest creation
- hidden randomness in upstream generation
- environment/library drift
- inconsistent protocol versions across runs

## How to verify determinism

```bash
python -m automechinterp_evaluator.cli submission-review \
  --bundle /path/to/bundle \
  --reruns 3 \
  --output-json /path/to/bundle/submission_review.json \
  --output-md /path/to/bundle/submission_review.md
```

## What to report publicly

- rerun count and agreement status
- protocol hash/version
- environment manifest path
- any known nondeterministic components
