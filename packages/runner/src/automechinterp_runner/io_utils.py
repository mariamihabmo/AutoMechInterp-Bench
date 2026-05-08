"""IO helpers for stage-2 runner."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


class Stage2Error(ValueError):
    """Raised for Stage-2 configuration or execution errors."""


def read_yaml(path: Path) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(path.read_text())
    except Exception as exc:  # pragma: no cover - defensive
        raise Stage2Error(f"Failed to parse YAML: {path}") from exc
    if not isinstance(payload, dict):
        raise Stage2Error(f"YAML must be a mapping: {path}")
    return payload


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception as exc:  # pragma: no cover - defensive
            raise Stage2Error(f"Invalid JSONL at {path}:{lineno}") from exc
        if not isinstance(row, dict):
            raise Stage2Error(f"JSONL row must be object at {path}:{lineno}")
        rows.append(row)
    if not rows:
        raise Stage2Error(f"Expected non-empty JSONL file: {path}")
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def update_manifest(bundle_dir: Path) -> Path:
    manifest = {}
    for filename in ("protocol.yaml", "hypothesis.jsonl", "evaluation_result.json"):
        path = bundle_dir / filename
        if path.exists():
            manifest[filename] = sha256_file(path)
    manifest_path = bundle_dir / "manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path
