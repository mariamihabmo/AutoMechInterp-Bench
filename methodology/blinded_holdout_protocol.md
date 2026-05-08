# Blinded Holdout Governance Protocol

**Status:** *protocol defined; no holdout submissions yet recorded.*

This document defines the procedure under which an external party can author
mechanistic-interpretability claim bundles that the AutoMechInterp benchmark
maintainers cannot see during authoring, and under which the released
benchmark cache reports a separate, independently-authored evaluation
slice. The benchmark currently has no such slice. This protocol exists so
that one can be added by a third party without renegotiating the contract.

## Why blinded holdout matters

Every benchmark-authored stress, control, and acceptance result in this
release is, in principle, vulnerable to evaluator-aware overfitting: the
maintainers know the contract, the gate logic, and the bundle authoring
conventions. Even with the released suite-targeted, agnostic, red-team,
and bundle-hacking probes, the benchmark cannot demonstrate that
acceptance generalizes to claims authored by parties without that
knowledge. A blinded holdout slice, authored under a sealed-envelope
protocol by an external party who never sees the maintainers' acceptance
heuristics, addresses this gap directly.

The current benchmark release accepts this limitation candidly in both
NeurIPS drafts and in `methodology/gap_analysis_2026-04-18.md`. This
protocol is the procedural artifact that allows the limitation to be
closed without changing the contract or the released artifact set.

## Roles

* **Holdout Authors.** One or more external parties (institutionally
  independent from the AutoMechInterp maintainers) who author claim
  bundles to the public contract specification *without consulting any
  AutoMechInterp maintainer about acceptance heuristics, threshold
  values, or example accepted bundles*. Holdout Authors should be
  identifiable in the attestation but the authoring decisions must
  predate any maintainer interaction about the holdout submission.
* **Holdout Custodian.** A non-maintainer (for example, a venue chair, a
  workshop organizer, or an institutional reviewer) who receives the
  sealed bundles, attestations, and evaluator version pin, and who
  releases the evaluation results only after the holdout window closes.
* **AutoMechInterp Maintainers.** The released-benchmark maintainers.
  May not see, modify, or pre-evaluate the holdout bundles before the
  Custodian releases the evaluation. Must publish the evaluator version
  pin and the contract before the holdout window opens.

## Protocol

1. **Contract pin.** Maintainers tag the evaluator at the version that
   will be used for the holdout window (for example,
   `automechinterp-evaluator==X.Y.Z`). The pin includes the contract
   constants module hash (the SHA-256 of
   `packages/evaluator/src/automechinterp_evaluator/constants.py`).
2. **Window open.** Custodian publishes the contract pin, this
   protocol, and the holdout submission template to a public channel
   that does not flow back through the maintainers (for example, a
   workshop CFP).
3. **Sealed authoring.** Each Holdout Author authors one or more claim
   bundles using only the publicly released contract specification.
   Authors must not solicit or receive any informal acceptance
   feedback from a maintainer during this phase. Each bundle is
   assigned a Custodian-issued opaque submission ID and is encrypted
   to the Custodian's public key.
4. **Sealed transmission.** Each Author submits to the Custodian
   exactly one tarball per submission, plus an attestation file
   (`attestation.json`, schema in `holdout/attestation_schema.json`)
   stating: institutional affiliation, submission UTC timestamp, a
   sworn statement of contract-only authoring, and the contract pin
   hash the bundle was authored against.
5. **Window close.** Custodian declares the window closed, computes
   the SHA-256 of every received tarball, and publishes the (opaque
   ID, SHA-256) pairs.
6. **Independent evaluation.** Custodian (or a designated third party
   who does not also maintain the benchmark) checks out the pinned
   evaluator, evaluates each tarball under the pinned contract,
   records `evaluation_result.json` and `submission_review.json` per
   bundle, and writes `holdout/results/<submission_id>/` records.
7. **Disclosure.** Custodian releases `holdout/results_summary.json`,
   recording per-bundle pass/fail, accepted-claim count, and any gate
   that was added or removed since the contract pin (must be empty if
   the pin is honored). Maintainers integrate the summary into the
   next benchmark release in a separate
   `holdout_breadth_summary.json` artifact, kept distinct from the
   maintainer-visible release breadth.

## What the benchmark commits to

* **Disclosure of negative results.** The holdout slice's results are
  reported as-is, including failures or zero acceptance.
* **No retroactive contract changes.** No gate threshold may be
  adjusted between window open and window close, even if a holdout
  author requests it. Adjustments are deferred to the *next* contract
  version after the holdout window closes.
* **Separation from released breadth.** Holdout-derived numbers are
  reported as a separate slice and never merged into the released
  breadth headline. Both numbers may be quoted in any successor paper.

## What the protocol does not promise

* It does not guarantee the existence of a holdout author. It is the
  procedural mechanism that makes one possible.
* It does not eliminate evaluator-aware overfitting on the
  maintainer-authored slice. It only contributes a separate slice
  whose authoring did not have access to maintainer heuristics.
* It does not address ground-truth questions about mechanistic
  interpretability. It addresses contract-relative reliability
  reproducibility under sealed authoring.

## Status of this slice

* Window open: not yet scheduled.
* Custodian: not yet appointed.
* **External blinded submissions received: 0.** `holdout/submissions/` is the empty-by-design slot reserved for this class.
* **Maintainer pilot submissions: 2.** Two `submission_kind="maintainer_pilot"` submissions are present under `holdout/pilot/submissions/` to demonstrate that the Custodian-side scaffolding (`holdout/tools/evaluate_holdout_submission.py`, `holdout/tools/build_results_summary.py`) is populate-able and the `contract_pin` audit is working across more than one bundle. Pilot submissions are explicitly **not counted as external evidence** and are reported as a separate slice in `holdout/results_summary.json`. The protocol's "no maintainer bundles" rule is preserved in the `submissions/` slot; the pilots exist in a deliberately separate `pilot/` sub-slot so the scaffolding can be validated without inflating the external-evidence count.
* `holdout/results_summary.json`: present; reports `n_external_blinded_submissions = 0` and the pilot outcome as a distinct slice. This summary is wired into `main/reproducibility_audit.py`.

## Pilot carve-out (`holdout/pilot/`)

The `pilot/` sub-slot exists for exactly one reason: to exercise the Custodian pipeline end-to-end so reviewers can confirm the scaffolding is real, not just a README. Pilot submissions:

* MUST set `submission_kind = "maintainer_pilot"` in the attestation.
* MUST carry an `attestation_text` that explicitly disclaims blinded authorship.
* ARE NEVER included in any "external-authored evidence" count in any release artifact or paper.
* DO validate the schema, SHA-256 hashing, contract-pin audit, and evaluator re-run path that an external submission would traverse.
