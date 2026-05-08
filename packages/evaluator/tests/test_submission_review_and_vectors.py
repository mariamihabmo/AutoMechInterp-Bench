from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from automechinterp_evaluator.cli import build_parser
from automechinterp_evaluator.evaluator import evaluate_bundle

# Local conftest helper; use a path-tolerant import to avoid collision with
# packages/runner/tests/conftest.py when both test trees are collected together.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_evaluator_tests_conftest", Path(__file__).resolve().parent / "conftest.py"
)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
sync_hashes = _mod.sync_hashes


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def test_evaluator_emits_gate_outcomes(bundle_dir: Path) -> None:
    result = evaluate_bundle(bundle_dir)
    claim = result["claim_reports"][0]
    assert "gate_outcomes" in claim
    assert claim["gate_outcomes"]["cross_model_transfer"] == "not_evaluated"
    assert claim["gate_outcomes"]["causal_effect"] in {"pass", "fail"}


def test_cross_model_transfer_uses_any_passing_target_without_row_order_overwrite(bundle_dir: Path) -> None:
    (bundle_dir / "cross_model_results.json").write_text(
        json.dumps(
            [
                {
                    "hypothesis_id": "h_ioi_name_movers",
                    "transfer_model": "failing-target",
                    "transfer_effect": -0.20,
                },
                {
                    "hypothesis_id": "h_ioi_name_movers",
                    "transfer_model": "passing-target",
                    "transfer_effect": 0.20,
                },
            ],
            indent=2,
        )
        + "\n"
    )
    # cross_model_results.json must be in the manifest
    # hash chain; refresh after writing the file.
    sync_hashes(bundle_dir)

    result = evaluate_bundle(bundle_dir)
    claim = result["claim_reports"][0]

    assert claim["checks"]["cross_model_transfer"] is True
    assert claim["metrics"]["cross_model_transfer_effect"] == 0.20
    assert claim["metrics"]["cross_model_transfer_model"] == "passing-target"
    assert claim["metrics"]["cross_model_transfer_evaluated_models"] == [
        "failing-target",
        "passing-target",
    ]
    assert claim["metrics"]["cross_model_transfer_passed_models"] == ["passing-target"]


def test_cli_submission_review(bundle_dir: Path, tmp_path: Path) -> None:
    parser = build_parser()
    out_json = tmp_path / "submission_review.json"
    out_md = tmp_path / "submission_review.md"
    args = parser.parse_args(
        [
            "submission-review",
            "--bundle",
            str(bundle_dir),
            "--reruns",
            "2",
            "--output-json",
            str(out_json),
            "--output-md",
            str(out_md),
        ]
    )
    rc = args.func(args)
    assert rc == 0
    payload = json.loads(out_json.read_text())
    assert payload["reruns_completed"] == 2
    assert "claim_actions" in payload
    assert "Deterministic:" in out_md.read_text()


def test_cli_module_entrypoint_displays_help() -> None:
    env = dict(os.environ)
    src = str(PACKAGE_ROOT / "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "automechinterp_evaluator.cli", "--help"],
        cwd=str(PACKAGE_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "submission-review" in result.stdout


def test_cli_reference_vectors(tmp_path: Path) -> None:
    parser = build_parser()
    out_dir = tmp_path / "vectors"
    args = parser.parse_args(["reference-vectors", "--output-dir", str(out_dir)])
    rc = args.func(args)
    assert rc == 0
    payload = json.loads((out_dir / "reference_vectors.json").read_text())
    vector_ids = {row["vector_id"] for row in payload["vectors"]}
    assert "single_model_confirmed" in vector_ids
    assert "cross_model_confirmed" in vector_ids


def test_cli_reviewer_kit(bundle_dir: Path, tmp_path: Path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "reviewer-kit",
            "--bundle",
            str(bundle_dir),
            "--output-dir",
            str(tmp_path),
        ]
    )
    rc = args.func(args)
    assert rc == 0
    kit_dir = tmp_path / "reviewer_kit"
    assert (kit_dir / "claim_ledger.json").exists()
    assert (kit_dir / "stage_gate_report.md").exists()
    assert (kit_dir / "protocol_critic_report.md").exists()
