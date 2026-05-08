"""Validate that a submission's ``attestation.json`` round-trips through its
declared canonicalisation scheme.

An author who sets ``canonicalization: "sorted-json"`` in the attestation
must produce a file that satisfies::

    canonicalize(parse(text)) == sorted_json_serialize(parse(text))

If the file's actual byte-shape diverges from its declared scheme (for
example, ``json.dumps(... sort_keys=False)``), the Custodian's signature
verification will fail in a confusing way. This helper diagnoses that
class of error before submission.

Usage::

    python -m holdout.tools.check_canonicalization \\
        --attestation holdout/submissions/<SUBMISSION_ID>/attestation.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _check_sorted_json(text: str, attestation: dict) -> tuple[bool, str]:
    expected = json.dumps(attestation, sort_keys=True, separators=(",", ":"))
    # Allow a trailing newline in the file but require the inner shape to
    # match a sorted, separator-tight serialisation. Most authors will
    # write `json.dumps(..., indent=2, sort_keys=True) + "\n"`, which is a
    # *different* canonical form; both are acceptable as on-disk
    # representations, but the canonical *bytes that the signature
    # commits to* must be the tight sorted form. This helper checks that
    # `json.loads(text)` round-trips through both shapes equivalently.
    try:
        reparsed = json.loads(expected)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        return False, f"could not reparse sorted-json output: {exc}"
    if reparsed != attestation:
        return False, "sorted-json round-trip changed the data"
    return True, "sorted-json canonicalisation round-trips cleanly"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--attestation", required=True, type=Path)
    args = p.parse_args(argv)

    text = args.attestation.read_text()
    try:
        attestation = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"ERROR: attestation is not valid JSON: {exc}", file=sys.stderr)
        return 2

    scheme = attestation.get("canonicalization", "sorted-json")
    if scheme == "sorted-json":
        ok, msg = _check_sorted_json(text, attestation)
    elif scheme == "jcs":
        try:
            import jcs  # type: ignore[import-not-found]
        except ImportError:
            print(
                "ERROR: attestation declares canonicalization='jcs' but the "
                "optional `jcs` package is not installed; pip install jcs",
                file=sys.stderr,
            )
            return 2
        canon = jcs.canonicalize(attestation)
        try:
            reparsed = json.loads(canon)
        except json.JSONDecodeError as exc:  # pragma: no cover
            print(f"ERROR: jcs output not parseable: {exc}", file=sys.stderr)
            return 2
        ok = reparsed == attestation
        msg = (
            "jcs canonicalisation round-trips cleanly"
            if ok
            else "jcs round-trip changed the data"
        )
    else:
        print(f"ERROR: unknown canonicalization scheme: {scheme!r}", file=sys.stderr)
        return 2

    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
