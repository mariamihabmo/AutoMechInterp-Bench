"""Custodian: evaluate a single sealed holdout submission under the pinned evaluator.

Given a submission directory containing:

* a sealed tarball ``bundle.tar.gz``
* a ``bundle.sha256`` file with the expected SHA-256 of that tarball
* an ``attestation.json`` file conforming to ``holdout/attestation_schema.json``

this script:

1. Validates the attestation against the schema.
2. Verifies the on-disk ``bundle.sha256`` matches the actual tarball hash.
3. Verifies the attestation's ``contract_pin.constants_sha256`` matches the
   SHA-256 of the current repo's
   ``packages/evaluator/src/automechinterp_evaluator/constants.py``.
4. **Cryptographically verifies the structured attestation signature** when
   ``submission_kind == "external_blinded"``. Verification uses the
   public key embedded in the attestation and the canonicalised payload
   per ``attestation.canonicalization``. If the optional ``cryptography``
   (or ``PyNaCl``) library is not installed the Custodian fails closed
   with a clear error \u2014 the v0 protocol does not silently accept
   structurally-shaped-but-unverified signatures.
5. Unseals the tarball into a scratch directory, runs ``evaluate_bundle``
   against it, and writes the result to a results directory alongside a
   ``submission_review.json`` capturing attestation, hashes, pin-match
   status, signature-verification status, and evaluator version.

Usage::

    python -m holdout.tools.evaluate_holdout_submission \\
        --submission-dir holdout/pilot/submissions/maintainer_pilot_0001 \\
        --results-dir holdout/pilot/results/maintainer_pilot_0001

The Custodian is expected to run this script at step 6 of the protocol
(see ``methodology/blinded_holdout_protocol.md``) and commit the resulting
``results/`` subdirectory only after window close.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Dict, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "holdout" / "attestation_schema.json"


def _generated_at_utc() -> str:
    """ISO-8601 UTC timestamp honoring ``SOURCE_DATE_EPOCH`` for byte-reproducible review artifacts.

    the Custodian flow must be byte-
    reproducible end-to-end — it is the workflow we ask external partners to
    trust. Mirrors ``holdout/tools/build_results_summary.py:_generated_at_utc``.
    Two custodians who re-run this script over the same submission tree will
    now produce byte-identical ``submission_review.json`` artifacts when both
    pin ``SOURCE_DATE_EPOCH`` (e.g. via the repo Makefile's default of
    ``1700000000``).
    """
    raw = os.environ.get("SOURCE_DATE_EPOCH")
    if raw:
        try:
            return datetime.fromtimestamp(int(raw), tz=timezone.utc).isoformat(timespec="seconds")
        except (TypeError, ValueError):
            pass
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
CONSTANTS_PATH = (
    REPO_ROOT / "packages" / "evaluator" / "src" / "automechinterp_evaluator" / "constants.py"
)
EVALUATOR_PYPROJECT = REPO_ROOT / "packages" / "evaluator" / "pyproject.toml"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Canonicalisation + signature verification
# ---------------------------------------------------------------------------


def canonicalize_attestation(attestation: Dict[str, Any], canonicalization: str) -> bytes:
    """Return the canonical byte payload that the signature commits to.

    The signature field itself (``attestation_signature.signature``) is
    omitted so that signing and verification are well-defined; the rest
    of the ``attestation_signature`` object (``scheme``, ``public_key``)
    is included to bind the key and scheme into the signed payload.
    """

    payload = json.loads(json.dumps(attestation))  # deep copy
    sig_obj = payload.get("attestation_signature")
    if isinstance(sig_obj, dict):
        sig_obj = {k: v for k, v in sig_obj.items() if k != "signature"}
        payload["attestation_signature"] = sig_obj

    if canonicalization == "sorted-json":
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if canonicalization == "jcs":
        try:
            import jcs  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - optional dep
            raise RuntimeError(
                "attestation declares canonicalization='jcs' but the optional "
                "`jcs` package is not installed; pip install jcs"
            ) from exc
        return jcs.canonicalize(payload)
    raise ValueError(f"unsupported canonicalization: {canonicalization!r}")


def _verify_ed25519(public_key: bytes, signature: bytes, payload: bytes) -> None:
    """Verify ed25519; raise on failure. Tries ``cryptography`` then ``nacl``."""

    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        try:
            key = Ed25519PublicKey.from_public_bytes(public_key)
        except ValueError as exc:
            raise ValueError(f"malformed ed25519 public key: {exc}") from exc
        try:
            key.verify(signature, payload)
        except InvalidSignature as exc:
            raise ValueError("ed25519 signature does not verify against payload") from exc
        return
    except ImportError:
        pass

    try:
        import nacl.exceptions  # type: ignore[import-not-found]
        import nacl.signing  # type: ignore[import-not-found]

        verify_key = nacl.signing.VerifyKey(public_key)
        try:
            verify_key.verify(payload, signature)
        except nacl.exceptions.BadSignatureError as exc:
            raise ValueError("ed25519 signature does not verify against payload") from exc
        return
    except ImportError:
        pass

    raise RuntimeError(
        "external_blinded submission requires cryptographic signature verification, "
        "but neither `cryptography` nor `PyNaCl` is installed in this environment. "
        "Install one (e.g. `pip install cryptography`) before running the Custodian "
        "evaluator on external_blinded submissions. The v0 protocol fails closed "
        "rather than silently accepting structurally-valid-but-unverified signatures."
    )


def _decode_b64(name: str, value: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"attestation_signature.{name} is not valid base64: {exc}") from exc


def verify_attestation_signature(attestation: Dict[str, Any]) -> Tuple[bool, str]:
    """Return ``(ok, scheme_label)``. Raises on hard failure for external_blinded.

    For ``submission_kind != "external_blinded"`` the structured-signature
    rule does not apply and verification is skipped (returns
    ``(False, "skipped:non-external")``). For external_blinded, this
    function performs full cryptographic verification or raises.
    """

    kind = attestation.get("submission_kind")
    sig = attestation.get("attestation_signature")
    if kind != "external_blinded":
        return False, "skipped:non-external"
    if not isinstance(sig, dict):  # already enforced upstream, defensive
        raise ValueError("attestation_signature must be a structured object for external_blinded")

    scheme = sig["scheme"]
    # the schema description places `canonicalization`
    # inside `attestation_signature` (see attestation_schema.json). The
    # historical code path read a top-level `canonicalization` key, which
    # the schema's `additionalProperties: false` actually forbids. Prefer
    # the schema-correct nested location, with a documented fallback to
    # the legacy top-level key for backward compatibility.
    canonicalization = sig.get(
        "canonicalization",
        attestation.get("canonicalization", "sorted-json"),
    )
    payload = canonicalize_attestation(attestation, canonicalization)
    public_key = _decode_b64("public_key", sig["public_key"])
    signature = _decode_b64("signature", sig["signature"])

    if scheme == "ed25519":
        if len(public_key) != 32:
            raise ValueError(f"ed25519 public_key must be 32 bytes, got {len(public_key)}")
        if len(signature) != 64:
            raise ValueError(f"ed25519 signature must be 64 bytes, got {len(signature)}")
        _verify_ed25519(public_key, signature, payload)
        return True, "ed25519"

    if scheme == "rsa-pss-sha256":
        try:
            from cryptography.exceptions import InvalidSignature
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
        except ImportError as exc:
            raise RuntimeError(
                "rsa-pss-sha256 verification requires the `cryptography` package; "
                "pip install cryptography"
            ) from exc
        try:
            key = serialization.load_der_public_key(public_key)
        except ValueError:
            try:
                key = serialization.load_pem_public_key(public_key)
            except ValueError as exc:
                raise ValueError(f"could not parse RSA public key: {exc}") from exc
        try:
            key.verify(  # type: ignore[union-attr]
                signature,
                payload,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
        except InvalidSignature as exc:
            raise ValueError("rsa-pss-sha256 signature does not verify against payload") from exc
        return True, "rsa-pss-sha256"

    if scheme == "institutional-pgp":
        # PGP verification requires a configured keyring + GnuPG binary; out of
        # scope for the v0 in-tree verifier. Document the limitation and fail
        # closed so the operator must explicitly opt out via --skip-signature.
        raise RuntimeError(
            "scheme=institutional-pgp is documented in the schema but its v0 "
            "verification path requires an out-of-band Custodian-managed GnuPG "
            "keyring; either re-sign with ed25519 or rsa-pss-sha256, or run the "
            "Custodian evaluator with --skip-signature and document the manual "
            "verification step in the submission_review.json `notes` field."
        )

    raise ValueError(f"unknown attestation_signature.scheme: {scheme!r}")


def _validate_attestation(attestation: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """Minimal, dependency-free validation against the attestation schema.

    We avoid introducing a ``jsonschema`` dependency; instead we check the
    schema's stated ``required`` keys, enum constraints, string patterns,
    and ``additionalProperties: false``. This intentionally mirrors the
    subset of JSON Schema the attestation schema actually uses.
    """

    required = schema.get("required", [])
    missing = [k for k in required if k not in attestation]
    if missing:
        raise ValueError(f"attestation missing required keys: {missing}")
    if schema.get("additionalProperties") is False:
        allowed = set(schema.get("properties", {}).keys())
        extra = [k for k in attestation if k not in allowed]
        if extra:
            raise ValueError(f"attestation has disallowed keys: {extra}")
    for key, spec in schema.get("properties", {}).items():
        if key not in attestation:
            continue
        value = attestation[key]
        if "enum" in spec and value not in spec["enum"]:
            raise ValueError(f"attestation.{key}={value!r} not in enum {spec['enum']}")
        if "pattern" in spec and not re.fullmatch(spec["pattern"], str(value)):
            raise ValueError(f"attestation.{key}={value!r} does not match pattern {spec['pattern']}")
        if spec.get("type") == "object" and "required" in spec:
            for sub in spec["required"]:
                if sub not in value:
                    raise ValueError(f"attestation.{key} missing required sub-key: {sub}")
            for sub, sub_spec in spec.get("properties", {}).items():
                if sub in value and "pattern" in sub_spec:
                    if not re.fullmatch(sub_spec["pattern"], str(value[sub])):
                        raise ValueError(
                            f"attestation.{key}.{sub}={value[sub]!r} does not match pattern"
                        )

    # Enforce structured signature for external_blinded.
    sig = attestation.get("attestation_signature")
    if attestation.get("submission_kind") == "external_blinded":
        if not isinstance(sig, dict):
            raise ValueError(
                "attestation.attestation_signature must be a structured object "
                "(scheme/signature/public_key) for external_blinded submissions; "
                "see holdout/CUSTODIAN_RUNBOOK.md \u00a7Attestation Signature Scheme."
            )
        for required_sub in ("scheme", "signature", "public_key"):
            if required_sub not in sig:
                raise ValueError(
                    f"attestation.attestation_signature missing required sub-key: {required_sub}"
                )
        if sig["scheme"] not in ("ed25519", "rsa-pss-sha256", "institutional-pgp"):
            raise ValueError(
                f"attestation.attestation_signature.scheme={sig['scheme']!r} not in allowed set"
            )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--submission-dir", required=True, type=Path)
    p.add_argument("--results-dir", required=True, type=Path)
    p.add_argument(
        "--allow-pin-mismatch",
        action="store_true",
        help=(
            "Record a pin mismatch in submission_review.json instead of exiting with a non-zero "
            "status. Intended only for Custodian audit runs that document historical drift."
        ),
    )
    p.add_argument(
        "--skip-signature",
        action="store_true",
        help=(
            "Skip cryptographic signature verification for external_blinded submissions. "
            "Use only when the scheme is `institutional-pgp` (verified out-of-band) or for "
            "documented historical-drift audits; the resulting submission_review.json will "
            "carry signature_verified=false and signature_status='skipped:operator-flag'."
        ),
    )
    return p.parse_args(argv)


def evaluate_submission(
    submission_dir: Path,
    results_dir: Path,
    *,
    allow_pin_mismatch: bool = False,
    skip_signature: bool = False,
) -> Dict[str, Any]:
    """Run the full Custodian evaluation flow; return the submission review dict."""

    submission_dir = submission_dir.resolve()
    results_dir = results_dir.resolve()

    attestation_path = submission_dir / "attestation.json"
    tarball_path = submission_dir / "bundle.tar.gz"
    expected_sha_path = submission_dir / "bundle.sha256"

    for required in (attestation_path, tarball_path, expected_sha_path):
        if not required.exists():
            raise FileNotFoundError(f"submission is missing: {required.name}")

    schema = json.loads(SCHEMA_PATH.read_text())
    attestation = json.loads(attestation_path.read_text())
    _validate_attestation(attestation, schema)

    # cryptographic signature
    # verification is mandatory for external_blinded unless the operator
    # explicitly opts out via --skip-signature (e.g. institutional-pgp).
    if attestation.get("submission_kind") == "external_blinded" and skip_signature:
        signature_verified = False
        signature_status = "skipped:operator-flag"
    else:
        try:
            ok, signature_status = verify_attestation_signature(attestation)
            signature_verified = ok
        except (ValueError, RuntimeError):
            # Surface verification failures as the same error type the rest
            # of the pipeline already raises so the CLI exit code is
            # non-zero and submission_review.json is not written.
            raise

    if attestation["submission_id"] != submission_dir.name:
        raise ValueError(
            f"attestation.submission_id={attestation['submission_id']!r} "
            f"does not match directory name {submission_dir.name!r}"
        )

    actual_sha = _sha256_file(tarball_path)
    expected_sha = expected_sha_path.read_text().split()[0].strip()
    if actual_sha != expected_sha:
        raise ValueError(
            f"bundle.tar.gz SHA-256 mismatch: actual={actual_sha} expected={expected_sha}"
        )

    repo_constants_sha = _sha256_file(CONSTANTS_PATH)
    pin_constants_sha = attestation["contract_pin"]["constants_sha256"]
    pin_match = repo_constants_sha == pin_constants_sha
    if not pin_match and not allow_pin_mismatch:
        raise ValueError(
            "contract_pin.constants_sha256 does not match the repo's current constants.py "
            f"(attestation={pin_constants_sha}, repo={repo_constants_sha}). Pass "
            "--allow-pin-mismatch only for documented historical-drift audits."
        )

    # Import the evaluator lazily so failing to import doesn't poison schema checks above.
    from automechinterp_evaluator.evaluator import evaluate_bundle

    try:
        evaluator_version = importlib_metadata.version("automechinterp-evaluator")
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover - defensive
        # prefer ``tomllib``
        # (or the ``tomli`` fallback for Python <3.11) over string-splitting
        # ``pyproject.toml``; only fall back to the legacy splitter when
        # neither is importable.
        evaluator_version = "unknown"
        if EVALUATOR_PYPROJECT.exists():
            try:
                import tomllib  # type: ignore[import-not-found]
            except ModuleNotFoundError:
                try:
                    import tomli as tomllib  # type: ignore[import-not-found,no-redef]
                except ModuleNotFoundError:
                    tomllib = None  # type: ignore[assignment]
            if tomllib is not None:
                try:
                    with EVALUATOR_PYPROJECT.open("rb") as fh:
                        data = tomllib.load(fh)
                    parsed = data.get("project", {}).get("version")
                    if isinstance(parsed, str) and parsed.strip():
                        evaluator_version = parsed
                except Exception:
                    pass
            if evaluator_version == "unknown":
                text = EVALUATOR_PYPROJECT.read_text()
                marker = 'version = "'
                if marker in text:
                    evaluator_version = text.split(marker, 1)[1].split('"', 1)[0]

    results_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with tarfile.open(tarball_path, "r:gz") as tar:
            # Protect against path traversal in a sealed tarball.
            for member in tar.getmembers():
                member_path = (tmp_path / member.name).resolve()
                if not str(member_path).startswith(str(tmp_path.resolve())):
                    raise ValueError(f"tarball member escapes scratch dir: {member.name!r}")
            tar.extractall(tmp_path)

        # Identify the bundle root — either the tmp dir itself if the
        # tarball contains the 3 input files at the top level, or the
        # single top-level directory otherwise.
        tops = [p for p in tmp_path.iterdir() if not p.name.startswith(".")]
        if (tmp_path / "protocol.yaml").exists():
            bundle_root = tmp_path
        elif len(tops) == 1 and tops[0].is_dir() and (tops[0] / "protocol.yaml").exists():
            bundle_root = tops[0]
        else:
            raise ValueError("could not locate protocol.yaml in extracted tarball")

        evaluation_result = evaluate_bundle(bundle_root)

    evaluation_path = results_dir / "evaluation_result.json"
    evaluation_path.write_text(json.dumps(evaluation_result, indent=2, sort_keys=True) + "\n")

    review = {
        "submission_id": attestation["submission_id"],
        "submission_kind": attestation["submission_kind"],
        "evaluated_at_utc": _generated_at_utc(),
        "evaluator_version": evaluator_version,
        "bundle_tarball_sha256": actual_sha,
        "contract_pin": attestation["contract_pin"],
        "contract_pin_match": pin_match,
        "repo_constants_sha256": repo_constants_sha,
        "attestation_file_sha256": _sha256_file(attestation_path),
        "author_institution": attestation["author_institution"],
        "signature_verified": signature_verified,
        "signature_status": signature_status,
        "overall": evaluation_result.get("overall", {}),
        "protocol_id": evaluation_result.get("protocol_id"),
        "protocol_hash": evaluation_result.get("protocol_hash"),
        "n_accepted_claims": int(evaluation_result.get("overall", {}).get("accepted_count", 0)),
        "n_claims": int(evaluation_result.get("overall", {}).get("hypothesis_count", 0)),
    }
    review_path = results_dir / "submission_review.json"
    review_path.write_text(json.dumps(review, indent=2, sort_keys=True) + "\n")
    return review


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    review = evaluate_submission(
        args.submission_dir,
        args.results_dir,
        allow_pin_mismatch=args.allow_pin_mismatch,
        skip_signature=args.skip_signature,
    )
    print(json.dumps({k: review[k] for k in ("submission_id", "submission_kind", "contract_pin_match", "signature_verified", "signature_status", "n_accepted_claims", "n_claims")}, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
