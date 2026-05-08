"""Regression tests for the F-017 and F-019 diagnostic scripts.

These scripts are standalone (they live under ``main/`` not the
evaluator package), but they depend on the evaluator's
``_bundle_analysis.iter_claim_rows`` contract — specifically the
``task`` key on each row and the ``failed_checks`` list. A refactor
of that contract would silently break these diagnostics, so we
exercise them here against the released bundles to catch schema
drift early.

The tests are deliberately lightweight: they run the scripts as
subprocesses, assert exit code 0, and assert that the emitted JSON
matches the script's documented schema. They do NOT re-assert
specific numeric values — those are the job of
``tools/check_headline_numbers.py``.
"""

from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
REPRO_DIR = REPO_ROOT / "main" / "output" / "repro"


def _require_released_bundles() -> None:
    """Skip the test cleanly if the released bundles aren't present.

    The evaluator package is distributable on its own; a consumer
    who installs just the package won't have ``main/output/...``.
    In that environment these scripts are not meaningful.
    """
    multitask = REPO_ROOT / "main" / "output" / "real_multi_task"
    if not multitask.exists():
        pytest.skip("released bundles not present; skipping diagnostic-script regression")


def _run(script: str) -> None:
    """Run a script at ``REPO_ROOT/main/<script>`` and fail fast on error.

    Stdout/stderr are captured and included in the failure message so
    a broken diagnostic in CI is debuggable from the test log alone.
    """
    path = REPO_ROOT / "main" / script
    assert path.exists(), f"diagnostic script missing: {path}"
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"{script} failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def _run_with_args(script: str, *args: str) -> None:
    path = REPO_ROOT / "main" / script
    assert path.exists(), f"diagnostic script missing: {path}"
    result = subprocess.run(
        [sys.executable, str(path), *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"{script} {' '.join(args)} failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_zero_task_real_repair_existing_summary_is_cached_only() -> None:
    _require_released_bundles()
    _run_with_args("zero_task_real_repair.py", "--summarize-existing")

    out = REPRO_DIR / "zero_task_real_repair.json"
    assert out.exists(), f"expected output not written: {out}"
    payload = json.loads(out.read_text())
    assert payload.get("generated_by") == "main/zero_task_real_repair.py"
    assert "superseded by these reruns" in payload.get("release_status", "")
    assert isinstance(payload.get("rows"), list)
    assert isinstance(payload.get("aggregate"), dict)

    aggregate = payload["aggregate"]
    assert aggregate["bundles_run"] == len(payload["rows"])
    assert aggregate["accepted_after_real_total"] >= aggregate["accepted_before_total"]
    assert isinstance(aggregate.get("tasks_with_any_real_accept_after"), list)


def test_docstring_distributed_repair_existing_summary_is_cached_only() -> None:
    _require_released_bundles()
    _run_with_args("docstring_distributed_repair.py", "--summarize-existing")

    out = REPRO_DIR / "docstring_distributed_repair.json"
    assert out.exists(), f"expected output not written: {out}"
    payload = json.loads(out.read_text())
    assert payload.get("generated_by") == "main/docstring_distributed_repair.py"
    assert "diagnostic real repair" in payload.get("status", "")
    assert isinstance(payload.get("rows"), list)
    assert isinstance(payload.get("aggregate"), dict)

    aggregate = payload["aggregate"]
    assert aggregate["bundles_run"] == len(payload["rows"])
    assert isinstance(aggregate.get("tasks_with_any_real_accept_after"), list)
    assert isinstance(aggregate.get("gate_failures_after_real"), dict)


def test_zero_task_gate_breakdown_runs_and_emits_expected_schema() -> None:
    _require_released_bundles()
    _run("zero_task_gate_breakdown.py")

    out = REPRO_DIR / "zero_task_gate_breakdown.json"
    assert out.exists(), f"expected output not written: {out}"
    payload = json.loads(out.read_text())

    # Schema envelope.
    assert payload.get("schema_version") == 2
    assert payload.get("generated_by") == "main/zero_task_gate_breakdown.py"
    assert isinstance(payload.get("zero_task_set"), list)
    assert isinstance(payload.get("per_task"), dict)
    assert isinstance(payload.get("aggregate"), dict)
    assert isinstance(payload.get("task_acceptance_counts"), dict)
    assert isinstance(payload.get("interpretation_notes"), list)
    assert set(payload["zero_task_set"]) == {
        task
        for task, counts in payload["task_acceptance_counts"].items()
        if int(counts.get("accepted", 0)) == 0
    }

    # Each per-task block carries the documented fields.
    required_fields = {
        "n_claims",
        "n_passed",
        "n_failed",
        "failed_gate_counts",
        "single_gate_only_count",
        "single_gate_only_by_gate",
        "multi_gate_count",
        "rejected_with_no_failed_gate",
        "top_failed_combinations",
    }
    for task in payload["zero_task_set"]:
        assert task in payload["per_task"], f"missing per_task block for {task}"
        block = payload["per_task"][task]
        missing = required_fields - set(block.keys())
        assert not missing, f"per_task[{task}] missing fields: {missing}"
        # The zero-task invariant: n_passed must be 0 for every task in
        # the dynamically-derived zero-task set.
        assert block["n_passed"] == 0, (
            f"{task} is in zero_task_set but has {block['n_passed']} accepted claims"
        )
        assert block["n_failed"] + block["n_passed"] == block["n_claims"]
        assert payload["task_acceptance_counts"][task]["accepted"] == 0

    # Aggregate invariants.
    agg = payload["aggregate"]
    assert agg["n_claims"] == sum(payload["per_task"][t]["n_claims"] for t in payload["zero_task_set"])
    assert agg["single_gate_only_count"] + agg["multi_gate_count"] + agg["rejected_with_no_failed_gate"] == agg["n_failed"]


def test_transfer_failure_breakdown_runs_and_emits_expected_schema() -> None:
    _require_released_bundles()
    transfer_summary = REPRO_DIR / "transfer_results_summary.json"
    if not transfer_summary.exists():
        pytest.skip("transfer_results_summary.json not generated; skipping")
    _run("transfer_failure_breakdown.py")

    out = REPRO_DIR / "transfer_failure_breakdown.json"
    assert out.exists(), f"expected output not written: {out}"
    payload = json.loads(out.read_text())

    # Schema envelope (bumped to v2 in this PR).
    assert payload.get("schema_version") == 2
    assert payload.get("generated_by") == "main/transfer_failure_breakdown.py"
    assert isinstance(payload.get("bucket_counts"), dict)
    for bucket in (
        "wrong_direction",
        "below_floor_correct_direction",
        "zero_or_missing",
        "passed",
        "other",
    ):
        assert bucket in payload["bucket_counts"], f"missing bucket: {bucket}"

    # v2 aggregate blocks added for F-017 Path C.
    ratio = payload.get("transfer_to_source_magnitude_ratio")
    assert isinstance(ratio, dict)
    assert {"n", "median", "max", "description"} <= set(ratio.keys())

    stability = payload.get("within_source_bundle_stability_control")
    assert isinstance(stability, dict)
    assert {
        "threshold_cv_abs",
        "stable_source_claims",
        "unstable_source_claims",
        "insufficient_cells_claims",
        "median_cv_abs",
        "description",
    } <= set(stability.keys())
    # Stability bucket totals sum to n_cross_model_tested.
    assert (
        stability["stable_source_claims"]
        + stability["unstable_source_claims"]
        + stability["insufficient_cells_claims"]
    ) == payload["n_cross_model_tested"]

    # Per-claim rows carry the v2-added fields.
    assert isinstance(payload.get("claims"), list)
    assert payload["claims"], "no per-claim rows emitted"
    sample = payload["claims"][0]
    for field in (
        "bundle",
        "hypothesis_id",
        "transfer_effect",
        "source_sign",
        "source_effect_mean",
        "source_effect_stdev",
        "source_effect_cv_abs",
        "source_n_cells",
        "source_stability",
        "transfer_to_source_ratio",
        "failure_mode",
    ):
        assert field in sample, f"per-claim row missing field: {field}"


def test_transfer_breadth_candidate_table_runs_and_emits_expected_schema() -> None:
    _require_released_bundles()
    _run("transfer_breadth_candidate_table.py")

    out = REPRO_DIR / "transfer_breadth_candidate_table.json"
    assert out.exists(), f"expected output not written: {out}"
    payload = json.loads(out.read_text())

    assert payload.get("generated_by") == "main/transfer_breadth_candidate_table.py"
    assert payload.get("status") == "diagnostic_queue_only_not_transfer_evidence"
    assert isinstance(payload.get("summary"), dict)
    assert isinstance(payload.get("top_candidates"), list)
    assert isinstance(payload.get("all_candidates"), list)
    assert isinstance(payload.get("interpretation_notes"), list)

    summary = payload["summary"]
    for field in (
        "candidate_claims",
        "non_country_candidate_claims",
        "already_transfer_confirmed_claims",
        "blocked_missing_local_model_snapshot",
        "same_family_missing_eligible_rows",
    ):
        assert field in summary, f"summary missing field: {field}"
    assert summary["candidate_claims"] == len(payload["all_candidates"])
    if payload["top_candidates"]:
        sample = payload["top_candidates"][0]
        for field in (
            "bundle",
            "hypothesis_id",
            "task",
            "priority_score",
            "priority_reasons",
            "current_transfer_status",
            "same_family_status",
            "same_family_eligible_claim_ids_missing_rows",
            "same_family_transfer_passed_claim_ids",
        ):
            assert field in sample, f"candidate row missing field: {field}"


def test_docstring_method_sensitivity_explorer_runs_and_emits_expected_schema() -> None:
    _require_released_bundles()
    _run("docstring_method_sensitivity_explorer.py")

    out = REPRO_DIR / "docstring_method_sensitivity_explorer.json"
    assert out.exists(), f"expected output not written: {out}"
    payload = json.loads(out.read_text())

    assert payload.get("generated_by") == "main/docstring_method_sensitivity_explorer.py"
    assert payload.get("status") == "diagnostic_queue_only_not_new_model_evidence"
    assert isinstance(payload.get("summary"), dict)
    assert isinstance(payload.get("ranked_claims"), list)
    assert isinstance(payload.get("recommended_program"), list)

    summary = payload["summary"]
    for field in (
        "docstring_method_sensitivity_failed_claims",
        "single_gate_only_method_sensitivity",
        "diagnosis_counts",
        "distributed_repair_accepted_claims",
        "distributed_repair_gate_failures",
    ):
        assert field in summary, f"summary missing field: {field}"
    assert summary["docstring_method_sensitivity_failed_claims"] == len(payload["ranked_claims"])
    if payload["ranked_claims"]:
        sample = payload["ranked_claims"][0]
        for field in (
            "bundle",
            "model",
            "hypothesis_id",
            "diagnosis",
            "repair_priority_score",
            "recommended_next_experiment",
        ):
            assert field in sample, f"ranked claim missing field: {field}"


def test_independent_agnostic_rehearsal_runner_emits_claim_boundary(tmp_path: Path) -> None:
    _require_released_bundles()
    out_json = tmp_path / "independent_agnostic_current.json"
    out_md = tmp_path / "independent_agnostic_current.md"
    _run_with_args(
        "run_independent_agnostic_stress.py",
        "--rehearsal-from-cached",
        "--contract",
        "current",
        "--json-out",
        str(out_json),
        "--md-out",
        str(out_md),
    )

    payload = json.loads(out_json.read_text())
    assert payload.get("generated_by") == "main/run_independent_agnostic_stress.py"
    assert payload.get("status") == "benchmark_authored_rehearsal_not_independent_evidence"
    assert payload.get("claim_boundary")
    stress = payload.get("stress_result")
    assert isinstance(stress, dict)
    assert stress["negatives"] > 0
    assert "false_accept_rate_ci95" in stress
    assert "not independent Goodhart evidence" in out_md.read_text()


def test_external_evidence_preflight_reports_playbook_and_zero_external_counts() -> None:
    _run("external_evidence_preflight.py")

    out = REPRO_DIR / "external_evidence_preflight.json"
    assert out.exists(), f"expected output not written: {out}"
    payload = json.loads(out.read_text())

    assert payload.get("generated_by") == "main/external_evidence_preflight.py"
    readiness = payload.get("author_path_readiness")
    assert isinstance(readiness, dict)
    assert readiness["package_tool_present"] is True
    assert readiness["preflight_tool_present"] is True
    assert readiness["quickstart_present"] is True
    assert readiness["external_evidence_playbook_present"] is True
    assert payload["external_blinded"]["n_submissions"] == 0
    assert payload["status"]["counts_as_external_evidence_now"] is False
    assert any("independent_researcher_external_evidence_playbook.md" in action for action in payload["next_actions"])


def test_independent_agnostic_runner_scores_scorable_negative_set(tmp_path: Path) -> None:
    _require_released_bundles()
    bundle_dir = REPO_ROOT / "main" / "output" / "real_multi_task" / "ioi_v0_gpt2-small"
    hypothesis = json.loads((bundle_dir / "hypothesis.jsonl").read_text().splitlines()[0])
    evidence = json.loads((bundle_dir / "evaluation_result.json").read_text())
    raw_cells = evidence["hypothesis_results"][0]["raw_cells"]
    negative_set = tmp_path / "negative_set.jsonl"
    negative_set.write_text(
        json.dumps(
            {
                "negative_id": "external_neg_000001",
                "task_id": "ioi_v0",
                "model_id": "gpt2-small",
                "claim_text": "A plausible but deliberately unsupported negative mechanism for intake scoring.",
                "candidate_components": hypothesis["candidate_components"],
                "predicted_effect_direction": hypothesis["predicted_effect_direction"],
                "predicted_min_effect": hypothesis["predicted_min_effect"],
                "predicted_specificity_ratio": hypothesis["predicted_specificity_ratio"],
                "author_slice": "scorable_fixture",
                "visibility": {
                    "saw_public_bundles": True,
                    "saw_gate_taxonomy": False,
                    "saw_v1_thresholds": False,
                    "received_scoring_feedback": False,
                },
                "evidence_cells": raw_cells,
            }
        )
        + "\n"
    )
    out_json = tmp_path / "independent_agnostic_scored.json"
    out_md = tmp_path / "independent_agnostic_scored.md"

    _run_with_args(
        "run_independent_agnostic_stress.py",
        "--negative-set",
        str(negative_set),
        "--contract",
        "current",
        "--json-out",
        str(out_json),
        "--md-out",
        str(out_md),
    )

    payload = json.loads(out_json.read_text())
    assert payload["status"] == "scorable_negative_set_scored_attestation_required"
    assert payload["scoring_available"] is True
    assert payload["negative_set_validation"]["scoring_ready"] is True
    assert payload["stress_result"]["negatives"] == 1
    assert payload["stress_result"]["false_accepts"] is not None
    assert "external provenance or custodian attestation" in out_md.read_text()


def test_prompt_variant_validity_audit_reports_schema() -> None:
    _require_released_bundles()
    _run("prompt_variant_validity_audit.py")

    payload = json.loads((REPRO_DIR / "prompt_variant_validity_audit.json").read_text())
    assert payload.get("generated_by") == "main/prompt_variant_validity_audit.py"
    assert payload.get("status") in {
        "pass",
        "warn_legacy_unsupported_prompt_variants_canonical_clean",
        "warn_unsupported_prompt_variants_in_existing_artifacts",
    }
    assert isinstance(payload.get("records"), list)
    assert isinstance(payload.get("canonical_records"), list)
    assert "canonical_files_with_unsupported_prompt_variants" in payload
    assert "canonical_affected_accepted_claims" in payload
    for row in payload["records"]:
        for field in (
            "bundle",
            "path",
            "task_id",
            "model_id",
            "used_prompt_variants",
            "supported_prompt_variants",
            "unsupported_prompt_variants",
            "accepted_claims_in_bundle",
        ):
            assert field in row, f"prompt audit row missing field: {field}"


def test_high_power_prompt_holdout_summary_marks_partial_outputs(tmp_path: Path) -> None:
    script_path = REPO_ROOT / "main" / "prompt_holdout_high_power_rerun.py"
    spec = importlib.util.spec_from_file_location("prompt_holdout_high_power_rerun", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    module.OUT_JSON = tmp_path / "summary.json"
    module.OUT_MD = tmp_path / "summary.md"
    module._write_summary([], planned_bundles=2, examples_per_cell=100)

    payload = json.loads(module.OUT_JSON.read_text())
    assert payload["completion_status"] == "partial"
    assert "partial" in payload["status"]
    assert "- Completion status: **partial**" in module.OUT_MD.read_text()


def test_contract_migration_decision_defers_without_independent_evidence(tmp_path: Path) -> None:
    _require_released_bundles()
    current_json = tmp_path / "current.json"
    current_md = tmp_path / "current.md"
    candidate_json = tmp_path / "candidate.json"
    candidate_md = tmp_path / "candidate.md"
    decision_json = tmp_path / "decision.json"
    decision_md = tmp_path / "decision.md"

    _run_with_args(
        "run_independent_agnostic_stress.py",
        "--rehearsal-from-cached",
        "--contract",
        "current",
        "--json-out",
        str(current_json),
        "--md-out",
        str(current_md),
    )
    _run_with_args(
        "run_independent_agnostic_stress.py",
        "--rehearsal-from-cached",
        "--contract",
        "contract_hardening_v1",
        "--json-out",
        str(candidate_json),
        "--md-out",
        str(candidate_md),
    )
    _run_with_args(
        "contract_migration_decision.py",
        "--current",
        str(current_json),
        "--candidate",
        str(candidate_json),
        "--retention",
        str(REPRO_DIR / "contract_hardening_v1_summary.json"),
        "--out-md",
        str(decision_md),
        "--out-json",
        str(decision_json),
        "--decision",
        "defer",
    )

    payload = json.loads(decision_json.read_text())
    assert payload.get("generated_by") == "main/contract_migration_decision.py"
    assert payload["decision_status"] == "deferred_pending_external_validation"
    assert payload["criteria"]["independent_evidence"] is False
    assert payload["adoptable_under_preregistered_criteria"] is False
    assert "Rehearsal or benchmark-authored stress is not independent validation" in decision_md.read_text()
