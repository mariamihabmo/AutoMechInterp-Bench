# Holdout Custodian Runbook

This runbook is for a person holding a private AutoMechInterp holdout suite.
The custodian's job is to run the public contract exactly once for a named
release and publish only aggregate results. Do not publish item-level
hypotheses, gate failures, prompt text, or generator details until the holdout
rotation policy says those items can be retired into the public set.

## Custodian Responsibilities

1. Keep the private suite outside this repository.
2. Verify the release version and contract pin before scoring.
3. Run the aggregate-only holdout command once for the named release.
4. Publish only the aggregate JSON/Markdown artifacts.
5. Refuse repeated scoring requests against the same private suite unless the
   governance document pre-registers a new major-version scoring event.

## Required Inputs

1. Private suite path containing claim bundles or a custodian-specific package.
2. Release version label, for example `v0.1-external-holdout`.
3. Contract pin/hash supplied by maintainers.
4. Python environment capable of running the released evaluator.

## Rehearsal Command

Maintainers may run rehearsal mode to test plumbing. Rehearsal is not
evidence-bearing:

```bash
python main/run_holdout.py \
  --rehearsal \
  --release-version v0-rehearsal \
  --use-cached-results
```

## External Holdout Command

For a real external suite, use:

```bash
python main/run_holdout.py \
  --private-suite /path/to/private/holdout_suite \
  --release-version v0.1-external-holdout \
  --output main/output/repro/holdout_v0.1_external.json
```

If the local helper does not support a required flag, stop and record the
missing capability. Do not work around aggregate-only safeguards by copying
private items into the public repository.

## Pre-Scoring Contract-Pin Verification

Before invoking the scoring command, the Custodian MUST confirm that the
release's contract pin matches the repository state being used to score. Two
checks together are sufficient:

1. **Repo state matches the announced release tag.**

   ```bash
   git fetch --tags
   git checkout <release-tag>
   git rev-parse HEAD     # record this commit hash in the custodian log
   ```

2. **The submission attestation's `contract_pin.constants_sha256` matches the
   repo's `packages/evaluator/.../constants.py`.** This is enforced
   automatically by `holdout/tools/evaluate_holdout_submission.py` (see the
   `pin_constants_sha == repo_constants_sha` check that aborts on mismatch),
   and by `holdout/tools/preflight_submission.py` for author-side rehearsal.
   Custodians can compute the expected hash manually with:

   ```bash
   python -c "import hashlib, pathlib; \
     p = pathlib.Path('packages/evaluator/src/automechinterp_evaluator/constants.py'); \
     print(hashlib.sha256(p.read_bytes()).hexdigest())"
   ```

If either check disagrees, **stop the scoring run** and reissue from the
correct release tag. A pin mismatch invalidates aggregate-only secrecy
guarantees because the gate semantics may have shifted between the announced
release and the running code.

## Allowed Public Outputs

Allowed:

1. Number of bundles scored.
2. Number of claims scored.
3. Accepted/rejected counts.
4. Aggregate false-accept or failure rates with confidence intervals.
5. Release version and contract hash.
6. Custodian attestation that private items were not exposed.

Not allowed:

1. Per-item hypothesis text.
2. Per-item gate outcomes.
3. Prompt templates.
4. Component identifiers if they reveal the private item.
5. Repeated score trajectories from tuning attempts.

## Failure Handling

If the holdout result is poor, publish the poor aggregate result. Do not adjust
the gates and rerun against the same private suite. A poor holdout result is a
scientific finding, not a reason to erase the run.

If the run fails because of tooling, publish a custodian failure note with:

1. command run,
2. error class,
3. whether any private content would be exposed by debugging,
4. recommended fix.

## Attestation Signature Scheme

Each submission MUST be accompanied by a signed attestation conforming to
`holdout/attestation_schema.json`. The Custodian accepts these signature
schemes (in order of preference):

1. **ed25519** (recommended). Authors generate a fresh keypair per submission
   window via `python -m holdout.tools.sign_submission keygen ...`; the
   public key MUST be bound to `author_institution` by being
   announced from an institutionally-controlled domain (HTTPS or DNS TXT
   record) at least 48 hours before the submission window opens.
2. **rsa-pss-sha256**. Permitted for institutions with FIPS-mode crypto
   constraints. Same out-of-band public-key publication requirement applies.
   Verification path uses the `cryptography` package's PSS+SHA-256 verifier
   (DER- or PEM-encoded public key embedded in `attestation_signature.public_key`).
3. **institutional-pgp**. Permitted only when the institution has a stable,
   long-lived PGP key whose fingerprint is recorded in the published
   custodian rehearsal log before the window opens. **In-tree verification
   for this scheme is currently out of scope** — the Custodian must verify
   via an out-of-band GnuPG keyring and run
   `evaluate_holdout_submission --skip-signature`, then document the manual
   verification step in the resulting `submission_review.json` `notes` field.

Canonicalization: the byte string that was signed MUST be either
`json.dumps(payload, sort_keys=True, separators=(",",":"))` ("sorted-json",
default) or RFC 8785 JCS ("jcs"). The Custodian rejects submissions whose
declared `canonicalization` field does not round-trip to the same bytes
under that method; authors can self-check via
`python -m holdout.tools.check_canonicalization --attestation ...`.

**Cryptographic verification is enforced.** `holdout.tools.evaluate_holdout_submission`
invokes `verify_attestation_signature(...)` for every `external_blinded`
submission. The Custodian environment MUST have `cryptography` (or
`PyNaCl`) installed; if neither is present the evaluator fails closed
rather than silently accepting a structurally-valid-but-unverified
signature. The verification path:

> **Asymmetric requirement.**
> Signature verification is **mandatory** for `submission_kind:
> external_blinded` — a missing or invalid signature MUST fail the
> Custodian evaluation. For `submission_kind: maintainer_pilot` the
> signature is informational only and does not gate acceptance, because
> maintainer pilots are pipeline self-tests rather than evidence-bearing
> submissions; their results are excluded from the headline acceptance
> count regardless of signature status.

1. canonicalises the attestation under its declared scheme, omitting
   the `attestation_signature.signature` byte-string but including the
   `scheme` and `public_key` sub-fields (so an attacker cannot swap the
   key after signing);
2. runs the scheme-appropriate verifier against the canonical payload;
3. records `signature_verified: true|false` and a `signature_status`
   string (`ed25519`, `rsa-pss-sha256`, `skipped:operator-flag`, or
   `skipped:non-external`) in the resulting `submission_review.json`.

A reproducible round-trip self-test pins this behaviour:
[`packages/evaluator/tests/test_holdout_signature_verification.py`](../packages/evaluator/tests/test_holdout_signature_verification.py).

The Custodian publishes the SHA-256 of every accepted public key in
`holdout/results_summary.json` so external auditors can verify each
submission independently of the Custodian.

## Package Boundaries

`holdout/` and `holdout/tools/` are Python packages with explicit
`__init__.py` files. Custodian scripts MUST import from them as
`from holdout.tools.preflight_submission import ...`, never via
`sys.path.insert` games. This prevents a top-level `tools/` shadowing
`holdout/tools/` during evaluation.

## Claim Boundaries

One external holdout run allows the paper to say:

"The release completed one aggregate-only private holdout execution under an
external custodian."

It does not allow:

"The benchmark is holdout-hardened" or "the benchmark is immune to gaming."
