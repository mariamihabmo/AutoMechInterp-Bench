# Tutorial: First Run

This tutorial walks through a complete first evaluation and interpretation loop.

## Goal

Produce one valid bundle run and understand how to read its outputs.

## 1) Create template bundle

```bash
python -m automechinterp_evaluator.cli init-template --output-dir /tmp/ami_tutorial
```

## 2) Evaluate

```bash
python -m automechinterp_evaluator.cli evaluate \
  --bundle /tmp/ami_tutorial \
  --output /tmp/ami_tutorial/result.json
```

## 3) Generate report

```bash
python -m automechinterp_evaluator.cli report \
  --bundle /tmp/ami_tutorial \
  --output /tmp/ami_tutorial/stage_gate_report.md
```

## 4) Run deterministic review

```bash
python -m automechinterp_evaluator.cli submission-review \
  --bundle /tmp/ami_tutorial \
  --reruns 3 \
  --output-json /tmp/ami_tutorial/submission_review.json \
  --output-md /tmp/ami_tutorial/submission_review.md
```

## 5) Read outputs in order

1. `failed_checks`
2. `not_evaluated_checks`
3. `gate_outcomes`
4. `evidence_tier`

## 6) Plan next experiment

Use the review markdown guidance to design a targeted resubmission.
