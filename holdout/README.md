# Blinded Holdout Slot

> **External blinded evidence to date: 0.** The two `maintainer_pilot`
> submissions in `results_summary.json:maintainer_pilot` are pipeline
> self-tests and contribute **zero** acceptance evidence. Only entries
> under `results_summary.json:external_blinded` count as held-out
> evidence; that slice is empty by design until an external author
> submits.

This directory holds the protocol, custodian tooling, attestation
schema, and reserved slot for an externally-authored, sealed-envelope
evaluation slice. The submissions slot itself (`submissions/`) is
empty by design until an external author submits; the surrounding
files are the scaffolding (protocol, runbook, schema, pilots) that
lets an external party submit without restructuring the repository.
The protocol is in `../methodology/blinded_holdout_protocol.md`.

**Current state:** no holdout submissions have been received. The
existence of this directory + the protocol document means an external
party can add a holdout slice without restructuring the repository or
renegotiating the contract.

## Contents (when populated)

- `submissions/<opaque_submission_id>/<bundle>/` — sealed bundles
  released after the holdout window closes. Each bundle contains the
  same artifacts as a normal claim bundle (`protocol.yaml`,
  `hypothesis.jsonl`, `evaluation_result.json`, `manifest.json`, and
  optionally `cross_model_results.json`).
- `submissions/<opaque_submission_id>/attestation.json` — the
  Author-signed attestation conforming to `attestation_schema.json`
  in this directory.
- `results/<opaque_submission_id>/` — Custodian-produced
  `evaluation_result.json` and `submission_review.json` for each
  bundle, regenerated under the pinned evaluator.
- `results_summary.json` — top-level summary of holdout-slice
  outcomes, kept distinct from the released-breadth summary.

## What goes here

- `holdout/submissions/` is the sealed slot for **external_blinded** submissions authored under the protocol. Each subdirectory is `submissions/<opaque_submission_id>/`. This slot is **currently empty-by-design** and must only be populated by an external Holdout Author.
- `holdout/results/` holds the Custodian-produced evaluation artifacts corresponding to entries under `holdout/submissions/`.
- `holdout/pilot/` is a narrow carve-out for **maintainer_pilot** submissions that exist solely to exercise the Custodian evaluation pipeline end-to-end. Pilot submissions are NEVER counted as external evidence. They are reported as a separate, clearly-labeled slice in `holdout/results_summary.json` so the scaffolding's presence is inspectable without inflating the external-evidence count.
- `holdout/tools/` contains both author-side helpers (`package_holdout_submission.py`, `preflight_submission.py`) and Custodian-side scripts (`evaluate_holdout_submission.py`, `build_results_summary.py`).
- `holdout/EXTERNAL_AUTHOR_QUICKSTART.md` is the shortest path for an external author to package and self-check a sealed submission without evaluating it.
- `holdout/results_summary.json` — top-level summary. Always reports external_blinded and maintainer_pilot slices separately and includes a pin-match audit.

Only artifacts produced under the protocol in `../methodology/blinded_holdout_protocol.md` belong under `submissions/` or `pilot/submissions/`. Maintainer-authored bundles from the released benchmark belong in `main/output/real_multilane/` or `main/output/real_multi_task/`.

## Why this slot is empty

The benchmark currently has no holdout submissions because no external
party has run the protocol yet. Releasing the protocol + scaffolding
allows future external partners (workshop chairs, third-party
research groups) to plug in without renegotiating the contract.
