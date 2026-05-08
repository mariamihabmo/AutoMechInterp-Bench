#!/usr/bin/env python3
"""Rank next transfer-breadth experiments from existing released artifacts.

This is an execution aid for WP4 in REMAINING_BLOCKERS_RELEASE_EXECUTION_PLAN.md.
It does not run new model interventions and does not assert new transfer
success. It combines:

- prompt-holdout robustness,
- current cross-model transfer status,
- same-family transfer preflight readiness,
- source-stability diagnostics,
- task-family concentration penalties,

to produce a ranked queue of concrete next transfer experiments.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _bundle_analysis import write_json, write_text
except ModuleNotFoundError:
    from main._bundle_analysis import write_json, write_text

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "main" / "output" / "repro"
OUT_JSON = REPRO / "transfer_breadth_candidate_table.json"
OUT_MD = REPRO / "transfer_breadth_candidate_table.md"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _claim_key(bundle: str, hypothesis_id: str) -> str:
    return f"{bundle}::{hypothesis_id}"


def _same_family_by_bundle(preflight: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = {}
    for row in preflight.get("ranked_candidates", []):
        rows[str(row.get("bundle"))] = row
    return rows


def _transfer_by_claim(near_miss: dict[str, Any], failure: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in near_miss.get("all_accepted_claim_transfers", []):
        rows[_claim_key(str(row["bundle"]), str(row["hypothesis_id"]))] = {
            "transfer_status": row.get("transfer_status"),
            "floor_fraction": row.get("floor_fraction"),
            "transfer_effect": row.get("transfer_effect"),
            "same_direction_as_source": row.get("same_direction_as_source"),
            "source_model": row.get("source_model"),
        }
    for row in failure.get("claims", []):
        key = _claim_key(str(row["bundle"]), str(row["hypothesis_id"]))
        rows.setdefault(key, {})
        rows[key].update(
            {
                "failure_mode": row.get("failure_mode"),
                "source_stability": row.get("source_stability"),
                "source_effect_cv_abs": row.get("source_effect_cv_abs"),
                "transfer_to_source_ratio": row.get("transfer_to_source_ratio"),
            }
        )
    return rows


def _score_candidate(row: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    if row["task"] != "country_capital_v0":
        score += 100
        reasons.append("non-country-capital task")
    else:
        score -= 25
        reasons.append("country-capital already dominates current transfer positives")

    if row.get("all_holdouts_pass"):
        score += 40
        reasons.append("passes all prompt-holdout checks")

    status = row.get("current_transfer_status")
    if status == "near_miss_below_floor":
        score += 60
        reasons.append("existing cross-model near miss")
    elif status == "confirmed":
        score -= 100
        reasons.append("already transfer-confirmed")
    elif status in {"opposite_direction_subthreshold", "opposite_direction_above_floor"}:
        score -= 30
        reasons.append("existing transfer direction problem")
    elif status is None:
        score += 20
        reasons.append("no released cross-model test yet")

    floor_fraction = row.get("floor_fraction")
    if isinstance(floor_fraction, (int, float)):
        score += min(40, int(float(floor_fraction) * 20))
        reasons.append(f"floor_fraction={float(floor_fraction):.3f}")

    same_family_status = row.get("same_family_status")
    if same_family_status == "ready_to_run_missing_rows":
        score += 30
        reasons.append("same-family transfer missing rows runnable locally")
    elif same_family_status == "already_scored":
        reasons.append("same-family transfer already scored for eligible claims")
    elif same_family_status == "ready_to_rerun_no_prompt_holdout_eligible_claims":
        score -= 15
        reasons.append("same-family rerun possible but no prompt-holdout-passing accepted claim")
    elif same_family_status == "blocked_missing_local_model_snapshot":
        score += 10
        reasons.append("scientifically queued; blocked only by local target-model snapshot")
    elif same_family_status:
        reasons.append(f"same-family status={same_family_status}")

    source_stability = row.get("source_stability")
    if source_stability == "stable":
        score += 20
        reasons.append("source effect stable")
    elif source_stability == "unstable":
        score -= 10
        reasons.append("source effect unstable; transfer result may be harder to interpret")

    return score, reasons


def build_table() -> dict[str, Any]:
    prompt = _load(REPRO / "prompt_holdout_transfer_control.json")
    near_miss = _load(REPRO / "transfer_near_miss_analysis.json")
    failure = _load(REPRO / "transfer_failure_breakdown.json")
    same_family = _load(REPRO / "same_family_transfer_preflight.json")
    transfer_rows = _transfer_by_claim(near_miss, failure)
    same_family_rows = _same_family_by_bundle(same_family)

    candidates: list[dict[str, Any]] = []
    already_confirmed: list[dict[str, Any]] = []

    for claim in prompt.get("claims", []):
        bundle = str(claim["bundle"])
        hypothesis_id = str(claim["hypothesis_id"])
        transfer = transfer_rows.get(_claim_key(bundle, hypothesis_id), {})
        same = same_family_rows.get(bundle, {})
        row = {
            "bundle": bundle,
            "hypothesis_id": hypothesis_id,
            "task": claim.get("task"),
            "source_model": claim.get("model"),
            "all_holdouts_pass": bool(claim.get("all_holdouts_pass")),
            "holdout_pass_count": sum(1 for h in claim.get("holdouts", []) if h.get("passes")),
            "holdout_total": len(claim.get("holdouts", [])),
            "current_transfer_status": transfer.get("transfer_status") or transfer.get("failure_mode"),
            "floor_fraction": transfer.get("floor_fraction"),
            "transfer_effect": transfer.get("transfer_effect"),
            "source_stability": transfer.get("source_stability"),
            "source_effect_cv_abs": transfer.get("source_effect_cv_abs"),
            "transfer_to_source_ratio": transfer.get("transfer_to_source_ratio"),
            "same_family_target_model": same.get("target_model"),
            "same_family_status": same.get("status"),
            "same_family_blocked_reason": same.get("blocked_reason"),
            "same_family_existing_rows": same.get("existing_same_family_rows"),
            "same_family_existing_claim_ids": same.get("existing_same_family_claim_ids"),
            "same_family_eligible_claim_ids_with_rows": same.get("eligible_claim_ids_with_same_family_rows"),
            "same_family_eligible_claim_ids_missing_rows": same.get("eligible_claim_ids_missing_same_family_rows"),
            "same_family_transfer_passed_claim_ids": same.get("same_family_transfer_passed_claim_ids"),
            "same_family_transfer_failed_claim_ids": same.get("same_family_transfer_failed_claim_ids"),
            "proposed_same_family_command": same.get("proposed_command"),
        }
        score, reasons = _score_candidate(row)
        row["priority_score"] = score
        row["priority_reasons"] = reasons
        if row["current_transfer_status"] == "confirmed":
            already_confirmed.append(row)
        else:
            candidates.append(row)

    candidates.sort(
        key=lambda row: (
            int(row["priority_score"]),
            int(row["all_holdouts_pass"]),
            row["task"] != "country_capital_v0",
            row["bundle"],
            row["hypothesis_id"],
        ),
        reverse=True,
    )

    non_country = [row for row in candidates if row["task"] != "country_capital_v0"]
    blocked_missing = [
        row for row in candidates if row.get("same_family_status") == "blocked_missing_local_model_snapshot"
    ]
    payload = {
        "generated_by": "main/transfer_breadth_candidate_table.py",
        "status": "diagnostic_queue_only_not_transfer_evidence",
        "source_artifacts": [
            "main/output/repro/prompt_holdout_transfer_control.json",
            "main/output/repro/transfer_near_miss_analysis.json",
            "main/output/repro/transfer_failure_breakdown.json",
            "main/output/repro/same_family_transfer_preflight.json",
        ],
        "summary": {
            "candidate_claims": len(candidates),
            "non_country_candidate_claims": len(non_country),
            "already_transfer_confirmed_claims": len(already_confirmed),
            "blocked_missing_local_model_snapshot": len(blocked_missing),
            "same_family_missing_eligible_rows": sum(
                len(row.get("same_family_eligible_claim_ids_missing_rows") or [])
                for row in candidates
            ),
            "top_priority": candidates[0] if candidates else None,
        },
        "top_candidates": candidates[:12],
        "all_candidates": candidates,
        "already_transfer_confirmed": already_confirmed,
        "interpretation_notes": [
            "This artifact ranks next experiments; it is not new transfer evidence.",
            "Non-country-capital claims are prioritized because current confirmed transfer is country-capital-heavy.",
            "A ready_to_run_missing_rows status means the target snapshot and command are available locally and at least one prompt-holdout-passing accepted claim lacks a same-family row.",
            "An already_scored status means the relevant same-family row exists; the remaining blocker is the observed transfer failure/near-miss, not missing execution.",
            "A blocked_missing_local_model_snapshot status means the next action is to supply the target-model snapshot and run the proposed command, not to update paper claims.",
            "Existing near misses are useful but should not be rescued by lowering the transfer floor without a versioned protocol migration.",
        ],
    }
    return payload


def format_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Transfer Breadth Candidate Table",
        "",
        payload["status"],
        "",
        f"- Candidate claims needing new transfer evidence: **{summary['candidate_claims']}**",
        f"- Non-country-capital candidate claims: **{summary['non_country_candidate_claims']}**",
        f"- Already transfer-confirmed claims: **{summary['already_transfer_confirmed_claims']}**",
        f"- Candidates blocked by missing local target-model snapshot: **{summary['blocked_missing_local_model_snapshot']}**",
        f"- Missing eligible same-family rows among candidates: **{summary['same_family_missing_eligible_rows']}**",
        "",
        "## Top candidates",
        "",
        "| Rank | Bundle | Hypothesis | Task | Source | Same-family target | Status | Score | Why |",
        "|---:|---|---|---|---|---|---|---:|---|",
    ]
    for idx, row in enumerate(payload["top_candidates"], start=1):
        reasons = "; ".join(row.get("priority_reasons", [])[:4])
        lines.append(
            f"| {idx} | `{row['bundle']}` | `{row['hypothesis_id']}` | `{row['task']}` | "
            f"`{row['source_model']}` | `{row.get('same_family_target_model') or 'n/a'}` | "
            f"`{row.get('same_family_status') or row.get('current_transfer_status') or 'not_tested'}` | "
            f"{row['priority_score']} | {reasons} |"
        )
    lines.extend(["", "## Concrete next commands", ""])
    for row in payload["top_candidates"][:6]:
        command = row.get("proposed_same_family_command")
        if not command:
            continue
        status = row.get("same_family_status") or "not recorded"
        blocked_reason = row.get("same_family_blocked_reason")
        if status == "ready_to_run_missing_rows":
            command_label = "Locally runnable command"
            blocker_label = "Current status"
        elif status == "already_scored":
            command_label = "Optional variance-check rerun command"
            blocker_label = "Current status"
        elif blocked_reason:
            command_label = "Command after blocker is resolved"
            blocker_label = "Current blocker"
        else:
            command_label = "Proposed command"
            blocker_label = "Current status"
        lines.extend(
            [
                f"### `{row['bundle']}` / `{row['hypothesis_id']}`",
                "",
                f"- {blocker_label}: {blocked_reason or status}",
                f"- {command_label}: `{command}`",
                "",
            ]
        )
    lines.extend(["## Interpretation", ""])
    lines.extend(f"- {note}" for note in payload["interpretation_notes"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank next transfer-breadth experiments from cached artifacts")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON, help="Output JSON path")
    parser.add_argument("--out-md", type=Path, default=OUT_MD, help="Output Markdown path")
    args = parser.parse_args()

    payload = build_table()
    write_json(args.out_json, payload)
    write_text(args.out_md, format_md(payload))
    print(str(args.out_json))


if __name__ == "__main__":
    main()
