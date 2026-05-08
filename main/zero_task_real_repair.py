#!/usr/bin/env python3
"""Run real-model confirmatory repair candidates for zero-accepted tasks.

The existing ``zero_task_confirmatory_repair.py`` is intentionally mock-only:
it proves the upgraded protocol plumbing can emit exploratory and confirmatory
cells, but it is not scientific evidence. This script is the empirical follow-up.

It copies selected zero-task released bundles into
``main/output/zero_task_real_repair/``, upgrades only the execution protocol
needed for a real confirmatory split, runs Stage-2 in ``mode=real``, and then
evaluates the resulting bundle under the current Stage-1 contract. Original
released bundles are not overwritten. The canonical aggregate now supersedes
same-named legacy zero-task bundles with these real-repair reruns, so bundle
and claim counts remain stable instead of double-counting old and repaired
versions.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from collections import Counter
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

SOURCE_DIR = ROOT / "main" / "output" / "real_multi_task"
OUT_DIR = ROOT / "main" / "output" / "zero_task_real_repair"
REPRO = ROOT / "main" / "output" / "repro"
OUT_JSON = REPRO / "zero_task_real_repair.json"
OUT_MD = REPRO / "zero_task_real_repair.md"

ZERO_TASKS = {
    "arithmetic_v0",
    "docstring_v0",
    "fact_recall_v0",
    "gendered_pronoun_v0",
    "greater_than_v0",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _failed_gate_counts(result: dict[str, Any]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in result.get("claim_reports", []):
        for gate in row.get("failed_checks", []):
            counter[str(gate)] += 1
    return dict(counter)


def _count_gate_failures(result: dict[str, Any], gate: str) -> int:
    return sum(int(gate in row.get("failed_checks", [])) for row in result.get("claim_reports", []))


def _bundle_dirs(tasks: set[str] | None, models: set[str] | None) -> list[Path]:
    rows: list[Path] = []
    for bundle_dir in sorted(SOURCE_DIR.iterdir()):
        if not bundle_dir.is_dir():
            continue
        if not (bundle_dir / "protocol.yaml").exists():
            continue
        if not (bundle_dir / "hypothesis.jsonl").exists():
            continue
        if not (bundle_dir / "evaluation_result_current.json").exists():
            continue
        protocol = yaml.safe_load((bundle_dir / "protocol.yaml").read_text())
        task_id = str(protocol["unit_of_work"]["task_id"])
        model_id = str(protocol["unit_of_work"]["model_id"])
        if task_id not in ZERO_TASKS:
            continue
        if tasks is not None and task_id not in tasks:
            continue
        if models is not None and model_id not in models:
            continue
        rows.append(bundle_dir)
    return rows


def _upgraded_protocol(protocol: dict[str, Any]) -> dict[str, Any]:
    upgraded = json.loads(json.dumps(protocol))
    task_id = str(upgraded["unit_of_work"]["task_id"])
    supported_variants = list(getattr(get_task_module(task_id), "PROMPT_VARIANTS", []) or ["base"])
    prompt_variants = (["base"] if "base" in supported_variants else []) + [
        variant for variant in supported_variants if variant != "base"
    ]
    upgraded["protocol_id"] = f"{protocol['protocol_id']}_confirmatory_repair_real"
    upgraded.setdefault("sample_size_policy", {})
    upgraded["sample_size_policy"]["require_confirmatory_split"] = True
    upgraded["sample_size_policy"]["exploratory_fraction"] = 0.3
    upgraded["sample_size_policy"]["min_cells_per_hypothesis"] = max(
        int(upgraded["sample_size_policy"].get("min_cells_per_hypothesis", 4)),
        8,
    )
    upgraded["execution_grid"] = {
        "seeds": [42, 123],
        "prompt_variants": prompt_variants[:2],
        "resample_ids": [0],
        "methods": list(protocol.get("execution_grid", {}).get("methods", ["activation_patching", "zero_ablation"])),
    }
    return upgraded


def _rewrite_hypotheses(hypotheses_text: str, protocol_id: str) -> str:
    rows: list[str] = []
    for line in hypotheses_text.splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        row["protocol_id"] = protocol_id
        row.setdefault("provider_id", "zero_task_real_repair_v1")
        row.setdefault("discovery_lane", "canonical_real_repair_v1")
        rows.append(json.dumps(row, sort_keys=False))
    return "\n".join(rows) + ("\n" if rows else "")


def _write_candidate_bundle(source_bundle: Path, target_bundle: Path, protocol: dict[str, Any]) -> None:
    if target_bundle.exists():
        shutil.rmtree(target_bundle)
    target_bundle.mkdir(parents=True, exist_ok=True)
    (target_bundle / "protocol.yaml").write_text(yaml.safe_dump(protocol, sort_keys=False))
    hypotheses_text = (source_bundle / "hypothesis.jsonl").read_text()
    (target_bundle / "hypothesis.jsonl").write_text(
        _rewrite_hypotheses(hypotheses_text, protocol["protocol_id"])
    )


def _run_one(source_bundle: Path, *, device: str, examples_per_cell: int) -> dict[str, Any]:
    protocol = yaml.safe_load((source_bundle / "protocol.yaml").read_text())
    current = _load_json(source_bundle / "evaluation_result_current.json")
    upgraded = _upgraded_protocol(protocol)
    target_bundle = OUT_DIR / source_bundle.name
    _write_candidate_bundle(source_bundle, target_bundle, upgraded)

    started = time.time()
    stage2 = run_stage2(
        Stage2Config(
            bundle_dir=target_bundle,
            mode="real",
            device=device,
            examples_per_cell=examples_per_cell,
            exploratory_fraction=float(upgraded["sample_size_policy"].get("exploratory_fraction", 0.3)),
        )
    )
    result = evaluate_bundle(target_bundle)
    (target_bundle / "evaluation_result_current.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    (target_bundle / "stage_gate_report.md").write_text(build_markdown_report(result))

    return {
        "bundle": source_bundle.name,
        "task": protocol["unit_of_work"]["task_id"],
        "model": protocol["unit_of_work"]["model_id"],
        "source_bundle": str(source_bundle.relative_to(ROOT)),
        "candidate_bundle": str(target_bundle.relative_to(ROOT)),
        "mode": "real",
        "device": device,
        "examples_per_cell": examples_per_cell,
        "stage2_cell_count": stage2["cell_count"],
        "runtime_seconds": time.time() - started,
        "accepted_before": int(current.get("overall", {}).get("accepted_count", 0)),
        "accepted_after_real": int(result.get("overall", {}).get("accepted_count", 0)),
        "confirmatory_present_failures_before": _count_gate_failures(current, "confirmatory_present"),
        "confirmatory_present_failures_after_real": _count_gate_failures(result, "confirmatory_present"),
        "confirmatory_ci_failures_before": _count_gate_failures(current, "confirmatory_ci"),
        "confirmatory_ci_failures_after_real": _count_gate_failures(result, "confirmatory_ci"),
        "failed_gates_before": _failed_gate_counts(current),
        "failed_gates_after_real": _failed_gate_counts(result),
        "accepted_hypotheses_after_real": [
            row["hypothesis_id"] for row in result.get("claim_reports", []) if bool(row.get("passed"))
        ],
        "tiers_after_real": {
            row["hypothesis_id"]: row["evidence_tier"] for row in result.get("claim_reports", [])
        },
        "upgraded_protocol": {
            "require_confirmatory_split": upgraded["sample_size_policy"]["require_confirmatory_split"],
            "exploratory_fraction": upgraded["sample_size_policy"]["exploratory_fraction"],
            "execution_grid": upgraded["execution_grid"],
        },
    }


def _summarize_existing_candidate(
    candidate_bundle: Path,
    previous_by_bundle: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    protocol_path = candidate_bundle / "protocol.yaml"
    result_path = candidate_bundle / "evaluation_result_current.json"
    if not protocol_path.exists() or not result_path.exists():
        return None
    protocol = yaml.safe_load(protocol_path.read_text())
    task = str(protocol["unit_of_work"]["task_id"])
    model = str(protocol["unit_of_work"]["model_id"])
    source_bundle = SOURCE_DIR / candidate_bundle.name
    if not source_bundle.exists():
        return None
    current = _load_json(source_bundle / "evaluation_result_current.json")
    result = _load_json(result_path)
    prior = (previous_by_bundle or {}).get(candidate_bundle.name, {})
    return {
        "bundle": candidate_bundle.name,
        "task": task,
        "model": model,
        "source_bundle": str(source_bundle.relative_to(ROOT)),
        "candidate_bundle": str(candidate_bundle.relative_to(ROOT)),
        "mode": "real",
        "device": prior.get("device", "unknown_existing"),
        "examples_per_cell": prior.get("examples_per_cell", "unknown_existing"),
        "stage2_cell_count": sum(len(row.get("raw_cells", [])) for row in _load_json(candidate_bundle / "evaluation_result.json").get("hypothesis_results", [])),
        "runtime_seconds": float(prior.get("runtime_seconds", 0.0) or 0.0),
        "accepted_before": int(current.get("overall", {}).get("accepted_count", 0)),
        "accepted_after_real": int(result.get("overall", {}).get("accepted_count", 0)),
        "confirmatory_present_failures_before": _count_gate_failures(current, "confirmatory_present"),
        "confirmatory_present_failures_after_real": _count_gate_failures(result, "confirmatory_present"),
        "confirmatory_ci_failures_before": _count_gate_failures(current, "confirmatory_ci"),
        "confirmatory_ci_failures_after_real": _count_gate_failures(result, "confirmatory_ci"),
        "failed_gates_before": _failed_gate_counts(current),
        "failed_gates_after_real": _failed_gate_counts(result),
        "accepted_hypotheses_after_real": [
            row["hypothesis_id"] for row in result.get("claim_reports", []) if bool(row.get("passed"))
        ],
        "tiers_after_real": {
            row["hypothesis_id"]: row["evidence_tier"] for row in result.get("claim_reports", [])
        },
        "upgraded_protocol": {
            "require_confirmatory_split": bool(protocol.get("sample_size_policy", {}).get("require_confirmatory_split")),
            "exploratory_fraction": protocol.get("sample_size_policy", {}).get("exploratory_fraction"),
            "execution_grid": protocol.get("execution_grid", {}),
        },
    }


def _existing_rows() -> list[dict[str, Any]]:
    if not OUT_DIR.exists():
        return []
    previous_by_bundle: dict[str, dict[str, Any]] = {}
    if OUT_JSON.exists():
        try:
            previous = _load_json(OUT_JSON)
            previous_by_bundle = {
                str(row.get("bundle")): row
                for row in previous.get("rows", [])
                if isinstance(row, dict) and row.get("bundle")
            }
        except Exception:
            previous_by_bundle = {}
    rows: list[dict[str, Any]] = []
    for candidate_bundle in sorted(OUT_DIR.iterdir()):
        if not candidate_bundle.is_dir():
            continue
        row = _summarize_existing_candidate(candidate_bundle, previous_by_bundle)
        if row is not None:
            rows.append(row)
    return rows


def _write_outputs(rows: list[dict[str, Any]]) -> None:
    aggregate = {
        "bundles_run": len(rows),
        "accepted_before_total": sum(int(row["accepted_before"]) for row in rows),
        "accepted_after_real_total": sum(int(row["accepted_after_real"]) for row in rows),
        "tasks_with_any_real_accept_after": sorted(
            {str(row["task"]) for row in rows if int(row["accepted_after_real"]) > 0}
        ),
        "confirmatory_present_failures_before": sum(int(row["confirmatory_present_failures_before"]) for row in rows),
        "confirmatory_present_failures_after_real": sum(int(row["confirmatory_present_failures_after_real"]) for row in rows),
        "confirmatory_ci_failures_before": sum(int(row["confirmatory_ci_failures_before"]) for row in rows),
        "confirmatory_ci_failures_after_real": sum(int(row["confirmatory_ci_failures_after_real"]) for row in rows),
        "runtime_seconds": sum(float(row["runtime_seconds"]) for row in rows),
    }
    payload = {
        "generated_by": "main/zero_task_real_repair.py",
        "aggregate": aggregate,
        "rows": rows,
        "release_status": (
            "Real Stage-2 repair reruns. In canonical aggregate reporting, "
            "same-named legacy zero-task bundles from main/output/real_multi_task "
            "are superseded by these reruns, so headline bundle and claim counts "
            "remain stable while repaired evidence is counted."
        ),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Zero-Task Real Confirmatory Repair",
        "",
        payload["release_status"],
        "",
        f"- Bundles run: **{aggregate['bundles_run']}**",
        f"- Accepted before: **{aggregate['accepted_before_total']}**",
        f"- Accepted after real repair: **{aggregate['accepted_after_real_total']}**",
        f"- Tasks with any real accepted claim after repair: **{', '.join(aggregate['tasks_with_any_real_accept_after']) or 'none'}**",
        f"- Runtime: **{aggregate['runtime_seconds'] / 60:.1f} min**",
        "",
        "| Bundle | Task | Model | Accepted before | Accepted after real | Accepted hypotheses | Candidate bundle |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for row in rows:
        accepted = ", ".join(f"`{hid}`" for hid in row["accepted_hypotheses_after_real"]) or "none"
        lines.append(
            f"| `{row['bundle']}` | `{row['task']}` | `{row['model']}` | "
            f"{row['accepted_before']} | {row['accepted_after_real']} | {accepted} | `{row['candidate_bundle']}` |"
        )
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run real zero-task confirmatory repair candidates")
    parser.add_argument("--tasks", default="", help="Comma-separated task filter")
    parser.add_argument("--models", default="", help="Comma-separated model filter")
    parser.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"],
                        help="Inference device. Defaults to 'cpu' for cross-platform reproducibility; pass --device mps on Apple silicon or --device cuda on Linux GPUs to enable hardware acceleration.")
    parser.add_argument("--examples-per-cell", type=int, default=12)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--summarize-existing",
        action="store_true",
        help="Regenerate the zero-task real-repair summary from existing candidate bundles without live model reruns.",
    )
    args = parser.parse_args()

    if args.summarize_existing:
        rows = _existing_rows()
        _write_outputs(rows)
        print(str(OUT_JSON))
        return

    tasks = {part.strip() for part in args.tasks.split(",") if part.strip()} or None
    models = {part.strip() for part in args.models.split(",") if part.strip()} or None
    candidates = _bundle_dirs(tasks, models)
    if args.limit > 0:
        candidates = candidates[: args.limit]
    if not candidates:
        raise SystemExit("No matching zero-task bundles found.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows_by_bundle = {str(row["bundle"]): row for row in _existing_rows()}
    for idx, source_bundle in enumerate(candidates, start=1):
        print(f"[{idx}/{len(candidates)}] real repair {source_bundle.name}", flush=True)
        rows_by_bundle[source_bundle.name] = _run_one(
            source_bundle,
            device=args.device,
            examples_per_cell=args.examples_per_cell,
        )
        _write_outputs([rows_by_bundle[name] for name in sorted(rows_by_bundle)])

    _write_outputs([rows_by_bundle[name] for name in sorted(rows_by_bundle)])
    print(str(OUT_JSON))


if __name__ == "__main__":
    main()
