#!/usr/bin/env python3
"""Rerun affected bundles with task-supported prompt variants.

This is an evidence-producing repair for the prompt-aliasing audit. It does not
overwrite released bundles. Instead it creates candidate rerun bundles under
``main/output/prompt_variant_repair/`` and records which previously accepted
claims survive when unsupported nominal variants such as ``varied`` or
``paraphrase`` are replaced by real variants supported by the task module.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_evaluator.evaluator import evaluate_bundle  # noqa: E402
from automechinterp_evaluator.reporting import build_markdown_report  # noqa: E402
from automechinterp_runner.runner import Stage2Config, run_stage2  # noqa: E402
from automechinterp_runner.tasks import get_task_module  # noqa: E402

REPRO = ROOT / "main" / "output" / "repro"
AUDIT_JSON = REPRO / "prompt_variant_validity_audit.json"
OUT_DIR = ROOT / "main" / "output" / "prompt_variant_repair"
OUT_JSON = REPRO / "prompt_variant_repair_rerun.json"
OUT_MD = REPRO / "prompt_variant_repair_rerun.md"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _source_result(bundle_dir: Path) -> dict[str, Any]:
    current = _load_json(bundle_dir / "evaluation_result_current.json")
    if current:
        return current
    return evaluate_bundle(bundle_dir)


def _passed_ids(result: dict[str, Any]) -> set[str]:
    return {str(row["hypothesis_id"]) for row in result.get("claim_reports", []) if row.get("passed")}


def _repaired_prompt_variants(task_id: str, used: list[str]) -> list[str]:
    supported = list(getattr(get_task_module(task_id), "PROMPT_VARIANTS", []) or ["base"])
    ordered_supported = (["base"] if "base" in supported else []) + [
        variant for variant in supported if variant != "base"
    ]
    repaired: list[str] = []
    for variant in used:
        if variant in supported and variant not in repaired:
            repaired.append(variant)
    for variant in ordered_supported:
        if len(repaired) >= max(1, len(used)):
            break
        if variant not in repaired:
            repaired.append(variant)
    return repaired or ordered_supported[:1]


def _rewrite_hypotheses(source_bundle: Path, protocol_id: str) -> str:
    rows: list[str] = []
    for line in (source_bundle / "hypothesis.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        row["protocol_id"] = protocol_id
        row.setdefault("provider_id", "prompt_variant_repair_v1")
        row.setdefault("discovery_lane", "prompt_variant_repair_v1")
        rows.append(json.dumps(row, sort_keys=False))
    return "\n".join(rows) + ("\n" if rows else "")


def _write_candidate_bundle(source_bundle: Path, target_bundle: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    protocol = yaml.safe_load((source_bundle / "protocol.yaml").read_text())
    protocol = json.loads(json.dumps(protocol))
    task_id = str(protocol["unit_of_work"]["task_id"])
    old_variants = [str(v) for v in protocol.get("execution_grid", {}).get("prompt_variants", [])]
    new_variants = _repaired_prompt_variants(task_id, old_variants)
    protocol["protocol_id"] = f"{protocol['protocol_id']}_prompt_variant_repair_v1"
    protocol["execution_grid"]["prompt_variants"] = new_variants

    if target_bundle.exists():
        shutil.rmtree(target_bundle)
    target_bundle.mkdir(parents=True, exist_ok=True)
    (target_bundle / "protocol.yaml").write_text(yaml.safe_dump(protocol, sort_keys=False))
    (target_bundle / "hypothesis.jsonl").write_text(_rewrite_hypotheses(source_bundle, protocol["protocol_id"]))
    return protocol, old_variants, new_variants


def _run_one(source_bundle: Path, *, device: str, examples_per_cell: int) -> dict[str, Any]:
    source_result = _source_result(source_bundle)
    accepted_before_ids = _passed_ids(source_result)
    target_bundle = OUT_DIR / source_bundle.name
    protocol, old_variants, new_variants = _write_candidate_bundle(source_bundle, target_bundle)

    started = time.time()
    stage2 = run_stage2(
        Stage2Config(
            bundle_dir=target_bundle,
            mode="real",
            device=device,
            examples_per_cell=examples_per_cell,
            exploratory_fraction=float(protocol.get("sample_size_policy", {}).get("exploratory_fraction", 0.3)),
        )
    )
    repair_result = evaluate_bundle(target_bundle)
    (target_bundle / "evaluation_result_current.json").write_text(
        json.dumps(repair_result, indent=2, sort_keys=True) + "\n"
    )
    (target_bundle / "stage_gate_report.md").write_text(build_markdown_report(repair_result))
    accepted_after_ids = _passed_ids(repair_result)
    retained = sorted(accepted_before_ids & accepted_after_ids)
    demoted = sorted(accepted_before_ids - accepted_after_ids)
    promoted = sorted(accepted_after_ids - accepted_before_ids)

    return {
        "bundle": source_bundle.name,
        "source_bundle": str(source_bundle.relative_to(ROOT)),
        "candidate_bundle": str(target_bundle.relative_to(ROOT)),
        "task": protocol["unit_of_work"]["task_id"],
        "model": protocol["unit_of_work"]["model_id"],
        "old_prompt_variants": old_variants,
        "new_prompt_variants": new_variants,
        "device": device,
        "examples_per_cell": examples_per_cell,
        "stage2_cell_count": stage2["cell_count"],
        "runtime_seconds": time.time() - started,
        "accepted_before": len(accepted_before_ids),
        "accepted_after": len(accepted_after_ids),
        "retained_previously_accepted": retained,
        "demoted_previously_accepted": demoted,
        "newly_promoted": promoted,
        "failed_gates_after": {
            gate: sum(int(gate in row.get("failed_checks", [])) for row in repair_result.get("claim_reports", []))
            for gate in sorted({gate for row in repair_result.get("claim_reports", []) for gate in row.get("failed_checks", [])})
        },
    }


def _existing_rows() -> list[dict[str, Any]]:
    if not OUT_DIR.exists():
        return []
    rows: list[dict[str, Any]] = []
    for candidate in sorted(OUT_DIR.iterdir()):
        if not candidate.is_dir():
            continue
        result_path = candidate / "evaluation_result_current.json"
        protocol_path = candidate / "protocol.yaml"
        source_path = None
        if not result_path.exists() or not protocol_path.exists():
            continue
        audit = _load_json(AUDIT_JSON)
        for record in audit.get("records", []):
            if record.get("bundle") == candidate.name:
                source_path = ROOT / str(record["path"])
                break
        if source_path is None or not source_path.exists():
            continue
        source_result = _source_result(source_path)
        repair_result = _load_json(result_path)
        protocol = yaml.safe_load(protocol_path.read_text())
        before = _passed_ids(source_result)
        after = _passed_ids(repair_result)
        rows.append(
            {
                "bundle": candidate.name,
                "source_bundle": str(source_path.relative_to(ROOT)),
                "candidate_bundle": str(candidate.relative_to(ROOT)),
                "task": protocol["unit_of_work"]["task_id"],
                "model": protocol["unit_of_work"]["model_id"],
                "old_prompt_variants": list(record.get("used_prompt_variants") or []),
                "new_prompt_variants": list(protocol.get("execution_grid", {}).get("prompt_variants", [])),
                "device": "unknown_existing",
                "examples_per_cell": "unknown_existing",
                "stage2_cell_count": sum(
                    len(row.get("raw_cells", []))
                    for row in _load_json(candidate / "evaluation_result.json").get("hypothesis_results", [])
                ),
                "runtime_seconds": 0.0,
                "accepted_before": len(before),
                "accepted_after": len(after),
                "retained_previously_accepted": sorted(before & after),
                "demoted_previously_accepted": sorted(before - after),
                "newly_promoted": sorted(after - before),
                "failed_gates_after": {
                    gate: sum(int(gate in row.get("failed_checks", [])) for row in repair_result.get("claim_reports", []))
                    for gate in sorted({gate for row in repair_result.get("claim_reports", []) for gate in row.get("failed_checks", [])})
                },
            }
        )
    return rows


def _write_summary(rows: list[dict[str, Any]], planned_total: int, planned_accepted_total: int | None = None) -> None:
    covered_before = sum(int(row["accepted_before"]) for row in rows)
    accepted_after = sum(int(row["accepted_after"]) for row in rows)
    retained = sum(len(row["retained_previously_accepted"]) for row in rows)
    demoted = sum(len(row["demoted_previously_accepted"]) for row in rows)
    promoted = sum(len(row["newly_promoted"]) for row in rows)
    planned_accepted = (
        planned_accepted_total
        if planned_accepted_total is not None
        else sum(1 for row in rows if int(row.get("accepted_before") or 0) > 0)
    )
    payload = {
        "generated_by": "main/prompt_variant_repair_rerun.py",
        "status": (
            "diagnostic repair reruns; canonical only when promoted through "
            "main/_bundle_analysis.py and documented in the methodology update"
        ),
        "planned_unsupported_prompt_bundles": planned_total,
        "planned_affected_bundles_with_accepts": planned_accepted,
        "bundles_rerun": len(rows),
        "accepted_before_in_rerun_bundles": covered_before,
        "accepted_after_sum": accepted_after,
        "previously_accepted_retained": retained,
        "previously_accepted_demoted": demoted,
        "new_promoted": promoted,
        "retention_rate_in_rerun_bundles": retained / covered_before if covered_before else 0.0,
        "rows": rows,
        "claim_boundary": (
            "These reruns test whether affected accepted claims survive real task-supported prompt variants. "
            "They repair the canonical release only after the canonical bundle-discovery layer promotes the candidate bundles; "
            "legacy unsupported-prompt artifacts remain historical evidence of the repaired failure mode."
        ),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Prompt Variant Repair Reruns",
        "",
        payload["claim_boundary"],
        "",
        f"- Planned unsupported-prompt bundles: **{planned_total}**",
        f"- Planned affected bundles with accepted claims: **{planned_accepted}**",
        f"- Bundles rerun: **{len(rows)}**",
        f"- Accepted claims covered before rerun: **{covered_before}**",
        f"- Accepted claims after rerun: **{accepted_after}**",
        f"- Previously accepted retained: **{retained}**",
        f"- Previously accepted demoted: **{demoted}**",
        f"- Newly promoted claims: **{promoted}**",
        f"- Retention rate in rerun bundles: **{payload['retention_rate_in_rerun_bundles'] * 100:.1f}%**",
        "",
        "| Bundle | Task | Model | Variants old -> new | Accepted before | Retained | Demoted | Candidate bundle |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['bundle']}` | `{row['task']}` | `{row['model']}` | "
            f"`{', '.join(row['old_prompt_variants'])}` -> `{', '.join(row['new_prompt_variants'])}` | "
            f"{row['accepted_before']} | {len(row['retained_previously_accepted'])} | "
            f"{len(row['demoted_previously_accepted'])} | `{row['candidate_bundle']}` |"
        )
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rerun prompt-variant repair candidates")
    parser.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"],
                        help="Inference device. Defaults to 'cpu' for cross-platform reproducibility; pass --device mps on Apple silicon or --device cuda on Linux GPUs to enable hardware acceleration.")
    parser.add_argument("--examples-per-cell", type=int, default=20)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--bundle", default="", help="Optional exact bundle name to rerun")
    parser.add_argument("--include-zero-accepted", action="store_true")
    parser.add_argument("--summarize-existing", action="store_true")
    args = parser.parse_args()

    audit = _load_json(AUDIT_JSON)
    if not audit:
        raise SystemExit("run main/prompt_variant_validity_audit.py first")
    include_zero_accepted = args.include_zero_accepted or args.summarize_existing
    planned = [
        row for row in audit.get("records", [])
        if include_zero_accepted or int(row.get("accepted_claims_in_bundle") or 0) > 0
    ]
    if args.bundle:
        planned = [row for row in planned if row.get("bundle") == args.bundle]
    planned_total = len(planned)
    planned_accepted_total = sum(1 for row in planned if int(row.get("accepted_claims_in_bundle") or 0) > 0)

    rows_by_bundle = {row["bundle"]: row for row in _existing_rows()}
    if args.summarize_existing:
        _write_summary([rows_by_bundle[name] for name in sorted(rows_by_bundle)], planned_total, planned_accepted_total)
        print(str(OUT_JSON))
        return

    todo = [row for row in planned if row.get("bundle") not in rows_by_bundle]
    if args.limit > 0:
        todo = todo[: args.limit]
    if not todo:
        _write_summary([rows_by_bundle[name] for name in sorted(rows_by_bundle)], planned_total, planned_accepted_total)
        print(str(OUT_JSON))
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for idx, record in enumerate(todo, start=1):
        source = ROOT / str(record["path"])
        print(f"[{idx}/{len(todo)}] prompt-variant repair {source.name}", flush=True)
        rows_by_bundle[source.name] = _run_one(
            source,
            device=args.device,
            examples_per_cell=args.examples_per_cell,
        )
        _write_summary([rows_by_bundle[name] for name in sorted(rows_by_bundle)], planned_total, planned_accepted_total)

    _write_summary([rows_by_bundle[name] for name in sorted(rows_by_bundle)], planned_total, planned_accepted_total)
    print(str(OUT_JSON))


if __name__ == "__main__":
    main()
