# File Formats And Schemas

This page is a practical schema map for bundle authors.

## Required files

- `protocol.yaml`
- `hypothesis.jsonl`
- `evaluation_result.json`
- `manifest.json`

## `protocol.yaml`

Defines the evaluation contract:

- task/model metadata
- execution grid
- control configuration
- gate thresholds
- statistical policy
- budget and constraints

## `hypothesis.jsonl`

Each row should include:

- stable `hypothesis_id`
- component type and location
- intervention direction
- claim text
- lane/provider metadata where available

## `evaluation_result.json`

Contains raw intervention cells used for gate computation.

Important properties:

- complete grid coverage for required slices
- consistent field typing
- explicit intervention and control records

## `manifest.json`

Contains SHA-256 hashes for required files.

Regenerate this file whenever any bundle artifact byte changes.

## Strongly recommended validation sequence

```bash
python -m automechinterp_evaluator.cli evaluate --bundle /path/to/bundle --output /path/to/bundle/result.json
python -m automechinterp_evaluator.cli report --bundle /path/to/bundle --output /path/to/bundle/stage_gate_report.md
python -m automechinterp_evaluator.cli submission-review --bundle /path/to/bundle --reruns 3 --output-json /path/to/bundle/submission_review.json --output-md /path/to/bundle/submission_review.md
```

## Canonical spec docs

- `docs/reference/claim_bundle_spec_v1.md`
- `docs/reference/BENCHMARK_CONTRACT.md`
