# CLI Reference

This page summarizes the primary evaluator CLI commands and how they are typically used together.

Repo-local note: these commands assume either `pip install -e packages/evaluator -e packages/runner`
or an explicit `PYTHONPATH=packages/evaluator/src` for evaluator-only CLI use.

## Command map

| Command | Purpose | Typical output |
|---|---|---|
| `init-template` | scaffold minimal valid bundle | bundle directory |
| `evaluate` | compute machine-readable gate/tier outputs | `result.json` |
| `report` | render markdown summary report | `stage_gate_report.md` |
| `submission-review` | run deterministic reruns + workflow guidance | `submission_review.json`, `submission_review.md` |
| `reference-vectors` | emit compatibility vectors for cross-impl checks | reference vector files |
| `reviewer-kit` | assemble a reviewer audit package | `reviewer_kit/` |

## `evaluate`

```bash
python -m automechinterp_evaluator.cli evaluate \
  --bundle /path/to/bundle \
  --output /path/to/bundle/result.json
```

Use this as the canonical machine-readable record for downstream tooling.

## `report`

```bash
python -m automechinterp_evaluator.cli report \
  --bundle /path/to/bundle \
  --output /path/to/bundle/stage_gate_report.md
```

Use this for human review, writeups, and triage meetings.

## `submission-review`

```bash
python -m automechinterp_evaluator.cli submission-review \
  --bundle /path/to/bundle \
  --reruns 3 \
  --output-json /path/to/bundle/submission_review.json \
  --output-md /path/to/bundle/submission_review.md
```

Recommended for any external submission or reproducibility claim.

## `reference-vectors`

```bash
python -m automechinterp_evaluator.cli reference-vectors
```

Use this to test behavioral compatibility when implementing third-party evaluators.

## `reviewer-kit`

```bash
python -m automechinterp_evaluator.cli reviewer-kit \
  --bundle /path/to/bundle \
  --output-dir .
```

Use this when you want a portable reviewer package with the claim ledger, stage-gate report, protocol critic report, and reproduction script. The kit is not fully standalone: reruns require either an installed evaluator package or a repo checkout exposed via `AUTOMECHINTERP_REPO_ROOT`.

## Command discovery

For authoritative flag details:

```bash
python -m automechinterp_evaluator.cli --help
python -m automechinterp_evaluator.cli <command> --help
```
