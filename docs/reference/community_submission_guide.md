# Community Submission Guide

# Community Submission Guide

This is the public, non-blinded intake path for external claim bundles. Use the
holdout packet instead when the author must stay blinded from the evaluator
until a custodian scores the submission.

This guide is deliberately conservative: a failed external submission is still
useful if the failure report is interpretable. Maintainers must not rewrite a
submission into an accepted result.

## 0. Install Or Run From Source

From a repository checkout:

```bash
python -m pip install -e packages/evaluator
```

If editable install is unavailable, run commands with:

```bash
PYTHONPATH=packages/evaluator/src
```

Verify the public CLI:

```bash
python -m automechinterp_evaluator.cli --help
```

## 1. Minimum Submission Package

1. A valid claim bundle following `claim_bundle_spec_v1.md`
2. The output of `submission-review`
3. Any auxiliary provenance needed to explain how the bundle was generated

The bundle itself must contain:

1. `protocol.yaml`
2. `hypothesis.jsonl`
3. `evaluation_result.json`
4. `manifest.json`
5. Optional `cross_model_results.json`

## 2. Recommended Workflow

```bash
python -m automechinterp_evaluator.cli submission-review \
  --bundle /path/to/bundle \
  --reruns 3 \
  --output-json /path/to/bundle/submission_review.json \
  --output-md /path/to/bundle/submission_review.md
```

If this fails, send the failure output with the bundle. Intake failures are
actionable compatibility evidence.

## 3. Author Provenance Note

Add a short `provenance.md` or `provenance.json` with:

1. author or anonymized institution;
2. whether the author had seen AutoMechInterp accepted examples;
3. whether any maintainer helped with content, not just packaging;
4. task, model, and claim-family scope;
5. whether the bundle is public, anonymous, or embargoed.

## 4. Maintainer Intake Log

Maintainers processing the bundle should create:

```text
main/output/community_submissions/<author_or_org>/intake_log.md
```

The log must record:

1. original files received;
2. exact review command;
3. all maintainer clarifications;
4. any packaging-only fixes;
5. final accepted/rejected/downgraded status;
6. whether the submission counts as external evidence.

It does **not** count as external evidence if a maintainer authored the
hypotheses, tuned thresholds, regenerated missing evidence cells, or rewrote
claim language to rescue the result.

## 5. What Maintainers Should Look For

1. deterministic rerun agreement
2. accepted or non-accepted tier with transparent failed checks
3. protocol quality via the protocol critic
4. honest scope language that matches the evidence tier

## 6. Important Warning

An accepted bundle is evidence that a claim satisfied the current contract under its released artifacts.
It is not a proof of mechanistic truth.
