from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

def display_path(path: str | Path) -> str:
    """Return a portable path for reports without embedding local user paths."""
    p = Path(path).expanduser()
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        pass
    try:
        return "~/" + str(p.resolve().relative_to(Path.home())).replace(os.sep, "/")
    except Exception:
        return str(p)

def _model_slug(model_id: str) -> str:
    return ''.join(ch if ch.isalnum() else '_' for ch in model_id)

def _candidate_names(model_id: str) -> list[str]:
    names = [model_id]
    try:
        from automechinterp_runner.models import resolve_model

        info = resolve_model(model_id)
        tl_name = info.transformer_lens_name
        names.extend(
            [
                tl_name,
                tl_name.replace('/', '--'),
                tl_name.split('/')[-1],
                tl_name.replace('/', os.sep),
            ]
        )
    except Exception:
        pass
    seen: set[str] = set()
    out: list[str] = []
    for name in names:
        if name and name not in seen:
            seen.add(name)
            out.append(name)
    return out

def candidate_search_roots() -> list[Path]:
    roots: list[Path] = []

    env_multi = os.environ.get('AUTOMECHINTERP_LOCAL_MODEL_DIRS', '')
    for item in env_multi.split(os.pathsep):
        item = item.strip()
        if item:
            roots.append(Path(item).expanduser())

    for env_name in ('HF_HOME', 'TRANSFORMERS_CACHE', 'HUGGINGFACE_HUB_CACHE'):
        value = os.environ.get(env_name)
        if value:
            roots.append(Path(value).expanduser())

    roots.extend(
        [
            Path.home() / '.cache' / 'huggingface' / 'hub',
            ROOT / 'models',
            ROOT / 'model_cache',
            ROOT / 'artifacts' / 'models',
            Path('/models'),
            Path('/root/.cache/huggingface/hub'),
        ]
    )

    dedup: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root)
        if key not in seen:
            seen.add(key)
            dedup.append(root)
    return dedup

def discover_local_model_dirs(model_id: str) -> list[Path]:
    hits: list[Path] = []

    specific_env = os.environ.get(f"AUTOMECHINTERP_MODEL_DIR_{_model_slug(model_id).upper()}")
    if specific_env:
        p = Path(specific_env).expanduser()
        if p.exists():
            hits.append(p)

    candidate_names = _candidate_names(model_id)
    for root in candidate_search_roots():
        if not root.exists():
            continue
        for name in candidate_names:
            direct = root / name
            if direct.exists():
                hits.append(direct)
        # HuggingFace snapshot-style cache names.
        for name in candidate_names:
            snapshotish = root / f"models--{name.replace('/', '--')}"
            if snapshotish.exists():
                hits.append(snapshotish)
                snapshots = snapshotish / 'snapshots'
                if snapshots.exists():
                    for child in sorted(snapshots.iterdir()):
                        if child.is_dir():
                            hits.append(child)

    dedup: list[Path] = []
    seen: set[str] = set()
    for hit in hits:
        resolved = str(hit.resolve())
        if resolved not in seen:
            seen.add(resolved)
            dedup.append(hit.resolve())
    return dedup

def _path_looks_loadable(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    has_config = (path / 'config.json').exists()
    has_weights = any((path / name).exists() for name in ('model.safetensors', 'pytorch_model.bin'))
    # wrap glob() in
    # sorted() so the loadable-check is order-deterministic across filesystems.
    has_shards = bool(sorted(path.glob('*.safetensors'))) or bool(sorted(path.glob('pytorch_model*.bin')))
    return has_config and (has_weights or has_shards)

def loadable_local_model_dirs(model_id: str) -> list[Path]:
    return [path for path in discover_local_model_dirs(model_id) if _path_looks_loadable(path)]

def probe_transfer_runtime() -> dict[str, Any]:
    payload: dict[str, Any] = {
        'python_version': os.sys.version.split()[0],
        'search_roots': [display_path(p) for p in candidate_search_roots()],
    }

    try:
        import transformers  # noqa: F401

        payload['transformers_importable'] = True
    except Exception as exc:
        payload['transformers_importable'] = False
        payload['transformers_error'] = f'{type(exc).__name__}: {exc}'

    try:
        import transformer_lens  # noqa: F401

        payload['transformer_lens_importable'] = True
    except Exception as exc:
        payload['transformer_lens_importable'] = False
        payload['transformer_lens_error'] = f'{type(exc).__name__}: {exc}'

    try:
        socket.getaddrinfo('huggingface.co', 443)
        payload['huggingface_dns_resolves'] = True
    except Exception as exc:
        payload['huggingface_dns_resolves'] = False
        payload['huggingface_dns_error'] = f'{type(exc).__name__}: {exc}'

    payload['runtime_ready_for_transfer'] = bool(
        payload.get('transformers_importable') and payload.get('transformer_lens_importable')
    )
    return payload

def load_hooked_transformer(
    model_id: str,
    *,
    device: str = 'cpu',
    local_model_dir: str | Path | None = None,
    local_only: bool = False,
):
    from automechinterp_runner.models import resolve_model
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from transformer_lens import HookedTransformer

    info = resolve_model(model_id)
    candidates: list[Path] = []
    if local_model_dir is not None:
        candidates.append(Path(local_model_dir).expanduser().resolve())
    candidates.extend(loadable_local_model_dirs(model_id))

    if candidates:
        chosen = candidates[0]
        hf_model = AutoModelForCausalLM.from_pretrained(
            chosen,
            local_files_only=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(
            chosen,
            local_files_only=True,
        )
        model = HookedTransformer.from_pretrained(
            info.transformer_lens_name,
            hf_model=hf_model,
            tokenizer=tokenizer,
            device=device,
        )
        setattr(model, '_automechinterp_local_model_dir', str(chosen))
        # explicitly enter eval mode and request
        # deterministic algorithms. ``warn_only=True`` keeps backward
        # compatibility with ops that have no deterministic implementation.
        model.eval()
        try:
            import torch
            torch.use_deterministic_algorithms(True, warn_only=True)
        except Exception:
            pass
        return model

    if local_only:
        searched = ', '.join(str(p) for p in candidate_search_roots())
        raise RuntimeError(
            f'No local model snapshot found for {model_id}. Searched roots: {searched}. '
            'Provide --local-model-dir or set AUTOMECHINTERP_MODEL_DIR_<MODEL_ID>.'
        )

    model = HookedTransformer.from_pretrained(info.transformer_lens_name, device=device)
    model.eval()
    try:
        import torch
        torch.use_deterministic_algorithms(True, warn_only=True)
    except Exception:
        pass
    return model
