#!/usr/bin/env python3
"""Run contract-preserving distributed-head repair candidates for docstring_v0.

The current zero-task repair showed that docstring claims are not blocked by
missing confirmatory cells anymore. They fail method_sensitivity because
activation patching is large while ablation is weak or direction-reversing.

This script tests a narrow, non-threshold-changing hypothesis: perhaps the
single-head docstring claims are under-specified because the behavior is
distributed across the top discovered heads. We therefore build multi-head
claims from the already-released top docstring heads and re-run Stage-2 under
the same contract. The output is diagnostic unless explicitly promoted through
the normal artifact-governance process.
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

SOURCE_DIR = ROOT / "main" / "output" / "zero_task_real_repair"
OUT_DIR = ROOT / "main" / "output" / "docstring_distributed_repair"
REPRO = ROOT / "main" / "output" / "repro"
OUT_JSON = REPRO / "docstring_distributed_repair.json"
OUT_MD = REPRO / "docstring_distributed_repair.md"


CANDIDATES: dict[str, list[list[dict[str, int | str]]]] = {
    "docstring_v0_gpt2-small": [
        [
            {"component_type": "head", "layer": 10, "head": 1},
            {"component_type": "head", "layer": 8, "head": 11},
        ],
        [
            {"component_type": "head", "layer": 10, "head": 1},
            {"component_type": "head", "layer": 9, "head": 2},
        ],
        [
            {"component_type": "head", "layer": 8, "head": 11},
            {"component_type": "head", "layer": 9, "head": 2},
        ],
        [
            {"component_type": "head", "layer": 10, "head": 1},
            {"component_type": "head", "layer": 8, "head": 11},
            {"component_type": "head", "layer": 9, "head": 2},
        ],
    ],
    "docstring_v0_pythia-70m": [
        [
            {"component_type": "head", "layer": 3, "head": 3},
            {"component_type": "head", "layer": 4, "head": 7},
        ],
        [
            {"component_type": "head", "layer": 3, "head": 3},
            {"component_type": "head", "layer": 4, "head": 4},
        ],
        [
            {"component_type": "head", "layer": 4, "head": 7},
            {"component_type": "head", "layer": 4, "head": 4},
        ],
        [
            {"component_type": "head", "layer": 3, "head": 3},
            {"component_type": "head", "layer": 4, "head": 7},
            {"component_type": "head", "layer": 4, "head": 4},
        ],
    ],
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _failed_gate_counts(result: dict[str, Any]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in result.get("claim_reports", []):
        counts.update(str(gate) for gate in row.get("failed_checks", []))
    return dict(counts)


def _method_summary(result: dict[str, Any]) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for row in result.get("claim_reports", []):
        metrics = row.get("metrics") or {}
        rows[str(row["hypothesis_id"])] = {
            "passed": bool(row.get("passed")),
            "tier": row.get("evidence_tier"),
            "failed_checks": list(row.get("failed_checks", [])),
            "method_sensitivity_std": metrics.get("method_sensitivity_std"),
            "method_sensitivity_type": metrics.get("method_sensitivity_type"),
            "confirmatory_ci_low": metrics.get("confirmatory_ci_low"),
            "confirmatory_ci_high": metrics.get("confirmatory_ci_high"),
            "specificity_ratio": metrics.get("specificity_ratio"),
        }
    return rows


def _candidate_label(components: list[dict[str, int | str]]) -> str:
    parts = []
    for comp in components:
        parts.append(f"L{comp['layer']}H{comp['head']}")
    return "+".join(parts)


def _write_bundle(source_bundle: Path, target_bundle: Path, protocol: dict[str, Any]) -> None:
    if target_bundle.exists():
        shutil.rmtree(target_bundle)
    target_bundle.mkdir(parents=True, exist_ok=True)
    (target_bundle / "protocol.yaml").write_text(yaml.safe_dump(protocol, sort_keys=False))

    bundle_name = source_bundle.name
    task_id = str(protocol["unit_of_work"]["task_id"])
    model_id = str(protocol["unit_of_work"]["model_id"])
    rows = []
    for idx, components in enumerate(CANDIDATES[bundle_name], start=1):
        label = _candidate_label(components)
        rows.append(
            {
                "hypothesis_id": f"h_docstring_distributed_{idx:03d}",
                "protocol_id": protocol["protocol_id"],
                "task_id": task_id,
                "model_id": model_id,
                "metric_id": "logit_diff",
                "claim_text": f"{label} jointly contributes to docstring_v0 under sufficiency and necessity tests",
                "candidate_components": components,
                "predicted_effect_direction": "increase",
                "predicted_min_effect": 0.02,
                "predicted_specificity_ratio": 2.0,
                "expected_failure_modes": ["distributed_computation", "method_sensitivity_instability"],
                "provider_id": "docstring_distributed_repair_v1",
                "discovery_lane": "docstring_distributed_repair_v1",
            }
        )
    (target_bundle / "hypothesis.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=False) + "\n" for row in rows)
    )


def _run_one(source_bundle: Path, *, device: str, examples_per_cell: int) -> dict[str, Any]:
    protocol = yaml.safe_load((source_bundle / "protocol.yaml").read_text())
    protocol = json.loads(json.dumps(protocol))
    task_id = str(protocol["unit_of_work"]["task_id"])
    supported_variants = list(getattr(get_task_module(task_id), "PROMPT_VARIANTS", []) or ["base"])
    prompt_variants = (["base"] if "base" in supported_variants else []) + [
        variant for variant in supported_variants if variant != "base"
    ]
    protocol["protocol_id"] = f"{protocol['protocol_id']}_distributed_repair_v1"
    protocol["claim_budget"]["max_total_claims"] = len(CANDIDATES[source_bundle.name])
    protocol["claim_budget"]["max_claims_per_task"] = len(CANDIDATES[source_bundle.name])
    protocol["execution_grid"]["prompt_variants"] = prompt_variants[:2]

    target_bundle = OUT_DIR / source_bundle.name
    _write_bundle(source_bundle, target_bundle, protocol)
    started = time.time()
    stage2 = run_stage2(
        Stage2Config(
            bundle_dir=target_bundle,
            mode="real",
            device=device,
            examples_per_cell=examples_per_cell,
            exploratory_fraction=float(protocol["sample_size_policy"].get("exploratory_fraction", 0.3)),
        )
    )
    result = evaluate_bundle(target_bundle)
    (target_bundle / "evaluation_result_current.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    (target_bundle / "stage_gate_report.md").write_text(build_markdown_report(result))
    return {
        "bundle": source_bundle.name,
        "candidate_bundle": str(target_bundle.relative_to(ROOT)),
        "task": protocol["unit_of_work"]["task_id"],
        "model": protocol["unit_of_work"]["model_id"],
        "mode": "real",
        "device": device,
        "examples_per_cell": examples_per_cell,
        "stage2_cell_count": stage2["cell_count"],
        "runtime_seconds": time.time() - started,
        "accepted_after_real": int(result.get("overall", {}).get("accepted_count", 0)),
        "accepted_hypotheses_after_real": [
            row["hypothesis_id"] for row in result.get("claim_reports", []) if bool(row.get("passed"))
        ],
        "failed_gates_after_real": _failed_gate_counts(result),
        "method_summary": _method_summary(result),
    }


def _existing_rows() -> list[dict[str, Any]]:
    if not OUT_DIR.exists():
        return []
    rows: list[dict[str, Any]] = []
    for candidate_bundle in sorted(OUT_DIR.iterdir()):
        if not candidate_bundle.is_dir():
            continue
        result_path = candidate_bundle / "evaluation_result_current.json"
        protocol_path = candidate_bundle / "protocol.yaml"
        if not result_path.exists() or not protocol_path.exists():
            continue
        result = _load_json(result_path)
        protocol = yaml.safe_load(protocol_path.read_text())
        rows.append(
            {
                "bundle": candidate_bundle.name,
                "candidate_bundle": str(candidate_bundle.relative_to(ROOT)),
                "task": protocol["unit_of_work"]["task_id"],
                "model": protocol["unit_of_work"]["model_id"],
                "mode": "real",
                "device": "unknown_existing",
                "examples_per_cell": "unknown_existing",
                "stage2_cell_count": sum(
                    len(row.get("raw_cells", []))
                    for row in _load_json(candidate_bundle / "evaluation_result.json").get("hypothesis_results", [])
                ),
                "runtime_seconds": 0.0,
                "accepted_after_real": int(result.get("overall", {}).get("accepted_count", 0)),
                "accepted_hypotheses_after_real": [
                    row["hypothesis_id"] for row in result.get("claim_reports", []) if bool(row.get("passed"))
                ],
                "failed_gates_after_real": _failed_gate_counts(result),
                "method_summary": _method_summary(result),
            }
        )
    return rows


def _write_summary(rows: list[dict[str, Any]]) -> None:
    REPRO.mkdir(parents=True, exist_ok=True)
    aggregate = {
        "bundles_run": len(rows),
        "accepted_after_real_total": sum(int(row["accepted_after_real"]) for row in rows),
        "tasks_with_any_real_accept_after": sorted(
            {str(row["task"]) for row in rows if int(row["accepted_after_real"]) > 0}
        ),
        "gate_failures_after_real": dict(
            sum((Counter(row["failed_gates_after_real"]) for row in rows), Counter())
        ),
    }
    payload = {
        "generated_by": "main/docstring_distributed_repair.py",
        "status": (
            "diagnostic real repair; not included in canonical aggregate unless explicitly promoted"
        ),
        "scientific_question": (
            "Can distributed multi-head docstring claims align sufficiency and necessity under the existing method_sensitivity gate?"
        ),
        "rows": rows,
        "aggregate": aggregate,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Docstring Distributed Repair",
        "",
        payload["status"],
        "",
        f"- Bundles run: **{aggregate['bundles_run']}**",
        f"- Accepted after real repair: **{aggregate['accepted_after_real_total']}**",
        f"- Tasks with any accepted claim: **{', '.join(aggregate['tasks_with_any_real_accept_after']) or 'none'}**",
        "",
        "| Bundle | Model | Accepted | Top failed gates | Candidate bundle |",
        "|---|---|---:|---|---|",
    ]
    for row in rows:
        top = ", ".join(
            f"{gate}:{count}"
            for gate, count in sorted(
                row["failed_gates_after_real"].items(),
                key=lambda item: (-item[1], item[0]),
            )[:4]
        ) or "none"
        lines.append(
            f"| `{row['bundle']}` | `{row['model']}` | {row['accepted_after_real']} | {top} | `{row['candidate_bundle']}` |"
        )
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Docstring distributed-head repair")
    parser.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"])
    parser.add_argument("--examples-per-cell", type=int, default=24)
    parser.add_argument("--summarize-existing", action="store_true")
    args = parser.parse_args()

    if args.summarize_existing:
        rows = _existing_rows()
        _write_summary(rows)
        print(str(OUT_JSON))
        return

    rows = []
    for name in sorted(CANDIDATES):
        source = SOURCE_DIR / name
        if not source.exists():
            raise FileNotFoundError(f"missing source bundle: {source}")
        rows.append(_run_one(source, device=args.device, examples_per_cell=args.examples_per_cell))
    _write_summary(rows)
    print(str(OUT_JSON))


if __name__ == "__main__":
    main()
