#!/usr/bin/env python3
"""Repo-wide integrity sweep for current-facing artifacts and docs."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "main" / "output" / "repro"
OUT_JSON = REPRO / "repo_integrity_sweep.json"
OUT_MD = REPRO / "repo_integrity_sweep.md"

CURRENT_FACING = [
    ROOT / "README.md",
    ROOT / "REMAINING_BLOCKERS_RELEASE_EXECUTION_PLAN.md",
    ROOT / "docs" / "reference" / "reproducibility_runbook.md",
    ROOT / "methodology" / "README.md",
    ROOT / "methodology" / "latest_gap_analysis.md",
    ROOT / "methodology" / "audit" / "verdict.md",
    ROOT / "papers" / "submissions" / "neurips2026_maintrack" / "paper_body.tex",
    ROOT / "papers" / "submissions" / "neurips2026_dnb" / "paper_body.tex",
    ROOT / "release-findings.md",
    ROOT / "release_takeaways.md",
    ROOT / "site_docs" / "generated" / "release-findings.md",
    ROOT / "main" / "output" / "repro" / "release_takeaways.md",
    ROOT / "main" / "output" / "repro" / "release_readiness_report.md",
    ROOT / "main" / "output" / "repro" / "direct_blocker_closure_report.md",
    ROOT / "main" / "output" / "repro" / "prompt_holdout_transfer_control.md",
]

ARCHIVAL_DOCS = [
    ROOT / "PROJECT_DEEP_DIVE.md",
    ROOT / "PROJECT_STATUS_AND_PATH_TO_RELEASE.md",
    ROOT / "MERGE_REVIEW_AND_COMPARISON.md",
    ROOT / "docs" / "reference" / "open_item_cross_model_transfer.md",
    ROOT / "methodology" / "gap_analysis_2026-04-22_merged.md",
    ROOT / "methodology" / "audit" / "v2_audit_report.md",
    ROOT / "methodology" / "audit" / "session_log.md",
    ROOT / "methodology" / "audit" / "next_session_backlog.md",
    ROOT / "methodology" / "audit" / "findings_inventory.md",
    ROOT / "methodology" / "gap_analysis_2026-04-18.md",
]

def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}

def _run(cmd: list[str]) -> dict[str, Any]:
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    # Sanitise the recorded command so the JSON artifact never embeds
    # an absolute interpreter path (which would leak the local
    # username under /Users/<name>/... or /home/<name>/...). The
    # actual subprocess still uses the resolved `cmd` list above; we
    # only rewrite the value that gets serialised to disk.
    recorded_cmd = ["python" if part == sys.executable else part for part in cmd]
    return {
        "command": recorded_cmd,
        "returncode": res.returncode,
        "stdout": res.stdout[-1200:],
        "stderr": res.stderr[-1200:],
    }

def _contains_stale_current_transfer(text: str, pattern: re.Pattern[str]) -> bool:
    for match in pattern.finditer(text):
        context = text[max(0, match.start() - 100): match.end() + 100].lower()
        if any(
            marker in context
            for marker in (
                "historical",
                "old ",
                "then-current",
                "superseded",
                "pre-replication",
                "at the time",
            )
        ):
            continue
        return True
    return False

def _is_historical_context(text: str, start: int, end: int) -> bool:
    context = text[max(0, start - 120): min(len(text), end + 120)].lower()
    return any(
        marker in context
        for marker in (
            "historical",
            "old ",
            "then-current",
            "superseded",
            "pre-replication",
            "at the time",
            "later country-capital-only",
        )
    )

def _stale_transfer_fraction_hits(text: str, *, current_fraction: str) -> list[str]:
    old_fractions = ((0, 12), (8, 12), (9, 23))
    hits: list[str] = []
    for numerator, denominator in old_fractions:
        fraction = f"{numerator}/{denominator}"
        spaced_fraction_pattern = rf"(?<!\d){numerator}\s*/\s*{denominator}(?!\d)"
        if fraction == current_fraction:
            continue
        pattern = re.compile(
            rf"(?:(?:current(?:ly)?|release(?:d)?|headline|canonical|tested accepted claims|accepted claims|cross_model_confirmed)[^.\n]{{0,120}}{spaced_fraction_pattern}|"
            rf"{spaced_fraction_pattern}[^.\n]{{0,120}}(?:current(?:ly)?|release(?:d)?|headline|canonical|tested accepted claims|accepted claims|cross_model_confirmed))",
            flags=re.IGNORECASE,
        )
        for match in pattern.finditer(text):
            if not _is_historical_context(text, match.start(), match.end()):
                hits.append(f"stale current transfer fraction {fraction}")
                break
    return hits

def _stale_audit_count_hits(text: str, *, current_count: int) -> list[str]:
    hits: list[str] = []
    patterns = (
        re.compile(r"\b(\d+)\s*/\s*\1\s+commands?\s+pass", re.IGNORECASE),
        re.compile(r"\b(\d+)[- ]command\s+(?:cached-)?artifact\s+audit", re.IGNORECASE),
        re.compile(r"\b(\d+)[- ]command\s+audit", re.IGNORECASE),
    )
    for pattern in patterns:
        for match in pattern.finditer(text):
            cited = int(match.group(1))
            if cited == current_count:
                continue
            if _is_historical_context(text, match.start(), match.end()):
                continue
            hits.append(f"stale current audit command count {cited}; expected {current_count}")
    return hits

def _audit_command_count(audit: dict[str, Any]) -> int:
    if os.environ.get("AUTOMECHINTERP_EXPECTED_AUDIT_COMMANDS"):
        return int(os.environ["AUTOMECHINTERP_EXPECTED_AUDIT_COMMANDS"])
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from main.reproducibility_audit import audit_commands

        return len(audit_commands())
    except Exception:
        pass
    return len(audit.get("commands") or [])

def main() -> int:
    REPRO.mkdir(parents=True, exist_ok=True)
    breadth = _load(REPRO / "benchmark_breadth_summary.json")
    field = _load(REPRO / "field_level_findings.json")
    transfer = _load(REPRO / "transfer_results_summary.json")
    zero_repair = _load(REPRO / "zero_task_confirmatory_repair.json")
    holdout = _load(ROOT / "holdout" / "results_summary.json")
    audit = _load(REPRO / "reproducibility_audit.json")
    prompt_audit = _load(REPRO / "prompt_variant_validity_audit.json")

    checks = []
    checks.append(_run([sys.executable, "tools/check_headline_numbers.py"]))

    transfer_num = int(transfer.get("transfer_confirmed_claims", 0) or 0)
    transfer_den = int(transfer.get("accepted_claims_tested", 0) or 0)
    transfer_fraction = f"{transfer_num}/{transfer_den}"
    transfer_fraction_pattern = re.compile(rf"{transfer_num}\s*/\s*{transfer_den}")
    audit_command_count = _audit_command_count(audit)
    prompt_affected_claims = int(prompt_audit.get("affected_accepted_claims_in_existing_artifacts") or 0)
    stale_findings = []
    stale_transfer_pattern = re.compile(
        r"(?:current(?:ly)?|release(?:d)?|headline|cites)[^.\n]{0,80}0/12",
        flags=re.IGNORECASE,
    )
    readiness_refs = [
        "main/output/repro/release_readiness_report.md",
        "main/output/repro/direct_blocker_closure_report.md",
    ]
    for path in CURRENT_FACING:
        if not path.exists():
            continue
        text = path.read_text()
        hits = []
        if _contains_stale_current_transfer(text, stale_transfer_pattern):
            hits.append("stale current 0/12 transfer headline")
        hits.extend(_stale_transfer_fraction_hits(text, current_fraction=transfer_fraction))
        hits.extend(_stale_audit_count_hits(text, current_count=audit_command_count))
        if (
            prompt_affected_claims
            and "Claims passing all held-out prompt variants" in text
            and "Prompt-variant repair caveat" not in text
        ):
            hits.append("prompt-holdout count lacks prompt-variant repair caveat")
        if "no accepted claim currently reaches `cross_model_confirmed`" in text:
            hits.append("stale README transfer sentence")
        stale_findings.append({
            "path": str(path.relative_to(ROOT)),
            "contains_current_transfer_fraction": bool(transfer_fraction_pattern.search(text)),
            "mentions_current_readiness_docs": any(ref in text for ref in readiness_refs),
            "stale_hits": hits,
        })

    archival_findings = []
    for path in ARCHIVAL_DOCS:
        if not path.exists():
            continue
        text = path.read_text()
        preamble = text[:800]
        archival_findings.append({
            "path": str(path.relative_to(ROOT)),
            "has_status_banner": (
                "Superseded status note." in preamble
                or "Status note." in preamble
                or "Current status" in preamble
            ),
            "contains_stale_current_transfer_fraction": _contains_stale_current_transfer(text, stale_transfer_pattern),
        })

    zero_rows = zero_repair.get("rows") or zero_repair.get("bundles") or []
    zero_agg = zero_repair.get("aggregate") or {}
    holdout_pilot = (holdout.get("maintainer_pilot") or {})
    pilot_summary = _load(ROOT / "holdout" / "pilot" / "results_summary.json")

    payload = {
        "generated_by": "main/repo_integrity_sweep.py",
        "headline": {
            "bundles": breadth.get("bundle_count"),
            "claims": breadth.get("claim_count"),
            "accepted": (field.get("totals") or {}).get("accepted"),
            "transfer_confirmed_claims": transfer.get("transfer_confirmed_claims"),
            "transfer_tested_claims": transfer.get("accepted_claims_tested"),
            "audit_command_count": audit_command_count,
            "prompt_variant_affected_accepted_claims": prompt_affected_claims,
        },
        "command_checks": checks,
        "current_facing_docs": stale_findings,
        "archival_docs": archival_findings,
        "zero_task_repair_schema": {
            "rows_or_bundles_present": bool(zero_rows),
            "row_count": len(zero_rows),
            "bundles_repaired_matches_rows": int(zero_agg.get("bundles_repaired") or 0) == len(zero_rows) if zero_rows else False,
        },
        "holdout_summary_consistency": {
            "maintainer_pilot_n_submissions": holdout_pilot.get("n_submissions"),
            "pilot_summary_n_submissions": ((pilot_summary.get("maintainer_pilot") or {}).get("n_submissions")),
            "counts_match": holdout_pilot.get("n_submissions") == ((pilot_summary.get("maintainer_pilot") or {}).get("n_submissions")),
        },
    }
    has_current_stale_hits = any(row["stale_hits"] for row in stale_findings)
    headline_check_failed = any(check["returncode"] != 0 for check in checks)
    payload["status"] = "fail" if has_current_stale_hits or headline_check_failed else "pass"
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Repo Integrity Sweep",
        "",
        f"- Canonical transfer headline: **{transfer_fraction}**",
        f"- Canonical audit command count: **{audit_command_count}**",
        f"- Headline check return code: **{checks[0]['returncode']}**",
        f"- Status: **{payload['status']}**",
        f"- Zero-task repair rows present: **{payload['zero_task_repair_schema']['rows_or_bundles_present']}**",
        f"- Holdout pilot summary counts match: **{payload['holdout_summary_consistency']['counts_match']}**",
        "",
        "## Current-facing docs",
        "",
        "| Path | Contains current transfer fraction | Mentions current readiness docs | Stale hits |",
        "|---|---|---|---|",
    ]
    for row in stale_findings:
        hits = ", ".join(row['stale_hits']) or 'none'
        lines.append(f"| `{row['path']}` | {row['contains_current_transfer_fraction']} | {row['mentions_current_readiness_docs']} | {hits} |")
    lines.extend([
        "",
        "## Archival docs",
        "",
        "| Path | Has status banner | Contains stale current transfer fraction |",
        "|---|---|---|",
    ])
    for row in archival_findings:
        lines.append(f"| `{row['path']}` | {row['has_status_banner']} | {row['contains_stale_current_transfer_fraction']} |")
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n")
    print(str(OUT_JSON))
    return 0 if payload["status"] == "pass" else 1

if __name__ == "__main__":
    raise SystemExit(main())
