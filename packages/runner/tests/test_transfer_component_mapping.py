from __future__ import annotations

import pytest

from main.run_real_multi_task import (
    map_transfer_component,
    transfer_cache_names_filter,
    transfer_contract_metadata,
    transfer_intervention_kind,
)


def test_transfer_maps_head_layer_and_clamps_head_index() -> None:
    mapped = map_transfer_component(
        {"component_type": "head", "layer": 11, "head": 20},
        source_n_layers=12,
        transfer_n_layers=24,
        transfer_n_heads=16,
    )

    assert mapped == {"component_type": "head", "layer": 22, "head": 15}


def test_transfer_maps_mlp_neuron_layer_and_clamps_neuron_index() -> None:
    mapped = map_transfer_component(
        {"component_type": "mlp_neuron", "layer": 10, "neuron": 5000},
        source_n_layers=12,
        transfer_n_layers=24,
        transfer_n_heads=16,
        transfer_d_mlp=4096,
    )

    assert mapped == {"component_type": "mlp_neuron", "layer": 20, "neuron": 4095}


def test_transfer_cache_filter_uses_mlp_hook_for_neuron_components() -> None:
    names_filter = transfer_cache_names_filter([
        {"component_type": "mlp_neuron", "layer": 20, "neuron": 1793}
    ])

    assert names_filter("blocks.20.mlp.hook_post")
    assert not names_filter("blocks.20.attn.hook_z")


def test_transfer_rejects_mixed_component_types() -> None:
    with pytest.raises(ValueError, match="Unsupported or mixed component types"):
        transfer_intervention_kind([
            {"component_type": "head", "layer": 1, "head": 2},
            {"component_type": "mlp", "layer": 3},
        ])


def test_transfer_contract_metadata_uses_evaluator_floor_and_direction() -> None:
    metadata = transfer_contract_metadata(0.03, -0.50)

    assert metadata["cross_model_effect_floor"] == pytest.approx(0.02)
    assert metadata["transfer_above_floor"] is True
    assert metadata["transfer_same_direction"] is False
    assert metadata["transfer_contract_pass"] is False
    assert metadata["transfer_positive"] is True


def test_transfer_contract_metadata_passes_same_direction_above_floor() -> None:
    metadata = transfer_contract_metadata(-0.03, -0.50)

    assert metadata["transfer_above_floor"] is True
    assert metadata["transfer_same_direction"] is True
    assert metadata["transfer_contract_pass"] is True
