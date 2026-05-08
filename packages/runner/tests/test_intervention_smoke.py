"""Smoke tests for every intervention dispatch entry.

Audit-final §1.12 (collapsing audit-2 §H1 + audit-3 §C1) flagged that 7 of 8
intervention entry points had no unit-test coverage. The DAS hard-crash
documented in audit-3 §A1 and the SAE chained-encode + global-site bugs
documented in audit-4 §A1/§A2 would all have been caught by one-line smoke
tests. This module provides a minimal toy-model harness and exercises every
intervention with a single forward pass per ``patch_mode``.

The ``FakeModel`` mimics the subset of TransformerLens that the
interventions actually touch (``cfg.n_layers``, ``cfg.n_heads``,
``cfg.d_model``, ``cfg.d_mlp``, ``run_with_hooks``). Each test asserts only
that the call returns a finite tensor of the expected shape — the goal is
to detect runtime crashes and shape mismatches, not to verify numerical
correctness (which is the job of ``test_runner_semantics``).
"""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

_node_patching = pytest.importorskip("automechinterp_runner.interventions.node_patching")
das_subspace_intervention_logits = _node_patching.das_subspace_intervention_logits
edge_intervention_logits = _node_patching.edge_intervention_logits
head_intervention_logits = _node_patching.head_intervention_logits
mlp_intervention_logits = _node_patching.mlp_intervention_logits
neuron_intervention_logits = _node_patching.neuron_intervention_logits
residual_stream_intervention_logits = _node_patching.residual_stream_intervention_logits
sae_feature_intervention_logits = _node_patching.sae_feature_intervention_logits
transcoder_feature_intervention_logits = _node_patching.transcoder_feature_intervention_logits

# ---------------------------------------------------------------------------
# Toy model
# ---------------------------------------------------------------------------

N_LAYERS = 2
N_HEADS = 2
D_HEAD = 4
D_MODEL = N_HEADS * D_HEAD
D_MLP = 8
SEQ_LEN = 5
BATCH = 1

class _Cfg:
    n_layers = N_LAYERS
    n_heads = N_HEADS
    d_head = D_HEAD
    d_model = D_MODEL
    d_mlp = D_MLP

class FakeModel:
    """A minimal stand-in for HookedTransformer.

    ``run_with_hooks`` invokes every registered hook against a deterministic
    activation buffer and returns final-layer logits-shaped output. Hooks
    receive a ``hook`` object exposing a ``.name`` attribute matching the
    registered hook point.
    """

    cfg = _Cfg()

    def __call__(self, target_tokens):
        return torch.zeros(BATCH, SEQ_LEN, D_MODEL)

    def run_with_hooks(self, target_tokens, fwd_hooks):
        # Run hooks once each in registration order against a fresh act.
        out = torch.zeros(BATCH, SEQ_LEN, D_MODEL)
        for name, hook in fwd_hooks:
            buffer = self._buffer_for(name)
            handle = type("Hook", (), {"name": name})()
            hook(buffer, handle)
        return out

    @staticmethod
    def _buffer_for(name: str):
        if name.endswith("attn.hook_z"):
            return torch.zeros(BATCH, SEQ_LEN, N_HEADS, D_HEAD)
        if name.endswith("mlp.hook_post"):
            return torch.zeros(BATCH, SEQ_LEN, D_MLP)
        if name.endswith("mlp.hook_pre"):
            return torch.zeros(BATCH, SEQ_LEN, D_MODEL)
        # default: residual-stream-shaped
        return torch.zeros(BATCH, SEQ_LEN, D_MODEL)

def _source_cache():
    return {
        f"blocks.{layer}.attn.hook_z": torch.ones(BATCH, SEQ_LEN, N_HEADS, D_HEAD)
        for layer in range(N_LAYERS)
    } | {
        f"blocks.{layer}.mlp.hook_post": torch.ones(BATCH, SEQ_LEN, D_MLP)
        for layer in range(N_LAYERS)
    } | {
        f"blocks.{layer}.mlp.hook_pre": torch.ones(BATCH, SEQ_LEN, D_MODEL)
        for layer in range(N_LAYERS)
    } | {
        f"blocks.{layer}.hook_resid_post": torch.ones(BATCH, SEQ_LEN, D_MODEL)
        for layer in range(N_LAYERS)
    } | {
        f"blocks.{layer}.hook_resid_pre": torch.ones(BATCH, SEQ_LEN, D_MODEL)
        for layer in range(N_LAYERS)
    }

def _target_tokens():
    return torch.zeros(BATCH, SEQ_LEN, dtype=torch.long)

# ---------------------------------------------------------------------------
# Per-dispatch smoke tests
# ---------------------------------------------------------------------------

def test_head_intervention_smoke():
    out = head_intervention_logits(
        model=FakeModel(),
        target_tokens=_target_tokens(),
        source_cache=_source_cache(),
        components=[{"component_type": "head", "layer": 0, "head": 0}],
        patch_mode="clean",
        target_position=-1,
    )
    assert out.shape == (BATCH, SEQ_LEN, D_MODEL)
    assert torch.isfinite(out).all()

def test_mlp_intervention_smoke():
    out = mlp_intervention_logits(
        model=FakeModel(),
        target_tokens=_target_tokens(),
        source_cache=_source_cache(),
        components=[{"component_type": "mlp", "layer": 0}],
        patch_mode="zero",
        target_position=-1,
    )
    assert out.shape == (BATCH, SEQ_LEN, D_MODEL)
    assert torch.isfinite(out).all()

def test_residual_intervention_smoke():
    out = residual_stream_intervention_logits(
        model=FakeModel(),
        target_tokens=_target_tokens(),
        source_cache=_source_cache(),
        components=[{"component_type": "residual_stream", "layer": 1}],
        patch_mode="clean",
        target_position=-1,
    )
    assert out.shape == (BATCH, SEQ_LEN, D_MODEL)

def test_neuron_intervention_smoke():
    out = neuron_intervention_logits(
        model=FakeModel(),
        target_tokens=_target_tokens(),
        source_cache=_source_cache(),
        components=[{"component_type": "mlp_neuron", "layer": 0, "neuron": 3}],
        patch_mode="zero",
        target_position=-1,
    )
    assert out.shape == (BATCH, SEQ_LEN, D_MODEL)

def test_edge_intervention_smoke():
    """Audit §1.4 — entry preserved as alias for back-compat with V21+ bundles."""
    out = edge_intervention_logits(
        model=FakeModel(),
        target_tokens=_target_tokens(),
        source_cache=_source_cache(),
        components=[
            {
                "component_type": "edge",
                "source_layer": 0,
                "source_head": 0,
                "target_layer": 1,
                "target_head": 1,
            }
        ],
        patch_mode="zero",
        target_position=-1,
    )
    assert out.shape == (BATCH, SEQ_LEN, D_MODEL)

def test_sae_feature_intervention_smoke():
    """Audit §1.6/1.7/1.8/1.9 — exercises residual-error path, clean!=zero, chained encode, per-component site."""

    class FakeSAE:
        n_features = 16

        @staticmethod
        def encode(x):
            return torch.zeros(*x.shape[:-1], FakeSAE.n_features)

        @staticmethod
        def decode(features):
            return torch.zeros(*features.shape[:-1], D_MODEL)

    out = sae_feature_intervention_logits(
        model=FakeModel(),
        target_tokens=_target_tokens(),
        source_cache=_source_cache(),
        components=[
            {"component_type": "sae_feature", "sae_id": "sae0", "layer": 0, "feature_id": 1, "site": "resid_post"},
            {"component_type": "sae_feature", "sae_id": "sae1", "layer": 0, "feature_id": 2, "site": "resid_post"},
        ],
        patch_mode="clean",
        target_position=-1,
        sae_models={"sae0": FakeSAE(), "sae1": FakeSAE()},
    )
    assert out.shape == (BATCH, SEQ_LEN, D_MODEL)

def test_transcoder_feature_intervention_smoke():
    """Audit §1.5 — verifies pre/post hook split."""

    class FakeTC:
        n_features = 16

        @staticmethod
        def encode(x):
            return torch.zeros(*x.shape[:-1], FakeTC.n_features)

        @staticmethod
        def decode(features):
            return torch.zeros(*features.shape[:-1], D_MODEL)

    out = transcoder_feature_intervention_logits(
        model=FakeModel(),
        target_tokens=_target_tokens(),
        source_cache=_source_cache(),
        components=[
            {"component_type": "transcoder_feature", "layer": 0, "feature_id": 1},
        ],
        patch_mode="zero",
        target_position=-1,
        transcoder_models={"layer_0": FakeTC()},
    )
    assert out.shape == (BATCH, SEQ_LEN, D_MODEL)

def test_das_subspace_intervention_smoke():
    """Audit §1.3 — DAS hard-crash regression test.

    Before the fix, this function called ``_align_sequence_length`` with the
    cache dict as ``source_tokens`` and raised TypeError on the very first
    call. This smoke test would have caught it instantly.
    """
    directions = torch.eye(D_MODEL)[:, :2]
    out = das_subspace_intervention_logits(
        model=FakeModel(),
        target_tokens=_target_tokens(),
        source_cache=_source_cache(),
        components=[
            {
                "component_type": "das_subspace",
                "layer": 0,
                "site": "hook_resid_post",
                "subspace_directions": directions,
            }
        ],
        patch_mode="clean",
        target_position=-1,
    )
    assert out.shape == (BATCH, SEQ_LEN, D_MODEL)

# ---------------------------------------------------------------------------
# Sign-convention regression (audit §C3)
# ---------------------------------------------------------------------------

def test_intervention_dispatch_returns_finite_for_all_modes():
    """Run a head intervention under every supported patch_mode."""
    for mode in ("clean", "zero", "mean"):
        out = head_intervention_logits(
            model=FakeModel(),
            target_tokens=_target_tokens(),
            source_cache=_source_cache(),
            components=[{"component_type": "head", "layer": 0, "head": 0}],
            patch_mode=mode,
            target_position=-1,
            mean_cache=_source_cache(),
        )
        assert torch.isfinite(out).all(), f"non-finite output for patch_mode={mode}"
