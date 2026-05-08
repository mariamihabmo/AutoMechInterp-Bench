#!/usr/bin/env python3
"""Run same-family transfer rows for prompt-repaired canonical bundles.

Paired-bundle replication can restore cross-model evidence for repaired
same-lane two-model bundles, but it does not cover same-family targets such as
GPT-2 Small -> GPT-2 Medium. This script fills only missing transfer rows for
accepted claims in prompt-repaired bundles and preserves any existing paired
replication rows already written to ``cross_model_results.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))
sys.path.insert(0, str(ROOT / "main"))

from automechinterp_evaluator.evaluator import evaluate_bundle  # noqa: E402
from automechinterp_evaluator.reporting import build_markdown_report  # noqa: E402
from automechinterp_runner.models import models_in_family, resolve_model  # noqa: E402
from _bundle_analysis import REAL_MULTILANE_DIR, REAL_MULTI_TASK_DIR, find_bundle_dirs, repo_relative  # noqa: E402
from _model_loading import load_hooked_transformer  # noqa: E402
from run_real_multi_task import run_cross_model_transfer  # noqa: E402

REPRO = ROOT / "main" / "output" / "repro"
OUT_JSON = REPRO / "prompt_repair_same_family_transfer.json"
OUT_MD = REPRO / "prompt_repair_same_family_transfer.md"


def _size_key(model_id: str) -> tuple[int, int, int]:
    info = resolve_model(model_id)
    return (int(info.n_layers), int(info.n_heads), int(info.d_model))


def _next_same_family_model(source_model: str) -> str | None:
    family = resolve_model(source_model).family
    family_models = sorted(models_in_family(family), key=_size_key)
    if source_model not in family_models:
        return None
    idx = family_models.index(source_model)
    return family_models[idx + 1] if idx + 1 < len(family_models) else None


def _load_json(path: Path) -> Any:
    if not path.exists():
        return [] if path.name == "cross_model_results.json" else {}
    return json.loads(path.read_text())


def _accepted_ids(bundle_dir: Path) -> set[str]:
    result = _load_json(bundle_dir / "evaluation_result_current.json")
    if not result:
        result = evaluate_bundle(bundle_dir)
    return {str(row["hypothesis_id"]) for row in result.get("claim_reports", []) if row.get("passed")}


def _existing_transfer_hids(bundle_dir: Path, target_model: str | None = None) -> set[str]:
    rows = _load_json(bundle_dir / "cross_model_results.json")
    return {
        str(row.get("hypothesis_id"))
        for row in rows
        if isinstance(row, dict)
        and (target_model is None or str(row.get("transfer_model")) == str(target_model))
    }


def _candidate_bundles(limit_to: set[str] | None = None) -> list[Path]:
    out: list[Path] = []
    for bundle in _prompt_repair_bundles(limit_to):
        protocol = yaml.safe_load((bundle / "protocol.yaml").read_text())
        source_model = str(protocol["unit_of_work"]["model_id"])
        target_model = _next_same_family_model(source_model)
        accepted = _accepted_ids(bundle)
        missing = accepted - _existing_transfer_hids(bundle, target_model)
        if missing:
            out.append(bundle)
    return out


def _prompt_repair_bundles(limit_to: set[str] | None = None) -> list[Path]:
    out: list[Path] = []
    for bundle in find_bundle_dirs(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR):
        if "prompt_variant_repair" not in str(bundle):
            continue
        if limit_to and bundle.name not in limit_to:
            continue
        accepted = _accepted_ids(bundle)
        if not accepted:
            continue
        out.append(bundle)
    return out


def _merge_rows(
    existing: list[dict[str, Any]],
    live_rows: list[dict[str, Any]],
    missing_hids: set[str],
    target_model: str,
) -> list[dict[str, Any]]:
    merged = list(existing)
    existing_keys = {
        (str(row.get("hypothesis_id")), str(row.get("transfer_model")))
        for row in merged
        if isinstance(row, dict)
    }
    for row in live_rows:
        hid = str(row.get("hypothesis_id"))
        key = (hid, str(row.get("transfer_model", target_model)))
        if hid in missing_hids and key not in existing_keys:
            merged.append(row)
            existing_keys.add(key)
    return merged


def _write_summary(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Prompt-Repair Same-Family Transfer",
        "",
        payload["claim_boundary"],
        "",
        f"- Mode: **{payload.get('mode', 'live_fill')}**",
        f"- Bundles summarized: **{payload.get('bundles_summarized', payload.get('bundles_updated', 0))}**",
        f"- Bundles updated: **{payload.get('bundles_updated', 0)}**",
        f"- Accepted claims with transfer rows: **{payload.get('accepted_claims_with_transfer_rows', 'n/a')}**",
        f"- Accepted claims missing transfer rows: **{payload.get('accepted_claims_missing_transfer_rows', 'n/a')}**",
        f"- Examples per transfer run: **{payload.get('n_examples', 'n/a')}**",
        "",
        "| Bundle | Source -> target | Filled / missing hypotheses | Rows before -> after |",
        "|---|---|---|---:|",
    ]
    for row in payload.get("rows", []):
        hids = row.get("filled_missing_hypotheses")
        if hids is None:
            hids = row.get("missing_hypotheses", [])
        hids_text = ", ".join(f"`{hid}`" for hid in hids) or "none"
        before = row.get("existing_rows_before", row.get("existing_transfer_rows", 0))
        after = row.get("merged_rows_after", row.get("existing_transfer_rows", before))
        lines.append(
            f"| `{row['bundle']}` | `{row['source_model']}` -> `{row.get('target_model') or 'none'}` | "
            f"{hids_text} | {before} -> {after} |"
        )
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n")


def _summarize_existing(limit_to: set[str] | None = None) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    accepted_with_rows = 0
    accepted_missing_rows = 0
    for bundle in _prompt_repair_bundles(limit_to):
        protocol = yaml.safe_load((bundle / "protocol.yaml").read_text())
        source_model = str(protocol["unit_of_work"]["model_id"])
        target_model = _next_same_family_model(source_model)
        accepted = _accepted_ids(bundle)
        existing_hids = _existing_transfer_hids(bundle, target_model)
        missing_hids = accepted - existing_hids
        accepted_with_rows += len(accepted & existing_hids)
        accepted_missing_rows += len(missing_hids)
        rows.append(
            {
                "bundle": bundle.name,
                "bundle_dir": repo_relative(bundle),
                "task": str(protocol["unit_of_work"]["task_id"]),
                "source_model": source_model,
                "target_model": target_model,
                "accepted_claims": sorted(accepted),
                "accepted_claims_with_transfer_rows": sorted(accepted & existing_hids),
                "missing_hypotheses": sorted(missing_hids),
                "existing_transfer_rows": len(_load_json(bundle / "cross_model_results.json")),
            }
        )

    return {
        "generated_by": "main/prompt_repair_same_family_transfer.py",
        "mode": "summarize_existing",
        "bundles_summarized": len(rows),
        "bundles_updated": 0,
        "accepted_claims_with_transfer_rows": accepted_with_rows,
        "accepted_claims_missing_transfer_rows": accepted_missing_rows,
        "rows": rows,
        "claim_boundary": (
            "Cached summary of same-family transfer rows for prompt-repaired canonical bundles. "
            "This mode performs no live model inference and is suitable for the materialized audit."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill missing same-family transfer rows for prompt-repaired bundles")
    parser.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"],
                        help="Inference device. Defaults to 'cpu' for cross-platform reproducibility; pass --device mps on Apple silicon or --device cuda on Linux GPUs to enable hardware acceleration.")
    parser.add_argument("--n-examples", type=int, default=100)
    parser.add_argument("--bundle", action="append", default=[], help="Exact bundle name to run; may be repeated.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--summarize-existing", action="store_true", help="Summarize cached transfer rows without live model inference.")
    args = parser.parse_args()

    limit_to = set(args.bundle) if args.bundle else None
    if args.summarize_existing:
        payload = _summarize_existing(limit_to)
        _write_summary(payload)
        print(str(OUT_JSON))
        return

    candidates = _candidate_bundles(limit_to)
    if args.limit:
        candidates = candidates[: args.limit]

    models: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    for idx, bundle in enumerate(candidates, start=1):
        protocol = yaml.safe_load((bundle / "protocol.yaml").read_text())
        source_model = str(protocol["unit_of_work"]["model_id"])
        task_id = str(protocol["unit_of_work"]["task_id"])
        target_model = _next_same_family_model(source_model)
        accepted = _accepted_ids(bundle)
        existing_rows = _load_json(bundle / "cross_model_results.json")
        existing_hids = _existing_transfer_hids(bundle, target_model)
        missing_hids = accepted - existing_hids
        if target_model is None or not missing_hids:
            continue

        print(f"[{idx}/{len(candidates)}] {bundle.name}: {source_model} -> {target_model}; missing={sorted(missing_hids)}", flush=True)
        if target_model not in models:
            models[target_model] = load_hooked_transformer(target_model, device=args.device, local_only=False)

        live_rows = run_cross_model_transfer(
            source_bundle_dir=bundle,
            transfer_model=models[target_model],
            transfer_model_id=target_model,
            source_model_id=source_model,
            task_id=task_id,
            n_examples=args.n_examples,
        )
        merged = _merge_rows(existing_rows, live_rows, missing_hids, target_model)
        (bundle / "cross_model_results.json").write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n")
        result = evaluate_bundle(bundle)
        (bundle / "evaluation_result_current.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        (bundle / "stage_gate_report.md").write_text(build_markdown_report(result))
        rows.append(
            {
                "bundle": bundle.name,
                "bundle_dir": repo_relative(bundle),
                "task": task_id,
                "source_model": source_model,
                "target_model": target_model,
                "accepted_claims": sorted(accepted),
                "filled_missing_hypotheses": sorted(missing_hids),
                "existing_rows_before": len(existing_rows),
                "merged_rows_after": len(merged),
            }
        )

    payload = {
        "generated_by": "main/prompt_repair_same_family_transfer.py",
        "device": args.device,
        "n_examples": args.n_examples,
        "bundles_updated": len(rows),
        "rows": rows,
        "claim_boundary": (
            "This fills missing same-family transfer rows for prompt-repaired canonical bundles. "
            "It preserves existing paired-bundle rows and does not lower the transfer gate."
        ),
    }
    _write_summary(payload)
    print(str(OUT_JSON))


if __name__ == "__main__":
    main()
