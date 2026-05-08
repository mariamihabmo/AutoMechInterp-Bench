from __future__ import annotations

import json
from pathlib import Path

import pytest

from automechinterp_evaluator.cli import build_parser
from automechinterp_evaluator.hypothesis_generation import generate_hypotheses_from_agent_output
from automechinterp_evaluator.io_utils import BundleError, read_jsonl


def _write_agent_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def test_generate_hypotheses_from_agent_json_aliases(bundle_dir: Path) -> None:
    # Remove seed template so generation writes canonical hypothesis file from scratch.
    (bundle_dir / "hypothesis.jsonl").unlink()

    agent_output = bundle_dir / "agent_output.json"
    _write_agent_json(
        agent_output,
        {
            "hypotheses": [
                {
                    "mechanistic_claim": "Candidate components increase target behavior.",
                    "components": [{"component_type": "head", "layer": 5, "head": 2}],
                    "predicted_effect_direction": "up",
                    "predicted_effect_size": 0.06,
                    "specificity_ratio": 4.5,
                    "failure_modes": ["template leakage"],
                }
            ]
        },
    )

    result = generate_hypotheses_from_agent_output(
        bundle_dir=bundle_dir,
        input_path=agent_output,
        input_format="auto",
        overwrite=False,
    )

    assert result["hypothesis_count"] == 1
    assert result["manifest"] is not None

    rows = read_jsonl(bundle_dir / "hypothesis.jsonl")
    assert rows[0]["protocol_id"] == "ioi_gpt2small_v1"
    assert rows[0]["task_id"] == "ioi_v0"
    assert rows[0]["predicted_effect_direction"] == "increase"
    assert rows[0]["claim_text"] == "Candidate components increase target behavior."
    assert rows[0]["hypothesis_id"].startswith("h_001_")


def test_generate_hypotheses_overwrite_protection(bundle_dir: Path) -> None:
    agent_output = bundle_dir / "agent_output.json"
    _write_agent_json(
        agent_output,
        {
            "hypotheses": [
                {
                    "hypothesis_id": "h_new",
                    "claim_text": "Candidate heads increase effect.",
                    "candidate_components": [{"component_type": "head", "layer": 1, "head": 1}],
                    "predicted_effect_direction": "increase",
                    "predicted_min_effect": 0.05,
                    "predicted_specificity_ratio": 5.0,
                    "expected_failure_modes": ["none"],
                }
            ]
        },
    )

    with pytest.raises(BundleError, match="Refusing to overwrite"):
        generate_hypotheses_from_agent_output(
            bundle_dir=bundle_dir,
            input_path=agent_output,
            input_format="auto",
            overwrite=False,
        )


def test_generate_hypotheses_validation_fails_on_missing_components(bundle_dir: Path) -> None:
    agent_output = bundle_dir / "agent_output.json"
    _write_agent_json(
        agent_output,
        {
            "hypotheses": [
                {
                    "hypothesis_id": "h_bad",
                    "claim_text": "Candidate claim without components.",
                    "predicted_effect_direction": "increase",
                    "predicted_min_effect": 0.05,
                    "predicted_specificity_ratio": 5.0,
                    "expected_failure_modes": ["none"],
                }
            ]
        },
    )

    with pytest.raises(BundleError, match="candidate_components"):
        generate_hypotheses_from_agent_output(
            bundle_dir=bundle_dir,
            input_path=agent_output,
            input_format="auto",
            output_path=bundle_dir / "hypothesis_new.jsonl",
            overwrite=False,
        )


def test_cli_generate_hypotheses_custom_output(bundle_dir: Path, tmp_path: Path) -> None:
    agent_output = tmp_path / "agent_output.json"
    _write_agent_json(
        agent_output,
        {
            "hypotheses": [
                {
                    "hypothesis_id": "h_cli",
                    "claim_text": "CLI-generated hypothesis.",
                    "candidate_components": [{"component_type": "head", "layer": 2, "head": 3}],
                    "predicted_effect_direction": "increase",
                    "predicted_min_effect": 0.05,
                    "predicted_specificity_ratio": 5.0,
                    "expected_failure_modes": ["none"],
                }
            ]
        },
    )

    out = tmp_path / "generated.jsonl"
    parser = build_parser()
    args = parser.parse_args(
        [
            "generate-hypotheses",
            "--bundle",
            str(bundle_dir),
            "--agent-output",
            str(agent_output),
            "--output",
            str(out),
        ]
    )
    rc = args.func(args)
    assert rc == 0
    assert out.exists()
