from __future__ import annotations

from pathlib import Path

import pytest

from automechinterp_runner.runner import (
    _build_mean_cache,
    _deterministic_permutation_indices,
    _random_controls_for_type,
    Stage2Config,
    run_stage2,
)
from automechinterp_runner.interventions.node_patching import neuron_intervention_logits


def test_random_controls_are_type_matched() -> None:
    mlp_controls = _random_controls_for_type("mlp", n_layers=12, n_heads=12, count=2, seed=7)
    residual_controls = _random_controls_for_type("residual_stream", n_layers=12, n_heads=12, count=2, seed=7)
    das_controls = _random_controls_for_type("das_subspace", n_layers=12, n_heads=12, count=2, seed=7)

    assert all(row["component_type"] == "mlp" for row in mlp_controls)
    assert all(row["component_type"] == "residual_stream" for row in residual_controls)
    assert all(row["component_type"] == "das_subspace" for row in das_controls)


def test_mean_cache_is_real_average() -> None:
    class FakeCache(dict):
        pass

    torch = pytest.importorskip("torch")

    cache_a = FakeCache({"blocks.0.attn.hook_z": torch.ones(1, 2, 1, 3)})
    cache_b = FakeCache({"blocks.0.attn.hook_z": torch.full((1, 2, 1, 3), 3.0)})
    mean_cache = _build_mean_cache([cache_a, cache_b])
    assert "blocks.0.attn.hook_z" in mean_cache
    assert float(mean_cache["blocks.0.attn.hook_z"].mean()) == 2.0


def test_deterministic_shuffle_indices_are_stable() -> None:
    assert _deterministic_permutation_indices(8, 1234) == _deterministic_permutation_indices(8, 1234)
    assert _deterministic_permutation_indices(8, 1234) != _deterministic_permutation_indices(8, 5678)


def test_mock_runner_emits_direction_field(tmp_path: Path) -> None:
    src = Path(__file__).resolve().parents[2] / "evaluator" / "templates" / "example_bundle"
    bundle = tmp_path / "bundle"
    import shutil

    shutil.copytree(src, bundle)
    run_stage2(Stage2Config(bundle_dir=bundle, mode="mock", device="cpu", examples_per_cell=1))

    import json

    payload = json.loads((bundle / "evaluation_result.json").read_text())
    directions = {cell["direction"] for row in payload["hypothesis_results"] for cell in row["raw_cells"]}
    assert directions
    assert directions.issubset({"sufficiency_patch", "necessity_ablate"})
    assert "necessity_ablate" in directions


def test_neuron_intervention_clamps_source_position_on_length_mismatch() -> None:
    torch = pytest.importorskip("torch")

    class FakeModel:
        class cfg:
            n_layers = 12

        def run_with_hooks(self, target_tokens, fwd_hooks):
            act = torch.zeros(1, 11, 20)
            for _, hook in fwd_hooks:
                act = hook(act, type("Hook", (), {"name": "blocks.0.mlp.hook_post"})())
            return act

    model = FakeModel()
    target_tokens = torch.zeros(1, 11, dtype=torch.long)
    source_cache = {"blocks.0.mlp.hook_post": torch.arange(1 * 10 * 20, dtype=torch.float32).reshape(1, 10, 20)}
    mean_cache = {"blocks.0.mlp.hook_post": torch.full((1, 10, 20), 7.0)}
    components = [{"component_type": "mlp_neuron", "layer": 0, "neuron": 3}]

    patched_clean = neuron_intervention_logits(
        model=model,
        target_tokens=target_tokens,
        source_cache=source_cache,
        components=components,
        patch_mode="clean",
        target_position=-1,
        mean_cache=mean_cache,
    )
    assert float(patched_clean[:, -1, 3]) == float(source_cache["blocks.0.mlp.hook_post"][:, -1, 3])

    patched_mean = neuron_intervention_logits(
        model=model,
        target_tokens=target_tokens,
        source_cache=source_cache,
        components=components,
        patch_mode="mean",
        target_position=-1,
        mean_cache=mean_cache,
    )
    assert float(patched_mean[:, -1, 3]) == 7.0
