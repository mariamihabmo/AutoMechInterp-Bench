"""Stage-2 runner that produces evaluation_result.json from interventions.

V10: Multi-lane architecture — supports head, mlp, residual_stream, edge,
mlp_neuron, and sae_feature intervention levels via INTERVENTION_DISPATCH.
"""

from __future__ import annotations

import hashlib
import inspect
import itertools
import io
import os
import platform
import subprocess
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from typing import Any

from .interventions.node_patching import (
    head_intervention_logits,
    mlp_intervention_logits,
    random_mlp_components,
    residual_stream_intervention_logits,
    edge_intervention_logits,
    neuron_intervention_logits,
    sae_feature_intervention_logits,
    das_subspace_intervention_logits,
    transcoder_feature_intervention_logits,
    random_head_components,
    random_edge_components,
    random_neuron_components,
    random_sae_features,
    adjacent_head_components,
    shift_layers,
)
from .io_utils import Stage2Error, read_jsonl, read_yaml, sha256_file, update_manifest, write_json
from .models import resolve_model
from .tasks import get_task_module

# read package version once, fail loud if it ever
# disagrees with the historical pinned default ("0.2.0"). The historical pin
# is what every released bundle's evaluation_result.json embeds, so a silent
# bump would invalidate provenance comparisons.
try:
    from . import __version__ as _PKG_VERSION
except ImportError:  # pragma: no cover - circular fallback
    _PKG_VERSION = "0.2.0"
if _PKG_VERSION != "0.2.0":
    # Future bumps must explicitly update this guard alongside the canonical
    # bundle re-runs. Keeping it failing-noisy preserves the artifact contract.
    raise RuntimeError(
        f"automechinterp_runner.__version__ changed to {_PKG_VERSION!r}; "
        "released bundles embed runner_version='0.2.0'. Update this guard and "
        "regenerate canonical artifacts before bumping."
    )


# ---------------------------------------------------------------------------
# Component-type-aware intervention dispatch (V12: 8 component types)
# ---------------------------------------------------------------------------

INTERVENTION_DISPATCH = {
    "head": head_intervention_logits,
    "mlp": mlp_intervention_logits,
    "residual_stream": residual_stream_intervention_logits,
    "edge": edge_intervention_logits,
    "mlp_neuron": neuron_intervention_logits,
    "sae_feature": sae_feature_intervention_logits,
    "das_subspace": das_subspace_intervention_logits,
    "transcoder_feature": transcoder_feature_intervention_logits,
}


@dataclass(frozen=True)
class Stage2Config:
    bundle_dir: Path
    device: str = "cpu"
    mode: str = "real"
    examples_per_cell: int = 20
    # default sourced from package metadata.
    runner_version: str = _PKG_VERSION
    exploratory_fraction: float = 0.3


def _pipeline_sha(bundle_dir: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=bundle_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        sha = result.stdout.strip()
        return sha or "unknown"
    except Exception:
        return "unknown"


def _stable_seed(parts: list[str | int]) -> int:
    joined = "|".join(str(p) for p in parts)
    digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _pin_torch_determinism(device: str) -> dict[str, str]:
    """Pin torch / numpy / python RNGs and request deterministic algorithms.

    CPU runs are
    largely deterministic by default, but cuDNN convolutions, scatter, and
    atomic adds are not — so GPU re-execution can drift even from a fixed
    seed. This helper:

    * seeds Python's ``random`` module, NumPy, and torch (CPU + CUDA) with a
      fixed canonical seed (``0``) so that any uncontrolled-RNG callsite has
      a stable starting state;
    * enables ``torch.use_deterministic_algorithms(True, warn_only=True)`` so
      that any non-deterministic kernel surfaces as a warning rather than
      silently producing a different result; ``warn_only`` is intentional —
      hard-failing inside ``transformer_lens`` would prevent third-party
      submissions from running on hardware that lacks deterministic kernels;
    * sets ``CUBLAS_WORKSPACE_CONFIG=:4096:8`` (the value PyTorch documents
      as required for deterministic cuBLAS GEMMs on CUDA >= 10.2) so that GPU
      runs emit reproducible matmuls when supported.

    The returned dict is folded into ``environment_lockfile`` so reviewers
    can see exactly which pins were applied for a given run. Importantly, the
    function is **best effort**: when torch is missing (mock mode in audit
    environments), it records ``torch_unavailable`` and proceeds without
    raising. CPU is treated as the canonical surface; GPU is approximate and
    is documented as such in the paper limitations.
    """
    pins: dict[str, str] = {"canonical_seed": "0"}
    try:
        import random as _random

        _random.seed(0)
        pins["python_random_seed"] = "0"
    except Exception as exc:  # pragma: no cover - stdlib should not fail
        pins["python_random_seed_error"] = repr(exc)
    try:
        import numpy as _np  # type: ignore

        _np.random.seed(0)
        pins["numpy_seed"] = "0"
    except Exception as exc:  # pragma: no cover - numpy may be absent
        pins["numpy_seed_error"] = repr(exc)
    try:
        import torch as _torch  # type: ignore

        _torch.manual_seed(0)
        pins["torch_manual_seed"] = "0"
        if _torch.cuda.is_available():
            _torch.cuda.manual_seed_all(0)
            pins["torch_cuda_manual_seed_all"] = "0"
            os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
            pins["CUBLAS_WORKSPACE_CONFIG"] = os.environ["CUBLAS_WORKSPACE_CONFIG"]
        try:
            _torch.use_deterministic_algorithms(True, warn_only=True)
            pins["torch_use_deterministic_algorithms"] = "True (warn_only)"
        except Exception as exc:  # pragma: no cover - older torch lacks warn_only
            pins["torch_use_deterministic_algorithms_error"] = repr(exc)
        try:
            _torch.backends.cudnn.deterministic = True
            _torch.backends.cudnn.benchmark = False
            pins["cudnn_deterministic"] = "True"
            pins["cudnn_benchmark"] = "False"
        except Exception as exc:  # pragma: no cover - cudnn missing on CPU-only builds
            pins["cudnn_pin_error"] = repr(exc)
    except ImportError:
        pins["torch"] = "unavailable"
    pins["device"] = device
    pins["determinism_surface"] = "cpu_canonical_gpu_approximate"
    # surface the warn-only torch policy as a
    # boolean so external tooling (and the paper reproducibility appendix)
    # can read the pin verbatim instead of parsing the human-readable
    # ``torch_use_deterministic_algorithms`` string.
    pins["torch_deterministic_warn_only"] = "True"
    return pins


def _validate_task(protocol: dict[str, Any]) -> None:
    task_id = protocol["unit_of_work"]["task_id"]
    try:
        task_module = get_task_module(task_id)
    except KeyError:
        raise Stage2Error(f"Stage-2 runner does not support task_id={task_id}")
    supported = set(getattr(task_module, "PROMPT_VARIANTS", []) or [])
    if supported:
        requested = [str(v) for v in protocol.get("execution_grid", {}).get("prompt_variants", [])]
        unsupported = sorted({variant for variant in requested if variant not in supported})
        if unsupported:
            raise Stage2Error(
                f"protocol for task_id={task_id} uses unsupported prompt variants "
                f"{unsupported}; supported variants are {sorted(supported)}"
            )


def _execution_grid(protocol: dict[str, Any]) -> list[tuple[int, str, int, str]]:
    grid = protocol["execution_grid"]
    return list(
        itertools.product(
            grid["seeds"],
            grid["prompt_variants"],
            grid["resample_ids"],
            grid["methods"],
        )
    )


def _patch_mode(method: str) -> str:
    """Map a method name to a patch_mode the interventions accept.

    Supported modes: ``"clean"``, ``"zero"``, ``"mean"``. Earlier versions
    silently returned ``"resample"`` for any method whose name contained that
    substring; no intervention dispatch entry implements ``"resample"``, so
    those bundles raised an opaque ValueError several frames removed from the
    cause. We now raise immediately at the
    method-name layer with a structured message naming the offending method.
    """
    lower = method.lower()
    if "zero" in lower:
        return "zero"
    if "mean" in lower:
        return "mean"
    if "resample" in lower:
        raise ValueError(
            f"_patch_mode: method {method!r} maps to patch_mode='resample', "
            "which is not implemented by any intervention dispatch entry. "
            "Use 'zero_ablation', 'mean_ablation', or 'activation_patching'."
        )
    return "clean"


def _capture_environment(include_transformer_lens: bool = False) -> dict[str, str]:
    """Capture environment info for provenance.

    In mock mode we intentionally skip importing ``transformer_lens`` because
    that dependency is unnecessary for synthetic Stage-2 execution and can be
    unavailable or expensive to import in lightweight audit environments.
    Real mode still records the version when requested.
    """
    env: dict[str, str] = {
        "python_version": sys.version,
        "platform": platform.platform(),
    }
    try:
        import torch
        env["torch_version"] = str(torch.__version__)
        if torch.cuda.is_available():
            env["gpu_name"] = torch.cuda.get_device_name(0)
            env["gpu_count"] = str(torch.cuda.device_count())
        else:
            env["gpu_name"] = "none"
    except ImportError:
        pass
    if include_transformer_lens:
        try:
            import transformer_lens
            env["transformer_lens_version"] = str(transformer_lens.__version__)
        except (ImportError, AttributeError):
            pass
    return env


def _sanitize_pip_freeze_line(line: str) -> str:
    """Redact machine-local file paths from pip freeze provenance output."""
    if not line:
        return line
    if line.startswith("-e "):
        lowered = line.lower()
        if "packages/evaluator" in lowered:
            return "-e <repo_root>/packages/evaluator"
        if "packages/runner" in lowered:
            return "-e <repo_root>/packages/runner"
        return "-e <local-editable-path-redacted>"
    if " @ file://" in line:
        pkg, _sep, _rest = line.partition(" @ file://")
        return f"{pkg} @ <local-file-url-redacted>"
    if "file://" in line:
        return line.replace("file://", "<local-file-url-redacted>")
    return line


def _pip_freeze() -> str:
    """Capture pip freeze output for reproducibility without leaking local paths."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        lines = [_sanitize_pip_freeze_line(line) for line in result.stdout.splitlines()]
        return "\n".join(lines).strip()
    except Exception:
        return "unavailable"


def _simulate_cell_values(
    hypothesis_id: str, seed: int, prompt_variant: str, resample_id: int, method: str,
) -> tuple[float, dict[str, float]]:
    base = _stable_seed([hypothesis_id, seed, prompt_variant, resample_id, method])
    treatment = 0.06 + (base % 400) / 10000.0
    controls = {
        "wrong_position": 0.005 + ((base >> 2) % 30) / 10000.0,
        "wrong_layer": 0.005 + ((base >> 4) % 30) / 10000.0,
        "random_component": 0.006 + ((base >> 6) % 30) / 10000.0,
        "mismatched_source": 0.005 + ((base >> 8) % 30) / 10000.0,
    }
    # Add extended controls with small effects
    controls["shuffled_token"] = 0.004 + ((base >> 10) % 20) / 10000.0
    controls["adjacent_head"] = 0.005 + ((base >> 12) % 25) / 10000.0
    return treatment, controls


def _extract_head_components(hypothesis: dict[str, Any]) -> list[dict[str, Any]]:
    components = hypothesis.get("candidate_components", [])
    if not isinstance(components, list):
        return []
    rows = [c for c in components if isinstance(c, dict) and c.get("component_type") == "head"]
    return [dict(c) for c in rows]


def _extract_components(hypothesis: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract all candidate components regardless of type."""
    components = hypothesis.get("candidate_components", [])
    if not isinstance(components, list):
        return []
    return [dict(c) for c in components if isinstance(c, dict)]


def _primary_component_type(components: list[dict[str, Any]]) -> str:
    """Return the dominant component type in the hypothesis."""
    if not components:
        return "head"
    types = [c.get("component_type", "head") for c in components]
    # Return most common type
    from collections import Counter
    return Counter(types).most_common(1)[0][0]


def _adjacent_components(
    components: list[dict[str, Any]],
    *,
    n_heads: int,
    d_mlp: int = 0,
) -> list[dict[str, Any]]:
    """Return structurally adjacent components for the V7 negative control.

    A previous implementation generated
    ``head + 1 % n_heads`` (modulo wrap) and ``neuron + 1`` /
    ``feature_id + 1`` with no upper bound, which silently produced
    out-of-range indices that the downstream intervention skipped (silent
    null intervention, not a valid negative control). This helper clamps
    every supported component type at the relevant boundary so the adjacent
    leg always patches a real, non-target component.

    ``d_mlp == 0`` indicates the caller could not look it up (legacy or
    non-HookedTransformer model); the fallback steps backward when possible
    so the resulting index is always in-range.
    """
    out: list[dict[str, Any]] = []
    for comp in components:
        ctype = comp.get("component_type")
        if ctype == "head":
            head = int(comp["head"])
            adj_head = head + 1 if head + 1 < n_heads else max(0, head - 1)
            out.append({**comp, "head": adj_head})
        elif ctype == "mlp_neuron":
            neuron = int(comp.get("neuron", 0))
            if d_mlp > 0:
                adj_neuron = neuron + 1 if neuron + 1 < d_mlp else max(0, neuron - 1)
            else:
                adj_neuron = neuron - 1 if neuron > 0 else neuron + 1
            out.append({**comp, "neuron": adj_neuron})
        elif ctype == "sae_feature":
            fid = int(comp.get("feature_id", 0))
            # SAE width is not on model.cfg; step backward when possible so
            # the result is in-range for any SAE with at least two features.
            adj_fid = fid - 1 if fid > 0 else fid + 1
            out.append({**comp, "feature_id": adj_fid})
        else:
            out.append(comp)
    return out


def _random_controls_for_type(
    comp_type: str, n_layers: int, n_heads: int, count: int, seed: int, d_model: int | None = None,
) -> list[dict[str, Any]]:
    """Generate random negative control components for the given type."""
    if comp_type == "head":
        return random_head_components(n_layers=n_layers, n_heads=n_heads, count=count, seed=seed)
    if comp_type == "mlp":
        return random_mlp_components(n_layers=n_layers, count=count, seed=seed)
    if comp_type == "residual_stream":
        return [
            {
                "component_type": "residual_stream",
                "layer": (seed + idx) % n_layers,
                "selection_source": "random_control",
            }
            for idx in range(max(1, count))
        ]
    elif comp_type == "edge":
        return random_edge_components(n_layers=n_layers, n_heads=n_heads, count=count, seed=seed)
    elif comp_type == "mlp_neuron":
        return random_neuron_components(n_layers=n_layers, count=count, seed=seed)
    elif comp_type == "sae_feature":
        return random_sae_features(n_layers=n_layers, count=count, seed=seed)
    if comp_type == "das_subspace":
        return [
            {
                "component_type": "das_subspace",
                "layer": (seed + idx) % n_layers,
                "subspace_dim": 1,
                "selection_source": "random_control",
            }
            for idx in range(max(1, count))
        ]
    if comp_type == "transcoder_feature":
        feature_dim = max(1, int(d_model or 1024))
        return [
            {
                "component_type": "transcoder_feature",
                "layer": (seed + idx) % n_layers,
                "feature_id": (seed * 17 + idx) % feature_dim,
                "selection_source": "random_control",
            }
            for idx in range(max(1, count))
        ]
    return random_head_components(n_layers=n_layers, n_heads=n_heads, count=count, seed=seed)


def _get_intervention_fn(comp_type: str):
    """Look up the intervention function for a component type."""
    fn = INTERVENTION_DISPATCH.get(comp_type)
    if fn is None:
        raise Stage2Error(f"No intervention function for component_type='{comp_type}'. "
                         f"Supported: {list(INTERVENTION_DISPATCH.keys())}")
    return fn


def _run_intervention(
    intervention_fn,
    *,
    mean_cache: Any | None = None,
    **kwargs,
):
    """Call an intervention function while only passing supported kwargs."""
    supported = inspect.signature(intervention_fn).parameters
    call_kwargs = dict(kwargs)
    if "mean_cache" in supported:
        call_kwargs["mean_cache"] = mean_cache
    return intervention_fn(**call_kwargs)


def _split_examples(
    examples: list,
    exploratory_fraction: float,
    *,
    min_per_slice: int = 2,
) -> tuple[list, list]:
    """Split examples into exploratory and confirmatory sets.

    refuses degenerate 1/1 splits. The default
    minimum-per-slice of 2 means the caller must supply at least
    ``ceil(min_per_slice / min(frac, 1-frac))`` examples (by default,
    that's 7 examples for ``exploratory_fraction=0.3``).
    """
    n = len(examples)
    split_idx = max(1, int(n * exploratory_fraction))
    if split_idx >= n:
        split_idx = max(1, n - 1)
    exploratory = examples[:split_idx]
    confirmatory = examples[split_idx:]
    if min_per_slice > 0 and (len(exploratory) < min_per_slice or len(confirmatory) < min_per_slice):
        raise Stage2Error(
            f"exploratory/confirmatory split too small: "
            f"exploratory={len(exploratory)}, confirmatory={len(confirmatory)}, "
            f"min_per_slice={min_per_slice}; increase --examples-per-cell "
            f"(need at least {int(min_per_slice / min(exploratory_fraction, 1 - exploratory_fraction)) + 1})."
        )
    return exploratory, confirmatory


def _deterministic_permutation_indices(length: int, seed: int) -> list[int]:
    import random

    order = list(range(max(0, length)))
    rng = random.Random(seed)
    rng.shuffle(order)
    return order


def _build_mean_cache(caches: list[Any]) -> dict[str, Any]:
    """Build a deterministic mean cache over a list of per-example caches."""
    if not caches:
        return {}

    import torch

    keys = sorted(set().union(*(cache.keys() for cache in caches)))
    mean_cache: dict[str, Any] = {}
    for key in keys:
        tensors = [cache[key] for cache in caches if key in cache]
        if not tensors:
            continue
        min_seq = min(int(t.shape[1]) for t in tensors)
        stacked = torch.stack([t[:, :min_seq].detach() for t in tensors], dim=0)
        mean_cache[key] = stacked.mean(dim=0)
    return mean_cache


def _compute_effect(
    *,
    task_module: Any,
    logits: Any,
    baseline_metric: float,
    example: Any,
    method: str,
) -> float:
    """Return a positive value when the intervention supports the claim semantics."""
    metric_value = task_module.metric(
        logits,
        target_token=example.target_token,
        distractor_token=example.distractor_token,
    )
    if method == "activation_patching":
        return float(metric_value - baseline_metric)
    return float(baseline_metric - metric_value)


def _real_cell_values(
    *,
    model: Any,
    hypothesis: dict[str, Any],
    seed: int,
    prompt_variant: str,
    resample_id: int,
    method: str,
    examples_per_cell: int,
    task_module: Any,
) -> tuple[float, dict[str, float], int]:
    dataset_seed = _stable_seed([hypothesis["hypothesis_id"], seed, prompt_variant, resample_id, method])
    examples = task_module.sample_examples(
        model=model,
        n=max(1, examples_per_cell),
        seed=dataset_seed,
        prompt_variant=prompt_variant,
    )
    return _real_cell_values_from_examples(
        model=model,
        hypothesis=hypothesis,
        method=method,
        examples=examples,
        dataset_seed=dataset_seed,
        task_module=task_module,
    )


def _real_cell_values_from_examples(
    *,
    model: Any,
    hypothesis: dict[str, Any],
    method: str,
    examples: list[Any],
    dataset_seed: int,
    task_module: Any,
) -> tuple[float, dict[str, float], int]:
    """Compute real treatment/control values from a provided shared example pool."""

    # V11: Dispatch based on component type
    components = _extract_components(hypothesis)
    comp_type = _primary_component_type(components)
    intervention_fn = _get_intervention_fn(comp_type)

    shifted = shift_layers(components, n_layers=int(model.cfg.n_layers))
    random_controls = _random_controls_for_type(
        comp_type=comp_type,
        n_layers=int(model.cfg.n_layers),
        n_heads=int(model.cfg.n_heads),
        count=max(1, len(components)),
        seed=dataset_seed,
        d_model=getattr(model.cfg, "d_model", None),
    )
    patch_mode = _patch_mode(method)

    treatment_values: list[float] = []
    wrong_position_values: list[float] = []
    wrong_layer_values: list[float] = []
    random_component_values: list[float] = []
    mismatched_values: list[float] = []
    shuffled_token_values: list[float] = []
    adjacent_head_values: list[float] = []

    import torch

    # Determine which cache hooks to capture based on component type
    cache_filters = ["attn.hook_z", "mlp.hook_post", "hook_resid_post"]

    infos = []
    # Audit-final §2.D.3: build the names_filter as a real closure over a
    # frozenset of suffixes (a) so it does not capture the loop variable
    # ``cache_filters`` by reference and (b) so look-up is O(1) per name
    # rather than O(len(cache_filters)).
    _cache_filter_set = frozenset(cache_filters)

    def _names_filter(name: str, _suffixes: frozenset[str] = _cache_filter_set) -> bool:
        return any(name.endswith(f) for f in _suffixes)

    with torch.no_grad():
        for ex in examples:
            clean_tokens = model.to_tokens(ex.clean_prompt)
            corrupt_tokens = model.to_tokens(ex.corrupt_prompt)
            clean_logits = model(clean_tokens)
            corrupt_logits = model(corrupt_tokens)
            clean_metric = task_module.metric(
                clean_logits,
                target_token=ex.target_token,
                distractor_token=ex.distractor_token,
            )
            corrupt_metric = task_module.metric(
                corrupt_logits,
                target_token=ex.target_token,
                distractor_token=ex.distractor_token,
            )
            _, clean_cache = model.run_with_cache(
                clean_tokens,
                names_filter=_names_filter,
            )
            infos.append(
                {
                    "example": ex,
                    "clean_tokens": clean_tokens,
                    "clean_metric": clean_metric,
                    "clean_cache": clean_cache,
                    "corrupt_tokens": corrupt_tokens,
                    "corrupt_metric": corrupt_metric,
                }
            )

    mean_cache = _build_mean_cache([info["clean_cache"] for info in infos])

    for idx, info in enumerate(infos):
        mismatch = infos[(idx + 1) % len(infos)]
        ex = info["example"]
        clean_tokens = info["clean_tokens"]
        corrupt_tokens = info["corrupt_tokens"]
        clean_metric = float(info["clean_metric"])
        corrupt_metric = float(info["corrupt_metric"])
        clean_cache = info["clean_cache"]
        target_tokens = corrupt_tokens if method == "activation_patching" else clean_tokens
        baseline_metric = corrupt_metric if method == "activation_patching" else clean_metric
        # ``mismatched_source`` control patches from a *different* example's
        # clean cache. For ablation methods the source cache is normally None
        # (the dispatcher derives intervention values from ``mean_cache``);
        # however, for the mismatched-source control we always pass an
        # alternate clean cache so the control isn't trivially identical to
        # the treatment. The dispatched
        # intervention falls back to mean-cache behaviour internally if the
        # source-cache information is unused for that method, but at minimum
        # the run is not bit-identical to the treatment.
        mismatched_source_cache = mismatch["clean_cache"]

        with torch.no_grad():
            # Treatment — use dispatched intervention function
            treatment_logits = _run_intervention(
                intervention_fn,
                mean_cache=mean_cache,
                model=model,
                target_tokens=target_tokens,
                source_cache=clean_cache,
                components=components,
                patch_mode=patch_mode,
                target_position=-1,
            )
            treatment_values.append(
                _compute_effect(
                    task_module=task_module,
                    logits=treatment_logits,
                    baseline_metric=baseline_metric,
                    example=ex,
                    method=method,
                )
            )

            # Wrong position control
            wrong_position_logits = _run_intervention(
                intervention_fn,
                mean_cache=mean_cache,
                model=model,
                target_tokens=target_tokens,
                source_cache=clean_cache,
                components=components,
                patch_mode=patch_mode,
                target_position=0,
            )
            wrong_position_values.append(
                _compute_effect(
                    task_module=task_module,
                    logits=wrong_position_logits,
                    baseline_metric=baseline_metric,
                    example=ex,
                    method=method,
                )
            )

            # Wrong layer control
            wrong_layer_logits = _run_intervention(
                intervention_fn,
                mean_cache=mean_cache,
                model=model,
                target_tokens=target_tokens,
                source_cache=clean_cache,
                components=shifted,
                patch_mode=patch_mode,
                target_position=-1,
            )
            wrong_layer_values.append(
                _compute_effect(
                    task_module=task_module,
                    logits=wrong_layer_logits,
                    baseline_metric=baseline_metric,
                    example=ex,
                    method=method,
                )
            )

            # Random component control — use type-matched randoms
            random_component_logits = _run_intervention(
                intervention_fn,
                mean_cache=mean_cache,
                model=model,
                target_tokens=target_tokens,
                source_cache=clean_cache,
                components=random_controls,
                patch_mode=patch_mode,
                target_position=-1,
            )
            random_component_values.append(
                _compute_effect(
                    task_module=task_module,
                    logits=random_component_logits,
                    baseline_metric=baseline_metric,
                    example=ex,
                    method=method,
                )
            )

            # Mismatched source control.
            #
            # Audit-final §gemini2.6: for ablation methods (``zero`` /
            # ``mean``), ``source_cache`` is unused inside the intervention,
            # so calling with ``components=random_controls, patch_mode='zero'``
            # would be byte-identical to ``random_component_logits``. To make
            # this control distinct we ablate at a *mismatched position* on
            # the same components, i.e. the first token rather than the
            # final answer position. For activation-patching methods the
            # control retains its original semantics (clean-patch from a
            # *different* example's clean cache).
            if method == "activation_patching":
                mismatched_logits = _run_intervention(
                    intervention_fn,
                    mean_cache=None,
                    model=model,
                    target_tokens=target_tokens,
                    source_cache=mismatched_source_cache,
                    components=components,
                    patch_mode="clean",
                    target_position=-1,
                )
            else:
                mismatched_logits = _run_intervention(
                    intervention_fn,
                    mean_cache=mean_cache,
                    model=model,
                    target_tokens=target_tokens,
                    source_cache=mismatched_source_cache,
                    components=components,
                    patch_mode=patch_mode,
                    target_position=0,  # ablate at a mismatched position
                )
            mismatched_values.append(
                _compute_effect(
                    task_module=task_module,
                    logits=mismatched_logits,
                    baseline_metric=baseline_metric,
                    example=ex,
                    method=method,
                )
            )

            # Shuffled token control (V7): run on shuffled corrupt tokens
            permutation = _deterministic_permutation_indices(
                int(target_tokens.shape[1]),
                _stable_seed([hypothesis["hypothesis_id"], dataset_seed, idx, "shuffle"]),
            )
            shuffle_index = torch.tensor(permutation, device=target_tokens.device, dtype=torch.long)
            shuffled_target = target_tokens[:, shuffle_index]
            shuffled_logits = _run_intervention(
                intervention_fn,
                mean_cache=mean_cache,
                model=model,
                target_tokens=shuffled_target,
                source_cache=clean_cache,
                components=components,
                patch_mode=patch_mode,
                target_position=-1,
            )
            shuffled_token_values.append(
                _compute_effect(
                    task_module=task_module,
                    logits=shuffled_logits,
                    baseline_metric=baseline_metric,
                    example=ex,
                    method=method,
                )
            )

            # Adjacent component control (V7) — see ``_adjacent_components``
            # docstring and ````.
            adj_components = _adjacent_components(
                components,
                n_heads=int(model.cfg.n_heads),
                d_mlp=int(getattr(model.cfg, "d_mlp", 0)),
            )
            if adj_components:
                adj_logits = _run_intervention(
                    intervention_fn,
                    mean_cache=mean_cache,
                    model=model,
                    target_tokens=target_tokens,
                    source_cache=clean_cache,
                    components=adj_components,
                    patch_mode=patch_mode,
                    target_position=-1,
                )
                adjacent_head_values.append(
                    _compute_effect(
                        task_module=task_module,
                        logits=adj_logits,
                        baseline_metric=baseline_metric,
                        example=ex,
                        method=method,
                    )
                )
            else:
                adjacent_head_values.append(0.0)

    treatment_effect = mean(treatment_values)
    controls = {
        "wrong_position": mean(wrong_position_values),
        "wrong_layer": mean(wrong_layer_values),
        "random_component": mean(random_component_values),
        "mismatched_source": mean(mismatched_values),
        "shuffled_token": mean(shuffled_token_values),
        "adjacent_head": mean(adjacent_head_values),
    }
    return treatment_effect, controls, dataset_seed


def run_stage2(config: Stage2Config) -> dict[str, Any]:
    bundle_dir = config.bundle_dir.resolve()
    protocol_path = bundle_dir / "protocol.yaml"
    hypothesis_path = bundle_dir / "hypothesis.jsonl"

    if not protocol_path.exists() or not hypothesis_path.exists():
        raise Stage2Error("Bundle must contain protocol.yaml and hypothesis.jsonl")

    protocol = read_yaml(protocol_path)
    hypotheses = read_jsonl(hypothesis_path)
    _validate_task(protocol)

    protocol_sha = sha256_file(protocol_path)
    grid = _execution_grid(protocol)
    model_ref = protocol["unit_of_work"]["model_id"]
    model_info = resolve_model(model_ref, protocol=protocol)
    pipeline_sha = _pipeline_sha(bundle_dir)
    task_id = protocol["unit_of_work"]["task_id"]
    task_module = get_task_module(task_id)

    # Read exploratory fraction from protocol or config
    ssp = protocol.get("sample_size_policy", {})
    exploratory_fraction = ssp.get("exploratory_fraction", config.exploratory_fraction)
    do_split = ssp.get("require_confirmatory_split", exploratory_fraction > 0.0)

    # Capture environment info (V7)
    env_info = _capture_environment(include_transformer_lens=(config.mode == "real"))
    # pin determinism BEFORE loading the
    # model so that any RNG-touching initialisation inside transformer_lens
    # observes the canonical seeds. Pins are recorded in env_info so reviewers
    # can see exactly which surface was deterministic for a given run.
    determinism_pins = _pin_torch_determinism(config.device)
    env_info["determinism_pins"] = determinism_pins
    pip_lockfile = _pip_freeze() if config.mode == "real" else "skipped_in_mock_mode"

    model = None
    if config.mode == "real":
        try:
            from transformer_lens import HookedTransformer
        except Exception as exc:  # pragma: no cover - import environment dependent
            raise Stage2Error("transformer_lens is required for mode=real") from exc
        with io.StringIO() as sink, redirect_stdout(sink):
            model = HookedTransformer.from_pretrained(
                model_info.transformer_lens_name,
                device=config.device,
            )
    elif config.mode != "mock":
        raise Stage2Error("mode must be one of: real, mock")

    hypothesis_results = []
    for hypothesis in hypotheses:
        hyp_id = hypothesis.get("hypothesis_id")
        if not isinstance(hyp_id, str) or not hyp_id.strip():
            raise Stage2Error("Each hypothesis row must include non-empty hypothesis_id")

        raw_cells = []
        for seed, prompt_variant, resample_id, method in grid:
            direction = "sufficiency_patch" if _patch_mode(str(method)) == "clean" else "necessity_ablate"
            if config.mode == "mock":
                treatment, controls = _simulate_cell_values(
                    hypothesis_id=hyp_id,
                    seed=int(seed),
                    prompt_variant=str(prompt_variant),
                    resample_id=int(resample_id),
                    method=str(method),
                )
                dataset_seed = _stable_seed([hyp_id, seed, prompt_variant, resample_id, method])
                runner_id = "stage2_mock_runner"

                if do_split:
                    # Mock mode: generate both slices with slight variation
                    for slice_name in ("exploratory", "confirmatory"):
                        slice_offset = 0.002 if slice_name == "exploratory" else 0.0
                        raw_cells.append(
                            _build_cell(
                                seed=seed,
                                prompt_variant=prompt_variant,
                                resample_id=resample_id,
                                method=method,
                                slice_name=slice_name,
                                treatment=treatment + slice_offset,
                                controls=controls,
                                runner_id=runner_id,
                                runner_version=config.runner_version,
                                pipeline_sha=pipeline_sha,
                                model_ref=model_ref,
                                dataset_seed=dataset_seed,
                                prompt_template_id=str(prompt_variant),
                                direction=direction,
                                env_info=env_info,
                            )
                        )
                else:
                    raw_cells.append(
                        _build_cell(
                            seed=seed,
                            prompt_variant=prompt_variant,
                            resample_id=resample_id,
                            method=method,
                            slice_name="confirmatory",
                            treatment=treatment,
                            controls=controls,
                            runner_id=runner_id,
                            runner_version=config.runner_version,
                            pipeline_sha=pipeline_sha,
                            model_ref=model_ref,
                            dataset_seed=dataset_seed,
                            prompt_template_id=str(prompt_variant),
                            direction=direction,
                            env_info=env_info,
                        )
                    )
            else:
                # Real mode with data splitting
                total_examples = config.examples_per_cell
                if do_split:
                    dataset_seed = _stable_seed([hyp_id, seed, prompt_variant, resample_id, method])
                    examples = task_module.sample_examples(
                        model=model,
                        n=max(2, total_examples),
                        seed=dataset_seed,
                        prompt_variant=str(prompt_variant),
                    )
                    runner_id = "stage2_tl_runner"
                    exploratory_examples, confirmatory_examples = _split_examples(examples, exploratory_fraction)

                    exp_treatment, exp_controls, _ = _real_cell_values_from_examples(
                        model=model,
                        hypothesis=hypothesis,
                        method=str(method),
                        examples=exploratory_examples,
                        dataset_seed=dataset_seed,
                        task_module=task_module,
                    )
                    raw_cells.append(
                        _build_cell(
                            seed=seed, prompt_variant=prompt_variant,
                            resample_id=resample_id, method=method,
                            slice_name="exploratory",
                            treatment=exp_treatment, controls=exp_controls,
                            runner_id=runner_id, runner_version=config.runner_version,
                            pipeline_sha=pipeline_sha, model_ref=model_ref,
                            dataset_seed=dataset_seed,
                            prompt_template_id=str(prompt_variant),
                            direction=direction,
                            env_info=env_info,
                        )
                    )

                    conf_treatment, conf_controls, _ = _real_cell_values_from_examples(
                        model=model,
                        hypothesis=hypothesis,
                        method=str(method),
                        examples=confirmatory_examples,
                        dataset_seed=dataset_seed,
                        task_module=task_module,
                    )
                    raw_cells.append(
                        _build_cell(
                            seed=seed, prompt_variant=prompt_variant,
                            resample_id=resample_id, method=method,
                            slice_name="confirmatory",
                            treatment=conf_treatment, controls=conf_controls,
                            runner_id=runner_id, runner_version=config.runner_version,
                            pipeline_sha=pipeline_sha, model_ref=model_ref,
                            dataset_seed=dataset_seed,
                            prompt_template_id=str(prompt_variant),
                            direction=direction,
                            env_info=env_info,
                        )
                    )
                else:
                    treatment, controls, dataset_seed = _real_cell_values(
                        model=model,
                        hypothesis=hypothesis,
                        seed=int(seed),
                        prompt_variant=str(prompt_variant),
                        resample_id=int(resample_id),
                        method=str(method),
                        examples_per_cell=total_examples,
                        task_module=task_module,
                    )
                    runner_id = "stage2_tl_runner"
                    raw_cells.append(
                        _build_cell(
                            seed=seed, prompt_variant=prompt_variant,
                            resample_id=resample_id, method=method,
                            slice_name="confirmatory",
                            treatment=treatment, controls=controls,
                            runner_id=runner_id, runner_version=config.runner_version,
                            pipeline_sha=pipeline_sha, model_ref=model_ref,
                            dataset_seed=dataset_seed,
                            prompt_template_id=str(prompt_variant),
                            direction=direction,
                            env_info=env_info,
                        )
                    )

        hypothesis_results.append(
            {
                "hypothesis_id": hyp_id,
                "raw_cells": raw_cells,
            }
        )

    evaluation_result = {
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": protocol_sha,
        "hypothesis_results": hypothesis_results,
    }

    eval_path = bundle_dir / "evaluation_result.json"
    write_json(eval_path, evaluation_result)
    manifest_path = update_manifest(bundle_dir)

    # Write environment lockfile (V7)
    lockfile_path = bundle_dir / "environment_lockfile.txt"
    lockfile_path.write_text(pip_lockfile)

    # Write hardware info (V7)
    env_path = bundle_dir / "environment_info.json"
    write_json(env_path, env_info)

    return {
        "bundle": str(bundle_dir),
        "mode": config.mode,
        "device": config.device,
        "protocol_id": protocol["protocol_id"],
        "hypothesis_count": len(hypothesis_results),
        "cell_count": sum(len(row["raw_cells"]) for row in hypothesis_results),
        "evaluation_result": str(eval_path),
        "manifest": str(manifest_path),
        "exploratory_fraction": exploratory_fraction,
        "data_split_enabled": do_split,
    }


def _build_cell(
    *,
    seed: int,
    prompt_variant: str,
    resample_id: int,
    method: str,
    slice_name: str,
    treatment: float,
    controls: dict[str, float],
    runner_id: str,
    runner_version: str,
    pipeline_sha: str,
    model_ref: str,
    dataset_seed: int,
    prompt_template_id: str,
    direction: str,
    env_info: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a raw cell dict with all required + optional provenance fields."""
    cell: dict[str, Any] = {
        "seed": int(seed),
        "prompt_variant": str(prompt_variant),
        "resample_id": int(resample_id),
        "method": str(method),
        "direction": direction,
        "slice": slice_name,
        "treatment_effect": float(treatment),
        "control_effects": {k: float(v) for k, v in controls.items()},
        "runner_id": runner_id,
        "runner_version": runner_version,
        "pipeline_sha": pipeline_sha,
        "model_ref": model_ref,
        "dataset_seed": int(dataset_seed),
        "prompt_template_id": prompt_template_id,
    }
    if env_info:
        cell["hardware_info"] = env_info
    return cell
