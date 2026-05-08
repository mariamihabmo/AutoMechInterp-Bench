#!/usr/bin/env python3
"""Repair legacy bundles that declared no confirmatory split but emitted only
exploratory-labeled raw cells.

Why this exists
---------------
Some archived ``real_multi_task`` bundles predate the current Stage-2 behavior.
Their protocols explicitly declare ``sample_size_policy.require_confirmatory_split:
false``, which means the single released slice should be treated as the
confirmatory slice. However, the archived ``evaluation_result.json`` files label
all raw cells as ``exploratory``. Under the current evaluator this mechanically
forces ``confirmatory_present = false`` and blocks those bundles even when the
protocol never required a separate exploratory/confirmatory split.

This script performs a *protocol-consistent migration* for that legacy case:

* only bundles with ``require_confirmatory_split: false`` are eligible;
* only bundles whose raw cells are *all* labeled ``exploratory`` are changed;
* the migration relabels those cells to ``confirmatory``;
* the pre-repair ``evaluation_result.json`` is preserved as
  ``evaluation_result_pre_legacy_slice_repair.json``;
* ``manifest.json``, ``evaluation_result_current.json``, and
  ``stage_gate_report.md`` are regenerated.

This is intentionally narrow. It does **not** invent missing data and it does
**not** create a faux exploratory/confirmatory split where none existed.

Outputs
-------
* Per-bundle repaired artifacts.
* ``main/output/repro/legacy_no_split_repair.json``
* ``main/output/repro/legacy_no_split_repair.md``
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))

from automechinterp_evaluator.evaluator import evaluate_bundle  # noqa: E402
from automechinterp_evaluator.hypothesis_generation import refresh_manifest  # noqa: E402
from automechinterp_evaluator.reporting import build_markdown_report  # noqa: E402

REPAIR_JSON = ROOT / "main" / "output" / "repro" / "legacy_no_split_repair.json"
REPAIR_MD = ROOT / "main" / "output" / "repro" / "legacy_no_split_repair.md"
SEARCH_ROOTS = [
    ROOT / "main" / "output" / "real_multi_task",
    ROOT / "main" / "output" / "real_multilane",
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _bundle_dirs() -> list[Path]:
    dirs: list[Path] = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.iterdir()):
            if path.is_dir() and (path / "protocol.yaml").exists() and (path / "evaluation_result.json").exists():
                dirs.append(path)
    return dirs


def _eligible(bundle_dir: Path) -> tuple[bool, str, dict[str, Any] | None]:
    protocol = yaml.safe_load((bundle_dir / "protocol.yaml").read_text())
    require_split = protocol.get("sample_size_policy", {}).get("require_confirmatory_split")
    if require_split is not False:
        return False, "require_confirmatory_split_not_false", protocol
    evaluation = _load_json(bundle_dir / "evaluation_result.json")
    slices = {
        cell.get("slice")
        for hyp in evaluation.get("hypothesis_results", [])
        for cell in hyp.get("raw_cells", [])
    }
    if slices != {"exploratory"}:
        return False, f"raw_slices={sorted(slices)!r}", protocol
    return True, "eligible", protocol


def _accepted_count(result: dict[str, Any] | None) -> int | None:
    if not isinstance(result, dict):
        return None
    overall = result.get("overall")
    if not isinstance(overall, dict):
        return None
    count = overall.get("accepted_count")
    return int(count) if isinstance(count, int) else None


def _load_prior_current(bundle_dir: Path) -> dict[str, Any] | None:
    path = bundle_dir / "evaluation_result_current.json"
    if not path.exists():
        return None
    try:
        payload = _load_json(path)
    except Exception:
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("claim_reports"), list):
        return None
    return payload


def repair_bundle(bundle_dir: Path) -> dict[str, Any] | None:
    ok, reason, protocol = _eligible(bundle_dir)
    if not ok:
        return {
            "bundle": bundle_dir.name,
            "path": str(bundle_dir.relative_to(ROOT)),
            "status": "skipped",
            "reason": reason,
        }

    prior_current = _load_prior_current(bundle_dir)
    accepted_before = _accepted_count(prior_current)

    evaluation_path = bundle_dir / "evaluation_result.json"
    backup_path = bundle_dir / "evaluation_result_pre_legacy_slice_repair.json"
    if not backup_path.exists():
        shutil.copy2(evaluation_path, backup_path)

    evaluation = _load_json(evaluation_path)
    changed_cells = 0
    changed_hypotheses = 0
    for hyp in evaluation.get("hypothesis_results", []):
        hyp_changed = False
        for cell in hyp.get("raw_cells", []):
            if cell.get("slice") == "exploratory":
                cell["slice"] = "confirmatory"
                changed_cells += 1
                hyp_changed = True
        if hyp_changed:
            changed_hypotheses += 1

    evaluation_path.write_text(json.dumps(evaluation, indent=2, sort_keys=False) + "\n")
    refresh_manifest(bundle_dir)
    result = evaluate_bundle(bundle_dir)
    (bundle_dir / "evaluation_result_current.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (bundle_dir / "stage_gate_report.md").write_text(build_markdown_report(result))

    claim_rows = []
    for row in result.get("claim_reports", []):
        claim_rows.append(
            {
                "hypothesis_id": row.get("hypothesis_id"),
                "passed": bool(row.get("passed")),
                "evidence_tier": row.get("evidence_tier"),
                "failed_checks": list(row.get("failed_checks", [])),
            }
        )

    return {
        "bundle": bundle_dir.name,
        "path": str(bundle_dir.relative_to(ROOT)),
        "status": "repaired",
        "reason": reason,
        "require_confirmatory_split": protocol.get("sample_size_policy", {}).get("require_confirmatory_split"),
        "changed_hypotheses": changed_hypotheses,
        "changed_cells": changed_cells,
        "accepted_before": accepted_before,
        "accepted_after": _accepted_count(result),
        "backup_path": str(backup_path.relative_to(ROOT)),
        "claim_reports_after": claim_rows,
    }


def format_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Legacy No-Split Bundle Repair",
        "",
        "This migration is intentionally narrow: it only repairs archived bundles that",
        "explicitly declared `require_confirmatory_split: false` yet labeled every raw",
        "cell as `exploratory`. Under current evaluator semantics, those bundles are",
        "supposed to use their single released slice as the confirmatory slice.",
        "",
        f"- Bundles scanned: **{payload['bundles_scanned']}**",
        f"- Bundles repaired: **{payload['bundles_repaired']}**",
        f"- Bundles skipped: **{payload['bundles_skipped']}**",
        f"- Accepted claims before repair (where cached current results existed): **{payload['accepted_before_total']}**",
        f"- Accepted claims after repair: **{payload['accepted_after_total']}**",
        "",
        "## Repaired bundles",
        "",
        "| bundle | changed cells | accepted before | accepted after | net change |",
        "|---|---:|---:|---:|---:|",
    ]
    repaired = [row for row in payload["bundles"] if row["status"] == "repaired"]
    for row in repaired:
        before = row.get("accepted_before")
        after = row.get("accepted_after")
        net = None if before is None or after is None else after - before
        lines.append(
            f"| `{row['bundle']}` | {row['changed_cells']} | "
            f"{before if before is not None else 'n/a'} | {after if after is not None else 'n/a'} | "
            f"{net if net is not None else 'n/a'} |"
        )
    lines.append("")

    if repaired:
        lines.extend(["## Per-bundle post-repair claim state", ""])
        for row in repaired:
            lines.append(f"### `{row['bundle']}`")
            lines.append("")
            lines.append(f"- Backup: `{row['backup_path']}`")
            lines.append(f"- Changed hypotheses: **{row['changed_hypotheses']}**")
            lines.append(f"- Changed cells: **{row['changed_cells']}**")
            for claim in row.get("claim_reports_after", []):
                lines.append(
                    f"- `{claim['hypothesis_id']}` → `{claim['evidence_tier']}`; "
                    f"passed={claim['passed']}; failed gates: "
                    f"{', '.join(f'`{g}`' for g in claim['failed_checks']) or '_none_'}"
                )
            lines.append("")

    skipped = [row for row in payload["bundles"] if row["status"] == "skipped"]
    if skipped:
        lines.extend(["## Skipped bundles", ""])
        reason_counts: dict[str, int] = {}
        for row in skipped:
            reason_counts[row["reason"]] = reason_counts.get(row["reason"], 0) + 1
        for reason, count in sorted(reason_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"- `{reason}`: {count}")
        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "This migration removes a protocol/artifact mismatch. It does **not** create new",
            "evidence or fabricate a held-out split. Any claims that remain blocked after the",
            "repair are blocked for substantive reasons (for example multiplicity, causal",
            "effect, robustness, or method sensitivity), not because the bundle mislabeled its",
            "only released slice.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    bundles = _bundle_dirs()
    rows = []
    for idx, bundle_dir in enumerate(bundles, start=1):
        print(f"[{idx}/{len(bundles)}] {bundle_dir.name}", flush=True)
        rows.append(repair_bundle(bundle_dir))
    rows = [row for row in rows if row is not None]

    repaired = [row for row in rows if row["status"] == "repaired"]
    payload = {
        "generated_by": "main/repair_legacy_no_split_bundles.py",
        "bundles_scanned": len(rows),
        "bundles_repaired": len(repaired),
        "bundles_skipped": sum(1 for row in rows if row["status"] == "skipped"),
        "accepted_before_total": sum(row.get("accepted_before") or 0 for row in repaired),
        "accepted_after_total": sum(row.get("accepted_after") or 0 for row in repaired),
        "bundles": rows,
    }
    REPAIR_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPAIR_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    REPAIR_MD.write_text(format_md(payload))
    print(str(REPAIR_JSON))


if __name__ == "__main__":
    main()
