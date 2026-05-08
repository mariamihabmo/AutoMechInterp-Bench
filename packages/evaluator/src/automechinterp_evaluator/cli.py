"""CLI for stage-1 harness."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .agent_output_generation import generate_agent_output
from .evaluator import evaluate_bundle
from .hypothesis_generation import generate_hypotheses_from_agent_output
from .io_utils import BundleError
from .reference_vectors import write_reference_vectors
from .reporting import write_markdown_report
from .reviewer_kit import build_reviewer_kit
from .submission_review import write_submission_review


def _cmd_evaluate(args: argparse.Namespace) -> int:
    bundle_dir = Path(args.bundle).resolve()
    result = evaluate_bundle(bundle_dir)
    rendered = json.dumps(result, sort_keys=True, indent=2)
    if args.output:
        output = Path(args.output)
        # create parent
        # directories so external callers can pass nested output paths
        # without first running ``mkdir -p`` themselves.
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n")
    else:
        print(rendered)
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    bundle_dir = Path(args.bundle).resolve()
    output = Path(args.output).resolve() if args.output else None
    report_path = write_markdown_report(bundle_dir, output)
    print(str(report_path))
    return 0


def _cmd_init_template(args: argparse.Namespace) -> int:
    dest = Path(args.output_dir).resolve()
    src = Path(__file__).resolve().parents[2] / "templates" / "example_bundle"
    if dest.exists() and any(dest.iterdir()):
        raise BundleError("init-template destination must be empty or missing")
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, dirs_exist_ok=True)
    print(str(dest))
    return 0


def _cmd_generate_hypotheses(args: argparse.Namespace) -> int:
    bundle_dir = Path(args.bundle).resolve()
    input_path = Path(args.agent_output).resolve()
    output = Path(args.output).resolve() if args.output else None

    result = generate_hypotheses_from_agent_output(
        bundle_dir=bundle_dir,
        input_path=input_path,
        input_format=args.input_format,
        output_path=output,
        overwrite=bool(args.overwrite),
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


def _cmd_generate_agent_output(args: argparse.Namespace) -> int:
    bundle_dir = Path(args.bundle).resolve()
    output = Path(args.output).resolve() if args.output else None
    component_catalog = Path(args.component_catalog).resolve() if args.component_catalog else None
    exploration_input = Path(args.exploration_input).resolve() if args.exploration_input else None

    result = generate_agent_output(
        bundle_dir=bundle_dir,
        output_path=output,
        hypothesis_count=int(args.count),
        predicted_direction=args.direction,
        component_catalog_path=component_catalog,
        exploration_input_path=exploration_input,
        components_per_hypothesis=int(args.components_per_hypothesis),
        overwrite=bool(args.overwrite),
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


def _cmd_submission_review(args: argparse.Namespace) -> int:
    bundle_dir = Path(args.bundle).resolve()
    output_json = Path(args.output_json).resolve() if args.output_json else None
    output_md = Path(args.output_md).resolve() if args.output_md else None
    _, json_path, md_path = write_submission_review(
        bundle_dir,
        reruns=int(args.reruns),
        output_json=output_json,
        output_md=output_md,
    )
    print(json.dumps({"json": str(json_path), "markdown": str(md_path)}, sort_keys=True, indent=2))
    return 0


def _cmd_reference_vectors(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir).resolve()
    _, json_path, md_path = write_reference_vectors(output_dir)
    print(json.dumps({"json": str(json_path), "markdown": str(md_path)}, sort_keys=True, indent=2))
    return 0


def _cmd_reviewer_kit(args: argparse.Namespace) -> int:
    bundle_dir = Path(args.bundle).resolve()
    output_dir = Path(args.output_dir).resolve()
    kit_dir = build_reviewer_kit(bundle_dir, output_dir)
    print(str(kit_dir))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="automechinterp-evaluator",
        description="Deterministic stage-gate harness for mechanistic claims",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    eval_p = sub.add_parser("evaluate", help="Evaluate a bundle and print JSON summary")
    eval_p.add_argument("--bundle", required=True, help="Path to bundle directory")
    eval_p.add_argument("--output", help="Optional output JSON path")
    eval_p.set_defaults(func=_cmd_evaluate)

    report_p = sub.add_parser("report", help="Generate stage_gate_report.md for bundle")
    report_p.add_argument("--bundle", required=True, help="Path to bundle directory")
    report_p.add_argument("--output", help="Optional report output path")
    report_p.set_defaults(func=_cmd_report)

    init_p = sub.add_parser("init-template", help="Copy example bundle template")
    init_p.add_argument("--output-dir", required=True, help="Destination directory")
    init_p.set_defaults(func=_cmd_init_template)

    gen_p = sub.add_parser(
        "generate-hypotheses",
        help="Convert agent output JSON/JSONL into validated hypothesis.jsonl",
    )
    gen_p.add_argument("--bundle", required=True, help="Bundle directory containing protocol.yaml")
    gen_p.add_argument("--agent-output", required=True, help="Path to agent output (json/jsonl)")
    gen_p.add_argument(
        "--input-format",
        default="auto",
        choices=["auto", "json", "jsonl"],
        help="Input parsing mode; defaults to auto-detect",
    )
    gen_p.add_argument("--output", help="Optional output path (default: <bundle>/hypothesis.jsonl)")
    gen_p.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing hypothesis.jsonl",
    )
    gen_p.set_defaults(func=_cmd_generate_hypotheses)

    agen_p = sub.add_parser(
        "generate-agent-output",
        help="Generate deterministic agent_output.json from protocol.yaml",
    )
    agen_p.add_argument("--bundle", required=True, help="Bundle directory containing protocol.yaml")
    agen_p.add_argument("--output", help="Optional output path (default: <bundle>/agent_output.json)")
    agen_p.add_argument(
        "--count",
        type=int,
        default=3,
        help="Number of hypotheses to generate (bounded by protocol claim budget)",
    )
    agen_p.add_argument(
        "--direction",
        choices=["increase", "decrease"],
        default="increase",
        help="Predicted effect direction for generated hypotheses",
    )
    agen_p.add_argument(
        "--component-catalog",
        help="Optional JSON file with component hints (list or {components:[...]})",
    )
    agen_p.add_argument(
        "--exploration-input",
        help=(
            "Optional exploration artifact JSON (list or object with findings/results). "
            "If provided, hypotheses are derived from these findings first."
        ),
    )
    agen_p.add_argument(
        "--components-per-hypothesis",
        type=int,
        default=2,
        help="How many components to attach to each generated hypothesis",
    )
    agen_p.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing agent_output.json",
    )
    agen_p.set_defaults(func=_cmd_generate_agent_output)

    sr_p = sub.add_parser(
        "submission-review",
        help="Run deterministic reruns and generate publication-facing workflow guidance",
    )
    sr_p.add_argument("--bundle", required=True, help="Bundle directory to review")
    sr_p.add_argument("--reruns", type=int, default=3, help="How many evaluator reruns to compare")
    sr_p.add_argument("--output-json", help="Optional JSON output path")
    sr_p.add_argument("--output-md", help="Optional Markdown output path")
    sr_p.set_defaults(func=_cmd_submission_review)

    rv_p = sub.add_parser(
        "reference-vectors",
        help="Emit compatibility vectors for third-party evaluator implementations",
    )
    rv_p.add_argument(
        "--output-dir",
        default="reference_vectors",
        help="Directory where reference vector artifacts should be written",
    )
    rv_p.set_defaults(func=_cmd_reference_vectors)

    rk_p = sub.add_parser(
        "reviewer-kit",
        help="Assemble a reviewer kit with artifacts, ledger, and reproduction script",
    )
    rk_p.add_argument("--bundle", required=True, help="Bundle directory to package")
    rk_p.add_argument(
        "--output-dir",
        default=".",
        help="Directory where the reviewer_kit folder should be created",
    )
    rk_p.set_defaults(func=_cmd_reviewer_kit)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        raise SystemExit(args.func(args))
    except BundleError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc


if __name__ == "__main__":
    main()
