#!/usr/bin/env python3
"""Summarize released transfer diagnostics for evaluated bundles."""

from __future__ import annotations

import json
from pathlib import Path

from _bundle_analysis import (
    REAL_MULTI_TASK_DIR,
    REAL_MULTILANE_DIR,
    _load_cached_or_evaluate_bundle,
    find_bundle_dirs,
    write_json,
    write_text,
)

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

def main() -> None:
    rows = []
    bundles_tested = 0
    accepted_claims_in_transfer_bundles = 0
    accepted_claims_with_transfer_effect = 0
    accepted_claims_not_evaluated = 0
    accepted_claims_below_floor = 0
    transfer_confirmed = 0

    for bundle_dir in find_bundle_dirs(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR):
        cross_path = bundle_dir / "cross_model_results.json"
        if not bundle_dir.is_dir() or not cross_path.exists():
            continue
        result = _load_cached_or_evaluate_bundle(bundle_dir)
        transfers = {row["hypothesis_id"]: row for row in json.loads(cross_path.read_text())}
        bundles_tested += 1
        for claim in result["claim_reports"]:
            if not claim["passed"]:
                continue
            accepted_claims_in_transfer_bundles += 1
            transfer_row = transfers.get(claim["hypothesis_id"])
            if transfer_row is None:
                accepted_claims_not_evaluated += 1
            else:
                accepted_claims_with_transfer_effect += 1
            transfer_effect = None if transfer_row is None else transfer_row.get("transfer_effect")
            gate_pass = claim["checks"].get("cross_model_transfer")
            below_floor = gate_pass is False
            accepted_claims_below_floor += int(below_floor)
            transfer_confirmed += int(claim["evidence_tier"] == "cross_model_confirmed")
            rows.append(
                {
                    "bundle": bundle_dir.name,
                    "hypothesis_id": claim["hypothesis_id"],
                    "evidence_tier": claim["evidence_tier"],
                    "transfer_effect": transfer_effect,
                    "cross_model_transfer_gate": gate_pass,
                    "source_model": None if transfer_row is None else transfer_row.get("source_model"),
                    "transfer_model": None if transfer_row is None else transfer_row.get("transfer_model"),
                    "why_not_transfer_confirmed": (
                        "below_floor_or_direction_failure"
                        if gate_pass is False
                        else ("not_tested" if gate_pass == "not_evaluated" else "passed")
                    ),
                }
            )

    payload = {
        "bundles_tested": bundles_tested,
        "accepted_claims_tested": accepted_claims_with_transfer_effect,
        "accepted_claims_with_transfer_effect": accepted_claims_with_transfer_effect,
        "accepted_claims_in_transfer_tested_bundles": accepted_claims_in_transfer_bundles,
        "accepted_claims_not_evaluated_in_transfer_bundles": accepted_claims_not_evaluated,
        "transfer_confirmed_claims": transfer_confirmed,
        "accepted_claims_below_floor_or_direction_failure": accepted_claims_below_floor,
        "claims": rows,
    }

    md_lines = [
        "# Transfer Results Summary",
        "",
        f"- Bundles tested: **{bundles_tested}**",
        f"- Accepted claims in transfer-tested bundles: **{accepted_claims_in_transfer_bundles}**",
        f"- Accepted claims with transfer effect: **{accepted_claims_with_transfer_effect}**",
        f"- Transfer-confirmed claims: **{transfer_confirmed}**",
        f"- Accepted claims still below transfer bar: **{accepted_claims_below_floor}**",
        f"- Accepted claims still not evaluated inside transfer-tested bundles: **{accepted_claims_not_evaluated}**",
        "",
        "| Bundle | Hypothesis | Tier | Transfer effect | Gate | Source | Transfer model |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        md_lines.append(
            f"| {row['bundle']} | {row['hypothesis_id']} | `{row['evidence_tier']}` | {row['transfer_effect']} | {row['cross_model_transfer_gate']} | {row['source_model']} | {row['transfer_model']} |"
        )

    out_dir = ROOT / "main" / "output" / "repro"
    write_json(out_dir / "transfer_results_summary.json", payload)
    write_text(out_dir / "transfer_results_summary.md", "\n".join(md_lines).rstrip() + "\n")
    print(str(out_dir / "transfer_results_summary.json"))


if __name__ == "__main__":
    main()
