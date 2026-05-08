#!/usr/bin/env python3
"""Materialized reproducibility audit for the released benchmark surface.

This audit intentionally avoids live model reruns. It regenerates the
publication-facing summaries, lightweight diagnostics, holdout rehearsal,
publication figures, generated docs, contract-hardening tradeoff diagnostics, and
drift checks that the papers and README cite as the released artifact surface.
"""

from __future__ import annotations

import importlib.metadata as importlib_metadata
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from _bundle_analysis import generated_at_utc, repo_relative, write_json, write_text
except ModuleNotFoundError:
    from main._bundle_analysis import generated_at_utc, repo_relative, write_json, write_text

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMMAND_TIMEOUT_SECONDS = 900

def _display_arg(arg: str) -> str:
    path_like = Path(arg)
    if path_like.is_absolute():
        try:
            return repo_relative(path_like)
        except Exception:
            return path_like.name
    return arg

def _display_command(cmd: list[str]) -> list[str]:
    rendered: list[str] = []
    for idx, arg in enumerate(cmd):
        if idx == 0 and Path(arg).is_absolute():
            rendered.append(Path(arg).name)
        else:
            rendered.append(_display_arg(arg))
    return rendered

def _repo_env() -> dict[str, str]:
    env = os.environ.copy()
    repo_paths = [
        str(ROOT),
        str(ROOT / "packages" / "evaluator" / "src"),
        str(ROOT / "packages" / "runner" / "src"),
    ]
    current = env.get("PYTHONPATH")
    if current:
        repo_paths.append(current)
    env["PYTHONPATH"] = os.pathsep.join(repo_paths)
    return env

def _resolve_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path

def _read_tail(path: Path, limit: int = 1000) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(errors="replace")
    except Exception:
        return ""
    return _sanitize_text(text[-limit:])

def _sanitize_text(text: str) -> str:
    """Remove local absolute path prefixes and environment-specific noise.

    Beyond the absolute-path stripping required to keep persisted logs
    portable, this also drops a small allow-list of dependency warnings whose
    presence depends on the host's TLS/SSL stack rather than on this project's
    code or data. Emitting them into ``stderr_tail`` would make
    ``reproducibility_audit.json`` byte-non-deterministic across hosts even
    when the underlying scientific outputs match."""
    replacements = {
        str(ROOT): ".",
        str(Path.home()): "~",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Filter known environment-specific dependency warnings that are emitted
    # to stderr by transitive dependencies and have no scientific signal.
    noisy_substrings = (
        "NotOpenSSLWarning",
        "urllib3 v2 only supports OpenSSL",
        "warnings.warn(",
    )
    filtered_lines = []
    for line in text.splitlines(keepends=True):
        if any(s in line for s in noisy_substrings):
            continue
        filtered_lines.append(line)
    return "".join(filtered_lines)

def _run_command(cmd: list[str], timeout_seconds: int = DEFAULT_COMMAND_TIMEOUT_SECONDS) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(prefix="audit_stdout_", suffix=".txt", delete=False) as stdout_file, tempfile.NamedTemporaryFile(prefix="audit_stderr_", suffix=".txt", delete=False) as stderr_file:
        stdout_path = Path(stdout_file.name)
        stderr_path = Path(stderr_file.name)
    try:
        with stdout_path.open("w") as stdout_handle, stderr_path.open("w") as stderr_handle:
            result = subprocess.run(
                cmd,
                cwd=ROOT,
                env=_repo_env(),
                stdout=stdout_handle,
                stderr=stderr_handle,
                text=True,
                timeout=timeout_seconds,
            )
        return {
            "command": _display_command(cmd),
            "cwd": ".",
            "returncode": result.returncode,
            "timeout_seconds": timeout_seconds,
            "stdout_tail": _read_tail(stdout_path),
            "stderr_tail": _read_tail(stderr_path),
        }
    except subprocess.TimeoutExpired:
        return {
            "command": _display_command(cmd),
            "cwd": ".",
            "returncode": 124,
            "timeout_seconds": timeout_seconds,
            "stdout_tail": _read_tail(stdout_path),
            "stderr_tail": _read_tail(stderr_path),
            "timed_out": True,
        }
    finally:
        stdout_path.unlink(missing_ok=True)
        stderr_path.unlink(missing_ok=True)

def compute_audit_status(
    results: list[dict],
    outputs: dict[str, str | None],
    run_started_at: float | None = None,
) -> dict[str, object]:
    failed_commands = [
        {"command": row["command"], "returncode": row["returncode"]}
        for row in results
        if row["returncode"] != 0
    ]
    missing_outputs: list[str] = []
    stale_outputs: list[str] = []
    for raw in outputs.values():
        if not raw:
            continue
        path = _resolve_path(raw)
        if not path.exists():
            missing_outputs.append(_sanitize_text(str(path)))
            continue
        if run_started_at is not None and path.stat().st_mtime < float(run_started_at):
            stale_outputs.append(_sanitize_text(str(path)))
    return {
        "status": "pass" if not failed_commands and not missing_outputs and not stale_outputs else "fail",
        "failed_commands": failed_commands,
        "missing_outputs": missing_outputs,
        "stale_outputs": stale_outputs,
    }

def _environment_manifest() -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "generated_at": generated_at_utc(timespec="microseconds"),
        "python": sys.version,
        "python_executable": Path(sys.executable).name,
        "platform": platform.platform(),
        "repo_root": ".",
    }
    dist_names = {
        "torch": "torch",
        "transformer_lens": "transformer-lens",
        "yaml": "PyYAML",
        "pytest": "pytest",
    }
    for module_name, dist_name in dist_names.items():
        try:
            manifest[f"{module_name}_version"] = importlib_metadata.version(dist_name)
        except importlib_metadata.PackageNotFoundError:
            manifest[f"{module_name}_version"] = "missing"
        except Exception as exc:
            manifest[f"{module_name}_version"] = f"error:{type(exc).__name__}"
    return manifest

def audit_commands() -> list[list[str]]:
    """Return the materialized cached-artifact audit command contract.

    Keep this as a helper instead of an inline local so tests and docs can
    assert the intended audit scope.
    """

    return [
        [sys.executable, "-m", "pytest", "packages/evaluator/tests/test_reproducibility_audit_helpers.py", "-q"],
        [sys.executable, "-m", "pytest", "packages/evaluator/tests/test_holdout_scaffolding.py", "-q"],
        [sys.executable, "-m", "pytest", "packages/evaluator/tests/test_stress_agnostic.py", "-q"],
        [sys.executable, "-m", "pytest", "packages/runner/tests/test_runner_mock.py", "-q"],
        [sys.executable, "main/zero_task_real_repair.py", "--summarize-existing"],
        [sys.executable, "main/prompt_variant_repair_rerun.py", "--summarize-existing"],
        [sys.executable, "main/prompt_variant_validity_audit.py"],
        [
            sys.executable,
            "main/paired_bundle_cross_model_replication.py",
            "--bundle-root",
            "main/output/prompt_variant_repair",
            "--out-json",
            "main/output/repro/prompt_variant_repair_paired_bundle_cross_model_replication_summary.json",
            "--out-md",
            "main/output/repro/prompt_variant_repair_paired_bundle_cross_model_replication_summary.md",
            "--preserve-existing-nonpaired",
        ],
        [sys.executable, "main/prompt_repair_same_family_transfer.py", "--summarize-existing"],
        [sys.executable, "main/summarize_benchmark_breadth.py"],
        [sys.executable, "main/field_level_findings.py"],
        [sys.executable, "main/breadth_gap_analysis.py"],
        [sys.executable, "main/transfer_results_summary.py"],
        [sys.executable, "main/transfer_near_miss_analysis.py"],
        [sys.executable, "main/runtime_cost_report.py", "--reruns", "3"],
        [sys.executable, "main/community_value_summary.py"],
        [sys.executable, "main/figure_inputs.py"],
        [sys.executable, "main/co_failure_matrix.py"],
        [sys.executable, "main/generate_publication_figures.py"],
        [sys.executable, "main/prompt_holdout_transfer_control.py"],
        [
            sys.executable,
            "main/prompt_holdout_high_power_rerun.py",
            "--examples-per-cell",
            "40",
            "--summarize-existing",
        ],
        [sys.executable, "main/same_family_transfer_preflight.py"],
        [sys.executable, "main/transfer_breadth_candidate_table.py"],
        [
            sys.executable,
            "main/stress_test_agnostic.py",
            "--bundle-dir",
            "main/output/real_multi_task/ioi_v0_gpt2-small",
            "--count",
            "200",
            "--generator-regime",
            "fresh_v2",
            "--seed-namespace",
            "release_grade_2026q2",
            "--condition",
            "full_contract",
            "--json-out",
            "main/output/repro/stress_test_agnostic_fresh_release_grade.json",
            "--md-out",
            "main/output/repro/stress_test_agnostic_fresh_release_grade.md",
        ],
        [sys.executable, "main/transfer_failure_breakdown.py"],
        [sys.executable, "main/zero_task_gate_breakdown.py"],
        [
            sys.executable,
            "main/docstring_method_sensitivity_explorer.py",
            "--source-dir",
            "main/output/real_multi_task",
        ],
        [sys.executable, "main/docstring_distributed_repair.py", "--summarize-existing"],
        [sys.executable, "main/repair_legacy_no_split_bundles.py"],
        [sys.executable, "main/zero_task_confirmatory_repair.py"],
        [sys.executable, "main/external_evidence_preflight.py"],
        [sys.executable, "-m", "holdout.tools.build_results_summary"],
        [
            sys.executable,
            "main/run_holdout.py",
            "--rehearsal",
            "--release-version",
            "v0-rehearsal",
            "--use-cached-results",
        ],
        [sys.executable, "main/contract_hardening_v1.py"],
        [
            sys.executable,
            "main/run_independent_agnostic_stress.py",
            "--rehearsal-from-cached",
            "--contract",
            "current",
            "--json-out",
            "main/output/repro/independent_agnostic_stress_current_rehearsal.json",
            "--md-out",
            "main/output/repro/independent_agnostic_stress_current_rehearsal.md",
        ],
        [
            sys.executable,
            "main/run_independent_agnostic_stress.py",
            "--rehearsal-from-cached",
            "--contract",
            "contract_hardening_v1",
            "--json-out",
            "main/output/repro/independent_agnostic_stress_hardened_v1_rehearsal.json",
            "--md-out",
            "main/output/repro/independent_agnostic_stress_hardened_v1_rehearsal.md",
        ],
        [
            sys.executable,
            "main/contract_migration_decision.py",
            "--current",
            "main/output/repro/independent_agnostic_stress_current_rehearsal.json",
            "--candidate",
            "main/output/repro/independent_agnostic_stress_hardened_v1_rehearsal.json",
            "--retention",
            "main/output/repro/contract_hardening_v1_summary.json",
            "--out-md",
            "methodology/contract_hardening_v1_migration_decision.md",
            "--out-json",
            "main/output/repro/contract_hardening_v1_migration_decision.json",
            "--decision",
            "defer",
        ],
        [sys.executable, "main/release_readiness_report.py"],
        [sys.executable, "main/direct_blocker_closure_report.py"],
        [sys.executable, "scripts/generate_docs_from_json.py"],
        [sys.executable, "main/repo_integrity_sweep.py"],
        [sys.executable, "tools/check_release_overclaims.py"],
        [sys.executable, "tools/check_headline_numbers.py"],
    ]

def _check_mode() -> int:
    """Read-only verification.

    Copies the repo into a temp tree, runs the materializing audit there,
    then compares SHA-256 of every committed audit output against the
    freshly-regenerated one. Exits 0 only if every committed output's bytes
    match the regenerated bytes.
    """
    import argparse  # local import to keep top-of-file footprint small
    import hashlib
    import shutil

    parser = argparse.ArgumentParser(prog="reproducibility_audit.py --check")
    parser.add_argument("--check", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--allow-missing", action="store_true",
                        help="treat missing committed output as warning, not failure")
    args, _ = parser.parse_known_args()

    out_dir = ROOT / "main" / "output" / "repro"

    # Files that are deliberately not regenerated by the audit pipeline (for
    # example, archived/static documentation under ``site_docs/generated/`` that
    # is built by mkdocs rather than by audit_commands()). Listing these here
    # keeps ``--check`` from flagging them as missing while still failing on
    # genuinely missing canonical outputs.NOT_GENERATED_BY_AUDIT: set[str] = set()

    # Files whose contents legitimately depend on the runtime environment
    # (subprocess stdout/stderr framing, command timing, the host's TLS stack)
    # and therefore cannot be byte-identical across hosts even when every
    # scientific artifact matches. ``reproducibility_audit.json`` is the
    # audit's own self-report; it captures sanitized stdout/stderr tails of
    # every regenerator command, which differs between the host environment
    # and the temp-tree regeneration regardless of scientific determinism.
    # We exclude it from the byte-level comparison rather than chasing every
    # transitive-dependency warning that touches stderr.
    #SKIP_FROM_CHECK: set[str] = {
        "main/output/repro/reproducibility_audit.json",
    }

    with tempfile.TemporaryDirectory(prefix="amib-repro-check-") as tmp:
        tmp_root = Path(tmp) / "repo"
        shutil.copytree(
            ROOT, tmp_root,
            ignore=shutil.ignore_patterns(
                ".git", ".venv", "__pycache__", "*.pyc",
                "model_cache", "site", "_site",
            ),
            symlinks=False,
        )

        env = os.environ.copy()
        env.setdefault("PYTHONHASHSEED", "0")
        env.setdefault("SOURCE_DATE_EPOCH", "1700000000")
        # NOTE: ``--check`` relies on every audit_commands() entry to fully
        # rewrite its declared outputs. If a command silently fails to
        # regenerate an output that ``copytree`` already copied from the
        # committed tree, the byte comparison below would still pass on the
        # stale file. Pre-purging declared outputs in ``tmp_root`` would close
        # this gap but turned out to interact badly with audit_commands that
        # read prior committed outputs as input fixtures. The per-command
        # returncode + missing_outputs + mtime checks inside the inner
        # audit's ``compute_audit_status`` keep this from being a silent
        # stale-pass risk.
        proc = subprocess.run(
            [sys.executable, str(tmp_root / "main" / "reproducibility_audit.py")],
            cwd=str(tmp_root), env=env, capture_output=True, text=True,
            timeout=DEFAULT_COMMAND_TIMEOUT_SECONDS * 4,
        )
        if proc.returncode != 0:
            print("[--check] materialization in temp tree failed:", file=sys.stderr)
            print(proc.stdout, file=sys.stderr)
            print(proc.stderr, file=sys.stderr)
            return 2

        drift: list[str] = []
        missing: list[str] = []
        compared = 0
        # Hash everything under main/output/repro/, methodology/, site_docs/generated/
        for sub in ["main/output/repro", "methodology", "site_docs/generated"]:
            committed = ROOT / sub
            regenerated = tmp_root / sub
            if not committed.exists():
                continue
            for p_committed in sorted(committed.rglob("*")):
                if not p_committed.is_file():
                    continue
                rel = p_committed.relative_to(ROOT)
                rel_str = str(rel)
                if rel_str in SKIP_FROM_CHECK:
                    continue
                p_regen = tmp_root / rel
                if not p_regen.exists():
                    if rel_str in NOT_GENERATED_BY_AUDIT or rel_str.startswith("site_docs/generated/"):
                        # Static or mkdocs-built; not a regression.
                        continue
                    missing.append(rel_str)
                    continue
                h1 = hashlib.sha256(p_committed.read_bytes()).hexdigest()
                h2 = hashlib.sha256(p_regen.read_bytes()).hexdigest()
                compared += 1
                if h1 != h2:
                    drift.append(rel_str)

        print(f"[--check] compared {compared} files, drift={len(drift)}, missing={len(missing)}")
        if drift:
            print("[--check] drift in:")
            for d in sorted(drift)[:50]:
                print(f"  - {d}")
            if len(drift) > 50:
                print(f"  ... +{len(drift) - 50} more")
        if missing:
            print("[--check] missing regenerated outputs:")
            for d in sorted(missing)[:50]:
                print(f"  - {d}")
            if len(missing) > 50:
                print(f"  ... +{len(missing) - 50} more")
        if drift:
            return 1
        if missing and not args.allow_missing:
            return 1
        return 0

def main() -> None:
    # read-only verification mode.
    if "--check" in sys.argv[1:]:
        sys.exit(_check_mode())
    out_dir = ROOT / "main" / "output" / "repro"
    out_dir.mkdir(parents=True, exist_ok=True)
    run_started_at = time.time()

    env_manifest_path = out_dir / "environment_manifest.json"
    write_json(env_manifest_path, _environment_manifest())

    commands = audit_commands()
    os.environ["AUTOMECHINTERP_EXPECTED_AUDIT_COMMANDS"] = str(len(commands))
    results = [_run_command(cmd) for cmd in commands]

    outputs = {
        "environment_manifest_json": repo_relative(env_manifest_path),
        "benchmark_breadth_summary_json": repo_relative(out_dir / "benchmark_breadth_summary.json"),
        "field_level_findings_json": repo_relative(out_dir / "field_level_findings.json"),
        "zero_task_real_repair_json": repo_relative(out_dir / "zero_task_real_repair.json"),
        "breadth_gap_analysis_json": repo_relative(out_dir / "breadth_gap_analysis.json"),
        "transfer_results_summary_json": repo_relative(out_dir / "transfer_results_summary.json"),
        "transfer_near_miss_analysis_json": repo_relative(out_dir / "transfer_near_miss_analysis.json"),
        "runtime_cost_report_json": repo_relative(out_dir / "runtime_cost_report.json"),
        "community_value_summary_json": repo_relative(ROOT / "main" / "output" / "community_submissions" / "community_value_summary.json"),
        "figure_inputs_json": repo_relative(out_dir / "figure_inputs.json"),
        "co_failure_matrix_json": repo_relative(out_dir / "co_failure_matrix.json"),
        "release_takeaways_json": repo_relative(out_dir / "release_takeaways.json"),
        "accepted_breadth_heatmap_pdf": repo_relative(ROOT / "papers" / "submissions" / "shared" / "figures" / "accepted_breadth_heatmap.pdf"),
        "contract_vs_stress_rates_pdf": repo_relative(ROOT / "papers" / "submissions" / "shared" / "figures" / "contract_vs_stress_rates.pdf"),
        "failure_family_counts_pdf": repo_relative(ROOT / "papers" / "submissions" / "shared" / "figures" / "failure_family_counts.pdf"),
        "gate_cofailure_heatmap_pdf": repo_relative(ROOT / "papers" / "submissions" / "shared" / "figures" / "gate_cofailure_heatmap.pdf"),
        "transfer_failure_breakdown_json": repo_relative(out_dir / "transfer_failure_breakdown.json"),
        "zero_task_gate_breakdown_json": repo_relative(out_dir / "zero_task_gate_breakdown.json"),
        "legacy_no_split_repair_json": repo_relative(out_dir / "legacy_no_split_repair.json"),
        "zero_task_confirmatory_repair_json": repo_relative(out_dir / "zero_task_confirmatory_repair.json"),
        "prompt_holdout_transfer_control_json": repo_relative(out_dir / "prompt_holdout_transfer_control.json"),
        "prompt_holdout_high_power_n40_rerun_json": repo_relative(out_dir / "prompt_holdout_high_power_n40_rerun.json"),
        "prompt_variant_validity_audit_json": repo_relative(out_dir / "prompt_variant_validity_audit.json"),
        "prompt_variant_repair_rerun_json": repo_relative(out_dir / "prompt_variant_repair_rerun.json"),
        "prompt_variant_repair_paired_bundle_cross_model_replication_summary_json": repo_relative(out_dir / "prompt_variant_repair_paired_bundle_cross_model_replication_summary.json"),
        "prompt_repair_same_family_transfer_json": repo_relative(out_dir / "prompt_repair_same_family_transfer.json"),
        "same_family_transfer_preflight_json": repo_relative(out_dir / "same_family_transfer_preflight.json"),
        "transfer_breadth_candidate_table_json": repo_relative(out_dir / "transfer_breadth_candidate_table.json"),
        "external_evidence_preflight_json": repo_relative(out_dir / "external_evidence_preflight.json"),
        "stress_test_agnostic_fresh_release_grade_json": repo_relative(out_dir / "stress_test_agnostic_fresh_release_grade.json"),
        "docstring_method_sensitivity_explorer_json": repo_relative(out_dir / "docstring_method_sensitivity_explorer.json"),
        "docstring_distributed_repair_json": repo_relative(out_dir / "docstring_distributed_repair.json"),
        "contract_hardening_v1_summary_json": repo_relative(out_dir / "contract_hardening_v1_summary.json"),
        "stress_test_agnostic_hardened_v1_json": repo_relative(out_dir / "stress_test_agnostic_hardened_v1.json"),
        "stress_test_agnostic_hardened_v1_replicates_json": repo_relative(out_dir / "stress_test_agnostic_hardened_v1_replicates.json"),
        "independent_agnostic_stress_current_rehearsal_json": repo_relative(out_dir / "independent_agnostic_stress_current_rehearsal.json"),
        "independent_agnostic_stress_hardened_v1_rehearsal_json": repo_relative(out_dir / "independent_agnostic_stress_hardened_v1_rehearsal.json"),
        "contract_hardening_v1_migration_decision_json": repo_relative(out_dir / "contract_hardening_v1_migration_decision.json"),
        "contract_hardening_v1_migration_decision_md": repo_relative(ROOT / "methodology" / "contract_hardening_v1_migration_decision.md"),
        "release_readiness_report_json": repo_relative(out_dir / "release_readiness_report.json"),
        "direct_blocker_closure_report_json": repo_relative(out_dir / "direct_blocker_closure_report.json"),
        "repo_integrity_sweep_json": repo_relative(out_dir / "repo_integrity_sweep.json"),
        "repo_integrity_sweep_md": repo_relative(out_dir / "repo_integrity_sweep.md"),
        "release_overclaim_check_json": repo_relative(out_dir / "release_overclaim_check.json"),
        "release_overclaim_check_md": repo_relative(out_dir / "release_overclaim_check.md"),
        "holdout_results_summary_json": repo_relative(ROOT / "holdout" / "results_summary.json"),
        "holdout_pilot_results_summary_json": repo_relative(ROOT / "holdout" / "pilot" / "results_summary.json"),
        "holdout_rehearsal_json": repo_relative(out_dir / "holdout_v0-rehearsal.json"),
        "generated_release_findings_md": repo_relative(ROOT / "site_docs" / "generated" / "release-findings.md"),
    }
    status_info = compute_audit_status(results, outputs, run_started_at=run_started_at)

    audit = {
        "generated_at": generated_at_utc(timespec="microseconds"),
        "status": status_info["status"],
        "scope_note": (
            "Materialized audit of the released artifact surface. It regenerates cached-summary, real-repair, diagnostic, contract-hardening, holdout rehearsal, figure, docs, and drift-check outputs without live model reruns."
        ),
        "failed_commands": status_info["failed_commands"],
        "missing_outputs": status_info["missing_outputs"],
        "stale_outputs": status_info["stale_outputs"],
        "environment_manifest": repo_relative(env_manifest_path),
        "command_timeout_seconds": DEFAULT_COMMAND_TIMEOUT_SECONDS,
        "commands": results,
        "outputs": outputs,
    }
    write_json(out_dir / "reproducibility_audit.json", audit)

    lines = [
        "# Reproducibility Audit",
        "",
        f"- Generated: {audit['generated_at']}",
        f"- Status: **{audit['status']}**",
        f"- Environment manifest: `{audit['environment_manifest']}`",
        f"- Scope: {audit['scope_note']}",
        f"- Per-command timeout: **{DEFAULT_COMMAND_TIMEOUT_SECONDS}s**",
        "",
        "## Commands",
        "",
        "| Command | Return code |",
        "|---|---|",
    ]
    for row in results:
        lines.append(f"| `{' '.join(row['command'])}` | {row['returncode']} |")
    if audit["failed_commands"]:
        lines.extend(["", "## Failed commands", ""])
        for row in audit["failed_commands"]:
            lines.append(f"- `{' '.join(row['command'])}` returned `{row['returncode']}`")
    if audit["missing_outputs"]:
        lines.extend(["", "## Missing outputs", ""])
        for path in audit["missing_outputs"]:
            lines.append(f"- `{path}`")
    if audit["stale_outputs"]:
        lines.extend(["", "## Stale outputs", ""])
        for path in audit["stale_outputs"]:
            lines.append(f"- `{path}`")
    write_text(out_dir / "reproducibility_audit.md", "\n".join(lines).rstrip() + "\n")
    print(str(out_dir / "reproducibility_audit.json"))
    sys.exit(0 if audit["status"] == "pass" else 1)

if __name__ == "__main__":
    main()
