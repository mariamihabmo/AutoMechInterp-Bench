# Bundle Checklist

Use this checklist before any public submission.

## Contract and integrity checks

- [ ] Required files exist in expected paths.
- [ ] `manifest.json` SHA-256 hashes match current bytes.
- [ ] `protocol.yaml` version is pinned and intentional.
- [ ] Hypothesis IDs are unique and stable.
- [ ] Execution grid has no accidental holes.
- [ ] Intervention directions are valid (`sufficiency_patch`, `necessity_ablate`).

## Evidence completeness checks

- [ ] Confirmatory slice is present where required.
- [ ] Exploratory slice is present where required.
- [ ] Required control families are present.
- [ ] Enough cells exist for statistical checks.

## Common rejection clusters

- missing confirmatory evidence
- method sensitivity instability
- robustness failures across perturbations
- negative control leakage
- statistical rigor failures (`confirmatory_ci`, `multiplicity`, `power_adequacy`)

## Final pre-submit run

```bash
python -m automechinterp_evaluator.cli submission-review \
  --bundle /path/to/bundle \
  --reruns 3 \
  --output-json /path/to/bundle/submission_review.json \
  --output-md /path/to/bundle/submission_review.md
```
