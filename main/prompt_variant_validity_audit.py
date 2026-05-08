#!/usr/bin/env python3
"""Audit whether artifact protocols use task-supported prompt variants.

Several task modules historically treated unknown prompt variants as the base
prompt. That is dangerous for a verifier benchmark because it can make a
protocol look prompt-robust when two nominal variants are actually identical.
This audit keeps that risk explicit for existing artifacts while the Stage-2
runner now fails loudly on future unsupported variants.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

try:
    from _bundle_analysis import (
        REAL_MULTILANE_DIR,
        REAL_MULTI_TASK_DIR,
        find_bundle_dirs,
        repo_relative,
        write_json,
        write_text,
    )
except ModuleNotFoundError:
    from main._bundle_analysis import (
        REAL_MULTILANE_DIR,
        REAL_MULTI_TASK_DIR,
        find_bundle_dirs,
        repo_relative,
        write_json,
        write_text,
    )

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_runner.tasks import get_task_module  # noqa: E402

SCAN_ROOTS = [
    ROOT / "main" / "output" / "real_multi_task",
    ROOT / "main" / "output" / "real_multilane",
    ROOT / "main" / "output" / "zero_task_real_repair",
    ROOT / "main" / "output" / "docstring_distributed_repair",
]
REPRO = ROOT / "main" / "output" / "repro"
OUT_JSON = REPRO / "prompt_variant_validity_audit.json"
OUT_MD = REPRO / "prompt_variant_validity_audit.md"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _protocol_paths() -> list[Path]:
    rows: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        rows.extend(sorted(root.glob("*/protocol.yaml")))
    return rows


def _accepted_count(bundle_dir: Path) -> int:
    current = _load_json(bundle_dir / "evaluation_result_current.json")
    if current:
        return int((current.get("overall") or {}).get("accepted_count") or 0)
    released = _load_json(bundle_dir / "evaluation_result.json")
    return int((released.get("overall") or {}).get("accepted_count") or 0)


def _unsupported_record(protocol_path: Path) -> dict[str, Any] | None:
    protocol = yaml.safe_load(protocol_path.read_text())
    task_id = str(protocol["unit_of_work"]["task_id"])
    model_id = str(protocol["unit_of_work"]["model_id"])
    used = [str(v) for v in protocol.get("execution_grid", {}).get("prompt_variants", [])]
    supported = list(getattr(get_task_module(task_id), "PROMPT_VARIANTS", []) or [])
    unsupported = sorted({variant for variant in used if variant not in supported})
    if not unsupported:
        return None
    bundle_dir = protocol_path.parent
    return {
        "bundle": bundle_dir.name,
        "path": repo_relative(bundle_dir),
        "task_id": task_id,
        "model_id": model_id,
        "used_prompt_variants": used,
        "supported_prompt_variants": supported,
        "unsupported_prompt_variants": unsupported,
        "accepted_claims_in_bundle": _accepted_count(bundle_dir),
    }


def main() -> None:
    records: list[dict[str, Any]] = []
    for protocol_path in _protocol_paths():
        record = _unsupported_record(protocol_path)
        if record is not None:
            records.append(record)

    affected_accepted = sum(int(row["accepted_claims_in_bundle"]) for row in records)
    canonical_protocols = [bundle / "protocol.yaml" for bundle in find_bundle_dirs(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR)]
    canonical_records = [
        record for record in (_unsupported_record(path) for path in canonical_protocols) if record is not None
    ]
    canonical_affected = sum(int(row["accepted_claims_in_bundle"]) for row in canonical_records)
    if not records:
        status = "pass"
    elif not canonical_records:
        status = "warn_legacy_unsupported_prompt_variants_canonical_clean"
    else:
        status = "warn_unsupported_prompt_variants_in_existing_artifacts"
    payload = {
        "generated_by": "main/prompt_variant_validity_audit.py",
        "status": status,
        "protocol_files_scanned": len(_protocol_paths()),
        "files_with_unsupported_prompt_variants": len(records),
        "affected_accepted_claims_in_existing_artifacts": affected_accepted,
        "canonical_protocol_files_scanned": len(canonical_protocols),
        "canonical_files_with_unsupported_prompt_variants": len(canonical_records),
        "canonical_affected_accepted_claims": canonical_affected,
        "future_runner_policy": "Stage-2 now raises Stage2Error for unsupported prompt variants.",
        "claim_boundary": (
            "Unsupported prompt variants in existing artifacts should be treated as prompt-aliasing risk, "
            "not evidence of prompt robustness for those nominal variants."
        ),
        "records": records,
        "canonical_records": canonical_records,
        "remediation": [
            "Do not upgrade any prompt-robustness claim from affected artifacts until the bundle is rerun with task-supported variants.",
            "Use task module PROMPT_VARIANTS when constructing future protocols.",
            "For docstring_v0, use variants such as base+detailed or base+brief rather than paraphrase.",
        ],
    }
    write_json(OUT_JSON, payload)

    lines = [
        "# Prompt Variant Validity Audit",
        "",
        f"- Status: **{payload['status']}**",
        f"- Protocol files scanned: **{payload['protocol_files_scanned']}**",
        f"- Files with unsupported prompt variants: **{payload['files_with_unsupported_prompt_variants']}**",
        f"- Accepted claims in affected existing artifacts: **{payload['affected_accepted_claims_in_existing_artifacts']}**",
        f"- Canonical files with unsupported prompt variants: **{payload['canonical_files_with_unsupported_prompt_variants']}**",
        f"- Canonical accepted claims in affected bundles: **{payload['canonical_affected_accepted_claims']}**",
        "",
        payload["claim_boundary"],
        "",
        "## Affected Artifacts",
        "",
        "| Bundle | Task | Model | Unsupported | Accepted claims |",
        "|---|---|---|---|---:|",
    ]
    if records:
        for row in records:
            lines.append(
                f"| `{row['path']}` | `{row['task_id']}` | `{row['model_id']}` | "
                f"`{', '.join(row['unsupported_prompt_variants'])}` | {row['accepted_claims_in_bundle']} |"
            )
    else:
        lines.append("| none | - | - | - | 0 |")
    lines.extend(["", "## Remediation", ""])
    lines.extend(f"- {item}" for item in payload["remediation"])
    write_text(OUT_MD, "\n".join(lines).rstrip() + "\n")
    print(str(OUT_JSON))


if __name__ == "__main__":
    main()
