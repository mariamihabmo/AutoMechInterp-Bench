#!/usr/bin/env python3
"""Independent-agnostic-stress intake and rehearsal wrapper.

This script has two deliberately separate modes:

1. ``--rehearsal-from-cached`` projects the existing benchmark-authored current
   and V1 stress artifacts into the independent-stress reporting schema. This
   is plumbing evidence only.
2. ``--negative-set`` validates an externally authored JSONL negative set
   against ``docs/reference/independent_agnostic_negative_spec.md``. If every
   row also includes scorable ``evidence_cells``, the same frozen negative set
   is evaluated under the requested contract and reported with a false-accept
   rate. Claim-upgrade language still requires external provenance or
   custodian attestation; a locally authored scorable set is only a pipeline
   rehearsal.

The separation is intentional: without an external author and scorable evidence
cells, the repository must not manufacture "independent" Goodhart evidence.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

try:
    from _bundle_analysis import (
        REAL_MULTI_TASK_DIR,
        REAL_MULTILANE_DIR,
        find_bundle_dirs,
        wilson_interval,
        write_json,
        write_text,
    )
    from contract_hardening_v1 import _harden_protocol
except ModuleNotFoundError:
    from main._bundle_analysis import (
        REAL_MULTI_TASK_DIR,
        REAL_MULTILANE_DIR,
        find_bundle_dirs,
        wilson_interval,
        write_json,
        write_text,
    )
    from main.contract_hardening_v1 import _harden_protocol

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "main" / "output" / "repro"
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.evaluator import evaluate_bundle  # noqa: E402
from automechinterp_evaluator.io_utils import sha256_file  # noqa: E402

REQUIRED_FIELDS = {
    "negative_id",
    "task_id",
    "model_id",
    "claim_text",
    "candidate_components",
    "predicted_effect_direction",
    "author_slice",
    "visibility",
}
REQUIRED_VISIBILITY_FIELDS = {
    "saw_public_bundles",
    "saw_gate_taxonomy",
    "saw_v1_thresholds",
    "received_scoring_feedback",
}
REQUIRED_EVIDENCE_CELL_FIELDS = {
    "seed",
    "prompt_variant",
    "resample_id",
    "method",
    "slice",
    "treatment_effect",
    "control_effects",
    "runner_id",
    "runner_version",
    "pipeline_sha",
    "model_ref",
    "dataset_seed",
    "prompt_template_id",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _read_negative_rows(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    with path.open() as handle:
        for lineno, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {lineno}: invalid JSON: {exc}")
                continue
            rows.append(row)
    return rows, errors


def _validate_negative_set(path: Path) -> dict[str, Any]:
    rows, errors = _read_negative_rows(path)
    ids: set[str] = set()
    slice_counts: dict[str, int] = {}
    task_counts: dict[str, int] = {}
    model_counts: dict[str, int] = {}
    rows_with_evidence_cells = 0

    for lineno, row in enumerate(rows, start=1):
        missing = REQUIRED_FIELDS - set(row)
        if missing:
            errors.append(f"line {lineno}: missing required fields {sorted(missing)}")
        visibility = row.get("visibility")
        if not isinstance(visibility, dict):
            errors.append(f"line {lineno}: visibility must be an object")
        else:
            missing_visibility = REQUIRED_VISIBILITY_FIELDS - set(visibility)
            if missing_visibility:
                errors.append(
                    f"line {lineno}: visibility missing fields {sorted(missing_visibility)}"
                )
        negative_id = str(row.get("negative_id"))
        if negative_id in ids:
            errors.append(f"line {lineno}: duplicate negative_id {negative_id!r}")
        ids.add(negative_id)
        if row.get("predicted_effect_direction") not in {"increase", "decrease"}:
            errors.append(f"line {lineno}: predicted_effect_direction must be increase or decrease")
        if not isinstance(row.get("candidate_components"), list) or not row.get("candidate_components"):
            errors.append(f"line {lineno}: candidate_components must be a non-empty list")
        evidence_cells = row.get("evidence_cells")
        if evidence_cells is not None:
            rows_with_evidence_cells += 1
            if not isinstance(evidence_cells, list) or not evidence_cells:
                errors.append(f"line {lineno}: evidence_cells must be a non-empty list when present")
            else:
                for cell_idx, cell in enumerate(evidence_cells, start=1):
                    if not isinstance(cell, dict):
                        errors.append(f"line {lineno}: evidence_cells[{cell_idx}] must be an object")
                        continue
                    missing_cell_fields = REQUIRED_EVIDENCE_CELL_FIELDS - set(cell)
                    if missing_cell_fields:
                        errors.append(
                            f"line {lineno}: evidence_cells[{cell_idx}] missing fields {sorted(missing_cell_fields)}"
                        )
                    if "control_effects" in cell and not isinstance(cell.get("control_effects"), dict):
                        errors.append(f"line {lineno}: evidence_cells[{cell_idx}].control_effects must be an object")

        author_slice = str(row.get("author_slice"))
        task = str(row.get("task_id"))
        model = str(row.get("model_id"))
        slice_counts[author_slice] = slice_counts.get(author_slice, 0) + 1
        task_counts[task] = task_counts.get(task, 0) + 1
        model_counts[model] = model_counts.get(model, 0) + 1

    visibility_rows = [row.get("visibility") or {} for row in rows if isinstance(row.get("visibility"), dict)]
    evidence_bearing_visibility = all(
        not bool(vis.get("saw_v1_thresholds")) and not bool(vis.get("received_scoring_feedback"))
        for vis in visibility_rows
    )
    return {
        "path": str(path),
        "n_rows": len(rows),
        "valid": not errors,
        "errors": errors[:50],
        "error_count": len(errors),
        "slice_counts": slice_counts,
        "task_counts": task_counts,
        "model_counts": model_counts,
        "visibility_evidence_bearing": evidence_bearing_visibility,
        "minimum_size_met": len(rows) >= 200,
        "rows_with_evidence_cells": rows_with_evidence_cells,
        "all_rows_have_evidence_cells": bool(rows) and rows_with_evidence_cells == len(rows),
        "scoring_ready": (not errors) and bool(rows) and rows_with_evidence_cells == len(rows),
    }


def _cached_current() -> dict[str, Any]:
    artifact = REPRO / "stress_test_agnostic_fresh_release_grade.json"
    payload = _load_json(artifact)
    row = ((payload.get("conditions") or {}).get("full_contract") or {})
    return {
        "source_artifact": str(artifact.relative_to(ROOT)),
        "negatives": int(row.get("total") or payload.get("negatives") or 0),
        "false_accepts": int(row.get("leaked") or 0),
        "false_accept_rate": float(row.get("false_accept_rate") or 0.0),
        "false_accept_rate_ci95": row.get("false_accept_rate_ci95") or {},
        "generator_regime": payload.get("generator_regime"),
        "seed_namespace": payload.get("seed_namespace"),
        "statistical_budget": payload.get("statistical_budget") or {},
    }


def _cached_hardened() -> dict[str, Any]:
    summary_artifact = REPRO / "contract_hardening_v1_summary.json"
    summary = _load_json(summary_artifact)
    row = summary.get("fresh_agnostic_hardened_v1") or _load_json(
        REPRO / "stress_test_agnostic_hardened_v1.json"
    )
    return {
        "source_artifact": str(summary_artifact.relative_to(ROOT)),
        "negatives": int(row.get("negatives") or 0),
        "false_accepts": int(row.get("leaked") or 0),
        "false_accept_rate": float(row.get("false_accept_rate") or 0.0),
        "false_accept_rate_ci95": row.get("false_accept_rate_ci95") or {},
        "generator_regime": row.get("generator_regime"),
        "seed_namespace": row.get("seed_namespace"),
        "statistical_budget": row.get("statistical_budget") or {},
        "contract_hardening_v1": row.get("contract_hardening_v1") or summary.get("contract_hardening_v1"),
    }


def _protocol_lookup() -> dict[tuple[str, str], dict[str, Any]]:
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for bundle_dir in find_bundle_dirs(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR):
        protocol = yaml.safe_load((bundle_dir / "protocol.yaml").read_text())
        key = (
            str(protocol["unit_of_work"]["task_id"]),
            str(protocol["unit_of_work"]["model_id"]),
        )
        lookup.setdefault(key, protocol)
    return lookup


def _protocol_for_group(
    lookup: dict[tuple[str, str], dict[str, Any]],
    *,
    task_id: str,
    model_id: str,
    contract: str,
    row_count: int,
) -> dict[str, Any]:
    key = (task_id, model_id)
    if key not in lookup:
        raise ValueError(f"no released protocol available for task/model {task_id}/{model_id}")
    protocol = copy.deepcopy(lookup[key])
    if contract == "contract_hardening_v1":
        protocol = _harden_protocol(protocol)
    protocol["protocol_id"] = f"independent_agnostic_{contract}_{task_id}_{model_id}"
    protocol.setdefault("claim_budget", {})
    protocol["claim_budget"]["max_total_claims"] = max(
        int(protocol["claim_budget"].get("max_total_claims", 0)),
        row_count,
    )
    protocol["claim_budget"]["max_claims_per_task"] = max(
        int(protocol["claim_budget"].get("max_claims_per_task", 0)),
        row_count,
    )
    return protocol


def _negative_to_hypothesis(row: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    return {
        "hypothesis_id": str(row["negative_id"]),
        "protocol_id": protocol["protocol_id"],
        "task_id": str(row["task_id"]),
        "model_id": str(row["model_id"]),
        "metric_id": str(protocol["unit_of_work"]["metric_id"]),
        "claim_text": str(row["claim_text"]),
        "candidate_components": row["candidate_components"],
        "predicted_effect_direction": str(row["predicted_effect_direction"]),
        "predicted_min_effect": float(
            row.get(
                "predicted_min_effect",
                protocol.get("statistical_policy", {}).get("min_effect_floor", 0.02),
            )
        ),
        "predicted_specificity_ratio": float(
            row.get(
                "predicted_specificity_ratio",
                protocol.get("stage_gates", {}).get("min_specificity_ratio", 2.0),
            )
        ),
        "expected_failure_modes": list(
            dict.fromkeys(
                [
                    "independent_agnostic_negative",
                    str(row.get("author_slice", "unspecified_slice")),
                    *(str(mode) for mode in row.get("expected_failure_modes", []) if str(mode).strip()),
                ]
            )
        ),
        "provider_id": "independent_agnostic_negative_set",
        "discovery_lane": str(row.get("author_slice", "independent_agnostic_negative")),
    }


def _normalise_cell(cell: dict[str, Any]) -> dict[str, Any]:
    normalised = dict(cell)
    normalised["seed"] = int(normalised["seed"])
    normalised["resample_id"] = int(normalised["resample_id"])
    normalised["dataset_seed"] = int(normalised["dataset_seed"])
    normalised["prompt_variant"] = str(normalised["prompt_variant"])
    normalised["method"] = str(normalised["method"])
    normalised["slice"] = str(normalised["slice"])
    normalised["runner_id"] = str(normalised["runner_id"])
    normalised["runner_version"] = str(normalised["runner_version"])
    normalised["pipeline_sha"] = str(normalised["pipeline_sha"])
    normalised["model_ref"] = str(normalised["model_ref"])
    normalised["prompt_template_id"] = str(normalised["prompt_template_id"])
    if "direction" in normalised:
        normalised["direction"] = str(normalised["direction"])
    normalised["treatment_effect"] = float(normalised["treatment_effect"])
    normalised["control_effects"] = {
        str(key): float(value)
        for key, value in (normalised.get("control_effects") or {}).items()
    }
    return normalised


def _write_scorable_bundle(bundle_dir: Path, protocol: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    protocol_path = bundle_dir / "protocol.yaml"
    hypothesis_path = bundle_dir / "hypothesis.jsonl"
    evaluation_path = bundle_dir / "evaluation_result.json"
    manifest_path = bundle_dir / "manifest.json"

    protocol_path.write_text(yaml.safe_dump(protocol, sort_keys=False))
    hypotheses = [_negative_to_hypothesis(row, protocol) for row in rows]
    hypothesis_path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in hypotheses)
        + ("\n" if hypotheses else "")
    )
    evaluation_result = {
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": sha256_file(protocol_path),
        "hypothesis_results": [
            {
                "hypothesis_id": str(row["negative_id"]),
                "raw_cells": [_normalise_cell(cell) for cell in row["evidence_cells"]],
            }
            for row in rows
        ],
    }
    evaluation_path.write_text(json.dumps(evaluation_result, indent=2, sort_keys=True) + "\n")
    manifest = {
        "protocol.yaml": sha256_file(protocol_path),
        "hypothesis.jsonl": sha256_file(hypothesis_path),
        "evaluation_result.json": sha256_file(evaluation_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def _score_negative_set(path: Path, contract: str) -> dict[str, Any]:
    rows, read_errors = _read_negative_rows(path)
    if read_errors:
        raise ValueError("; ".join(read_errors[:10]))
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["task_id"]), str(row["model_id"]))].append(row)

    lookup = _protocol_lookup()
    group_results: list[dict[str, Any]] = []
    leaked_negatives: list[dict[str, Any]] = []
    false_accepts = 0
    total = 0
    with tempfile.TemporaryDirectory(prefix=f"independent_agnostic_{contract}_") as tmpdir:
        tmp_root = Path(tmpdir)
        for (task_id, model_id), group_rows in sorted(grouped.items()):
            protocol = _protocol_for_group(
                lookup,
                task_id=task_id,
                model_id=model_id,
                contract=contract,
                row_count=len(group_rows),
            )
            bundle_dir = tmp_root / f"{task_id}_{model_id}".replace("/", "_")
            _write_scorable_bundle(bundle_dir, protocol, group_rows)
            evaluation = evaluate_bundle(bundle_dir)
            reports = evaluation.get("claim_reports", [])
            group_leaks = [row for row in reports if row.get("passed")]
            false_accepts += len(group_leaks)
            total += int(evaluation.get("overall", {}).get("hypothesis_count", len(group_rows)))
            leaked_negatives.extend(
                {
                    "negative_id": str(row["hypothesis_id"]),
                    "task_id": task_id,
                    "model_id": model_id,
                    "evidence_tier": row.get("evidence_tier"),
                    "failed_checks": row.get("failed_checks", []),
                }
                for row in group_leaks
            )
            group_results.append(
                {
                    "task_id": task_id,
                    "model_id": model_id,
                    "negatives": int(evaluation.get("overall", {}).get("hypothesis_count", len(group_rows))),
                    "false_accepts": len(group_leaks),
                    "false_accept_rate": len(group_leaks) / len(group_rows) if group_rows else 0.0,
                    "accepted_ids_sha256": hashlib.sha256(
                        "\n".join(sorted(str(row["hypothesis_id"]) for row in group_leaks)).encode("utf-8")
                    ).hexdigest(),
                }
            )

    return {
        "source_artifact": str(path),
        "negatives": total,
        "false_accepts": false_accepts,
        "false_accept_rate": false_accepts / total if total else 0.0,
        "false_accept_rate_ci95": wilson_interval(false_accepts, total),
        "group_results": group_results,
        "leaked_negative_count": len(leaked_negatives),
        "leaked_negatives": leaked_negatives[:50],
    }


def _build_payload(args: argparse.Namespace) -> dict[str, Any]:
    validation = _validate_negative_set(args.negative_set) if args.negative_set else None
    if args.rehearsal_from_cached:
        stress = _cached_current() if args.contract == "current" else _cached_hardened()
        status = "benchmark_authored_rehearsal_not_independent_evidence"
        scoring_available = True
    else:
        if validation and validation["scoring_ready"]:
            stress = _score_negative_set(args.negative_set, args.contract)
            scoring_available = True
            status = (
                "scorable_negative_set_scored_attestation_required"
                if validation["visibility_evidence_bearing"]
                else "scorable_negative_set_scored_not_evaluator_agnostic"
            )
        else:
            stress = {
                "negatives": validation["n_rows"] if validation else 0,
                "false_accepts": None,
                "false_accept_rate": None,
                "false_accept_rate_ci95": {},
                "source_artifact": None,
            }
            status = "negative_set_validated_scoring_unavailable_missing_evidence_cells"
            scoring_available = False

    return {
        "generated_by": "main/run_independent_agnostic_stress.py",
        "contract": args.contract,
        "status": status,
        "scoring_available": scoring_available,
        "negative_set_validation": validation,
        "stress_result": stress,
        "claim_boundary": (
            "This is benchmark-authored rehearsal output, not independent Goodhart evidence."
            if args.rehearsal_from_cached
            else (
                "This scores a scorable negative set, but it becomes independent Goodhart evidence only with external provenance or custodian attestation."
                if scoring_available
                else "This validates input format only; false-accept scoring requires scorable evidence_cells or a registered generator."
            )
        ),
        "required_for_claim_upgrade": [
            "externally authored negative set frozen before scoring",
            "same negative set scored under current and V1 candidate contracts",
            "false-accept rates with Wilson confidence intervals",
            "accepted-claim and accepted-task retention under V1",
            "migration decision recorded before paper claim upgrade",
        ],
    }


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value * 100:.1f}%"
    return "n/a" if value is None else str(value)


def format_md(payload: dict[str, Any]) -> str:
    stress = payload["stress_result"]
    validation = payload.get("negative_set_validation")
    lines = [
        "# Independent Agnostic Stress Report",
        "",
        f"- Contract: **{payload['contract']}**",
        f"- Status: **{payload['status']}**",
        f"- Scoring available: **{payload['scoring_available']}**",
        f"- Negatives: **{stress.get('negatives', 'n/a')}**",
        f"- False accepts: **{stress.get('false_accepts', 'n/a')}**",
        f"- FAR: **{_fmt(stress.get('false_accept_rate'))}**",
        f"- 95% CI: **{(stress.get('false_accept_rate_ci95') or {}).get('label', 'n/a')}**",
        f"- Source artifact: `{stress.get('source_artifact') or 'n/a'}`",
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"],
        "",
    ]
    if validation is not None:
        lines.extend(
            [
                "## Negative Set Validation",
                "",
                f"- Path: `{validation['path']}`",
                f"- Rows: **{validation['n_rows']}**",
                f"- Valid: **{validation['valid']}**",
                f"- Minimum size met: **{validation['minimum_size_met']}**",
                f"- Evidence-bearing visibility: **{validation['visibility_evidence_bearing']}**",
                f"- Rows with evidence cells: **{validation['rows_with_evidence_cells']}**",
                f"- Scoring-ready: **{validation['scoring_ready']}**",
                f"- Error count: **{validation['error_count']}**",
                "",
            ]
        )
    lines.extend(["## Required For Claim Upgrade", ""])
    lines.extend(f"- {item}" for item in payload["required_for_claim_upgrade"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Independent agnostic stress intake/rehearsal")
    parser.add_argument("--negative-set", type=Path, default=None, help="External negative JSONL to validate")
    parser.add_argument("--contract", choices=["current", "contract_hardening_v1"], required=True)
    parser.add_argument(
        "--rehearsal-from-cached",
        action="store_true",
        help="Use existing benchmark-authored stress artifacts and label output as rehearsal.",
    )
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--md-out", type=Path, required=True)
    args = parser.parse_args()

    if not args.rehearsal_from_cached and args.negative_set is None:
        raise SystemExit("provide --negative-set, or use --rehearsal-from-cached for cached rehearsal output")

    payload = _build_payload(args)
    write_json(args.json_out, payload)
    write_text(args.md_out, format_md(payload))
    print(str(args.json_out))


if __name__ == "__main__":
    main()
