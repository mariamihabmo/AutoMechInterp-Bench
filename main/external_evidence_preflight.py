#!/usr/bin/env python3
"""Summarize external holdout evidence status and remaining blockers.

This is an honest preflight/status report, not a substitute for a real blinded
external submission. It exists so the repository can execute every local step
around the external-evidence gap without pretending that scaffolding equals
external validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from _bundle_analysis import write_json, write_text
except ModuleNotFoundError:
    from main._bundle_analysis import write_json, write_text

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "main" / "output" / "repro"
HOLDOUT_SUMMARY = ROOT / "holdout" / "results_summary.json"
HOLDOUT_PILOT_SUMMARY = ROOT / "holdout" / "pilot" / "results_summary.json"
HOLDOUT_REHEARSAL = REPRO / "holdout_v0-rehearsal.json"
AUTHOR_PACKAGER = ROOT / "holdout" / "tools" / "package_holdout_submission.py"
AUTHOR_PREFLIGHT = ROOT / "holdout" / "tools" / "preflight_submission.py"
AUTHOR_QUICKSTART = ROOT / "holdout" / "EXTERNAL_AUTHOR_QUICKSTART.md"
EXTERNAL_PLAYBOOK = ROOT / "docs" / "reference" / "independent_researcher_external_evidence_playbook.md"
OUT_JSON = REPRO / "external_evidence_preflight.json"
OUT_MD = REPRO / "external_evidence_preflight.md"


def _load(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def main() -> None:
    REPRO.mkdir(parents=True, exist_ok=True)
    summary = _load(HOLDOUT_SUMMARY) or {}
    pilot_summary = _load(HOLDOUT_PILOT_SUMMARY) or {}
    rehearsal = _load(HOLDOUT_REHEARSAL) or {}

    external = summary.get("external_blinded", {})
    pilot = summary.get("maintainer_pilot", {})
    pilot_only = pilot_summary.get("maintainer_pilot", {})

    payload = {
        "schema_version": 1,
        "generated_by": "main/external_evidence_preflight.py",
        "external_blinded": {
            "n_submissions": int(external.get("n_submissions") or 0),
            "n_evaluated": int(external.get("n_evaluated") or 0),
            "n_accepted_claims": int(external.get("n_accepted_claims") or 0),
            "all_pin_matches": external.get("all_pin_matches"),
        },
        "maintainer_pilot": {
            "n_submissions": int(pilot.get("n_submissions") or pilot_only.get("n_submissions") or 0),
            "n_evaluated": int(pilot.get("n_evaluated") or pilot_only.get("n_evaluated") or 0),
            "all_pin_matches": pilot.get("all_pin_matches", pilot_only.get("all_pin_matches")),
        },
        "holdout_rehearsal": {
            "artifact_exists": HOLDOUT_REHEARSAL.exists(),
            "mode": rehearsal.get("mode"),
            "release_version": rehearsal.get("release_version"),
            "aggregate": rehearsal.get("aggregate"),
        },
        "author_path_readiness": {
            "package_tool_present": AUTHOR_PACKAGER.exists(),
            "preflight_tool_present": AUTHOR_PREFLIGHT.exists(),
            "quickstart_present": AUTHOR_QUICKSTART.exists(),
            "external_evidence_playbook_present": EXTERNAL_PLAYBOOK.exists(),
        },
        "status": {
            "has_real_external_submission": int(external.get("n_submissions") or 0) > 0,
            "has_evaluated_external_submission": int(external.get("n_evaluated") or 0) > 0,
            "has_external_accepted_bundle": int(external.get("n_accepted_claims") or 0) > 0,
            "counts_as_external_evidence_now": int(external.get("n_evaluated") or 0) > 0,
        },
        "blocked_reasons": [
            reason
            for reason, active in [
                ("no_external_blinded_submission_present", int(external.get("n_submissions") or 0) == 0),
                ("no_external_submission_evaluated", int(external.get("n_evaluated") or 0) == 0),
                ("no_external_accepted_claims_recorded", int(external.get("n_accepted_claims") or 0) == 0),
            ]
            if active
        ],
        "next_actions": [
            "Ingest one real external_blinded bundle through the submission-review pipeline.",
            "Score one real private-suite holdout run with an external custodian.",
            "Keep maintainer pilot and rehearsal artifacts separated from external evidence counts in every report.",
            "Use holdout/tools/package_holdout_submission.py plus holdout/tools/preflight_submission.py to reduce author-side packaging friction.",
            "Use docs/reference/independent_researcher_external_evidence_playbook.md as the operational recruiting, custody, and Goodhart-validation checklist.",
        ],
        "notes": [
            "Maintainer pilot and rehearsal artifacts exercise plumbing only; they do not count as external evidence.",
            "This report deliberately emits no private-suite path or per-item holdout information.",
        ],
    }
    write_json(OUT_JSON, payload)

    lines = [
        "# External Evidence Preflight",
        "",
        f"- External blinded submissions: **{payload['external_blinded']['n_submissions']}**",
        f"- External blinded submissions evaluated: **{payload['external_blinded']['n_evaluated']}**",
        f"- External blinded accepted claims: **{payload['external_blinded']['n_accepted_claims']}**",
        f"- Maintainer pilot submissions: **{payload['maintainer_pilot']['n_submissions']}**",
        f"- Maintainer pilot evaluated: **{payload['maintainer_pilot']['n_evaluated']}**",
        f"- Holdout rehearsal artifact present: **{payload['holdout_rehearsal']['artifact_exists']}**",
        f"- Author packager present: **{payload['author_path_readiness']['package_tool_present']}**",
        f"- Author preflight present: **{payload['author_path_readiness']['preflight_tool_present']}**",
        f"- Author quickstart present: **{payload['author_path_readiness']['quickstart_present']}**",
        f"- External evidence playbook present: **{payload['author_path_readiness']['external_evidence_playbook_present']}**",
        "",
        "## Status",
        "",
        f"- Counts as external evidence now: **{payload['status']['counts_as_external_evidence_now']}**",
        "",
        "## Blocked reasons",
        "",
    ]
    if payload["blocked_reasons"]:
        for reason in payload["blocked_reasons"]:
            lines.append(f"- `{reason}`")
    else:
        lines.append("- None.")
    lines.extend([
        "",
        "## Next actions",
        "",
    ])
    for action in payload["next_actions"]:
        lines.append(f"- {action}")
    lines.extend([
        "",
        "Maintainer pilot and rehearsal artifacts remain useful as operational checks, but they are not external evidence and should never be counted as such.",
    ])
    write_text(OUT_MD, "\n".join(lines).rstrip() + "\n")
    print(str(OUT_JSON))


if __name__ == "__main__":
    main()
