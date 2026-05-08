# Submitting A Claim Bundle

This page defines a practical, reproducible submission workflow.

## Required files

- `protocol.yaml`
- `hypothesis.jsonl`
- `evaluation_result.json`
- `manifest.json`

Optional:

- `cross_model_results.json`

## Submission lifecycle

1. Build bundle artifacts from discovery outputs.
2. Validate schema and hash integrity.
3. Run evaluator and report generation.
4. Run deterministic submission review.
5. Resolve failed gate clusters.
6. Resubmit with updated evidence.

## Mandatory validation commands

```bash
python -m automechinterp_evaluator.cli evaluate \
  --bundle /path/to/bundle \
  --output /path/to/bundle/result.json

python -m automechinterp_evaluator.cli report \
  --bundle /path/to/bundle \
  --output /path/to/bundle/stage_gate_report.md

python -m automechinterp_evaluator.cli submission-review \
  --bundle /path/to/bundle \
  --reruns 3 \
  --output-json /path/to/bundle/submission_review.json \
  --output-md /path/to/bundle/submission_review.md
```

## What makes a submission strong

- complete confirmatory and exploratory slices where required
- coherent control evidence
- robust behavior across perturbations
- statistical checks that pass under declared policy
- deterministic rerun agreement

## What usually blocks acceptance

| Failure family | Typical symptom | Suggested follow-up |
|---|---|---|
| confirmatory completeness | `confirmatory_present` fails | regenerate confirmatory slice |
| method sensitivity | unstable outcomes across methods | tighten intervention protocol consistency |
| robustness | effect collapses under perturbations | add robustness-focused follow-up experiments |
| controls leakage | strong control effects | redesign controls and baseline comparisons |
| statistical rigor | CI/power/multiplicity failures | increase evidence quality and sample adequacy |

## Submission package recommendation

When sharing externally, include:

- full bundle directory
- `submission_review.json`
- `submission_review.md`
- protocol hash/version
- environment manifest path
