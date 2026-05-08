# Contributing

## Local dev loop

```bash
python -m pytest packages/evaluator/tests -q
python -m pytest packages/runner/tests -q
python scripts/generate_docs_from_json.py
```

## Contribution types

- new task implementations
- new discovery-lane integrations
- gate diagnostics and reporting improvements
- docs/tutorial improvements
- reproducibility and CI hardening

## Pull request expectations

- tests for behavior changes
- docs updates for interface/contract changes
- migration notes for protocol-impacting changes

## Suggested first contributions

- improve failure diagnostic text clarity
- add bundle examples for new component types
- strengthen schema validation error messages
- add tutorial steps for common resubmission workflows
