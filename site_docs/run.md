# Run The Evaluator

This page is the operational reference for executing evaluator workflows.

## Standard command sequence

### 1) Evaluate bundle

```bash
python -m automechinterp_evaluator.cli evaluate \
  --bundle /path/to/bundle \
  --output /path/to/bundle/result.json
```

### 2) Render markdown report

```bash
python -m automechinterp_evaluator.cli report \
  --bundle /path/to/bundle \
  --output /path/to/bundle/stage_gate_report.md
```

### 3) Run deterministic submission review

```bash
python -m automechinterp_evaluator.cli submission-review \
  --bundle /path/to/bundle \
  --reruns 3 \
  --output-json /path/to/bundle/submission_review.json \
  --output-md /path/to/bundle/submission_review.md
```

### 4) Generate compatibility vectors (optional)

```bash
python -m automechinterp_evaluator.cli reference-vectors
```

## When to use each output

| Artifact | Best use |
|---|---|
| `result.json` | machine-readable outcomes for automation |
| `stage_gate_report.md` | human review and narrative analysis |
| `submission_review.json` | deterministic rerun and decision tracking |
| `submission_review.md` | remediation planning |

## Operational recommendations

- Always run `submission-review` for external or publication-facing bundles.
- Track protocol version/hash alongside every output artifact.
- Keep bundle artifacts immutable after manifest hashing.

## Failure triage pattern

1. Count failed gates across claims.
2. Separate structural incompleteness (`not_evaluated`) from contradictory evidence (`fail`).
3. Prioritize fixes by concentration (highest-frequency failure families first).
4. Re-run deterministic review before resubmitting.

## Command discovery

```bash
python -m automechinterp_evaluator.cli --help
python -m automechinterp_evaluator.cli <command> --help
```
