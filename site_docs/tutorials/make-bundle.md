# Tutorial: Create A Bundle

This tutorial focuses on authoring a high-quality bundle from your own discovery pipeline.

## 1) Write protocol

Create `protocol.yaml` with fixed thresholds, control settings, and statistical policy.

## 2) Register hypotheses

Create `hypothesis.jsonl` with stable IDs, component metadata, and intervention directions.

## 3) Generate raw cells

Run your lane-specific execution and write `evaluation_result.json` with complete required slices.

## 4) Bind integrity hashes

Generate `manifest.json` from final file bytes.

## 5) Validate end-to-end

```bash
python -m automechinterp_evaluator.cli evaluate --bundle /path/to/bundle --output /path/to/bundle/result.json
python -m automechinterp_evaluator.cli report --bundle /path/to/bundle --output /path/to/bundle/stage_gate_report.md
python -m automechinterp_evaluator.cli submission-review --bundle /path/to/bundle --reruns 3 --output-json /path/to/bundle/submission_review.json --output-md /path/to/bundle/submission_review.md
```

## 6) Verify resubmission readiness

Do not resubmit until top failure clusters are addressed with targeted new evidence.
