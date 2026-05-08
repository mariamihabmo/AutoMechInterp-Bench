#!/usr/bin/env python3
"""Probe whether same-family transfer is blocked by software, weights, or network."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'packages' / 'runner' / 'src'))
sys.path.insert(0, str(ROOT / 'packages' / 'evaluator' / 'src'))
sys.path.insert(0, str(ROOT / 'main'))

from _model_loading import display_path, discover_local_model_dirs, loadable_local_model_dirs, probe_transfer_runtime  # noqa: E402

REPRO = ROOT / 'main' / 'output' / 'repro'
OUT_JSON = REPRO / 'transfer_runtime_probe.json'
OUT_MD = REPRO / 'transfer_runtime_probe.md'
TARGETS = ['gpt2-medium', 'pythia-160m']


def main() -> None:
    runtime = probe_transfer_runtime()
    targets = {}
    for model_id in TARGETS:
        targets[model_id] = {
            'discovered_local_dirs': [display_path(p) for p in discover_local_model_dirs(model_id)],
            'loadable_local_dirs': [display_path(p) for p in loadable_local_model_dirs(model_id)],
        }

    payload = {
        'generated_by': 'main/transfer_runtime_probe.py',
        'runtime': runtime,
        'targets': targets,
        'diagnosis': {
            'software_stack_ready': bool(runtime.get('runtime_ready_for_transfer')),
            'target_snapshots_present': any(v['loadable_local_dirs'] for v in targets.values()),
            'online_model_resolution_available': bool(runtime.get('huggingface_dns_resolves')),
        },
    }
    REPRO.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')

    lines = [
        '# Transfer Runtime Probe',
        '',
        f"- Software stack ready: **{payload['diagnosis']['software_stack_ready']}**",
        f"- Any local target-model snapshots present: **{payload['diagnosis']['target_snapshots_present']}**",
        f"- Online model resolution available from this runtime: **{payload['diagnosis']['online_model_resolution_available']}**",
        '',
        '## Per-target status',
        '',
        '| Target model | Discovered dirs | Loadable dirs |',
        '|---|---:|---:|',
    ]
    for model_id, info in targets.items():
        lines.append(f"| `{model_id}` | {len(info['discovered_local_dirs'])} | {len(info['loadable_local_dirs'])} |")
    lines.extend([
        '',
        'Interpretation: if the software stack is ready but loadable local snapshots are absent and online resolution is unavailable, then the remaining blocker is genuinely missing target-model weights rather than a Python/package issue.',
    ])
    OUT_MD.write_text('\n'.join(lines).rstrip() + '\n')
    print(str(OUT_JSON))


if __name__ == '__main__':
    main()
