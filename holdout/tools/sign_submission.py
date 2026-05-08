"""Author-side helper: sign a holdout ``attestation.json`` with ed25519.

Usage (typical external_blinded workflow)::

    # one-time: generate a keypair (private key is sensitive; keep it offline).
    python -m holdout.tools.sign_submission keygen \\
        --private-out attestation_signing_key.pem \\
        --public-out  attestation_signing_pub.pem

    # before each submission: sign the attestation in place.
    python -m holdout.tools.sign_submission sign \\
        --attestation holdout/submissions/<SUBMISSION_ID>/attestation.json \\
        --private-key attestation_signing_key.pem

The ``sign`` command:

1. Reads the attestation JSON.
2. Derives the public key from the private key and embeds it as
   ``attestation_signature.public_key`` (base64-encoded raw 32 bytes).
3. Sets ``attestation_signature.scheme = "ed25519"`` and clears any
   existing signature byte-string so the canonical payload is well
   defined.
4. Canonicalises the payload per ``attestation.canonicalization`` (the
   default ``sorted-json`` is the only scheme this helper writes).
5. Signs the canonical payload with the private key and writes the
   base64-encoded raw 64-byte signature into
   ``attestation_signature.signature``.
6. Writes the attestation back to disk (sorted-json, trailing newline)
   so the on-disk file is byte-identical to what the Custodian will
   re-canonicalise during verification.

Round-trip self-check (recommended)::

    python -m holdout.tools.sign_submission verify \\
        --attestation holdout/submissions/<SUBMISSION_ID>/attestation.json

This re-runs the same verification path that
``holdout.tools.evaluate_holdout_submission`` will execute on the
Custodian side, so an author can confirm a successful signature before
sealing the submission.

Implementation notes :

* The canonical payload that the signature commits to deliberately
  excludes the ``attestation_signature.signature`` field but **includes**
  the ``scheme`` and ``public_key`` sub-fields. This binds the chosen
  scheme and key into the signature so an attacker cannot swap the
  ``public_key`` after signing.
* Only ``ed25519`` is implemented in this v0 helper. The schema also
  permits ``rsa-pss-sha256`` and ``institutional-pgp``; authors using
  those schemes must provide their own signing toolchain.
* Requires ``cryptography`` (preferred) or ``PyNaCl`` to be installed.
  Both libraries are commonly already present in scientific Python
  environments; if neither is available the helper fails closed with a
  clear install instruction.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path
from typing import Tuple


# Reuse the canonicalisation + verification helpers from the evaluator so
# the author and the Custodian see exactly the same canonical bytes.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from holdout.tools.evaluate_holdout_submission import (  # noqa: E402
    canonicalize_attestation,
    verify_attestation_signature,
)


def _load_ed25519() -> Tuple[str, object]:
    """Return (backend_name, module-or-class). Tries cryptography then nacl."""

    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519  # type: ignore[import-not-found]

        return "cryptography", ed25519
    except ImportError:
        pass
    try:
        import nacl.signing  # type: ignore[import-not-found]

        return "nacl", nacl.signing
    except ImportError:
        pass
    raise RuntimeError(
        "ed25519 signing requires `cryptography` or `PyNaCl`; "
        "pip install cryptography"
    )


def keygen(private_out: Path, public_out: Path) -> None:
    backend, mod = _load_ed25519()
    if backend == "cryptography":
        from cryptography.hazmat.primitives import serialization

        priv = mod.Ed25519PrivateKey.generate()
        priv_bytes = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub_raw = priv.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    else:  # nacl
        signing_key = mod.SigningKey.generate()
        priv_bytes = bytes(signing_key)  # raw 32-byte seed
        pub_raw = bytes(signing_key.verify_key)

    private_out.write_bytes(priv_bytes)
    private_out.chmod(0o600)
    public_out.write_text(base64.b64encode(pub_raw).decode("ascii") + "\n")
    print(f"wrote private key to {private_out} (mode 0600)")
    print(f"wrote public key  to {public_out} (base64-encoded raw ed25519 public key)")


def _load_private_key(path: Path) -> Tuple[bytes, bytes]:
    """Return ``(public_raw_bytes, sign_payload_callable_input)``-like duo.

    For the cryptography backend we return the loaded private-key object's
    sign function bound through a closure; for nacl we return the
    SigningKey. To keep the function signature simple we return
    ``(public_raw, signer)`` where ``signer`` is a callable taking
    ``bytes`` payload and returning ``bytes`` signature.
    """

    backend, _ = _load_ed25519()
    raw = path.read_bytes()
    if backend == "cryptography":
        from cryptography.hazmat.primitives import serialization

        try:
            priv = serialization.load_pem_private_key(raw, password=None)
        except ValueError:
            # Fall back to raw 32-byte seed (nacl-style key file).
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey,
            )

            priv = Ed25519PrivateKey.from_private_bytes(raw)
        pub_raw = priv.public_key().public_bytes(  # type: ignore[union-attr]
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        def _sign(payload: bytes) -> bytes:
            return priv.sign(payload)  # type: ignore[union-attr]

        return pub_raw, _sign

    # nacl backend
    import nacl.signing  # type: ignore[import-not-found]

    if len(raw) != 32:
        raise ValueError(
            "nacl backend expects a raw 32-byte private seed file; "
            "use the `cryptography` backend for PEM-encoded keys"
        )
    signing_key = nacl.signing.SigningKey(raw)
    pub_raw = bytes(signing_key.verify_key)

    def _sign_nacl(payload: bytes) -> bytes:
        return bytes(signing_key.sign(payload).signature)

    return pub_raw, _sign_nacl


def sign(attestation_path: Path, private_key_path: Path) -> None:
    attestation = json.loads(attestation_path.read_text())
    # prefer the schema-correct location of
    # `canonicalization` (inside `attestation_signature`); fall back to
    # the legacy top-level key for backward compatibility.
    sig_obj = attestation.setdefault("attestation_signature", {})
    canonicalization = sig_obj.get(
        "canonicalization",
        attestation.get("canonicalization", "sorted-json"),
    )
    pub_raw, signer = _load_private_key(private_key_path)

    sig_obj["scheme"] = "ed25519"
    sig_obj["public_key"] = base64.b64encode(pub_raw).decode("ascii")
    sig_obj["canonicalization"] = canonicalization
    sig_obj["signature"] = ""  # placeholder, excluded from canonical payload

    payload = canonicalize_attestation(attestation, canonicalization)
    raw_signature = signer(payload)
    sig_obj["signature"] = base64.b64encode(raw_signature).decode("ascii")

    attestation_path.write_text(
        json.dumps(attestation, indent=2, sort_keys=True) + "\n"
    )
    print(f"signed {attestation_path} (scheme=ed25519, canonicalization={canonicalization})")


def verify(attestation_path: Path) -> None:
    attestation = json.loads(attestation_path.read_text())
    ok, status = verify_attestation_signature(attestation)
    if ok:
        print(f"OK: signature verifies (status={status})")
    else:
        print(f"NOT VERIFIED (status={status})")
        sys.exit(1)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)

    p_kg = sub.add_parser("keygen", help="Generate a new ed25519 keypair.")
    p_kg.add_argument("--private-out", required=True, type=Path)
    p_kg.add_argument("--public-out", required=True, type=Path)

    p_sn = sub.add_parser("sign", help="Sign an attestation.json in place.")
    p_sn.add_argument("--attestation", required=True, type=Path)
    p_sn.add_argument("--private-key", required=True, type=Path)

    p_vf = sub.add_parser(
        "verify",
        help="Locally verify a signed attestation.json (round-trip self-check).",
    )
    p_vf.add_argument("--attestation", required=True, type=Path)

    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "keygen":
        keygen(args.private_out, args.public_out)
    elif args.command == "sign":
        sign(args.attestation, args.private_key)
    elif args.command == "verify":
        verify(args.attestation)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
