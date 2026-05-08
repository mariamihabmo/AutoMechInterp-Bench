from __future__ import annotations

import shutil
from pathlib import Path

from automechinterp_runner.cli import build_parser


def _copy_template_bundle(tmp_path: Path) -> Path:
    src = Path(__file__).resolve().parents[2] / "evaluator" / "templates" / "example_bundle"
    dst = tmp_path / "bundle"
    shutil.copytree(src, dst)
    return dst


def test_cli_run_mock(tmp_path: Path) -> None:
    bundle = _copy_template_bundle(tmp_path)
    parser = build_parser()
    args = parser.parse_args(
        [
            "run",
            "--bundle",
            str(bundle),
            "--mode",
            "mock",
            "--device",
            "cpu",
            "--examples-per-cell",
            "1",
        ]
    )
    rc = args.func(args)
    assert rc == 0
    assert (bundle / "evaluation_result.json").exists()
