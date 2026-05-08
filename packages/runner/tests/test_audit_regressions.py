"""Regression tests for runner fixes documented in ``final_opus_audit.md``.

§1.6 — ``neuron_intervention_logits`` must raise ``ValueError`` rather than
       silently fall back to zero ablation when the requested ``patch_mode``
       is incompatible with the supplied caches/parameters. Mean / clean
       ablation results are statistically distinct from zero ablation, and
       silent degradation contaminates treatment effects without surfacing
       in cell metadata.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from automechinterp_runner.interventions.node_patching import (
    neuron_intervention_logits,
)

class _StubModel:
    """Minimal stand-in for HookedTransformer.

    The validation branch of ``neuron_intervention_logits`` runs before any
    forward pass, so we only need ``cfg.n_layers`` to be defined.
    """

    def __init__(self, n_layers: int = 4) -> None:
        self.cfg = SimpleNamespace(n_layers=n_layers)

@pytest.fixture
def neuron_components() -> list[dict]:
    return [
        {"component_type": "mlp_neuron", "layer": 0, "neuron": 5},
    ]

def test_clean_without_source_cache_raises(neuron_components: list[dict]) -> None:
    with pytest.raises(ValueError, match="source_cache"):
        neuron_intervention_logits(
            model=_StubModel(),
            target_tokens=None,
            source_cache=None,
            components=neuron_components,
            patch_mode="clean",
            target_position=-1,
        )

def test_mean_without_mean_cache_raises(neuron_components: list[dict]) -> None:
    with pytest.raises(ValueError, match="mean_cache"):
        neuron_intervention_logits(
            model=_StubModel(),
            target_tokens=None,
            source_cache=object(),
            components=neuron_components,
            patch_mode="mean",
            target_position=-1,
            mean_cache=None,
        )

def test_clamp_without_clamp_value_raises(neuron_components: list[dict]) -> None:
    with pytest.raises(ValueError, match="clamp_value"):
        neuron_intervention_logits(
            model=_StubModel(),
            target_tokens=None,
            source_cache=object(),
            components=neuron_components,
            patch_mode="clamp",
            target_position=-1,
            clamp_value=None,
        )

def test_unknown_patch_mode_raises(neuron_components: list[dict]) -> None:
    with pytest.raises(ValueError, match="unsupported patch_mode"):
        neuron_intervention_logits(
            model=_StubModel(),
            target_tokens=None,
            source_cache=object(),
            components=neuron_components,
            patch_mode="bogus",
            target_position=-1,
        )

# ---------------------------------------------------------------------------
# §1.7 — sae_feature_intervention_logits raises on missing caches
# ---------------------------------------------------------------------------

from automechinterp_runner.interventions.node_patching import (
    sae_feature_intervention_logits,
    adjacent_head_components,
)

@pytest.fixture
def sae_components() -> list[dict]:
    return [
        {"component_type": "sae_feature", "sae_id": "sae0", "layer": 0, "feature_id": 3},
    ]

def _stub_sae_models() -> dict:
    # The upfront validator runs before any SAE is touched; an empty stand-in
    # model dict that registers the sae_id is enough to bypass the
    # ``sae_models`` guard while still hitting the patch_mode guards.
    return {"sae0": object()}

def test_sae_clean_without_source_cache_raises(sae_components: list[dict]) -> None:
    with pytest.raises(ValueError, match="source_cache"):
        sae_feature_intervention_logits(
            model=_StubModel(),
            target_tokens=None,
            source_cache=None,
            components=sae_components,
            patch_mode="clean",
            target_position=-1,
            sae_models=_stub_sae_models(),
        )

def test_sae_mean_without_mean_cache_raises(sae_components: list[dict]) -> None:
    with pytest.raises(ValueError, match="mean_cache"):
        sae_feature_intervention_logits(
            model=_StubModel(),
            target_tokens=None,
            source_cache=object(),
            components=sae_components,
            patch_mode="mean",
            target_position=-1,
            mean_cache=None,
            sae_models=_stub_sae_models(),
        )

def test_sae_unknown_patch_mode_raises(sae_components: list[dict]) -> None:
    with pytest.raises(ValueError, match="unsupported patch_mode"):
        sae_feature_intervention_logits(
            model=_StubModel(),
            target_tokens=None,
            source_cache=object(),
            components=sae_components,
            patch_mode="bogus",
            target_position=-1,
            sae_models=_stub_sae_models(),
        )

# ---------------------------------------------------------------------------
# §1.9 — adjacent_head_components clamps at the boundary instead of wrapping
# ---------------------------------------------------------------------------

def test_adjacent_head_clamps_last_head() -> None:
    """For 12-head model, head 11's adjacent control must be 10, not 0."""
    out = adjacent_head_components(
        [{"component_type": "head", "layer": 5, "head": 11}], n_heads=12
    )
    assert out[0]["head"] == 10
    assert out[0]["selection_source"] == "adjacent_head_control"

def test_adjacent_head_steps_up_when_room() -> None:
    out = adjacent_head_components(
        [{"component_type": "head", "layer": 5, "head": 3}], n_heads=12
    )
    assert out[0]["head"] == 4

# ---------------------------------------------------------------------------
# §1.17 — intervention numeric correctness (now that torch is installed)
# ---------------------------------------------------------------------------

import torch  # noqa: E402  (deferred import keeps non-torch tests running)

from automechinterp_runner.interventions.node_patching import (  # noqa: E402
    head_intervention_logits,
    _apply_patch,
)

class _RealCfg:
    n_layers = 2
    n_heads = 4
    d_head = 3
    d_model = 12
    d_mlp = 8

class _CapturingModel:
    """FakeModel variant that captures the post-hook buffer for assertion."""

    cfg = _RealCfg()
    BATCH = 1
    SEQ = 4

    def __init__(self) -> None:
        self.captured: dict[str, torch.Tensor] = {}

    def __call__(self, target_tokens):  # pragma: no cover - smoke fallback
        return torch.zeros(self.BATCH, self.SEQ, self.cfg.d_model)

    def run_with_hooks(self, target_tokens, fwd_hooks):
        for name, hook in fwd_hooks:
            buf = self._buffer_for(name).clone()
            handle = type("Hook", (), {"name": name})()
            hook(buf, handle)
            self.captured[name] = buf
        return torch.zeros(self.BATCH, self.SEQ, self.cfg.d_model)

    def _buffer_for(self, name: str) -> torch.Tensor:
        # Pre-hook activation: a constant tensor of 7.0 so that any change
        # by the patch is unambiguously detectable.
        if name.endswith("attn.hook_z"):
            return torch.full(
                (self.BATCH, self.SEQ, self.cfg.n_heads, self.cfg.d_head), 7.0
            )
        return torch.full((self.BATCH, self.SEQ, self.cfg.d_model), 7.0)

def _ones_z_cache(value: float = 1.0) -> dict[str, torch.Tensor]:
    return {
        f"blocks.{layer}.attn.hook_z": torch.full(
            (1, 4, _RealCfg.n_heads, _RealCfg.d_head), value
        )
        for layer in range(_RealCfg.n_layers)
    }

def test_head_zero_ablation_actually_zeros_target_head() -> None:
    """§1.17(a): zero-mode patch must set targeted head to 0 at target_position."""
    model = _CapturingModel()
    head_intervention_logits(
        model=model,
        target_tokens=torch.zeros(1, 4, dtype=torch.long),
        source_cache=None,
        components=[{"component_type": "head", "layer": 1, "head": 2}],
        patch_mode="zero",
        target_position=-1,
    )
    z = model.captured["blocks.1.attn.hook_z"]
    # target_position = -1 → last position (3)
    assert torch.equal(z[:, 3, 2, :], torch.zeros(1, _RealCfg.d_head))
    # Other heads at the same position must remain at the pre-hook value (7.0)
    for h in (0, 1, 3):
        assert torch.equal(z[:, 3, h, :], torch.full((1, _RealCfg.d_head), 7.0))
    # Other positions for the targeted head must remain untouched.
    for p in (0, 1, 2):
        assert torch.equal(z[:, p, 2, :], torch.full((1, _RealCfg.d_head), 7.0))

def test_head_mean_uses_mean_cache_not_zero() -> None:
    """§1.17(c): mean and zero must produce numerically distinct outcomes."""
    mean_cache = _ones_z_cache(value=3.5)
    model = _CapturingModel()
    head_intervention_logits(
        model=model,
        target_tokens=torch.zeros(1, 4, dtype=torch.long),
        source_cache=None,
        components=[{"component_type": "head", "layer": 0, "head": 1}],
        patch_mode="mean",
        target_position=-1,
        mean_cache=mean_cache,
    )
    z_mean = model.captured["blocks.0.attn.hook_z"]
    # Mean-mode must place the mean-cache value (3.5) at the target site,
    # not 0.0 (which is what a silent zero fallback would produce).
    assert torch.equal(z_mean[:, 3, 1, :], torch.full((1, _RealCfg.d_head), 3.5))

def test_head_mean_without_cache_raises() -> None:
    """§1.17(b): mean-mode without mean_cache must raise, not silently zero-fill."""
    with pytest.raises(ValueError, match="mean_cache"):
        head_intervention_logits(
            model=_CapturingModel(),
            target_tokens=torch.zeros(1, 4, dtype=torch.long),
            source_cache=None,
            components=[{"component_type": "head", "layer": 0, "head": 0}],
            patch_mode="mean",
            target_position=-1,
            mean_cache=None,
        )

def test_apply_patch_mean_full_position_uses_cache() -> None:
    """§1.17(c) parallel for the no-head-index branch (MLP / residual)."""
    tensor = torch.full((1, 4, _RealCfg.d_model), 7.0)
    mean_buf = torch.full((1, 4, _RealCfg.d_model), 2.25)
    _apply_patch(tensor, source=None, position=2, index=None, patch_mode="mean", mean_cache=mean_buf)
    assert torch.equal(tensor[:, 2, :], torch.full((1, _RealCfg.d_model), 2.25))
    # Position 3 must remain at the pre-patch value.
    assert torch.equal(tensor[:, 3, :], torch.full((1, _RealCfg.d_model), 7.0))

# ---------------------------------------------------------------------------
# final_critical_audit_v2.md §1 — adjacent component clamp for mlp_neuron and
# sae_feature so the V7 negative control never degenerates into a silent
# null intervention via an out-of-range index.
# ---------------------------------------------------------------------------

from automechinterp_runner.runner import _adjacent_components  # noqa: E402

def test_adjacent_neuron_clamps_at_d_mlp_boundary() -> None:
    """The last neuron must step backward, not overflow past ``d_mlp``."""
    out = _adjacent_components(
        [{"component_type": "mlp_neuron", "layer": 3, "neuron": 3071}],
        n_heads=12,
        d_mlp=3072,
    )
    assert out[0]["neuron"] == 3070

def test_adjacent_neuron_steps_up_when_room() -> None:
    """A non-boundary neuron preserves the legacy ``neuron + 1`` semantics."""
    out = _adjacent_components(
        [{"component_type": "mlp_neuron", "layer": 1, "neuron": 100}],
        n_heads=12,
        d_mlp=3072,
    )
    assert out[0]["neuron"] == 101

def test_adjacent_neuron_without_d_mlp_steps_backward_for_nonzero() -> None:
    """When ``d_mlp`` is unknown, prefer the safer ``neuron - 1`` direction."""
    out = _adjacent_components(
        [{"component_type": "mlp_neuron", "layer": 1, "neuron": 100}],
        n_heads=12,
        d_mlp=0,
    )
    assert out[0]["neuron"] == 99

def test_adjacent_neuron_zero_steps_up() -> None:
    """neuron 0 must step up since there is no neuron -1."""
    out = _adjacent_components(
        [{"component_type": "mlp_neuron", "layer": 0, "neuron": 0}],
        n_heads=12,
        d_mlp=3072,
    )
    assert out[0]["neuron"] == 1

def test_adjacent_sae_feature_steps_back_for_nonzero() -> None:
    """SAE width is not on model.cfg; the helper steps backward when possible."""
    out = _adjacent_components(
        [{"component_type": "sae_feature", "sae_id": "s0", "layer": 0, "feature_id": 5678}],
        n_heads=12,
    )
    assert out[0]["feature_id"] == 5677

def test_adjacent_sae_feature_zero_steps_up() -> None:
    out = _adjacent_components(
        [{"component_type": "sae_feature", "sae_id": "s0", "layer": 0, "feature_id": 0}],
        n_heads=12,
    )
    assert out[0]["feature_id"] == 1

def test_adjacent_unknown_type_passes_through() -> None:
    """Unknown component types are passed through unchanged so callers do not
    silently lose components."""
    out = _adjacent_components(
        [{"component_type": "edge", "from_layer": 1, "to_layer": 2}],
        n_heads=12,
    )
    assert out[0] == {"component_type": "edge", "from_layer": 1, "to_layer": 2}
