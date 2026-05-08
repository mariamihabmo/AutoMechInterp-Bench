"""Utilities for generating validated hypothesis.jsonl from agent output."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .io_utils import (
    BundleError,
    read_json_any,
    read_jsonl,
    read_yaml,
    sha256_file,
    write_json,
    write_jsonl,
)
from .loader import validate_hypotheses, validate_protocol


def _detect_input_format(path: Path, input_format: str) -> str:
    if input_format in {"json", "jsonl"}:
        return input_format
    if input_format != "auto":
        raise BundleError("input_format must be one of: auto, json, jsonl")

    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return "jsonl"
    return "json"


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        if not payload:
            raise BundleError("Agent output contains empty list")
        if not all(isinstance(row, dict) for row in payload):
            raise BundleError("Agent JSON list must contain only objects")
        return [dict(row) for row in payload]

    if isinstance(payload, dict):
        for key in ("hypotheses", "items", "candidates"):
            rows = payload.get(key)
            if isinstance(rows, list):
                if not rows or not all(isinstance(row, dict) for row in rows):
                    raise BundleError(f"Agent JSON '{key}' must be a non-empty list of objects")
                return [dict(row) for row in rows]
        return [dict(payload)]

    raise BundleError("Agent output JSON must be an object or list of objects")


def _normalized_hypothesis_id(row: dict[str, Any], idx: int) -> str:
    raw_id = row.get("hypothesis_id")
    if isinstance(raw_id, str) and raw_id.strip():
        return raw_id.strip()

    seed = row.get("claim_text") or row.get("mechanistic_claim") or json.dumps(row, sort_keys=True)
    digest = hashlib.sha256(str(seed).encode("utf-8")).hexdigest()[:10]
    return f"h_{idx:03d}_{digest}"


def _normalize_row(row: dict[str, Any], protocol: dict, idx: int) -> dict[str, Any]:
    unit = protocol["unit_of_work"]

    normalized = dict(row)

    # Canonical aliases that agents frequently use.
    if "claim_text" not in normalized and "mechanistic_claim" in normalized:
        normalized["claim_text"] = normalized["mechanistic_claim"]
    if "candidate_components" not in normalized and "components" in normalized:
        normalized["candidate_components"] = normalized["components"]
    if "predicted_min_effect" not in normalized and "predicted_effect_size" in normalized:
        normalized["predicted_min_effect"] = normalized["predicted_effect_size"]
    if "predicted_specificity_ratio" not in normalized and "specificity_ratio" in normalized:
        normalized["predicted_specificity_ratio"] = normalized["specificity_ratio"]
    if "expected_failure_modes" not in normalized and "failure_modes" in normalized:
        normalized["expected_failure_modes"] = normalized["failure_modes"]

    normalized["protocol_id"] = protocol["protocol_id"]
    normalized["task_id"] = unit["task_id"]
    normalized["model_id"] = unit["model_id"]
    normalized["metric_id"] = unit["metric_id"]

    direction = normalized.get("predicted_effect_direction")
    if isinstance(direction, str):
        mapped = {
            "up": "increase",
            "positive": "increase",
            "inc": "increase",
            "down": "decrease",
            "negative": "decrease",
            "dec": "decrease",
        }.get(direction.strip().lower())
        if mapped:
            normalized["predicted_effect_direction"] = mapped

    normalized["hypothesis_id"] = _normalized_hypothesis_id(normalized, idx)

    # Keep this explicit to avoid accidental empty field failures from sparse agent output.
    if "expected_failure_modes" not in normalized:
        normalized["expected_failure_modes"] = ["agent_unspecified_failure_modes"]

    return normalized


def _load_agent_rows(input_path: Path, input_format: str) -> list[dict[str, Any]]:
    detected = _detect_input_format(input_path, input_format)
    if detected == "jsonl":
        return read_jsonl(input_path)
    payload = read_json_any(input_path)
    return _extract_rows(payload)


def refresh_manifest(bundle_dir: Path) -> Path:
    manifest: dict[str, str] = {}
    for filename in ("protocol.yaml", "hypothesis.jsonl", "evaluation_result.json"):
        path = bundle_dir / filename
        if path.exists():
            manifest[filename] = sha256_file(path)
    manifest_path = bundle_dir / "manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path


def generate_hypotheses_from_agent_output(
    *,
    bundle_dir: Path,
    input_path: Path,
    input_format: str = "auto",
    output_path: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    protocol_path = bundle_dir / "protocol.yaml"
    if not protocol_path.exists():
        raise BundleError("Bundle must contain protocol.yaml before generating hypotheses")

    protocol = read_yaml(protocol_path)
    validate_protocol(protocol)

    rows = _load_agent_rows(input_path, input_format)
    normalized = [_normalize_row(row, protocol=protocol, idx=i) for i, row in enumerate(rows, start=1)]
    validate_hypotheses(normalized, protocol)

    canonical_target = bundle_dir / "hypothesis.jsonl"
    target = output_path or canonical_target
    if target.exists() and not overwrite:
        raise BundleError(f"Refusing to overwrite existing file without --overwrite: {target}")

    write_jsonl(target, normalized)
    manifest_path: str | None = None
    if target.resolve() == canonical_target.resolve():
        manifest_path = str(refresh_manifest(bundle_dir))

    return {
        "bundle": str(bundle_dir),
        "input": str(input_path),
        "output": str(target),
        "manifest": manifest_path,
        "hypothesis_count": len(normalized),
        "hypothesis_ids": [row["hypothesis_id"] for row in normalized],
    }
