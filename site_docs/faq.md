# FAQ

## Scope

### Is this a ground-truth circuit benchmark?

No. AutoMechInterp verifies claim evidence under a fixed contract.

### Does `rejected` mean a claim is impossible?

No. It means the submitted evidence failed required gates.

### Why are acceptance rates often low?

The benchmark is reliability-first and intentionally penalizes weak controls, low robustness, and incomplete confirmatory evidence.

## Submissions

### Can I use my own discovery pipeline?

Yes. Any pipeline can submit if artifacts satisfy the bundle spec.

### How do I decide what to fix after failures?

Use `submission-review` outputs; they map failures to next experiments.

### Is cross-model transfer always required?

No. It depends on target tier and available transfer evidence.

## Reproducibility

### How do I run a full audit?

```bash
python main/reproducibility_audit.py
```

### Where are environment details written?

`main/output/repro/environment_manifest.json`

### Where are schema definitions?

- [File formats and schemas](reference/schemas.md)
- `docs/reference/claim_bundle_spec_v1.md`
