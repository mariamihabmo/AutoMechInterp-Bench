"""Dedicated tests for the models module.

Tests model registry lookup, fallback behavior, family grouping,
and listing functionality.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_runner.models import (
    ModelInfo,
    resolve_model,
    list_models,
    list_families,
    models_in_family,
)


class TestModelRegistry:
    def test_gpt2_small_exists(self):
        info = resolve_model("gpt2-small")
        assert isinstance(info, ModelInfo)
        assert info.model_id == "gpt2-small"
        assert info.family == "gpt2"

    def test_gpt2_medium_exists(self):
        info = resolve_model("gpt2-medium")
        assert info.model_id == "gpt2-medium"
        assert info.n_layers > 0

    def test_pythia_70m_exists(self):
        info = resolve_model("pythia-70m")
        assert info.model_id == "pythia-70m"
        assert info.family == "pythia"

    def test_unknown_model_with_fallback(self):
        protocol = {
            "unit_of_work": {
                "model_id": "unknown-model",
                "model_spec": {"n_layers": 6, "n_heads": 8},
            },
        }
        info = resolve_model("unknown-model", protocol=protocol)
        assert info.model_id == "unknown-model"
        assert info.n_layers == 6

    def test_unknown_model_without_fallback_raises(self):
        with pytest.raises(ValueError, match="Unknown model_id"):
            resolve_model("no_such_model")

    def test_list_models_returns_non_empty(self):
        models = list_models()
        assert len(models) >= 3
        assert "gpt2-small" in models

    def test_list_families(self):
        families = list_families()
        assert "gpt2" in families
        assert "pythia" in families

    def test_models_in_family(self):
        gpt2_models = models_in_family("gpt2")
        assert len(gpt2_models) >= 1
        assert "gpt2-small" in gpt2_models

    def test_model_info_has_tl_name(self):
        info = resolve_model("gpt2-small")
        assert info.transformer_lens_name is not None
        assert len(info.transformer_lens_name) > 0

    def test_model_info_has_layer_and_head_counts(self):
        info = resolve_model("gpt2-small")
        assert info.n_layers == 12
        assert info.n_heads == 12

    def test_model_info_has_d_model(self):
        info = resolve_model("gpt2-small")
        assert info.d_model > 0
