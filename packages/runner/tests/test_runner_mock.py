from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

from automechinterp_runner.runner import Stage2Config, run_stage2

def _copy_template_bundle(tmp_path: Path) -> Path:
    src = Path(__file__).resolve().parents[2] / "evaluator" / "templates" / "example_bundle"
    dst = tmp_path / "bundle"
    shutil.copytree(src, dst)
    return dst

def test_stage2_mock_writes_evaluation_result_with_provenance(tmp_path: Path) -> None:
    bundle = _copy_template_bundle(tmp_path)
    result = run_stage2(
        Stage2Config(
            bundle_dir=bundle,
            mode="mock",
            device="cpu",
            examples_per_cell=1,
        )
    )

    assert result["mode"] == "mock"
    eval_path = bundle / "evaluation_result.json"
    payload = json.loads(eval_path.read_text())
    assert payload["hypothesis_results"]
    cell = payload["hypothesis_results"][0]["raw_cells"][0]
    for key in (
        "runner_id",
        "runner_version",
        "pipeline_sha",
        "model_ref",
        "dataset_seed",
        "prompt_template_id",
    ):
        assert key in cell

def test_stage2_mock_output_is_stage1_parseable(tmp_path: Path) -> None:
    bundle = _copy_template_bundle(tmp_path)
    run_stage2(Stage2Config(bundle_dir=bundle, mode="mock", device="cpu", examples_per_cell=1))

    stage1_src = Path(__file__).resolve().parents[2] / "evaluator" / "src"
    sys.path.insert(0, str(stage1_src))
    from automechinterp_evaluator.evaluator import evaluate_bundle

    result = evaluate_bundle(bundle)
    assert result["overall"]["hypothesis_count"] >= 1

def test_stage2_rejects_unsupported_task(tmp_path: Path) -> None:
    bundle = _copy_template_bundle(tmp_path)
    protocol_path = bundle / "protocol.yaml"
    text = protocol_path.read_text().replace("task_id: ioi_v0", "task_id: closing_brackets_v0")
    protocol_path.write_text(text)

    with pytest.raises(Exception, match="task_id=closing_brackets_v0"):
        run_stage2(Stage2Config(bundle_dir=bundle, mode="mock", device="cpu", examples_per_cell=1))

def test_stage2_rejects_unsupported_prompt_variant(tmp_path: Path) -> None:
    """Pin the post-prompt-variant-repair invariant: the Stage-2 runner MUST
    raise ``Stage2Error`` (not silently alias to a default) when a protocol
    requests a prompt variant the registered task does not declare. This is
    the same validation referenced in
    ``main/prompt_variant_validity_audit.py`` ("Stage-2 now raises
    Stage2Error for unsupported prompt variants.").
    """

    bundle = _copy_template_bundle(tmp_path)
    protocol_path = bundle / "protocol.yaml"
    text = protocol_path.read_text().replace(
        "prompt_variants: [base, paraphrase]",
        "prompt_variants: [base, definitely_not_a_real_variant_v0]",
    )
    protocol_path.write_text(text)

    with pytest.raises(Exception, match="unsupported prompt variants"):
        run_stage2(Stage2Config(bundle_dir=bundle, mode="mock", device="cpu", examples_per_cell=1))
