#!/usr/bin/env python3
"""Within-model prompt-holdout transfer control for accepted claims.

This script asks a narrower, locally-executable transfer question than
cross-model replication:

    If an accepted claim is evaluated on multiple prompt variants in the
    released bundle, does its confirmatory treatment effect persist when one
    prompt variant is held out and treated as an unseen prompt family?

Method
------
For each accepted claim in a bundle with at least two prompt variants:

* keep only confirmatory raw cells
* for each prompt variant v:
    - source mean = mean confirmatory treatment over all OTHER prompt variants
    - holdout mean = mean confirmatory treatment on v
    - holdout passes iff it matches the source direction and its absolute
      magnitude exceeds the bundle's causal-effect floor
* a claim passes the prompt-holdout control iff ALL held-out prompt variants
  pass under that rule

This is intentionally a diagnostic control, not a new evidence tier. It does
not change the benchmark contract and it does not replace cross-model
transfer. It tells us whether the released accepted claims are narrowly tied
to one prompt template or whether they generalize across the prompt variants
already present in the visible release.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main._bundle_analysis import (  # noqa: E402
    REAL_MULTILANE_DIR,
    REAL_MULTI_TASK_DIR,
    find_bundle_dirs,
    read_jsonl,
    read_yaml,
    write_json,
    write_text,
)

REPRO_DIR = ROOT / "main" / "output" / "repro"


def _sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _load_current_result(bundle_dir: Path) -> dict[str, Any]:
    for name in ("evaluation_result_current.json", "evaluation_result.json"):
        path = bundle_dir / name
        if path.exists():
            payload = json.loads(path.read_text())
            if isinstance(payload.get("claim_reports"), list):
                return payload
    raise FileNotFoundError(f"No current evaluated summary for bundle: {bundle_dir}")


def _load_repro_json(name: str) -> dict[str, Any]:
    path = REPRO_DIR / name
    if not path.exists():
        return {}
    payload = json.loads(path.read_text())
    return payload if isinstance(payload, dict) else {}


def _prompt_variant_aliasing_summary() -> dict[str, Any]:
    audit = _load_repro_json("prompt_variant_validity_audit.json")
    repair = _load_repro_json("prompt_variant_repair_rerun.json")
    affected = int(audit.get("affected_accepted_claims_in_existing_artifacts") or 0)
    canonical_affected = int(audit.get("canonical_affected_accepted_claims") or 0)
    canonical_files = int(audit.get("canonical_files_with_unsupported_prompt_variants") or 0)
    return {
        "affected_accepted_claims_in_existing_artifacts": affected,
        "canonical_affected_accepted_claims": canonical_affected,
        "canonical_files_with_unsupported_prompt_variants": canonical_files,
        "repair_covered_accepted_claims": int(repair.get("accepted_before_in_rerun_bundles") or 0),
        "repair_retained_previously_accepted": int(repair.get("previously_accepted_retained") or 0),
        "repair_demoted_previously_accepted": int(repair.get("previously_accepted_demoted") or 0),
        "status": "warn_prompt_holdout_pre_repair" if canonical_affected else "pass",
        "claim_boundary": (
            "Prompt-holdout counts are computed on a canonical surface that still includes "
            "unsupported nominal prompt variants. These counts must not be cited as settled "
            "prompt robustness; use prompt_variant_repair_rerun.json for the repair frontier."
            if canonical_affected
            else "The current canonical prompt-holdout surface has no unsupported prompt variants in accepted bundles."
        ),
    }


def build_payload() -> dict[str, Any]:
    claim_rows: list[dict[str, Any]] = []
    bundle_rows: list[dict[str, Any]] = []

    for bundle_dir in find_bundle_dirs(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR):
        protocol = read_yaml(bundle_dir / "protocol.yaml")
        prompt_variants = [str(v) for v in protocol.get("execution_grid", {}).get("prompt_variants", [])]
        if len(prompt_variants) < 2:
            continue

        current = _load_current_result(bundle_dir)
        accepted_ids = {
            report["hypothesis_id"]
            for report in current.get("claim_reports", [])
            if bool(report.get("passed"))
        }
        if not accepted_ids:
            continue

        hypotheses = {row["hypothesis_id"]: row for row in read_jsonl(bundle_dir / "hypothesis.jsonl")}
        raw_eval = json.loads((bundle_dir / "evaluation_result.json").read_text())
        by_hid = {
            row["hypothesis_id"]: row.get("raw_cells", [])
            for row in raw_eval.get("hypothesis_results", [])
        }
        floor = float(protocol.get("stage_gates", {}).get("min_causal_effect", 0.02))

        bundle_claims: list[dict[str, Any]] = []
        for report in current.get("claim_reports", []):
            hid = report["hypothesis_id"]
            if hid not in accepted_ids:
                continue
            confirmatory_cells = [
                cell
                for cell in by_hid.get(hid, [])
                if str(cell.get("slice", "confirmatory")) == "confirmatory"
            ]
            by_prompt = {
                variant: [float(cell["treatment_effect"]) for cell in confirmatory_cells if str(cell.get("prompt_variant")) == variant]
                for variant in prompt_variants
            }
            if any(len(values) == 0 for values in by_prompt.values()):
                continue

            holdouts: list[dict[str, Any]] = []
            all_holdouts_pass = True
            for holdout_variant in prompt_variants:
                source_values = [
                    value
                    for variant, values in by_prompt.items()
                    if variant != holdout_variant
                    for value in values
                ]
                holdout_values = by_prompt[holdout_variant]
                source_mean = _mean(source_values)
                holdout_mean = _mean(holdout_values)
                same_direction = _sign(source_mean) != 0 and _sign(source_mean) == _sign(holdout_mean)
                above_floor = abs(holdout_mean) >= floor
                passes = bool(same_direction and above_floor)
                retention_ratio = abs(holdout_mean) / max(abs(source_mean), 1e-12)
                holdouts.append(
                    {
                        "holdout_prompt_variant": holdout_variant,
                        "source_mean": source_mean,
                        "holdout_mean": holdout_mean,
                        "same_direction": same_direction,
                        "above_floor": above_floor,
                        "passes": passes,
                        "retention_ratio": retention_ratio,
                        "n_source_cells": len(source_values),
                        "n_holdout_cells": len(holdout_values),
                    }
                )
                all_holdouts_pass = all_holdouts_pass and passes

            hypothesis = hypotheses.get(hid, {})
            claim_row = {
                "bundle": bundle_dir.name,
                "task": protocol["unit_of_work"]["task_id"],
                "model": protocol["unit_of_work"]["model_id"],
                "hypothesis_id": hid,
                "claim_text": hypothesis.get("claim_text"),
                "evidence_tier": report.get("evidence_tier"),
                "discovery_lane": hypothesis.get("discovery_lane", "canonical_real"),
                "prompt_variants": prompt_variants,
                "causal_effect_floor": floor,
                "all_holdouts_pass": all_holdouts_pass,
                "holdouts": holdouts,
            }
            claim_rows.append(claim_row)
            bundle_claims.append(claim_row)

        if bundle_claims:
            bundle_rows.append(
                {
                    "bundle": bundle_dir.name,
                    "task": protocol["unit_of_work"]["task_id"],
                    "model": protocol["unit_of_work"]["model_id"],
                    "accepted_claims_tested": len(bundle_claims),
                    "claims_passing_all_holdouts": sum(1 for row in bundle_claims if row["all_holdouts_pass"]),
                    "claims": [row["hypothesis_id"] for row in bundle_claims],
                }
            )

    total_holdout_checks = sum(len(row["holdouts"]) for row in claim_rows)
    passing_holdout_checks = sum(
        1
        for row in claim_rows
        for holdout in row["holdouts"]
        if holdout["passes"]
    )
    all_holdouts_pass_count = sum(1 for row in claim_rows if row["all_holdouts_pass"])

    by_model: dict[str, dict[str, int]] = {}
    by_task: dict[str, dict[str, int]] = {}
    for row in claim_rows:
        by_model.setdefault(row["model"], {"claims_tested": 0, "claims_passing_all_holdouts": 0})
        by_model[row["model"]]["claims_tested"] += 1
        by_model[row["model"]]["claims_passing_all_holdouts"] += int(row["all_holdouts_pass"])
        by_task.setdefault(row["task"], {"claims_tested": 0, "claims_passing_all_holdouts": 0})
        by_task[row["task"]]["claims_tested"] += 1
        by_task[row["task"]]["claims_passing_all_holdouts"] += int(row["all_holdouts_pass"])

    failing_claims = [row for row in claim_rows if not row["all_holdouts_pass"]]
    strongest_holdouts = sorted(
        [
            {
                "bundle": row["bundle"],
                "hypothesis_id": row["hypothesis_id"],
                "task": row["task"],
                "model": row["model"],
                "holdout_prompt_variant": holdout["holdout_prompt_variant"],
                "holdout_mean": holdout["holdout_mean"],
                "source_mean": holdout["source_mean"],
                "retention_ratio": holdout["retention_ratio"],
                "passes": holdout["passes"],
            }
            for row in claim_rows
            for holdout in row["holdouts"]
        ],
        key=lambda item: (item["passes"], abs(item["holdout_mean"]), item["retention_ratio"]),
        reverse=True,
    )[:10]

    return {
        "schema_version": 1,
        "generated_by": "main/prompt_holdout_transfer_control.py",
        "accepted_claims_with_multi_prompt": len(claim_rows),
        "claims_passing_all_holdouts": all_holdouts_pass_count,
        "claims_failing_any_holdout": len(claim_rows) - all_holdouts_pass_count,
        "total_holdout_checks": total_holdout_checks,
        "passing_holdout_checks": passing_holdout_checks,
        "bundle_summaries": bundle_rows,
        "by_model": by_model,
        "by_task": by_task,
        "failing_claims": failing_claims,
        "strongest_holdouts": strongest_holdouts,
        "claims": claim_rows,
        "prompt_variant_aliasing": _prompt_variant_aliasing_summary(),
        "notes": [
            "This is a within-model prompt generalization control built from released raw cells.",
            "It does not alter evidence tiers and does not replace cross-model transfer.",
            "A claim passes the prompt-holdout control only if every held-out prompt variant matches the source direction and exceeds the bundle's causal-effect floor.",
        ],
    }


def format_markdown(payload: dict[str, Any]) -> str:
    aliasing = payload.get("prompt_variant_aliasing") or {}
    lines = [
        "# Prompt-Holdout Transfer Control",
        "",
        f"- Accepted claims with multi-prompt coverage: **{payload['accepted_claims_with_multi_prompt']}**",
        f"- Claims passing all held-out prompt variants: **{payload['claims_passing_all_holdouts']} / {payload['accepted_claims_with_multi_prompt']}**",
        f"- Passing hold-out checks: **{payload['passing_holdout_checks']} / {payload['total_holdout_checks']}**",
        "",
        "This is a within-model prompt control, not a new evidence tier. It asks whether accepted claims remain causal on held-out prompt variants already present in the release.",
    ]
    if aliasing.get("canonical_affected_accepted_claims"):
        lines.extend([
            "",
            "> **Prompt-variant repair caveat.** This report is computed on the visible pre-repair release. "
            f"`prompt_variant_validity_audit.json` found unsupported nominal variants in artifacts containing **{aliasing['affected_accepted_claims_in_existing_artifacts']}** accepted claims, "
            f"and `prompt_variant_repair_rerun.json` covers **{aliasing['repair_covered_accepted_claims']}** of them, retaining **{aliasing['repair_retained_previously_accepted']}** and demoting **{aliasing['repair_demoted_previously_accepted']}**. "
            "Do not cite the holdout count below as settled prompt robustness until repaired bundles are promoted and dependent diagnostics are rerun.",
        ])
    elif aliasing.get("affected_accepted_claims_in_existing_artifacts"):
        lines.extend([
            "",
            "> **Prompt-variant repair caveat/status.** Legacy artifacts still contain unsupported nominal variants in bundles that previously held accepted claims, "
            f"but the current canonical surface has **{aliasing['canonical_files_with_unsupported_prompt_variants']}** unsupported-prompt files and **{aliasing['canonical_affected_accepted_claims']}** affected accepted claims after prompt-repair promotion. "
            f"The promotion frontier retained **{aliasing['repair_retained_previously_accepted']}** and demoted **{aliasing['repair_demoted_previously_accepted']}** of **{aliasing['repair_covered_accepted_claims']}** previously accepted affected claims.",
        ])
    lines.extend([
        "",
        "## By model",
        "",
        "| Model | Claims tested | Claims passing all holdouts |",
        "|---|---|---|",
    ])
    for model, row in sorted(payload["by_model"].items()):
        lines.append(
            f"| `{model}` | {row['claims_tested']} | {row['claims_passing_all_holdouts']} |"
        )

    lines.extend([
        "",
        "## By task",
        "",
        "| Task | Claims tested | Claims passing all holdouts |",
        "|---|---|---|",
    ])
    for task, row in sorted(payload["by_task"].items()):
        lines.append(
            f"| `{task}` | {row['claims_tested']} | {row['claims_passing_all_holdouts']} |"
        )

    lines.extend([
        "",
        "## Bundle summary",
        "",
        "| Bundle | Task | Model | Accepted claims tested | Passing all holdouts |",
        "|---|---|---|---|---|",
    ])
    for row in payload["bundle_summaries"]:
        lines.append(
            f"| `{row['bundle']}` | `{row['task']}` | `{row['model']}` | {row['accepted_claims_tested']} | {row['claims_passing_all_holdouts']} |"
        )

    lines.extend([
        "",
        "## Failing claims",
        "",
    ])
    if not payload["failing_claims"]:
        lines.append("- None.")
    else:
        for row in payload["failing_claims"]:
            lines.append(f"### `{row['bundle']}` / `{row['hypothesis_id']}`")
            lines.append("")
            for holdout in row["holdouts"]:
                marker = "PASS" if holdout["passes"] else "FAIL"
                lines.append(
                    f"- {marker} `{holdout['holdout_prompt_variant']}`: holdout_mean={holdout['holdout_mean']:+.6f}, "
                    f"source_mean={holdout['source_mean']:+.6f}, same_direction={holdout['same_direction']}, "
                    f"above_floor={holdout['above_floor']}"
                )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    REPRO_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    out_json = REPRO_DIR / "prompt_holdout_transfer_control.json"
    out_md = REPRO_DIR / "prompt_holdout_transfer_control.md"
    write_json(out_json, payload)
    write_text(out_md, format_markdown(payload))
    print(str(out_json))


if __name__ == "__main__":
    main()
