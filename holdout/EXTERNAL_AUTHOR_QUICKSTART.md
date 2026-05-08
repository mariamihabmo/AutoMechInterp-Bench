# External Author Quickstart

This is the shortest honest path for an external, blinded holdout author.

## What you need

- A bundle directory containing the canonical bundle files:
  `protocol.yaml`, `hypothesis.jsonl`, `evaluation_result.json`, and `manifest.json`.
- This repository at the pinned contract version.
- Your Custodian-issued opaque submission ID. (To request a submission ID,
  email the Custodian-of-record listed at the top of [`CUSTODIAN_RUNBOOK.md`](CUSTODIAN_RUNBOOK.md);
  pre-window coordination is part of the protocol.)
- Your institution name.
- An ed25519 keypair whose public key has been published from an
  institutionally-controlled domain at least 48 hours before the
  submission window opens (see [`CUSTODIAN_RUNBOOK.md`](CUSTODIAN_RUNBOOK.md#attestation-signature-scheme)).
- One of `cryptography` or `PyNaCl` installed for signing
  (`pip install cryptography` is the recommended path).

## 0. Generate a signing keypair (one-time)

```bash
python -m holdout.tools.sign_submission keygen \
  --private-out attestation_signing_key.pem \
  --public-out  attestation_signing_pub.b64
```

The private key file is created with mode `0600`. Keep it offline; the
public-key file is what you publish to your institutional domain.

## 1. Package the sealed submission

```bash
python -m holdout.tools.package_holdout_submission \
  --bundle-dir /path/to/your/bundle \
  --submission-dir holdout/submissions/<SUBMISSION_ID> \
  --submission-id <SUBMISSION_ID> \
  --submission-kind external_blinded \
  --author-institution "Your Institution" \
  --attestation-signature "PLACEHOLDER-WILL-BE-REPLACED-BY-SIGN-STEP"
```

This writes three files into `holdout/submissions/<SUBMISSION_ID>/`:

- `bundle.tar.gz`
- `bundle.sha256`
- `attestation.json`

`cross_model_results.json` is included automatically when present in the source bundle.

## 2. Sign the attestation in place

```bash
python -m holdout.tools.sign_submission sign \
  --attestation holdout/submissions/<SUBMISSION_ID>/attestation.json \
  --private-key attestation_signing_key.pem
```

This populates `attestation_signature.scheme = "ed25519"`,
`attestation_signature.public_key` (base64 raw 32 bytes), and
`attestation_signature.signature` (base64 raw 64 bytes signing the
canonical payload).

## 3. Author-side self-check

```bash
python -m holdout.tools.sign_submission verify \
  --attestation holdout/submissions/<SUBMISSION_ID>/attestation.json

python -m holdout.tools.check_canonicalization \
  --attestation holdout/submissions/<SUBMISSION_ID>/attestation.json

python -m holdout.tools.preflight_submission \
  --submission-dir holdout/submissions/<SUBMISSION_ID>
```

These run the **same** verification path that the Custodian will run, so a
failure here prevents a confusing failure on the Custodian side. They check:

- ed25519 signature verifies against the canonical payload,
- declared `canonicalization` round-trips,
- attestation schema conformance,
- tarball SHA-256 consistency,
- contract-pin hash match against the current repo constants.

None of these run the evaluator, so the blinded-holdout separation is
preserved.

## 4. Hand off to the Custodian

Transmit the sealed submission directory to the Custodian using the agreed channel.
Do **not** run `holdout.tools.evaluate_holdout_submission` yourself if you are trying
 to preserve a blinded external slice.

## Notes

- `submission_kind=external_blinded` is the only kind that can ever count as external evidence.
- `submission_kind=maintainer_pilot` exists only for maintainers' pipeline rehearsals and never counts as external evidence.
- The current contract pin is embedded automatically from this repository's evaluator version and `constants.py` hash.
