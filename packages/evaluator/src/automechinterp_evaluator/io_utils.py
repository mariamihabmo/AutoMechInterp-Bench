"""IO helpers for JSON/YAML/JSONL with deterministic writing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


# Audit-final §2.D.2: every text read/write in this module is now explicitly
# UTF-8. Relying on the platform default makes Windows submitters see
# UnicodeDecodeError on non-ASCII bundle metadata and lets BOM-prefixed JSON
# from Excel users slip into the parser as ``\ufeff{``. Strip a leading BOM
# defensively in every read path so we round-trip cleanly.

_UTF8 = "utf-8"
_UTF8_SIG = "utf-8-sig"


class BundleError(ValueError):
    """Raised when bundle files are malformed or inconsistent."""


def _read_text(path: Path) -> str:
    # ``utf-8-sig`` transparently strips a UTF-8 BOM if present; otherwise it
    # behaves identically to ``utf-8``.
    return path.read_text(encoding=_UTF8_SIG)


def _reject_non_finite(token: str) -> Any:
    """``json.loads`` parse_constant hook.

    Audit-final §gpt2.B1: stdlib ``json`` accepts the non-standard tokens
    ``NaN``, ``Infinity``, and ``-Infinity`` by default. Bundle files must
    be strict JSON, and downstream stats are undefined on non-finite
    numbers, so reject them at parse time with a structured error.
    """
    raise BundleError(
        f"non-finite JSON token {token!r} is rejected; bundle JSON must be "
        "strict (no NaN/Infinity literals)"
    )


def read_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(_read_text(path))
    except Exception as exc:  # pragma: no cover - defensive
        raise BundleError(f"Failed to parse YAML: {path}") from exc
    if not isinstance(data, dict):
        raise BundleError(f"YAML must be a mapping: {path}")
    return data


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(_read_text(path), parse_constant=_reject_non_finite)
    except BundleError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise BundleError(f"Failed to parse JSON: {path}") from exc
    if not isinstance(data, dict):
        raise BundleError(f"JSON must be an object: {path}")
    return data


def read_json_any(path: Path) -> Any:
    try:
        return json.loads(_read_text(path), parse_constant=_reject_non_finite)
    except BundleError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise BundleError(f"Failed to parse JSON: {path}") from exc


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, line in enumerate(_read_text(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line, parse_constant=_reject_non_finite)
        except BundleError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise BundleError(f"Invalid JSONL at {path}:{lineno}") from exc
        if not isinstance(row, dict):
            raise BundleError(f"JSONL row must be object at {path}:{lineno}")
        rows.append(row)
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding=_UTF8,
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [json.dumps(row, sort_keys=True, allow_nan=False) for row in rows]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding=_UTF8)


def write_text(path: Path, payload: str) -> None:
    path.write_text(payload, encoding=_UTF8)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()
