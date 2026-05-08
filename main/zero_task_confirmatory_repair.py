#!/usr/bin/env python3
"""Mock-mode confirmatory-stage repair rehearsal for zero-task bundles.

Goal
----
The breadth-gap register said to first fix confirmatory-stage generation for the
zero-task execution failures and then re-run discovery. In this environment we
cannot run new real-model discovery because the required model weights are not
available offline. What we *can* do is execute the engineering part honestly:

* rebuild the zero-task canonical bundles under an upgraded confirmatory-aware
  Stage-2 protocol;
* run Stage-2 in ``mode=mock`` so the plumbing is exercised end-to-end;
* re-evaluate those repaired candidate bundles under the current evaluator; and
* record whether the confirmatory-stage failure mode disappears.

This is explicitly an **engineering rehearsal**, not new scientific evidence.
The output is useful because it distinguishes "the pipeline could not even emit
confirmatory cells" from "the task remains scientifically hard even once the
pipeline is fixed".
"""

from __future__ import annotations

import json
import shutil
import sys
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

import automechinterp_evaluator.evaluator as evaluator_module  # noqa: E402
from automechinterp_evaluator.evaluator import evaluate_bundle  # noqa: E402
from automechinterp_evaluator.reporting import build_markdown_report  # noqa: E402
from automechinterp_runner.runner import Stage2Config, run_stage2  # noqa: E402
from automechinterp_runner.tasks import get_task_module  # noqa: E402

SOURCE_DIR = ROOT / "main" / "output" / "real_multi_task"
REPAIR_DIR = ROOT / "main" / "output" / "zero_task_confirmatory_repair"
REPRO = ROOT / "main" / "output" / "repro"
OUT_JSON = REPRO / "zero_task_confirmatory_repair.json"
OUT_MD = REPRO / "zero_task_confirmatory_repair.md"


@contextmanager
def _fast_stat_budget(bootstrap_resamples: int = 256, permutation_iterations: int = 256):
    original_bootstrap = evaluator_module._bootstrap_ci
    original_perm = evaluator_module._permutation_p_value

    def bootstrap_wrapper(values, confidence=0.95, n_resamples=None, seed="bootstrap"):
        return original_bootstrap(
            values,
            confidence=confidence,
            n_resamples=bootstrap_resamples if n_resamples is None else min(int(n_resamples), bootstrap_resamples),
            seed=seed,
        )

    def perm_wrapper(values, n_permutations=None, seed="permtest"):
        return original_perm(
            values,
            n_permutations=permutation_iterations if n_permutations is None else min(int(n_permutations), permutation_iterations),
            seed=seed,
        )

    evaluator_module._bootstrap_ci = bootstrap_wrapper
    evaluator_module._permutation_p_value = perm_wrapper
    try:
        yield
    finally:
        evaluator_module._bootstrap_ci = original_bootstrap
        evaluator_module._permutation_p_value = original_perm


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
    total = 0
    for row in result.get("claim_reports", []):
        total += int(gate in row.get("failed_checks", []))
    return total


def _bundle_dirs() -> list[Path]:
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
        task_id = protocol["unit_of_work"]["task_id"]
        if task_id in ZERO_TASKS:
            rows.append(bundle_dir)
    return rows


def _upgraded_protocol(protocol: dict[str, Any]) -> dict[str, Any]:
    upgraded = json.loads(json.dumps(protocol))
    task_id = str(upgraded["unit_of_work"]["task_id"])
    supported_variants = list(getattr(get_task_module(task_id), "PROMPT_VARIANTS", []) or ["base"])
    prompt_variants = (["base"] if "base" in supported_variants else []) + [
        variant for variant in supported_variants if variant != "base"
    ]
    upgraded["protocol_id"] = f"{protocol['protocol_id']}_confirmatory_repair_mock"
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
    rows = []
    for line in hypotheses_text.splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        row["protocol_id"] = protocol_id
        rows.append(json.dumps(row, sort_keys=False))
    return "\n".join(rows) + ("\n" if rows else "")


def _write_bundle(bundle_dir: Path, protocol: dict[str, Any], hypotheses_text: str) -> None:
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "protocol.yaml").write_text(yaml.safe_dump(protocol, sort_keys=False))
    rewritten = _rewrite_hypotheses(hypotheses_text, protocol["protocol_id"])
    (bundle_dir / "hypothesis.jsonl").write_text(rewritten)


def main() -> None:
    REPAIR_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []

    for idx, source_bundle in enumerate(_bundle_dirs(), start=1):
        print(f"[{idx}] repairing {source_bundle.name}", flush=True)
        protocol = yaml.safe_load((source_bundle / "protocol.yaml").read_text())
        current = _load_json(source_bundle / "evaluation_result_current.json")
        hypotheses_text = (source_bundle / "hypothesis.jsonl").read_text()
        upgraded = _upgraded_protocol(protocol)
        repaired_dir = REPAIR_DIR / source_bundle.name
        _write_bundle(repaired_dir, upgraded, hypotheses_text)

        run_stage2(
            Stage2Config(
                bundle_dir=repaired_dir,
                mode="mock",
                device="cpu",
                examples_per_cell=8,
                exploratory_fraction=float(upgraded["sample_size_policy"].get("exploratory_fraction", 0.3)),
            )
        )
        with _fast_stat_budget():
            repaired_result = evaluate_bundle(repaired_dir)
        (repaired_dir / "evaluation_result_current.json").write_text(
            json.dumps(repaired_result, indent=2, sort_keys=True) + "\n"
        )
        (repaired_dir / "stage_gate_report.md").write_text(build_markdown_report(repaired_result))

        row = {
            "bundle": source_bundle.name,
            "task": protocol["unit_of_work"]["task_id"],
            "model": protocol["unit_of_work"]["model_id"],
            "source_bundle": str(source_bundle.relative_to(ROOT)),
            "repaired_bundle": str(repaired_dir.relative_to(ROOT)),
            "mode": "mock",
            "accepted_before": int(current.get("overall", {}).get("accepted_count", 0)),
            "accepted_after_mock": int(repaired_result.get("overall", {}).get("accepted_count", 0)),
            "confirmatory_present_failures_before": _count_gate_failures(current, "confirmatory_present"),
            "confirmatory_present_failures_after_mock": _count_gate_failures(repaired_result, "confirmatory_present"),
            "confirmatory_ci_failures_before": _count_gate_failures(current, "confirmatory_ci"),
            "confirmatory_ci_failures_after_mock": _count_gate_failures(repaired_result, "confirmatory_ci"),
            "failed_gates_before": _failed_gate_counts(current),
            "failed_gates_after_mock": _failed_gate_counts(repaired_result),
            "upgraded_protocol": {
                "require_confirmatory_split": upgraded["sample_size_policy"]["require_confirmatory_split"],
                "exploratory_fraction": upgraded["sample_size_policy"]["exploratory_fraction"],
                "execution_grid": upgraded["execution_grid"],
            },
            "notes": [
                "Mock-mode repair candidate only. No scientific claim promotion is justified from this artifact.",
                "Useful question answered: does confirmatory-stage plumbing remain a blocker once the protocol is upgraded?",
            ],
        }
        rows.append(row)

    tasks_before = defaultdict(int)
    tasks_after = defaultdict(int)
    for row in rows:
        tasks_before[row["task"]] += int(row["accepted_before"] > 0)
        tasks_after[row["task"]] += int(row["accepted_after_mock"] > 0)

    aggregate = {
        "bundles_repaired": len(rows),
        "confirmatory_present_failures_before": sum(row["confirmatory_present_failures_before"] for row in rows),
        "confirmatory_present_failures_after_mock": sum(row["confirmatory_present_failures_after_mock"] for row in rows),
        "confirmatory_ci_failures_before": sum(row["confirmatory_ci_failures_before"] for row in rows),
        "confirmatory_ci_failures_after_mock": sum(row["confirmatory_ci_failures_after_mock"] for row in rows),
        "accepted_before_total": sum(row["accepted_before"] for row in rows),
        "accepted_after_mock_total": sum(row["accepted_after_mock"] for row in rows),
        "tasks_with_any_mock_accepted_after": sorted({row["task"] for row in rows if row["accepted_after_mock"] > 0}),
    }

    payload = {
        "generated_by": "main/zero_task_confirmatory_repair.py",
        "aggregate": aggregate,
        "bundles": rows,
        "rows": rows,
        "warning": "Engineering rehearsal only. Mock-mode accepted counts do NOT change released headline numbers and must not be cited as scientific evidence.",
        "fast_stat_budget": {"bootstrap_resamples": 256, "permutation_iterations": 256},
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Zero-Task Confirmatory Repair (Mock Rehearsal)",
        "",
        payload["warning"],
        "",
        f"- Bundles rebuilt in mock mode: **{aggregate['bundles_repaired']}**",
        f"- confirmatory_present failures before: **{aggregate['confirmatory_present_failures_before']}**",
        f"- confirmatory_present failures after mock repair: **{aggregate['confirmatory_present_failures_after_mock']}**",
        f"- confirmatory_ci failures before: **{aggregate['confirmatory_ci_failures_before']}**",
        f"- confirmatory_ci failures after mock repair: **{aggregate['confirmatory_ci_failures_after_mock']}**",
        f"- Tasks with any mock accepted claims after repair: **{', '.join(aggregate['tasks_with_any_mock_accepted_after']) or 'none'}**",
        "",
        "## Per-bundle summary",
        "",
        "| Bundle | Task | Model | Accepted before | Accepted after (mock) | confirmatory_present before | confirmatory_present after (mock) |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['bundle']}` | `{row['task']}` | `{row['model']}` | {row['accepted_before']} | {row['accepted_after_mock']} | "
            f"{row['confirmatory_present_failures_before']} | {row['confirmatory_present_failures_after_mock']} |"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.append(
        "If confirmatory-stage failures disappear in these repaired mock bundles, the remaining breadth problem is no longer a pure plumbing issue. "
        "That means the next honest step is real-model discovery / Stage-2 execution, not more evaluator surgery."
    )
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n")
    print(str(OUT_JSON))


if __name__ == "__main__":
    from collections import defaultdict
    main()
