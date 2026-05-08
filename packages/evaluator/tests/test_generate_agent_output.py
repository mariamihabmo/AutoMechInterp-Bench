from __future__ import annotations

import json
from pathlib import Path

import pytest

from automechinterp_evaluator.agent_output_generation import generate_agent_output
from automechinterp_evaluator.cli import build_parser
from automechinterp_evaluator.hypothesis_generation import generate_hypotheses_from_agent_output
from automechinterp_evaluator.io_utils import BundleError, read_json_any, read_jsonl
from .conftest import read_yaml, write_yaml


def test_generate_agent_output_default(bundle_dir: Path) -> None:
    out = bundle_dir / "agent_output.json"
    result = generate_agent_output(bundle_dir=bundle_dir, output_path=out, hypothesis_count=2, overwrite=False)

    assert result["hypothesis_count"] == 2
    payload = read_json_any(out)
    assert payload["agent_metadata"]["protocol_id"] == "ioi_gpt2small_v1"
    assert payload["agent_metadata"]["source_mode"] == "template"
    assert len(payload["hypotheses"]) == 2
    assert payload["hypotheses"][0]["predicted_effect_direction"] == "increase"


def test_generate_agent_output_with_component_catalog(bundle_dir: Path, tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(
        json.dumps(
            {
                "components": [
                    {"component_type": "head", "layer": 4, "head": 1},
                    {"component_type": "head", "layer": 5, "head": 2},
                ]
            }
        )
    )

    out = bundle_dir / "agent_output.json"
    generate_agent_output(
        bundle_dir=bundle_dir,
        output_path=out,
        hypothesis_count=1,
        component_catalog_path=catalog_path,
        overwrite=False,
    )

    payload = read_json_any(out)
    comps = payload["hypotheses"][0]["components"]
    assert comps[0]["layer"] == 4


def test_generate_agent_output_from_exploration_findings(bundle_dir: Path, tmp_path: Path) -> None:
    exploration = tmp_path / "exploration.json"
    exploration.write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "summary": "Name mover candidate from autonomous sweep.",
                        "components": [
                            {"component_type": "head", "layer": 9, "head": 9},
                            {"component_type": "head", "layer": 10, "head": 0},
                        ],
                        "metric_delta": 0.11,
                        "specificity_ratio": 8.0,
                        "direction": "increase",
                        "failure_modes": ["prompt_shift"],
                    }
                ]
            }
        )
    )

    out = bundle_dir / "agent_output.json"
    result = generate_agent_output(
        bundle_dir=bundle_dir,
        output_path=out,
        hypothesis_count=1,
        exploration_input_path=exploration,
        overwrite=False,
    )
    assert result["source_mode"] == "exploration"
    assert result["exploration_input_used"] is True

    payload = read_json_any(out)
    assert payload["agent_metadata"]["source_mode"] == "exploration"
    assert payload["hypotheses"][0]["mechanistic_claim"].startswith("Name mover")
    assert payload["hypotheses"][0]["predicted_effect_size"] >= 0.11
    assert payload["hypotheses"][0]["specificity_ratio"] >= 8.0


def test_generate_agent_output_exploration_without_components_fails(bundle_dir: Path, tmp_path: Path) -> None:
    exploration = tmp_path / "exploration_empty.json"
    exploration.write_text(json.dumps({"findings": [{"summary": "no components here"}]}))

    with pytest.raises(BundleError, match="No usable exploration findings"):
        generate_agent_output(
            bundle_dir=bundle_dir,
            hypothesis_count=1,
            exploration_input_path=exploration,
            overwrite=True,
        )


def test_generate_agent_output_overwrite_protection(bundle_dir: Path) -> None:
    out = bundle_dir / "agent_output.json"
    generate_agent_output(bundle_dir=bundle_dir, output_path=out, hypothesis_count=1, overwrite=False)

    with pytest.raises(BundleError, match="Refusing to overwrite"):
        generate_agent_output(bundle_dir=bundle_dir, output_path=out, hypothesis_count=1, overwrite=False)


def test_generate_agent_output_respects_claim_budget(bundle_dir: Path) -> None:
    with pytest.raises(BundleError, match="claim budget"):
        generate_agent_output(bundle_dir=bundle_dir, hypothesis_count=999, overwrite=True)


def test_generate_agent_output_requires_model_spec_for_unknown_model(bundle_dir: Path) -> None:
    protocol = read_yaml(bundle_dir / "protocol.yaml")
    protocol["unit_of_work"]["model_id"] = "custom-transformer"
    protocol["unit_of_work"].pop("model_spec", None)
    write_yaml(bundle_dir / "protocol.yaml", protocol)

    with pytest.raises(BundleError, match="Unable to infer model shape"):
        generate_agent_output(bundle_dir=bundle_dir, hypothesis_count=1, overwrite=True)


def test_cli_generate_agent_output_and_roundtrip(bundle_dir: Path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "generate-agent-output",
            "--bundle",
            str(bundle_dir),
            "--count",
            "2",
            "--overwrite",
        ]
    )
    rc = args.func(args)
    assert rc == 0

    # Convert generated agent output into canonical hypothesis.jsonl.
    result = generate_hypotheses_from_agent_output(
        bundle_dir=bundle_dir,
        input_path=bundle_dir / "agent_output.json",
        input_format="auto",
        overwrite=True,
    )
    assert result["hypothesis_count"] == 2
    rows = read_jsonl(bundle_dir / "hypothesis.jsonl")
    assert len(rows) == 2
