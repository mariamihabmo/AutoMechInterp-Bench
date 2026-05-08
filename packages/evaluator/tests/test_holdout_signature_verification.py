"""Unit tests for the cryptographic signing + verification path.

Audit-final \u00a72.E.1 / latest_opus_audit \u00a7P2-A.1, P2-D.1, P2-D.5: the
holdout Custodian's signature gate must (a) actually verify ed25519
signatures and (b) reject obvious tampering. These tests pin a
known-good keypair against a fixed attestation, then exercise:

* round-trip sign \u2192 verify (must accept),
* tampered ``signature`` field (must reject),
* tampered ``public_key`` field (must reject \u2014 the canonical payload
  binds the public key into the signature),
* tampered payload field (must reject),
* malformed base64 (must reject).
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

cryptography = pytest.importorskip("cryptography")
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

from holdout.tools.evaluate_holdout_submission import (  # noqa: E402
    canonicalize_attestation,
    verify_attestation_signature,
)

def _make_attestation() -> dict:
    return {
        "submission_id": "test_sig_0001",
        "submission_kind": "external_blinded",
        "canonicalization": "sorted-json",
        "author_institution": "Anonymous University",
        "contract_pin": {
            "constants_sha256": "0" * 64,
            "evaluator_version": "0.0.0-test",
        },
        "attestation_signature": {
            "scheme": "ed25519",
            "public_key": "",
            "signature": "",
        },
    }

def _sign(attestation: dict, priv: Ed25519PrivateKey) -> dict:
    from cryptography.hazmat.primitives import serialization

    pub_raw = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    attestation["attestation_signature"]["public_key"] = base64.b64encode(pub_raw).decode("ascii")
    attestation["attestation_signature"]["signature"] = ""
    payload = canonicalize_attestation(attestation, "sorted-json")
    sig = priv.sign(payload)
    attestation["attestation_signature"]["signature"] = base64.b64encode(sig).decode("ascii")
    return attestation

def test_signature_round_trip_accepts():
    priv = Ed25519PrivateKey.generate()
    att = _sign(_make_attestation(), priv)
    ok, status = verify_attestation_signature(att)
    assert ok is True
    assert status == "ed25519"

def test_tampered_signature_rejects():
    priv = Ed25519PrivateKey.generate()
    att = _sign(_make_attestation(), priv)
    sig = att["attestation_signature"]["signature"]
    sig_bytes = bytearray(base64.b64decode(sig))
    sig_bytes[0] ^= 0x01
    att["attestation_signature"]["signature"] = base64.b64encode(bytes(sig_bytes)).decode("ascii")
    with pytest.raises(ValueError, match="does not verify"):
        verify_attestation_signature(att)

def test_tampered_public_key_rejects():
    priv = Ed25519PrivateKey.generate()
    att = _sign(_make_attestation(), priv)
    other = Ed25519PrivateKey.generate()
    from cryptography.hazmat.primitives import serialization

    other_pub = other.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    att["attestation_signature"]["public_key"] = base64.b64encode(other_pub).decode("ascii")
    with pytest.raises(ValueError, match="does not verify"):
        verify_attestation_signature(att)

def test_tampered_payload_rejects():
    priv = Ed25519PrivateKey.generate()
    att = _sign(_make_attestation(), priv)
    att["author_institution"] = "Different Institution"
    with pytest.raises(ValueError, match="does not verify"):
        verify_attestation_signature(att)

def test_malformed_base64_rejects():
    priv = Ed25519PrivateKey.generate()
    att = _sign(_make_attestation(), priv)
    att["attestation_signature"]["signature"] = "not!valid!base64!"
    with pytest.raises(ValueError, match="not valid base64"):
        verify_attestation_signature(att)

def test_wrong_signature_length_rejects():
    att = _make_attestation()
    att["attestation_signature"]["public_key"] = base64.b64encode(b"\x00" * 32).decode("ascii")
    att["attestation_signature"]["signature"] = base64.b64encode(b"\x00" * 16).decode("ascii")
    with pytest.raises(ValueError, match="signature must be 64 bytes"):
        verify_attestation_signature(att)

def test_non_external_kind_skips():
    att = _make_attestation()
    att["submission_kind"] = "maintainer_pilot"
    ok, status = verify_attestation_signature(att)
    assert ok is False
    assert status.startswith("skipped")

def test_canonicalization_excludes_signature_field():
    """The canonical payload must omit the signature byte-string itself but
    include the scheme/public_key fields (so an attacker cannot swap keys
    after signing)."""

    att = _make_attestation()
    att["attestation_signature"]["public_key"] = "AAAA"
    att["attestation_signature"]["signature"] = "BBBB"
    payload_a = canonicalize_attestation(att, "sorted-json")

    att["attestation_signature"]["signature"] = "CCCC"  # signature changed
    payload_b = canonicalize_attestation(att, "sorted-json")
    assert payload_a == payload_b, "signature byte-string must not affect canonical payload"

    att["attestation_signature"]["public_key"] = "DDDD"  # public key changed
    payload_c = canonicalize_attestation(att, "sorted-json")
    assert payload_a != payload_c, "public_key change must affect canonical payload"
