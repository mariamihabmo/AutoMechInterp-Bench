"""Compatibility vectors for third-party evaluator implementations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import CORE_GATES, EVIDENCE_TIER_ORDER
from .evaluator import _classify_evidence_tier, _normalize_gate_outcomes
from .io_utils import write_json, write_text


def _all_core_checks() -> dict[str, bool | str]:
    checks = {gate: True for gate in CORE_GATES}
    checks["cross_model_transfer"] = "not_evaluated"
    return checks


def build_reference_vectors() -> dict[str, Any]:
    """Build a small canonical set of tiering vectors."""
    vectors = []

    cases: list[tuple[str, dict[str, bool | str], bool, str]] = [
        (
            "single_model_confirmed",
            _all_core_checks(),
            True,
            "All core gates pass; transfer is not evaluated; both slices are present.",
        ),
        (
            "cross_model_confirmed",
            {**_all_core_checks(), "cross_model_transfer": True},
            True,
            "All core and optional gates pass with both slices present.",
        ),
        (
            "causal_plus_robustness",
            _all_core_checks(),
            False,
            "All core gates pass, but the exploratory slice is missing so the claim is not accepted.",
        ),
        (
            "causal_tested_unstable",
            {**_all_core_checks(), "multiplicity": False, "cross_model_transfer": "not_evaluated"},
            True,
            "Causal chain is intact but a core statistical gate fails.",
        ),
        (
            "suggestive",
            {**_all_core_checks(), "robustness": False, "method_sensitivity": False, "cross_model_transfer": "not_evaluated"},
            True,
            "Causal and control evidence remain, but robustness and sensitivity gates fail.",
        ),
        (
            "rejected",
            {**_all_core_checks(), "causal_effect": False, "cross_model_transfer": "not_evaluated"},
            True,
            "The claim fails the causal gate and must be rejected.",
        ),
    ]

    for vector_id, checks, exploratory_present, notes in cases:
        evidence_tier, passed, failed_checks, not_evaluated_checks, _demotion = _classify_evidence_tier(
            checks,
            exploratory_present=exploratory_present,
        )
        vectors.append(
            {
                "vector_id": vector_id,
                "checks": checks,
                "gate_outcomes": _normalize_gate_outcomes(checks),
                "exploratory_present": exploratory_present,
                "expected_evidence_tier": evidence_tier,
                "expected_passed": passed,
                "failed_checks": failed_checks,
                "not_evaluated_checks": not_evaluated_checks,
                "notes": notes,
            }
        )

    return {
        "schema_version": "1.0",
        "tier_order": list(EVIDENCE_TIER_ORDER),
        "vectors": vectors,
    }


def format_reference_vectors(payload: dict[str, Any]) -> str:
    lines = [
        "# Reference Vectors",
        "",
        "Canonical compatibility vectors for tier classification and gate normalization.",
        "",
    ]
    for vector in payload["vectors"]:
        lines.extend(
            [
                f"## {vector['vector_id']}",
                "",
                f"- Expected tier: `{vector['expected_evidence_tier']}`",
                f"- Expected passed: {vector['expected_passed']}",
                f"- Exploratory present: {vector['exploratory_present']}",
                f"- Failed checks: {', '.join(vector['failed_checks']) if vector['failed_checks'] else 'none'}",
                (
                    f"- Not evaluated: {', '.join(vector['not_evaluated_checks'])}"
                    if vector["not_evaluated_checks"]
                    else "- Not evaluated: none"
                ),
                f"- Notes: {vector['notes']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_reference_vectors(output_dir: Path) -> tuple[dict[str, Any], Path, Path]:
    payload = build_reference_vectors()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "reference_vectors.json"
    md_path = output_dir / "reference_vectors.md"
    write_json(json_path, payload)
    write_text(md_path, format_reference_vectors(payload))
    return payload, json_path, md_path
