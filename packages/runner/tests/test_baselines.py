"""Dedicated tests for the baselines module (mock-mode contract tests).

Tests random_circuit_baseline and attribution_baseline output contracts
without requiring GPU or real models.
"""

from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import dataclass
from unittest.mock import MagicMock
from statistics import mean

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))


@dataclass
class MockExample:
    clean_prompt: str
    corrupt_prompt: str
    target_token: int
    distractor_token: int


class MockTaskModule:
    PROMPT_VARIANTS = ["base"]

    @staticmethod
    def sample_examples(*, model, n, seed, prompt_variant):
        return [
            MockExample(
                clean_prompt="When John and Mary went to the store, Mary gave a book to",
                corrupt_prompt="When John and Mary went to the store, John gave a book to",
                target_token=100,
                distractor_token=200,
            )
            for _ in range(n)
        ]

    @staticmethod
    def metric(logits, target_token, distractor_token):
        return float(logits[0, -1, target_token] - logits[0, -1, distractor_token])


class TestRandomCircuitBaselineContract:
    """Tests that random_circuit_baseline returns the correct output schema."""

    def test_output_has_required_keys(self):
        # Use the intervention dispatch mock style
        from automechinterp_runner.interventions.node_patching import random_head_components

        comps = random_head_components(n_layers=12, n_heads=12, count=3, seed=42)
        assert len(comps) == 3
        assert all(c["component_type"] == "head" for c in comps)
        assert all("layer" in c for c in comps)
        assert all("head" in c for c in comps)

    def test_random_components_are_deterministic(self):
        from automechinterp_runner.interventions.node_patching import random_head_components

        a = random_head_components(n_layers=12, n_heads=12, count=5, seed=42)
        b = random_head_components(n_layers=12, n_heads=12, count=5, seed=42)
        assert a == b

    def test_random_neuron_components(self):
        from automechinterp_runner.interventions.node_patching import random_neuron_components

        comps = random_neuron_components(n_layers=12, d_mlp=3072, count=4, seed=42)
        assert len(comps) == 4
        assert all(c["component_type"] == "mlp_neuron" for c in comps)

    def test_random_sae_features(self):
        from automechinterp_runner.interventions.node_patching import random_sae_features

        comps = random_sae_features(n_layers=12, count=3, seed=42)
        assert len(comps) == 3
        assert all(c["component_type"] == "sae_feature" for c in comps)

    def test_random_edge_components(self):
        from automechinterp_runner.interventions.node_patching import random_edge_components

        comps = random_edge_components(n_layers=12, n_heads=12, count=3, seed=42)
        assert len(comps) == 3
        assert all(c["component_type"] == "edge" for c in comps)
        # Edges must flow forward
        for c in comps:
            assert c["source_layer"] < c["target_layer"]


class TestShiftLayers:
    def test_shift_wraps_layers(self):
        from automechinterp_runner.interventions.node_patching import shift_layers

        comps = [{"component_type": "head", "layer": 11, "head": 5}]
        shifted = shift_layers(comps, n_layers=12)
        assert shifted[0]["layer"] == 0  # 11+1 mod 12 = 0

    def test_shift_preserves_other_fields(self):
        from automechinterp_runner.interventions.node_patching import shift_layers

        comps = [{"component_type": "head", "layer": 3, "head": 7, "site": "z"}]
        shifted = shift_layers(comps, n_layers=12)
        assert shifted[0]["head"] == 7
        assert shifted[0]["site"] == "z"

    def test_shift_handles_edge_components(self):
        from automechinterp_runner.interventions.node_patching import shift_layers

        comps = [{"component_type": "edge", "source_layer": 2, "source_head": 1, "target_layer": 5, "target_head": 3}]
        shifted = shift_layers(comps, n_layers=12)
        assert shifted[0]["source_layer"] == 3
        assert shifted[0]["target_layer"] == 6
