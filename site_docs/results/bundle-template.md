# Bundle Page Template

Use this template when publishing one evaluated bundle page.

## 1) Metadata

- bundle ID
- task
- model
- lane/provider
- protocol version/hash
- evaluation timestamp

## 2) Reproduce commands

```bash
python -m automechinterp_evaluator.cli evaluate \
  --bundle <bundle-dir> \
  --output <bundle-dir>/result.json

python -m automechinterp_evaluator.cli report \
  --bundle <bundle-dir> \
  --output <bundle-dir>/stage_gate_report.md

python -m automechinterp_evaluator.cli submission-review \
  --bundle <bundle-dir> \
  --reruns 3 \
  --output-json <bundle-dir>/submission_review.json \
  --output-md <bundle-dir>/submission_review.md
```

## 3) Outcome summary

- final evidence tier
- `failed_checks`
- `not_evaluated_checks`
- top diagnostics

## 4) Gate matrix

Provide a table for all gate outcomes (`pass` / `fail` / `not_evaluated`) per claim.

## 5) Artifact links

- `protocol.yaml`
- `hypothesis.jsonl`
- `evaluation_result.json`
- `manifest.json`
- `result.json`
- `stage_gate_report.md`
- `submission_review.json`
- `submission_review.md`

## 6) Resubmission notes

If not accepted, include planned follow-up experiments tied directly to failed gate families.
