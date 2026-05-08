# How To Run In CI

## Baseline CI pipeline

```bash
python -m pytest packages/evaluator/tests -q
python -m pytest packages/runner/tests -q
python tools/check_headline_numbers.py
python scripts/generate_docs_from_json.py
```

## Deterministic checks in CI

For at least one representative bundle:

```bash
python -m automechinterp_evaluator.cli submission-review \
  --bundle main/output/real_multi_task/ioi_v0_gpt2-small \
  --reruns 3
```

## Recommended CI artifacts

- `result.json`
- `stage_gate_report.md`
- `submission_review.json`
- `submission_review.md`
- reproducibility audit outputs

## Release audit job

For release branches, run the materialized audit as a separate job so the fast
test lane stays useful:

```bash
python main/reproducibility_audit.py
```

The current audit contract runs 43 cached-artifact commands and fails if any
command fails, any expected output is missing, or any expected output is stale
relative to the audit start time. It does not execute live model interventions.

## Release-gating recommendation

Block release if:

- tests fail
- deterministic rerun mismatch appears
- required docs generation fails
- headline numbers in README/papers drift from canonical artifacts
- the materialized audit reports failed, missing, or stale outputs
