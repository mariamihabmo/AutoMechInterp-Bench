"""CLI for Stage-2 runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .io_utils import Stage2Error
from .runner import Stage2Config, run_stage2


def _cmd_run(args: argparse.Namespace) -> int:
    config = Stage2Config(
        bundle_dir=Path(args.bundle).resolve(),
        device=args.device,
        mode=args.mode,
        examples_per_cell=int(args.examples_per_cell),
    )
    result = run_stage2(config)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="automechinterp-runner",
        description="Run Stage-2 interventions and emit evaluation_result.json",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run Stage-2 pipeline")
    run_p.add_argument("--bundle", required=True, help="Bundle directory")
    run_p.add_argument("--device", default="cpu", help="Torch device, e.g. cpu or cuda")
    run_p.add_argument("--mode", default="real", choices=["real", "mock"], help="Execution mode")
    run_p.add_argument(
        "--examples-per-cell",
        type=int,
        default=20,
        help=(
            "Number of examples per execution-grid cell in real mode. "
            "Defaults to 20 to match Stage2Config and avoid degenerate "
            "exploratory/confirmatory splits."
        ),
    )
    run_p.set_defaults(func=_cmd_run)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        raise SystemExit(args.func(args))
    except Stage2Error as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
