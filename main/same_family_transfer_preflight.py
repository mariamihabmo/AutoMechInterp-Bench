#!/usr/bin/env python3
"""Plan same-family transfer runs from the strongest accepted released claims.

This script ranks candidate source bundles/claims using already-released
accepted claims plus the prompt-holdout control, then records whether the
current environment can *actually* execute the next same-family transfer
experiment without pretending that missing weights are available.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'packages' / 'runner' / 'src'))
sys.path.insert(0, str(ROOT / 'packages' / 'evaluator' / 'src'))
sys.path.insert(0, str(ROOT / 'main'))

from automechinterp_runner.models import models_in_family, resolve_model  # noqa: E402
from _model_loading import display_path, discover_local_model_dirs, loadable_local_model_dirs, probe_transfer_runtime  # noqa: E402
from _bundle_analysis import REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, find_bundle_dirs  # noqa: E402

REPRO = ROOT / 'main' / 'output' / 'repro'
OUT_JSON = REPRO / 'same_family_transfer_preflight.json'
OUT_MD = REPRO / 'same_family_transfer_preflight.md'
PROMPT_HOLDOUT = REPRO / 'prompt_holdout_transfer_control.json'

def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())

def _size_key(model_id: str) -> tuple[int, int, int]:
    info = resolve_model(model_id)
    return (int(info.n_layers), int(info.n_heads), int(info.d_model))

def _next_same_family_model(source_model: str) -> str | None:
    family = resolve_model(source_model).family
    family_models = sorted(models_in_family(family), key=_size_key)
    if source_model not in family_models:
        return None
    idx = family_models.index(source_model)
    if idx + 1 >= len(family_models):
        return None
    return family_models[idx + 1]

def _proposed_command(bundle: str, target_model: str, local_dirs: list[Path]) -> str:
    canonical = {path.name: path for path in find_bundle_dirs(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR)}
    bundle_dir = canonical.get(bundle)
    if bundle_dir is None:
        multilane = ROOT / 'main' / 'output' / 'real_multilane' / bundle
        multitask = ROOT / 'main' / 'output' / 'real_multi_task' / bundle
        bundle_dir = multilane if multilane.exists() else multitask
    parts = [
        'python',
        'main/run_transfer_release.py',
        '--bundle-dir',
        display_path(bundle_dir),
        '--transfer-model',
        target_model,
        '--device',
        'cpu',
        '--local-only',
    ]
    if local_dirs:
        parts.extend(['--local-model-dir', display_path(local_dirs[0])])
    else:
        parts.extend(['--local-model-dir', '<path-to-local-model-snapshot>'])
    return ' '.join(parts)

def _canonical_bundle_dirs() -> dict[str, Path]:
    return {path.name: path for path in find_bundle_dirs(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR)}

def _existing_same_family_rows(bundle: str, target_model: str | None, canonical: dict[str, Path]) -> list[dict[str, Any]]:
    if target_model is None:
        return []
    bundle_dir = canonical.get(bundle)
    if bundle_dir is None:
        return []
    cross_path = bundle_dir / 'cross_model_results.json'
    if not cross_path.exists():
        return []
    try:
        rows = json.loads(cross_path.read_text())
    except Exception:
        return []
    if not isinstance(rows, list):
        return []
    return [
        row
        for row in rows
        if isinstance(row, dict) and str(row.get('transfer_model')) == str(target_model)
    ]

def main() -> None:
    prompt_holdout = _load_json(PROMPT_HOLDOUT)
    runtime = probe_transfer_runtime()
    canonical = _canonical_bundle_dirs()

    claims_by_bundle: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in prompt_holdout.get('claims', []):
        claims_by_bundle[str(row['bundle'])].append(row)

    ranked_candidates: list[dict[str, Any]] = []
    for bundle, rows in sorted(claims_by_bundle.items()):
        exemplar = rows[0]
        total_claims = len(rows)
        all_pass_count = sum(1 for row in rows if row.get('all_holdouts_pass'))
        holdout_checks = sum(len(row.get('holdouts', [])) for row in rows)
        passing_checks = sum(
            1
            for row in rows
            for holdout in row.get('holdouts', [])
            if holdout.get('passes')
        )
        target_model = _next_same_family_model(str(exemplar['model']))
        local_dirs = loadable_local_model_dirs(target_model) if target_model else []
        discovered_dirs = discover_local_model_dirs(target_model) if target_model else []
        existing_rows = _existing_same_family_rows(bundle, target_model, canonical)
        existing_claim_ids = sorted({str(row.get('hypothesis_id')) for row in existing_rows if row.get('hypothesis_id')})
        transfer_passed_ids = sorted(
            {
                str(row.get('hypothesis_id'))
                for row in existing_rows
                if row.get('transfer_contract_pass') is True
            }
        )
        transfer_failed_ids = sorted(
            {
                str(row.get('hypothesis_id'))
                for row in existing_rows
                if row.get('hypothesis_id') and row.get('transfer_contract_pass') is not True
            }
        )
        eligible_ids = [row['hypothesis_id'] for row in rows if row.get('all_holdouts_pass')]
        eligible_with_rows = sorted(set(eligible_ids) & set(existing_claim_ids))
        eligible_missing_rows = sorted(set(eligible_ids) - set(existing_claim_ids))
        candidate = {
            'bundle': bundle,
            'task': exemplar['task'],
            'source_model': exemplar['model'],
            'target_model': target_model,
            'accepted_claims_with_multi_prompt': total_claims,
            'claims_passing_all_holdouts': all_pass_count,
            'passing_holdout_checks': passing_checks,
            'total_holdout_checks': holdout_checks,
            'eligible_claim_ids': eligible_ids,
            'blocked_claim_ids': [row['hypothesis_id'] for row in rows if not row.get('all_holdouts_pass')],
            'existing_same_family_rows': len(existing_rows),
            'existing_same_family_claim_ids': existing_claim_ids,
            'eligible_claim_ids_with_same_family_rows': eligible_with_rows,
            'eligible_claim_ids_missing_same_family_rows': eligible_missing_rows,
            'same_family_transfer_passed_claim_ids': transfer_passed_ids,
            'same_family_transfer_failed_claim_ids': transfer_failed_ids,
            'discovered_local_dirs': [display_path(p) for p in discovered_dirs],
            'loadable_local_dirs': [display_path(p) for p in local_dirs],
        }
        ranked_candidates.append(candidate)

    ranked_candidates.sort(
        key=lambda row: (
            row['claims_passing_all_holdouts'],
            row['passing_holdout_checks'],
            -row['total_holdout_checks'],
            row['bundle'],
        ),
        reverse=True,
    )

    executable_runs: list[dict[str, Any]] = []
    already_scored_runs: list[dict[str, Any]] = []
    blocked_runs: list[dict[str, Any]] = []
    for row in ranked_candidates:
        target_model = row.get('target_model')
        if not target_model:
            row['status'] = 'blocked_no_larger_same_family_model'
            row['blocked_reason'] = 'source_model_already_largest_in_family_or_unregistered'
            blocked_runs.append(row)
            continue

        # recompute target-specific
        # local model dirs here so the proposed command points at the right
        # snapshot. Previously this used the leaked `local_dirs` loop variable
        # from the candidate-building scope above, which produced commands like
        # `--local-model-dir model_cache/gpt2-medium` for pythia-160m targets.
        row_local_dirs = loadable_local_model_dirs(target_model)
        row['proposed_command'] = _proposed_command(row['bundle'], target_model, row_local_dirs)

        if not runtime.get('runtime_ready_for_transfer'):
            row['status'] = 'blocked_runtime_dependency'
            row['blocked_reason'] = 'transformer_lens_or_transformers_not_importable'
            blocked_runs.append(row)
        elif row['loadable_local_dirs'] and row['eligible_claim_ids_missing_same_family_rows']:
            row['status'] = 'ready_to_run_missing_rows'
            row['missing_row_count'] = len(row['eligible_claim_ids_missing_same_family_rows'])
            executable_runs.append(row)
        elif row['loadable_local_dirs'] and row['eligible_claim_ids_with_same_family_rows']:
            row['status'] = 'already_scored'
            row['missing_row_count'] = 0
            already_scored_runs.append(row)
        elif row['loadable_local_dirs']:
            row['status'] = 'ready_to_rerun_no_prompt_holdout_eligible_claims'
            row['missing_row_count'] = 0
            already_scored_runs.append(row)
        else:
            row['status'] = 'blocked_missing_local_model_snapshot'
            dns_ok = bool(runtime.get('huggingface_dns_resolves'))
            row['blocked_reason'] = (
                f'no_loadable_local_snapshot_for_{target_model}; '
                f'huggingface_dns_resolves={dns_ok}'
            )
            blocked_runs.append(row)

    payload = {
        'generated_by': 'main/same_family_transfer_preflight.py',
        'prompt_holdout_source': str(PROMPT_HOLDOUT.relative_to(ROOT)),
        'runtime': runtime,
        'ranked_candidates': ranked_candidates,
        'ready_to_run_count': len(executable_runs),
        'missing_eligible_same_family_rows_count': sum(int(row.get('missing_row_count') or 0) for row in executable_runs),
        'already_scored_count': len(already_scored_runs),
        'blocked_count': len(blocked_runs),
        'ready_to_run': executable_runs,
        'already_scored': already_scored_runs,
        'blocked': blocked_runs,
        'notes': [
            'This is a preflight and prioritization artifact, not a transfer result.',
            'Candidates are ranked by prompt-holdout robustness because within-model held-out prompt stability is the best released triage signal for next same-family transfer runs.',
            'ready_to_run_missing_rows means at least one prompt-holdout-passing accepted claim lacks a same-family row and local weights are available.',
            'already_scored means the eligible prompt-holdout-passing accepted claims already have same-family rows; re-running them may check variance but is not missing evidence.',
            'blocked_missing_local_model_snapshot means the software stack is present but no local target-model weights were found under the discovered cache/model roots.',
        ],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')

    lines = [
        '# Same-Family Transfer Preflight',
        '',
        f"- Ranked candidate bundles: **{len(ranked_candidates)}**",
        f"- Ready to run locally for missing eligible rows: **{len(executable_runs)}**",
        f"- Missing eligible same-family rows: **{payload['missing_eligible_same_family_rows_count']}**",
        f"- Already scored locally: **{len(already_scored_runs)}**",
        f"- Blocked: **{len(blocked_runs)}**",
        f"- `transformers` importable: **{runtime.get('transformers_importable', False)}**",
        f"- `transformer_lens` importable: **{runtime.get('transformer_lens_importable', False)}**",
        f"- Hugging Face DNS resolves from this environment: **{runtime.get('huggingface_dns_resolves', False)}**",
        '',
        'This artifact records both the scientific queue and the operational readiness state. A blocked status is an honest statement that the current environment cannot produce the real transfer result yet.',
        '',
        '## Ranked candidates',
        '',
        '| Bundle | Task | Source model | Target model | Claims passing all holdouts | Existing rows | Missing eligible rows | Local snapshot | Status |',
        '|---|---|---|---|---:|---:|---:|---|---|',
    ]
    for row in ranked_candidates:
        has_local = 'yes' if row['loadable_local_dirs'] else 'no'
        lines.append(
            f"| `{row['bundle']}` | `{row['task']}` | `{row['source_model']}` | `{row.get('target_model') or 'n/a'}` | "
            f"{row['claims_passing_all_holdouts']}/{row['accepted_claims_with_multi_prompt']} | "
            f"{row['existing_same_family_rows']} | {len(row['eligible_claim_ids_missing_same_family_rows'])} | "
            f"{has_local} | `{row['status']}` |"
        )

    if blocked_runs:
        lines.extend(['', '## Blocked runs', ''])
        for row in blocked_runs:
            lines.append(f"### `{row['bundle']}` -> `{row.get('target_model') or 'n/a'}`")
            lines.append('')
            lines.append(f"- Reason: {row.get('blocked_reason', 'unspecified')}")
            if row.get('eligible_claim_ids'):
                lines.append(
                    '- Best claim ids to transfer first: ' + ', '.join(f"`{hid}`" for hid in row['eligible_claim_ids'][:5])
                )
            if row.get('discovered_local_dirs'):
                lines.append(
                    '- Discovered local directories (not all loadable): ' + ', '.join(f"`{p}`" for p in row['discovered_local_dirs'][:5])
                )
            lines.append(f"- Proposed command once weights are available: `{row.get('proposed_command', 'n/a')}`")
            lines.append('')

    OUT_MD.write_text('\n'.join(lines).rstrip() + '\n')
    print(str(OUT_JSON))

if __name__ == '__main__':
    main()
