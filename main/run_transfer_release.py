#!/usr/bin/env python3
"""Generate released cross-model transfer artifacts for an evaluated bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'packages' / 'evaluator' / 'src'))
sys.path.insert(0, str(ROOT / 'packages' / 'runner' / 'src'))
sys.path.insert(0, str(ROOT / 'main'))

from automechinterp_evaluator.evaluator import evaluate_bundle
from automechinterp_evaluator.reporting import build_markdown_report
from _model_loading import load_hooked_transformer, probe_transfer_runtime
from run_real_multi_task import run_cross_model_transfer


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate cross-model transfer results for a released bundle')
    parser.add_argument('--bundle-dir', type=Path, default=ROOT / 'main' / 'output' / 'real_multi_task' / 'ioi_v0_gpt2-small')
    parser.add_argument('--transfer-model', default='pythia-70m')
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--n-examples', type=int, default=10)
    parser.add_argument('--local-model-dir', type=Path, default=None, help='Path to a local Hugging Face snapshot / model directory for the transfer model.')
    parser.add_argument('--local-only', action='store_true', help='Fail fast unless the transfer model can be loaded from a local snapshot.')
    args = parser.parse_args()

    bundle_dir = args.bundle_dir.resolve()
    protocol = __import__('yaml').safe_load((bundle_dir / 'protocol.yaml').read_text())
    task_id = protocol['unit_of_work']['task_id']
    source_model_id = protocol['unit_of_work']['model_id']

    runtime = probe_transfer_runtime()
    if not runtime.get('runtime_ready_for_transfer'):
        raise SystemExit(
            'Transfer runtime is not ready: '
            f"transformers_importable={runtime.get('transformers_importable')} "
            f"transformer_lens_importable={runtime.get('transformer_lens_importable')}"
        )

    try:
        transfer_model = load_hooked_transformer(
            args.transfer_model,
            device=args.device,
            local_model_dir=args.local_model_dir,
            local_only=args.local_only,
        )
    except Exception as exc:
        raise SystemExit(
            'Unable to load the transfer model from the local environment. '
            'Provide --local-model-dir pointing at a local Hugging Face snapshot or '
            'set AUTOMECHINTERP_MODEL_DIR_<MODEL_ID>. Original error: '
            f'{type(exc).__name__}: {exc}'
        ) from exc

    run_cross_model_transfer(
        source_bundle_dir=bundle_dir,
        transfer_model=transfer_model,
        transfer_model_id=args.transfer_model,
        source_model_id=source_model_id,
        task_id=task_id,
        n_examples=args.n_examples,
    )

    result = evaluate_bundle(bundle_dir)
    (bundle_dir / 'evaluation_result_current.json').write_text(
        json.dumps(result, indent=2, sort_keys=True) + '\n'
    )
    (bundle_dir / 'stage_gate_report.md').write_text(build_markdown_report(result))
    print(str(bundle_dir / 'cross_model_results.json'))


if __name__ == '__main__':
    main()
