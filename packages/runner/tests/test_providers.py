"""Tests for all 5 discovery lane providers.

Validates:
- Each provider emits schema-valid hypothesis dicts
- Provenance metadata is stamped on every hypothesis
- Component types match expected values per lane
- Budget parameter is respected
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_runner.providers import list_providers, get_provider
from automechinterp_runner.providers.circuits_sweep import CircuitSweepProvider
from automechinterp_runner.providers.openai_autointerp import OpenAIAutoInterpProvider
from automechinterp_runner.providers.efficient_neuron_explanations import EfficientNeuronExplanationsProvider
from automechinterp_runner.providers.sae_autointerp import SAEAutoInterpProvider
from automechinterp_runner.providers.petri_behavioral import PetriBehavioralProvider

# Required fields in every hypothesis (from constants.py schema)
REQUIRED_FIELDS = {
    "hypothesis_id", "protocol_id", "task_id", "model_id",
    "metric_id", "claim_text", "candidate_components",
    "predicted_effect_direction", "predicted_min_effect",
    "predicted_specificity_ratio",
}

PROVENANCE_FIELDS = {"provider_id", "provider_version", "discovery_lane"}

PROTOCOL = {
    "protocol_id": "test_provider_protocol",
    "frozen": True,
    "unit_of_work": {
        "task_id": "ioi_v0",
        "model_id": "gpt2-small",
        "metric_id": "logit_diff",
    },
}

MOCK_EXPLANATIONS = [
    {"layer": 5, "neuron": 200, "explanation_text": "Fires on brackets", "simulation_score": 0.85},
    {"layer": 7, "neuron": 412, "explanation_text": "Activates on names", "simulation_score": 0.72},
]

MOCK_SAE_FEATURES = [
    {"sae_id": "gpt2_sae", "layer": 6, "feature_id": 1234, "description": "IOI feature", "site": "resid_post"},
]

MOCK_BEHAVIORAL = [
    {"component_type": "head", "layer": 9, "head": 6, "site": "z", "predicted_direction": "increase", "min_effect": 0.05},
]


def _validate_hypothesis(h: dict, expected_type: str | None = None):
    """Assert a hypothesis dict has all required fields and valid values."""
    missing = REQUIRED_FIELDS - set(h.keys())
    assert not missing, f"Missing required fields: {missing}"

    assert isinstance(h["hypothesis_id"], str) and h["hypothesis_id"].strip()
    assert h["protocol_id"] == PROTOCOL["protocol_id"]
    assert h["task_id"] == "ioi_v0"
    assert h["model_id"] == "gpt2-small"
    assert h["predicted_effect_direction"] in ("increase", "decrease")
    assert isinstance(h["predicted_min_effect"], (int, float))
    assert isinstance(h["predicted_specificity_ratio"], (int, float))
    assert isinstance(h["candidate_components"], list)
    assert len(h["candidate_components"]) >= 1

    if expected_type:
        assert h["candidate_components"][0]["component_type"] == expected_type


def _validate_provenance(h: dict, provider_name: str):
    """Assert provenance metadata is stamped."""
    missing = PROVENANCE_FIELDS - set(h.keys())
    assert not missing, f"Missing provenance fields: {missing}"
    assert h["provider_id"] == provider_name
    assert isinstance(h["provider_version"], str)
    assert h["discovery_lane"] == provider_name


# ---- Registration ----

class TestProviderRegistry:
    def test_all_providers_registered(self):
        providers = list_providers()
        assert "circuits_sweep" in providers
        assert "openai_autointerp" in providers
        assert "efficient_neuron_explanations" in providers
        assert "sae_autointerp" in providers
        assert "petri_behavioral" in providers

    def test_get_provider_returns_instance(self):
        provider = get_provider("circuits_sweep")
        assert provider is not None
        assert hasattr(provider, "propose")


# ---- Lane A: Circuit Sweep ----

class TestCircuitSweepProvider:
    def test_emits_head_hypotheses(self):
        provider = CircuitSweepProvider(mode="mock", top_k=3)
        hypotheses = provider.propose(PROTOCOL, budget=3)
        assert len(hypotheses) <= 3
        for h in hypotheses:
            _validate_hypothesis(h, expected_type="head")
            _validate_provenance(h, "circuits_sweep")

    def test_budget_respected(self):
        provider = CircuitSweepProvider(mode="mock", top_k=10)
        hypotheses = provider.propose(PROTOCOL, budget=2)
        assert len(hypotheses) <= 2


# ---- Lane B1: OpenAI AutoInterp ----

class TestOpenAIAutoInterpProvider:
    def test_emits_neuron_hypotheses(self):
        provider = OpenAIAutoInterpProvider(explanations=MOCK_EXPLANATIONS)
        hypotheses = provider.propose(PROTOCOL, budget=5)
        assert len(hypotheses) == len(MOCK_EXPLANATIONS)
        for h in hypotheses:
            _validate_hypothesis(h, expected_type="mlp_neuron")
            _validate_provenance(h, "openai_autointerp")
            assert "explanation_text" in h.get("metadata", {}) or "explanation_text" in h

    def test_empty_explanations(self):
        provider = OpenAIAutoInterpProvider(explanations=[])
        hypotheses = provider.propose(PROTOCOL, budget=5)
        assert hypotheses == []


# ---- Lane B2: Efficient Neuron Explanations ----

class TestEfficientNeuronExplanationsProvider:
    def test_emits_neuron_hypotheses(self):
        provider = EfficientNeuronExplanationsProvider(explanations=MOCK_EXPLANATIONS)
        hypotheses = provider.propose(PROTOCOL, budget=5)
        assert len(hypotheses) == len(MOCK_EXPLANATIONS)
        for h in hypotheses:
            _validate_hypothesis(h, expected_type="mlp_neuron")
            _validate_provenance(h, "efficient_neuron_explanations")


# ---- Lane B3: SAE AutoInterp ----

class TestSAEAutoInterpProvider:
    def test_emits_sae_hypotheses(self):
        provider = SAEAutoInterpProvider(features=MOCK_SAE_FEATURES)
        hypotheses = provider.propose(PROTOCOL, budget=5)
        assert len(hypotheses) == len(MOCK_SAE_FEATURES)
        for h in hypotheses:
            _validate_hypothesis(h, expected_type="sae_feature")
            _validate_provenance(h, "sae_autointerp")


# ---- Lane C: Petri Behavioral ----

class TestPetriBehavioralProvider:
    def test_emits_mixed_hypotheses(self):
        provider = PetriBehavioralProvider(candidates=MOCK_BEHAVIORAL)
        hypotheses = provider.propose(PROTOCOL, budget=5)
        assert len(hypotheses) == len(MOCK_BEHAVIORAL)
        for h in hypotheses:
            _validate_hypothesis(h)
            _validate_provenance(h, "petri_behavioral")

    def test_preserves_component_type(self):
        provider = PetriBehavioralProvider(candidates=MOCK_BEHAVIORAL)
        hypotheses = provider.propose(PROTOCOL, budget=5)
        assert hypotheses[0]["candidate_components"][0]["component_type"] == "head"
