# Demo (2-5 min)

This demo runs template bundle -> evaluation -> report -> rerun check.

## 1) Create template bundle

```bash
python -m automechinterp_evaluator.cli init-template --output-dir /tmp/ami_demo
```

## 2) Evaluate bundle

```bash
python -m automechinterp_evaluator.cli evaluate \
  --bundle /tmp/ami_demo \
  --output /tmp/ami_demo/result.json
```

## 3) Render markdown report

```bash
python -m automechinterp_evaluator.cli report \
  --bundle /tmp/ami_demo \
  --output /tmp/ami_demo/stage_gate_report.md
```

## 4) Run deterministic review

```bash
python -m automechinterp_evaluator.cli submission-review \
  --bundle /tmp/ami_demo \
  --reruns 3 \
  --output-json /tmp/ami_demo/submission_review.json \
  --output-md /tmp/ami_demo/submission_review.md
```

## Inspect

- `result.json`
- `stage_gate_report.md`
- `submission_review.md`
