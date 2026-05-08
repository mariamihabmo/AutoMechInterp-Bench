"""Node-level, edge-level, neuron-level, and SAE-feature interventions.

V10: Multi-lane architecture — added neuron_intervention_logits for
individual MLP neuron patching, sae_feature_intervention_logits for
SAE encode→ablate→decode patching, and control helpers for neurons
and SAE features.
"""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any

# ---------------------------------------------------------------------------
# Sequence-length alignment (Pitfall #61)
# ---------------------------------------------------------------------------

def _align_sequence_length(
    target_tokens: Any,
    source_tokens: Any | None = None,
    *,
    warn: bool = True,
) -> tuple[Any, Any | None]:
    """Ensure target and source tokens have aligned sequence lengths.

    If source_tokens is provided and has a different length, truncate the
    longer one to match. This prevents silent misalignment when patching
    across prompts with different tokenization lengths.

    Note on BOS shifts: TransformerLens prepends a BOS token by default.
    When using position=-1, this is handled correctly. When using explicit
    positions, callers must account for the BOS offset.
    """
    if source_tokens is None:
        return target_tokens, None

    t_len = target_tokens.shape[-1] if hasattr(target_tokens, 'shape') else len(target_tokens)
    s_len = source_tokens.shape[-1] if hasattr(source_tokens, 'shape') else len(source_tokens)

    if t_len != s_len:
        min_len = min(t_len, s_len)
        target_tokens = target_tokens[:, :min_len] if hasattr(target_tokens, 'shape') else target_tokens[:min_len]
        if source_tokens is not None:
            source_tokens = source_tokens[:, :min_len] if hasattr(source_tokens, 'shape') else source_tokens[:min_len]

    return target_tokens, source_tokens

def _normalize_position(position: int, seq_len: int) -> int:
    if position < 0:
        pos = seq_len + position
    else:
        pos = position
    pos = max(0, min(seq_len - 1, pos))
    return pos

# ---------------------------------------------------------------------------
# Component grouping helpers
# ---------------------------------------------------------------------------

def _group_head_components(components: list[dict[str, Any]], n_layers: int, n_heads: int) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for comp in components:
        if comp.get("component_type") != "head":
            continue
        layer = int(comp.get("layer", -1))
        head = int(comp.get("head", -1))
        if layer < 0 or layer >= n_layers or head < 0 or head >= n_heads:
            continue
        grouped[layer].append(head)
    return dict(grouped)

def _group_mlp_components(components: list[dict[str, Any]], n_layers: int) -> list[int]:
    """Extract MLP layer indices from components."""
    layers: list[int] = []
    for comp in components:
        if comp.get("component_type") != "mlp":
            continue
        layer = int(comp.get("layer", -1))
        if 0 <= layer < n_layers:
            layers.append(layer)
    return sorted(set(layers))

def _group_residual_components(components: list[dict[str, Any]], n_layers: int) -> list[int]:
    """Extract residual stream layer indices from components."""
    layers: list[int] = []
    for comp in components:
        if comp.get("component_type") != "residual_stream":
            continue
        layer = int(comp.get("layer", -1))
        if 0 <= layer < n_layers:
            layers.append(layer)
    return sorted(set(layers))

def _group_edge_components(
    components: list[dict[str, Any]], n_layers: int, n_heads: int,
) -> list[dict[str, Any]]:
    """Extract edge (composition) specifications from components.

    Each edge component specifies a source head and a target head,
    representing the composition path source_head → target_head.
    """
    edges: list[dict[str, Any]] = []
    for comp in components:
        if comp.get("component_type") != "edge":
            continue
        src_layer = int(comp.get("source_layer", -1))
        src_head = int(comp.get("source_head", -1))
        tgt_layer = int(comp.get("target_layer", -1))
        tgt_head = int(comp.get("target_head", -1))

        if not (0 <= src_layer < n_layers and 0 <= src_head < n_heads):
            continue
        if not (0 <= tgt_layer < n_layers and 0 <= tgt_head < n_heads):
            continue
        if src_layer >= tgt_layer:
            continue  # edges must flow forward

        edges.append({
            "source_layer": src_layer,
            "source_head": src_head,
            "target_layer": tgt_layer,
            "target_head": tgt_head,
        })
    return edges

# ---------------------------------------------------------------------------
# Component generators (for controls)
# ---------------------------------------------------------------------------

def shift_layers(components: list[dict[str, Any]], n_layers: int) -> list[dict[str, Any]]:
    shifted = []
    for comp in components:
        ctype = comp.get("component_type", "")
        if ctype not in (
            "head", "mlp", "residual_stream", "edge",
            "mlp_neuron", "sae_feature", "das_subspace",
        ):
            continue
        new = {**comp}
        if "layer" in new:
            new["layer"] = (int(new["layer"]) + 1) % n_layers
        if "source_layer" in new:
            new["source_layer"] = (int(new["source_layer"]) + 1) % n_layers
        if "target_layer" in new:
            new["target_layer"] = (int(new["target_layer"]) + 1) % n_layers
        shifted.append(new)
    return shifted

def random_head_components(n_layers: int, n_heads: int, count: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    for _ in range(max(1, count)):
        rows.append(
            {
                "component_type": "head",
                "layer": rng.randrange(n_layers),
                "head": rng.randrange(n_heads),
                "selection_source": "random_control",
            }
        )
    return rows

def random_mlp_components(n_layers: int, count: int, seed: int) -> list[dict[str, Any]]:
    """Generate random MLP layer components for controls."""
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    for _ in range(max(1, count)):
        rows.append(
            {
                "component_type": "mlp",
                "layer": rng.randrange(n_layers),
                "selection_source": "random_control",
            }
        )
    return rows

def random_edge_components(n_layers: int, n_heads: int, count: int, seed: int) -> list[dict[str, Any]]:
    """Generate random edge (composition) components for controls."""
    # a single-layer model has no edge
    # composition path; ``rng.randrange(src_layer + 1, n_layers)`` would
    # otherwise raise ``ValueError: empty range`` deep inside the loop. Fail
    # closed early with a clear message rather than allow that obscure
    # crash. None of the released models have <2 layers, so this is
    # defensive only.
    if n_layers < 2:
        raise ValueError(
            f"random_edge_components requires n_layers>=2 to form a composition path; got n_layers={n_layers}"
        )
    if n_heads < 1:
        raise ValueError(f"random_edge_components requires n_heads>=1; got n_heads={n_heads}")
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    for _ in range(max(1, count)):
        src_layer = rng.randrange(max(1, n_layers - 1))
        tgt_layer = rng.randrange(src_layer + 1, n_layers)
        rows.append(
            {
                "component_type": "edge",
                "source_layer": src_layer,
                "source_head": rng.randrange(n_heads),
                "target_layer": tgt_layer,
                "target_head": rng.randrange(n_heads),
                "selection_source": "random_control",
            }
        )
    return rows

def adjacent_head_components(
    components: list[dict[str, Any]], n_heads: int,
) -> list[dict[str, Any]]:
    """Generate adjacent-head control: shift each head index by +1.

    previously this used modulo arithmetic
    (``(head + 1) % n_heads``) which wraps the last head's "adjacent" control
    back to head 0 — for a 12-head model, head 11's neighbour was head 0,
    which is not strict adjacency. We now clamp at the upper boundary by
    stepping ``-1`` instead of ``+1`` whenever the next index would overflow.

    a single-head model has no
    "adjacent" head and the previous fallback ``max(0, head - 1)`` returned
    head 0 — i.e., a no-op control. Fail closed instead so a future
    diagnostic toy model with ``n_heads<2`` cannot silently weaken the
    control signal.
    """
    if n_heads < 2:
        raise ValueError(
            f"adjacent_head_components requires n_heads>=2 to form a strict-adjacency control; got n_heads={n_heads}"
        )
    shifted: list[dict[str, Any]] = []
    for comp in components:
        if comp.get("component_type") != "head":
            continue
        head = int(comp["head"])
        if head + 1 < n_heads:
            adj = head + 1
        else:
            adj = max(0, head - 1)
        shifted.append({
            **comp,
            "head": adj,
            "selection_source": "adjacent_head_control",
        })
    return shifted

# ---------------------------------------------------------------------------
# Patch application
# ---------------------------------------------------------------------------

def _apply_patch(
    tensor: Any,
    source: Any,
    position: int,
    index: int | None,
    patch_mode: str,
    mean_cache: Any | None = None,
) -> Any:
    """Apply a patch to a tensor at given position and optional index.

    Supports: clean (from source), zero, mean (from precomputed mean cache).
    Handles source/target sequence length mismatches by clamping source position.

    Audit-final §gpt.P1.6 / §gemini.5: ``patch_mode='mean'`` with a missing
    ``mean_cache`` is now a hard ``ValueError`` rather than a silent fallback
    to zero ablation. Mean-ablation and zero-ablation are distinct controls;
    silently degrading the former into the latter contaminates treatment
    statistics in a way that is not visible from the cell metadata.
    """
    if index is not None:
        if patch_mode == "clean":
            src_pos = min(position, source.shape[1] - 1)
            tensor[:, position, index, :] = source[:, src_pos, index, :]
        elif patch_mode == "zero":
            tensor[:, position, index, :] = 0.0
        elif patch_mode == "mean":
            if mean_cache is None:
                raise ValueError(
                    "_apply_patch(patch_mode='mean'): mean_cache is None for "
                    "head-indexed patch; refusing to silently fall back to zero "
                    "ablation. Provide a populated mean_cache from the runner "
                    "or use patch_mode='zero' explicitly."
                )
            mc_pos = min(position, mean_cache.shape[1] - 1)
            tensor[:, position, index, :] = mean_cache[:, mc_pos, index, :]
        else:
            raise ValueError(f"Unsupported patch_mode: {patch_mode}")
    else:
        # Full-position for MLP / residual stream (no head index)
        if patch_mode == "clean":
            src_pos = min(position, source.shape[1] - 1)
            tensor[:, position, :] = source[:, src_pos, :]
        elif patch_mode == "zero":
            tensor[:, position, :] = 0.0
        elif patch_mode == "mean":
            if mean_cache is None:
                raise ValueError(
                    "_apply_patch(patch_mode='mean'): mean_cache is None for "
                    "full-position patch; refusing to silently fall back to "
                    "zero ablation. Provide a populated mean_cache from the "
                    "runner or use patch_mode='zero' explicitly."
                )
            mc_pos = min(position, mean_cache.shape[1] - 1)
            tensor[:, position, :] = mean_cache[:, mc_pos, :]
        else:
            raise ValueError(f"Unsupported patch_mode: {patch_mode}")
    return tensor

# ---------------------------------------------------------------------------
# Intervention functions
# ---------------------------------------------------------------------------

def head_intervention_logits(
    *,
    model: Any,
    target_tokens: Any,
    source_cache: Any,
    components: list[dict[str, Any]],
    patch_mode: str,
    target_position: int,
    mean_cache: Any | None = None,
) -> Any:
    """Run head-level intervention (attn.hook_z)."""
    n_layers = int(model.cfg.n_layers)
    n_heads = int(model.cfg.n_heads)
    grouped = _group_head_components(components, n_layers=n_layers, n_heads=n_heads)
    if not grouped:
        return model(target_tokens)

    def make_hook(layer: int):
        def hook_fn(z, hook):
            seq_len = z.shape[1]
            pos = _normalize_position(target_position, seq_len)
            for head in grouped[layer]:
                source = source_cache[hook.name] if source_cache is not None else None
                mc = mean_cache[hook.name] if mean_cache is not None and hook.name in mean_cache else None
                _apply_patch(z, source, pos, head, patch_mode, mc)
            return z

        return hook_fn

    hooks = [(f"blocks.{layer}.attn.hook_z", make_hook(layer)) for layer in sorted(grouped)]
    return model.run_with_hooks(target_tokens, fwd_hooks=hooks)

def mlp_intervention_logits(
    *,
    model: Any,
    target_tokens: Any,
    source_cache: Any,
    components: list[dict[str, Any]],
    patch_mode: str,
    target_position: int,
    mean_cache: Any | None = None,
) -> Any:
    """Run MLP-level intervention (mlp.hook_post)."""
    n_layers = int(model.cfg.n_layers)
    mlp_layers = _group_mlp_components(components, n_layers)
    if not mlp_layers:
        return model(target_tokens)

    def make_hook(layer: int):
        def hook_fn(act, hook):
            seq_len = act.shape[1]
            pos = _normalize_position(target_position, seq_len)
            source = source_cache[hook.name] if source_cache is not None else None
            mc = mean_cache[hook.name] if mean_cache is not None and hook.name in mean_cache else None
            _apply_patch(act, source, pos, None, patch_mode, mc)
            return act

        return hook_fn

    hooks = [(f"blocks.{layer}.mlp.hook_post", make_hook(layer)) for layer in mlp_layers]
    return model.run_with_hooks(target_tokens, fwd_hooks=hooks)

def residual_stream_intervention_logits(
    *,
    model: Any,
    target_tokens: Any,
    source_cache: Any,
    components: list[dict[str, Any]],
    patch_mode: str,
    target_position: int,
    mean_cache: Any | None = None,
) -> Any:
    """Run residual-stream intervention (hook_resid_post)."""
    n_layers = int(model.cfg.n_layers)
    resid_layers = _group_residual_components(components, n_layers)
    if not resid_layers:
        return model(target_tokens)

    def make_hook(layer: int):
        def hook_fn(resid, hook):
            seq_len = resid.shape[1]
            pos = _normalize_position(target_position, seq_len)
            source = source_cache[hook.name] if source_cache is not None else None
            mc = mean_cache[hook.name] if mean_cache is not None and hook.name in mean_cache else None
            _apply_patch(resid, source, pos, None, patch_mode, mc)
            return resid

        return hook_fn

    hooks = [(f"blocks.{layer}.hook_resid_post", make_hook(layer)) for layer in resid_layers]
    return model.run_with_hooks(target_tokens, fwd_hooks=hooks)

def edge_intervention_logits(
    *,
    model: Any,
    target_tokens: Any,
    source_cache: Any,
    components: list[dict[str, Any]],
    patch_mode: str,
    target_position: int,
    mean_cache: Any | None = None,
) -> Any:
    """Edge intervention: ablate the source head's output at the source layer.

    .. warning::
        Despite the name, this is **not** path-patching in the sense of
        Goldowsky-Dill et al. (2023). The current implementation patches the
        ``attn.hook_z`` slot for the source head only; the declared
        ``target_head`` and ``target_layer`` are recorded for bookkeeping but
        do not constrain the patch's downstream propagation. The effect that
        reaches the target layer is therefore the source head's effect on
        *every* downstream computation, not the source→target edge in
        isolation.

        Bundles authored against this entry point should be interpreted as
        "source head ablation" claims rather than "edge composition" claims.
        A true path-patching implementation requires a two-pass forward
        (freeze residual stream at intervening layers, then add back the
        clean source contribution at exactly the target's residual input)
        and is tracked as future work.

    The historical name is preserved for back-compat with V21+ bundles that
    declare ``component_type: "edge"``; see
    :func:`source_head_ablation_intervention_logits` for the canonical name.
    """
    n_layers = int(model.cfg.n_layers)
    n_heads = int(model.cfg.n_heads)
    edges = _group_edge_components(components, n_layers, n_heads)
    if not edges:
        return model(target_tokens)

    # Group edges by source layer for efficient hooking
    source_hooks: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        source_hooks[edge["source_layer"]].append(edge)

    def make_hook(layer: int, layer_edges: list[dict[str, Any]]):
        def hook_fn(z, hook):
            seq_len = z.shape[1]
            pos = _normalize_position(target_position, seq_len)
            for edge in layer_edges:
                src_head = edge["source_head"]
                source = source_cache[hook.name] if source_cache is not None else None
                mc = mean_cache[hook.name] if mean_cache is not None and hook.name in mean_cache else None
                _apply_patch(z, source, pos, src_head, patch_mode, mc)
            return z

        return hook_fn

    hooks = [
        (f"blocks.{layer}.attn.hook_z", make_hook(layer, layer_edges))
        for layer, layer_edges in sorted(source_hooks.items())
    ]
    return model.run_with_hooks(target_tokens, fwd_hooks=hooks)

# Canonical name. ``edge_intervention_logits`` is retained as an alias above
# but new code should call this function and new bundles should use
# ``component_type: "source_head_ablation"`` once the contract bumps.
source_head_ablation_intervention_logits = edge_intervention_logits

# ---------------------------------------------------------------------------
# Neuron-level intervention (V10: mlp_neuron)
# ---------------------------------------------------------------------------

def _group_neuron_components(
    components: list[dict[str, Any]], n_layers: int,
) -> dict[int, list[int]]:
    """Group mlp_neuron components by layer → [neuron indices]."""
    grouped: dict[int, list[int]] = defaultdict(list)
    for comp in components:
        if comp.get("component_type") != "mlp_neuron":
            continue
        layer = int(comp.get("layer", -1))
        neuron = int(comp.get("neuron", -1))
        if 0 <= layer < n_layers and neuron >= 0:
            grouped[layer].append(neuron)
    return dict(grouped)

def neuron_intervention_logits(
    *,
    model: Any,
    target_tokens: Any,
    source_cache: Any,
    components: list[dict[str, Any]],
    patch_mode: str,
    target_position: int,
    mean_cache: Any | None = None,
    clamp_value: float | None = None,
) -> Any:
    """Patch individual MLP neurons at mlp.hook_post.

    For each targeted neuron, replaces its activation at the target
    position with:
    - ``clean``: the activation from source_cache
    - ``zero``: zeroed out
    - ``mean``: mean activation from mean_cache
    - ``clamp``: clamped to ``clamp_value``
    """
    n_layers = int(model.cfg.n_layers)
    grouped = _group_neuron_components(components, n_layers)
    if not grouped:
        return model(target_tokens)

    # refuse to silently fall back to zero ablation
    # when the requested patch_mode is incompatible with the supplied caches.
    # Mean and clean ablations are distinct controls from zero ablation;
    # silent degradation contaminates treatment statistics without surfacing
    # in cell metadata.  This mirrors `_apply_patch` (used by head / MLP /
    # residual interventions), which raises rather than degrades.
    if patch_mode == "clean" and source_cache is None:
        raise ValueError(
            "neuron_intervention_logits: patch_mode='clean' requires a populated "
            "source_cache; refusing to silently fall back to zero ablation."
        )
    if patch_mode == "mean" and mean_cache is None:
        raise ValueError(
            "neuron_intervention_logits: patch_mode='mean' requires a populated "
            "mean_cache; refusing to silently fall back to zero ablation."
        )
    if patch_mode == "clamp" and clamp_value is None:
        raise ValueError(
            "neuron_intervention_logits: patch_mode='clamp' requires a clamp_value."
        )
    if patch_mode not in ("clean", "zero", "mean", "clamp"):
        raise ValueError(
            f"neuron_intervention_logits: unsupported patch_mode={patch_mode!r}"
        )

    def make_hook(layer: int):
        def hook_fn(act, hook):
            # act shape: [batch, seq, d_mlp]
            seq_len = act.shape[1]
            pos = _normalize_position(target_position, seq_len)
            for neuron_idx in grouped[layer]:
                if neuron_idx >= act.shape[-1]:
                    continue
                if patch_mode == "clean":
                    source_tensor = source_cache[hook.name]
                    src_pos = min(pos, source_tensor.shape[1] - 1)
                    act[:, pos, neuron_idx] = source_tensor[:, src_pos, neuron_idx]
                elif patch_mode == "zero":
                    act[:, pos, neuron_idx] = 0.0
                elif patch_mode == "mean":
                    mean_tensor = mean_cache[hook.name]
                    mean_pos = min(pos, mean_tensor.shape[1] - 1)
                    act[:, pos, neuron_idx] = mean_tensor[:, mean_pos, neuron_idx]
                else:  # clamp
                    act[:, pos, neuron_idx] = clamp_value
            return act
        return hook_fn

    hooks = [
        (f"blocks.{layer}.mlp.hook_post", make_hook(layer))
        for layer in sorted(grouped)
    ]
    return model.run_with_hooks(target_tokens, fwd_hooks=hooks)

# ---------------------------------------------------------------------------
# SAE feature intervention (V10: sae_feature)
# ---------------------------------------------------------------------------

def _group_sae_feature_components(
    components: list[dict[str, Any]],
) -> dict[str, dict[int, list[int]]]:
    """Group sae_feature components by sae_id → layer → [feature_ids]."""
    result: dict[str, dict[int, list[int]]] = {}
    for comp in components:
        if comp.get("component_type") != "sae_feature":
            continue
        sae_id = str(comp.get("sae_id", ""))
        layer = int(comp.get("layer", -1))
        fid = int(comp.get("feature_id", -1))
        if not sae_id or layer < 0 or fid < 0:
            continue
        if sae_id not in result:
            result[sae_id] = defaultdict(list)
        result[sae_id][layer].append(fid)
    # Convert defaultdicts to dicts
    return {k: dict(v) for k, v in result.items()}

def sae_feature_intervention_logits(
    *,
    model: Any,
    target_tokens: Any,
    source_cache: Any,
    components: list[dict[str, Any]],
    patch_mode: str,
    target_position: int,
    mean_cache: Any | None = None,
    sae_models: dict[str, Any] | None = None,
    clamp_value: float | None = None,
) -> Any:
    """Patch SAE features via encode → ablate → decode → patch cycle.

    For each targeted feature:
    1. Run SAE encoder on the residual/MLP activations at the hook point
    2. Zero, clamp, or replace the specific feature activation
    3. Reconstruct via SAE decoder
    4. Patch the reconstructed activations back

    Parameters
    ----------
    sae_models : dict[str, Any]
        Mapping of sae_id → SAE model object with ``encode()`` and
        ``decode()`` methods.
    clamp_value : float, optional
        Value to clamp features to when ``patch_mode="clamp"``.
    """
    grouped = _group_sae_feature_components(components)
    if not grouped:
        return model(target_tokens)
    # Audit-final §gpt2.A1: a missing ``sae_models`` mapping no longer
    # silently degrades to a plain forward pass. SAE-feature claims are
    # claims about SAE-feature space; running them without an SAE is
    # implementation drift, not a graceful fallback.
    if not sae_models:
        raise ValueError(
            "sae_feature_intervention_logits: ``sae_models`` is required when "
            "components include sae_feature entries; got "
            f"{len(grouped)} layer-groups but no SAE registry. Either provide "
            "a {sae_id: sae_model_with_encode_decode} mapping in the runner "
            "config, or remove sae_feature components from the bundle."
        )

    # refuse to silently fall back to zero ablation
    # when patch_mode is incompatible with the supplied caches/parameters.
    # Mirrors neuron_intervention_logits (§1.6) and the head/MLP path. The
    # cell metadata labels the row by ``patch_mode``; running a different
    # operation than the label says is implementation drift, not a graceful
    # degradation.
    if patch_mode == "clean" and source_cache is None:
        raise ValueError(
            "sae_feature_intervention_logits: patch_mode='clean' requires a "
            "populated source_cache; refusing to silently fall back to zero "
            "ablation."
        )
    if patch_mode == "mean" and mean_cache is None:
        raise ValueError(
            "sae_feature_intervention_logits: patch_mode='mean' requires a "
            "populated mean_cache; refusing to silently fall back to zero "
            "ablation."
        )
    if patch_mode == "clamp" and clamp_value is None:
        raise ValueError(
            "sae_feature_intervention_logits: patch_mode='clamp' requires a "
            "clamp_value."
        )
    if patch_mode not in ("clean", "zero", "mean", "clamp"):
        raise ValueError(
            f"sae_feature_intervention_logits: unsupported patch_mode={patch_mode!r}"
        )

    # Per-component site lookup so mixed-site bundles route hooks correctly
    # rather than collapsing to whichever site the first component declared.
    site_map = {
        "resid_post": "hook_resid_post",
        "resid_pre": "hook_resid_pre",
        "mlp_post": "mlp.hook_post",
    }

    def _comp_site(comp: dict[str, Any]) -> str:
        return site_map.get(comp.get("site") or "resid_post", "hook_resid_post")

    # Group interventions by (layer, site) — one hook fires per pair so each
    # SAE encodes against the activation space it was trained on.
    hook_layers: dict[tuple[int, str], list[tuple[str, list[int]]]] = defaultdict(list)
    for comp in components:
        if comp.get("component_type") != "sae_feature":
            continue
        sae_id = comp.get("sae_id")
        if sae_id is None or sae_id not in sae_models:
            continue
        layer = int(comp.get("layer", -1))
        fid = int(comp.get("feature_id", -1))
        if layer < 0 or fid < 0:
            continue
        site = _comp_site(comp)
        # Aggregate feature ids per (layer, site, sae_id) so multiple
        # interventions on the same SAE compose into one encode/decode cycle.
        key = (layer, site)
        existing = next((row for row in hook_layers[key] if row[0] == sae_id), None)
        if existing is None:
            hook_layers[key].append((sae_id, [fid]))
        elif fid not in existing[1]:
            existing[1].append(fid)

    if not hook_layers:
        return model(target_tokens)

    def make_hook(layer: int, hook_site: str, interventions: list[tuple[str, list[int]]]):
        def hook_fn(act, hook):
            seq_len = act.shape[1]
            pos = _normalize_position(target_position, seq_len)
            # Snapshot the activation BEFORE any SAE perturbs it. Without this,
            # the second SAE at the same layer would encode from the first
            # SAE's reconstruction (a chained-encode bug).
            original = act[:, pos, :].clone()  # [batch, d_model]
            delta = None  # accumulated correction across all SAEs at this hook
            for sae_id, feature_ids in interventions:
                sae = sae_models[sae_id]
                # Encode the unperturbed activation. ``.clone()`` defends
                # against SAEs that return a view into internal state.
                features = sae.encode(original).clone()  # [batch, n_features]
                modified = features.clone()

                # Pre-encode source / mean activations once per intervention
                # so each fid uses consistent reference values.
                source_features = None
                mean_features = None
                if patch_mode == "clean" and source_cache is not None:
                    src_act = source_cache.get(hook.name)
                    if src_act is not None and src_act.shape[1] > pos:
                        source_features = sae.encode(src_act[:, pos, :])
                if patch_mode == "mean" and mean_cache is not None:
                    mean_act = mean_cache.get(hook.name)
                    if mean_act is not None and mean_act.shape[1] > pos:
                        # Use mean(encode(x)) NOT encode(mean(x)) — sparse
                        # features are non-linear under encoding.
                        mean_features = sae.encode(mean_act[:, pos, :])

                for fid in feature_ids:
                    if fid >= modified.shape[-1]:
                        continue
                    if patch_mode == "zero":
                        modified[:, fid] = 0.0
                    elif patch_mode == "clean":
                        if source_features is None:
                            # source_cache was
                            # provided (upfront validator passed) but the
                            # specific hook key was missing or had a too-short
                            # sequence length. Surface the cache-miss as a
                            # hard error rather than silently zero-ablate.
                            raise ValueError(
                                "sae_feature_intervention_logits(clean): "
                                f"source_cache has no usable activation at "
                                f"hook={hook.name!r} pos={pos}; refusing to "
                                "fall back to zero ablation."
                            )
                        modified[:, fid] = source_features[:, fid]
                    elif patch_mode == "clamp" and clamp_value is not None:
                        modified[:, fid] = clamp_value
                    elif patch_mode == "mean":
                        if mean_features is None:
                            raise ValueError(
                                "sae_feature_intervention_logits(mean): "
                                f"mean_cache has no usable activation at "
                                f"hook={hook.name!r} pos={pos}; refusing to "
                                "fall back to zero ablation."
                            )
                        modified[:, fid] = mean_features[:, fid]
                    else:
                        modified[:, fid] = 0.0

                # Standard SAE intervention with residual-error preservation:
                #     patched = decode(modified) + (act - decode(encode(act)))
                #            = act + (decode(modified) - decode(features))
                # This isolates the targeted-feature effect from SAE
                # reconstruction error on every other feature.
                step = sae.decode(modified) - sae.decode(features)
                delta = step if delta is None else (delta + step)

            if delta is not None:
                act[:, pos, :] = original + delta
            return act
        return hook_fn

    hooks = [
        (f"blocks.{layer}.{hook_site}", make_hook(layer, hook_site, interventions))
        for (layer, hook_site), interventions in sorted(hook_layers.items())
    ]
    return model.run_with_hooks(target_tokens, fwd_hooks=hooks)

def transcoder_feature_intervention_logits(
    *,
    model: Any,
    target_tokens: Any,
    source_cache: Any,
    components: list[dict[str, Any]],
    patch_mode: str,
    target_position: int,
    mean_cache: Any | None = None,
    transcoder_models: dict[str, Any] | None = None,
    clamp_value: float | None = None,
) -> Any:
    """Patch transcoder features via encode → ablate → decode → patch cycle.

    V12: Transcoders differ from SAEs in that they map:
        MLP input → features → MLP output  (NOT autoencoder)
    This allows fine-grained ablation of individual transcoder features
    which correspond to specific computational sub-circuits within MLPs.

    Implementation: we register **two** hooks per layer. The pre-MLP hook
    captures the input activation and computes the encoded features; the
    post-MLP hook decodes the (modified) features and adds the difference
    against the original transcoder reconstruction so that the model's MLP
    output is preserved up to the targeted-feature delta. Earlier versions
    wrote the decoded output (which lives in MLP-output space) into
    ``mlp.hook_pre``, silently corrupting the residual stream because
    ``d_mlp_pre == d_model`` in GPT-2 / Pythia.
    """
    # Group by layer
    layer_features: dict[int, list[int]] = defaultdict(list)
    for comp in components:
        if comp.get("component_type") != "transcoder_feature":
            continue
        layer = int(comp.get("layer", -1))
        fid = int(comp.get("feature_id", -1))
        if layer >= 0 and fid >= 0:
            layer_features[layer].append(fid)

    if not layer_features:
        return model(target_tokens)
    # Audit-final §gpt2.A2: a missing ``transcoder_models`` mapping no longer
    # silently degrades to whole-MLP-input patching. The fallback path that
    # used to live below is preserved as ``transcoder_legacy_full_mlp_patch``
    # in the dispatcher (TODO: register if needed); ``transcoder_feature``
    # itself now requires a real transcoder.
    if not transcoder_models:
        raise ValueError(
            "transcoder_feature_intervention_logits: ``transcoder_models`` is "
            "required when components include transcoder_feature entries; "
            f"got {len(layer_features)} layer-groups but no transcoder "
            "registry. Either provide a {'layer_<n>': transcoder_with_encode_decode} "
            "mapping in the runner config, or remove transcoder_feature "
            "components from the bundle."
        )

    n_layers = int(model.cfg.n_layers)
    # Per-layer scratch space shared between the pre- and post-MLP hooks.
    # Keys: layer index. Values: dict with original/features/modified tensors.
    scratch: dict[int, dict[str, Any]] = {}

    def make_pre_hook(layer: int, feature_ids: list[int]):
        def hook_fn(act, hook):
            seq_len = act.shape[1]
            pos = _normalize_position(target_position, seq_len)
            # ``transcoder_models`` is guaranteed truthy here (validated at
            # function entry; see ).
            tc = transcoder_models.get(f"layer_{layer}")
            if tc is None:
                scratch[layer] = {"skip": True}
                return act

            # Encode the unmodified input activation. ``.clone()`` defends
            # against transcoders that return a view into internal state.
            input_act = act[:, pos, :].clone()
            features = tc.encode(input_act).clone()
            modified = features.clone()

            source_features = None
            mean_features = None
            if patch_mode == "clean" and source_cache is not None:
                src = source_cache.get(f"blocks.{layer}.mlp.hook_pre")
                if src is not None and src.shape[1] > pos:
                    source_features = tc.encode(src[:, pos, :])
            if patch_mode == "mean" and mean_cache is not None:
                m = mean_cache.get(f"blocks.{layer}.mlp.hook_pre")
                if m is not None and m.shape[1] > pos:
                    mean_features = tc.encode(m[:, pos, :])

            for fid in feature_ids:
                if fid >= modified.shape[-1]:
                    continue
                if patch_mode == "zero":
                    modified[:, fid] = 0.0
                elif patch_mode == "clean":
                    modified[:, fid] = (
                        source_features[:, fid] if source_features is not None else 0.0
                    )
                elif patch_mode == "clamp" and clamp_value is not None:
                    modified[:, fid] = clamp_value
                elif patch_mode == "mean":
                    modified[:, fid] = (
                        mean_features[:, fid] if mean_features is not None else 0.0
                    )
                else:
                    modified[:, fid] = 0.0

            scratch[layer] = {
                "pos": pos,
                "tc": tc,
                "features": features,
                "modified": modified,
                "skip": False,
            }
            return act
        return hook_fn

    def make_post_hook(layer: int):
        def hook_fn(act, hook):
            data = scratch.get(layer)
            if data is None or data.get("skip"):
                return act
            tc = data["tc"]
            pos = data["pos"]
            features = data["features"]
            modified = data["modified"]
            # Patched MLP output = original MLP output + (decode(modified) -
            # decode(features)). This isolates the targeted-feature delta
            # while preserving any reconstruction error of the transcoder
            # against the model's actual MLP output.
            delta = tc.decode(modified) - tc.decode(features)
            act[:, pos, :] = act[:, pos, :] + delta
            return act
        return hook_fn

    hooks: list[tuple[str, Any]] = []
    for layer, fids in sorted(layer_features.items()):
        if layer >= n_layers:
            continue
        hooks.append((f"blocks.{layer}.mlp.hook_pre", make_pre_hook(layer, fids)))
        hooks.append((f"blocks.{layer}.mlp.hook_post", make_post_hook(layer)))

    return model.run_with_hooks(target_tokens, fwd_hooks=hooks)

# ---------------------------------------------------------------------------
# Control generators for neuron and SAE feature lanes (V10)
# ---------------------------------------------------------------------------

def random_neuron_components(
    n_layers: int, d_mlp: int = 3072, count: int = 1, seed: int = 0,
) -> list[dict[str, Any]]:
    """Generate random MLP neuron components for controls."""
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    for _ in range(max(1, count)):
        rows.append({
            "component_type": "mlp_neuron",
            "layer": rng.randrange(n_layers),
            "neuron": rng.randrange(d_mlp),
            "selection_source": "random_control",
        })
    return rows

def random_sae_features(
    sae_id: str = "default_sae", n_layers: int = 12, n_features: int = 16384,
    count: int = 1, seed: int = 0,
) -> list[dict[str, Any]]:
    """Generate random SAE feature components for controls."""
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    for _ in range(max(1, count)):
        rows.append({
            "component_type": "sae_feature",
            "sae_id": sae_id,
            "layer": rng.randrange(n_layers),
            "feature_id": rng.randrange(n_features),
            "site": "resid_post",
            "selection_source": "random_control",
        })
    return rows

# ---------------------------------------------------------------------------
# DAS subspace intervention (V11)
# ---------------------------------------------------------------------------

def das_subspace_intervention_logits(
    *,
    model: Any,
    target_tokens: Any,
    source_cache: Any,
    components: list[dict[str, Any]],
    patch_mode: str = "clean",
    target_position: int = -1,
) -> Any:
    """Distributed Alignment Search subspace intervention.

    Each component specifies a rotation matrix (subspace_directions)
    and a layer. We project the residual stream onto the subspace
    directions and patch only those projections from source_cache.

    Component dict fields:
        component_type: "das_subspace"
        layer: int
        site: str (default "hook_resid_post")
        subspace_directions: Tensor of shape (d_model, k) or None
            If None, falls back to full residual stream patching.
    """
    import torch

    # NOTE: do not call ``_align_sequence_length`` here. ``source_cache`` is a
    # cache dict (str -> Tensor), not a token tensor; passing it as the
    # ``source_tokens`` argument silently treats ``len(dict)`` as a sequence
    # length and corrupts ``target_tokens`` into a tuple. DAS works on cached
    # residuals — no token-length alignment is needed.

    # Group by layer
    layer_subspaces: dict[int, list[Any]] = defaultdict(list)
    missing_directions: list[int] = []
    for comp in components:
        if comp.get("component_type") != "das_subspace":
            continue
        layer = int(comp["layer"])
        directions = comp.get("subspace_directions")  # Tensor (d_model, k)
        if directions is None or not hasattr(directions, "shape"):
            missing_directions.append(layer)
        layer_subspaces[layer].append(directions)

    if not layer_subspaces:
        return model(target_tokens)

    # Audit-final §gpt2.A3 / §gemini2.4: a DAS subspace intervention without
    # an actual subspace basis is not a DAS intervention; it is a full
    # residual-stream patch. Earlier versions silently took that fallback
    # path, which mislabels the scientific claim. The honest contract is
    # "if you submit das_subspace, you supply subspace_directions".
    if missing_directions:
        raise ValueError(
            "das_subspace_intervention_logits: missing subspace_directions for "
            f"layers {sorted(set(missing_directions))}. DAS requires a "
            "(d_model, k) basis; falling back to a full residual-stream patch "
            "would silently relabel the intervention. Provide a real basis "
            "or change component_type to 'residual_stream'."
        )

    def make_hook(layer_idx, subspaces):
        def hook_fn(value, hook):
            pos = target_position if target_position >= 0 else value.shape[1] + target_position
            pos = max(0, min(pos, value.shape[1] - 1))

            site = "hook_resid_post"
            source_key = f"blocks.{layer_idx}.{site}"
            if source_key not in source_cache:
                return value

            source_act = source_cache[source_key]
            if source_act.shape[1] <= pos:
                return value

            for directions in subspaces:
                if directions is not None and hasattr(directions, 'shape'):
                    # Project onto subspace and patch only those directions
                    orig = value[:, pos, :].clone()
                    src = source_act[:, pos, :]
                    # Project diff onto subspace
                    proj_src = directions @ (directions.T @ src.T)
                    proj_orig = directions @ (directions.T @ orig.T)
                    value[:, pos, :] = orig + (proj_src - proj_orig).T
                else:
                    # Full residual stream patch (fallback)
                    value[:, pos, :] = source_act[:, pos, :]
            return value
        return hook_fn

    hooks = [
        (f"blocks.{layer}.hook_resid_post", make_hook(layer, subspaces))
        for layer, subspaces in sorted(layer_subspaces.items())
    ]
    return model.run_with_hooks(target_tokens, fwd_hooks=hooks)
