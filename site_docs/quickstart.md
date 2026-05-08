# Quickstart (10 min)

This quickstart is designed to get you from zero to a deterministic bundle review with outputs you can interpret immediately.

## Goal

By the end of this flow you will have:

- run evaluator and runner tests
- executed deterministic submission review on a bundle
- inspected gate failures and remediation guidance
- run a full reproducibility audit command

## Step 1: validate packages

```bash
# Recommended once per fresh checkout
python -m pip install -e packages/evaluator -e packages/runner

# Evaluator tests
python -m pytest packages/evaluator/tests -q

# Runner tests
python -m pytest packages/runner/tests -q
```

If either suite fails, resolve environment issues before evaluating claims.

## Step 2: run deterministic submission review

```bash
# If you skipped editable installs, prefix with:
# PYTHONPATH=packages/evaluator/src

python -m automechinterp_evaluator.cli submission-review \
  --bundle /path/to/bundle \
  --reruns 3 \
  --output-json /path/to/bundle/submission_review.json \
  --output-md /path/to/bundle/submission_review.md
```

This command runs evaluation multiple times to check rerun agreement and writes workflow guidance.

## Step 3: inspect outputs in this order

1. `submission_review.json`
2. `submission_review.md`
3. bundle-level `result.json` (if generated in your workflow)
4. bundle-level `stage_gate_report.md`

## Step 4: run repository reproducibility audit

```bash
# from repository root
python main/reproducibility_audit.py
```

This produces environment and benchmark summary artifacts under `main/output/repro/`.
It is a cached-artifact audit rather than a live model rerun: the current
contract runs 43 commands, fails on missing/stale outputs, and ends with the
repo-integrity, release-overclaim, and README/paper headline-number drift
checks.

## Quick interpretation checklist

- Are failures concentrated in one gate family?
- Are missing slices causing `not_evaluated` outcomes?
- Do reruns agree across all claims?
- Is failure remediation specific enough to guide next experiments?

## Common first-run problems

| Problem | Likely cause | First fix |
|---|---|---|
| schema parse failure | malformed bundle file | validate keys/types in `hypothesis.jsonl` and `evaluation_result.json` |
| manifest mismatch | file changed after hashing | regenerate `manifest.json` |
| many `confirmatory_present` failures | missing confirmatory slice | regenerate raw cells with required slices |
| many `method_sensitivity` failures | unstable intervention setup | review intervention method consistency and control setup |

## Next docs

- [Setup](setup.md)
- [Run the evaluator](run.md)
- [Interpret results](interpret.md)
- [Submitting a claim bundle](submit.md)
