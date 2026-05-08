from __future__ import annotations

from pathlib import Path

from main.reproducibility_audit import audit_commands, compute_audit_status, _sanitize_text

def test_compute_audit_status_passes_when_commands_and_outputs_are_clean(tmp_path: Path) -> None:
    output_path = tmp_path / "artifact.json"
    output_path.write_text("{}\n")

    status = compute_audit_status(
        [{"command": ["python", "ok.py"], "returncode": 0}],
        {"artifact": str(output_path)},
        run_started_at=output_path.stat().st_mtime - 1,
    )

    assert status["status"] == "pass"
    assert status["failed_commands"] == []
    assert status["missing_outputs"] == []
    assert status["stale_outputs"] == []

def test_compute_audit_status_fails_on_missing_output(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.json"

    status = compute_audit_status(
        [{"command": ["python", "ok.py"], "returncode": 0}],
        {"missing": str(missing_path)},
    )

    assert status["status"] == "fail"
    assert status["failed_commands"] == []
    assert status["missing_outputs"] == [_sanitize_text(str(missing_path))]

def test_compute_audit_status_fails_on_stale_output(tmp_path: Path) -> None:
    output_path = tmp_path / "artifact.json"
    output_path.write_text("{}\n")

    status = compute_audit_status(
        [{"command": ["python", "ok.py"], "returncode": 0}],
        {"artifact": str(output_path)},
        run_started_at=output_path.stat().st_mtime + 1,
    )

    assert status["status"] == "fail"
    assert status["missing_outputs"] == []
    assert status["stale_outputs"] == [_sanitize_text(str(output_path))]

def test_audit_command_contract_covers_current_release_surface() -> None:
    commands = audit_commands()
    rendered = [" ".join(command) for command in commands]

    assert len(commands) == 43
    assert any("main/zero_task_real_repair.py --summarize-existing" in command for command in rendered)
    assert any("main/field_level_findings.py" in command for command in rendered)
    assert any("main/breadth_gap_analysis.py" in command for command in rendered)
    assert any("main/community_value_summary.py" in command for command in rendered)
    assert any("main/figure_inputs.py" in command for command in rendered)
    assert any("main/co_failure_matrix.py" in command for command in rendered)
    assert any("main/transfer_near_miss_analysis.py" in command for command in rendered)
    assert any("main/stress_test_agnostic.py" in command for command in rendered)
    assert any("stress_test_agnostic_fresh_release_grade.json" in command for command in rendered)
    assert any("main/prompt_variant_validity_audit.py" in command for command in rendered)
    assert any("main/prompt_variant_repair_rerun.py --summarize-existing" in command for command in rendered)
    assert any("main/prompt_holdout_high_power_rerun.py --examples-per-cell 40 --summarize-existing" in command for command in rendered)
    assert any("main/paired_bundle_cross_model_replication.py --bundle-root main/output/prompt_variant_repair" in command for command in rendered)
    assert any("main/prompt_repair_same_family_transfer.py --summarize-existing" in command for command in rendered)
    assert any("main/transfer_breadth_candidate_table.py" in command for command in rendered)
    assert any("main/docstring_method_sensitivity_explorer.py" in command for command in rendered)
    assert any("main/docstring_distributed_repair.py --summarize-existing" in command for command in rendered)
    assert any("main/contract_hardening_v1.py" in command for command in rendered)
    assert any("main/run_independent_agnostic_stress.py" in command for command in rendered)
    assert any("main/contract_migration_decision.py" in command for command in rendered)
    assert any("main/run_holdout.py" in command for command in rendered)
    assert any("main/direct_blocker_closure_report.py" in command for command in rendered)
    assert any("main/repo_integrity_sweep.py" in command for command in rendered)
    assert any("tools/check_release_overclaims.py" in command for command in rendered)
    assert rendered[-1].endswith("tools/check_headline_numbers.py")
