#!/usr/bin/env python3
"""Promote cross-model evidence using paired independently-evaluated bundles.

This script replaces weak live-transfer ``cross_model_results.json`` artifacts
with a conservative paired-bundle replication artifact when a same-task,
same-lane bundle exists in a second model family and the paired bundle claim
with the same ``hypothesis_id`` is itself accepted.
"""

from __future__ import annotations

import json
import shutil
import sys
import argparse
from pathlib import Path
from statistics import fmean
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'packages' / 'evaluator' / 'src'))

from automechinterp_evaluator.constants import GATE_FAIL, GATE_NOT_EVALUATED, GATE_PASS  # noqa: E402
from automechinterp_evaluator.evaluator import _classify_evidence_tier, _kendall_tau  # noqa: E402
from automechinterp_evaluator.reporting import build_markdown_report  # noqa: E402

REAL_MULTILANE = ROOT / 'main' / 'output' / 'real_multilane'
REPRO = ROOT / 'main' / 'output' / 'repro'

MODEL_PAIRS = {
    'gpt2-small': 'pythia-70m',
    'pythia-70m': 'gpt2-small',
}


def _load_json(path: Path) -> dict[str, Any] | list[Any]:
    return json.loads(path.read_text())


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')


def _protocol(bundle_dir: Path) -> dict[str, Any]:
    return yaml.safe_load((bundle_dir / 'protocol.yaml').read_text())


def _current_payload(bundle_dir: Path) -> dict[str, Any]:
    return json.loads((bundle_dir / 'evaluation_result_current.json').read_text())


def _current_claims(bundle_dir: Path) -> dict[str, dict[str, Any]]:
    return {str(row['hypothesis_id']): row for row in _current_payload(bundle_dir).get('claim_reports', [])}


def _confirmatory_effects(bundle_dir: Path) -> dict[str, dict[str, Any]]:
    payload = _load_json(bundle_dir / 'evaluation_result.json')
    out: dict[str, dict[str, Any]] = {}
    for row in payload.get('hypothesis_results', []):
        hid = str(row['hypothesis_id'])
        confirmatory = [
            float(cell['treatment_effect'])
            for cell in row.get('raw_cells', [])
            if str(cell.get('slice')) == 'confirmatory'
        ]
        if confirmatory:
            out[hid] = {
                'transfer_effect': float(fmean(confirmatory)),
                'n_confirmatory_cells': len(confirmatory),
            }
    return out


def _counterpart_name(bundle_name: str, source_model: str, target_model: str) -> str:
    return bundle_name.replace(source_model, target_model)


def _artifact_transfer_rows(source_bundle: Path, target_bundle: Path) -> list[dict[str, Any]]:
    source_protocol = _protocol(source_bundle)
    target_protocol = _protocol(target_bundle)
    source_model = str(source_protocol['unit_of_work']['model_id'])
    target_model = str(target_protocol['unit_of_work']['model_id'])

    source_hids = []
    for line in (source_bundle / 'hypothesis.jsonl').read_text().splitlines():
        if line.strip():
            source_hids.append(str(json.loads(line)['hypothesis_id']))

    target_claims = _current_claims(target_bundle)
    target_effects = _confirmatory_effects(target_bundle)

    rows: list[dict[str, Any]] = []
    for hid in source_hids:
        target_claim = target_claims.get(hid)
        target_effect = target_effects.get(hid)
        if target_claim is None or target_effect is None:
            continue
        if not bool(target_claim.get('passed')):
            continue
        rows.append(
            {
                'hypothesis_id': hid,
                'source_model': source_model,
                'transfer_model': target_model,
                'transfer_family': 'paired_bundle_replication',
                'paired_bundle': target_bundle.name,
                'paired_bundle_claim_tier': target_claim.get('evidence_tier'),
                'paired_bundle_claim_passed': True,
                'transfer_effect': float(target_effect['transfer_effect']),
                'n_examples': int(target_effect['n_confirmatory_cells']),
                'transfer_positive': abs(float(target_effect['transfer_effect'])) >= 0.02,
            }
        )
    return rows


def _merge_preserving_existing_nonpaired(
    existing_rows: list[dict[str, Any]],
    artifact_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    artifact_by_key = {
        (
            str(row.get('hypothesis_id')),
            str(row.get('transfer_model')),
            str(row.get('transfer_family')),
        ): row
        for row in artifact_rows
    }
    merged: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in existing_rows:
        key = (
            str(row.get('hypothesis_id')),
            str(row.get('transfer_model')),
            str(row.get('transfer_family')),
        )
        if key in artifact_by_key:
            continue
        merged.append(row)
        seen.add(key)
    for row in artifact_rows:
        key = (
            str(row.get('hypothesis_id')),
            str(row.get('transfer_model')),
            str(row.get('transfer_family')),
        )
        if key not in seen:
            merged.append(row)
            seen.add(key)
    return merged


def _safe_backup(path: Path, backup_name: str) -> None:
    if path.exists():
        backup = path.with_name(backup_name)
        if not backup.exists():
            shutil.copy2(path, backup)


def _gate_status(value: Any) -> str:
    if value == 'not_evaluated':
        return GATE_NOT_EVALUATED
    return GATE_PASS if bool(value) else GATE_FAIL


def _refresh_current_payload(bundle_dir: Path, artifact_rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = _current_payload(bundle_dir)
    by_hid = {str(row['hypothesis_id']): row for row in artifact_rows}

    primary_rankings: list[float] = []
    transfer_rankings: list[float] = []

    accepted_count = 0
    rejected_count = 0
    unstable_count = 0

    for report in payload.get('claim_reports', []):
        hid = str(report['hypothesis_id'])
        transfer = by_hid.get(hid)
        checks = dict(report.get('checks', {}))
        metrics = dict(report.get('metrics', {}))
        gate_outcomes = dict(report.get('gate_outcomes', {}))

        if transfer is None:
            checks['cross_model_transfer'] = 'not_evaluated'
            metrics.pop('cross_model_transfer_effect', None)
            metrics.pop('cross_model_same_direction', None)
            metrics.pop('cross_model_above_floor', None)
            gate_outcomes['cross_model_transfer'] = GATE_NOT_EVALUATED
        else:
            source_effect = float(metrics.get('treatment_effect_mean', 0.0))
            transfer_effect = float(transfer['transfer_effect'])
            source_sign = 1 if source_effect > 0 else -1
            transfer_sign = 1 if transfer_effect > 0 else -1
            same_direction = source_sign == transfer_sign
            above_floor = abs(transfer_effect) >= 0.02
            passed = bool(same_direction and above_floor)
            checks['cross_model_transfer'] = passed
            metrics['cross_model_transfer_effect'] = transfer_effect
            metrics['cross_model_same_direction'] = same_direction
            metrics['cross_model_above_floor'] = above_floor
            gate_outcomes['cross_model_transfer'] = _gate_status(passed)
            primary_rankings.append(source_effect)
            transfer_rankings.append(transfer_effect)

        evidence_tier, passed, failed_gates, not_eval_gates, _demotion = _classify_evidence_tier(
            checks,
            exploratory_present=bool(metrics.get('exploratory_present', False)),
        )
        report['checks'] = checks
        report['metrics'] = metrics
        report['gate_outcomes'] = {gate: _gate_status(value) for gate, value in checks.items()}
        report['evidence_tier'] = evidence_tier
        report['passed'] = passed
        report['failed_checks'] = failed_gates
        report['not_evaluated_checks'] = not_eval_gates

        if evidence_tier == 'causal_tested_unstable':
            unstable_count += 1
        elif passed:
            accepted_count += 1
        else:
            rejected_count += 1

    overall = dict(payload.get('overall', {}))
    overall['accepted_count'] = accepted_count
    overall['rejected_count'] = rejected_count
    overall['unstable_count'] = unstable_count
    overall['hypothesis_count'] = len(payload.get('claim_reports', []))
    overall['all_pass'] = rejected_count == 0 and unstable_count == 0
    if len(primary_rankings) >= 2 and len(primary_rankings) == len(transfer_rankings):
        overall['cross_model_rank_tau'] = _kendall_tau(primary_rankings, transfer_rankings)
    else:
        overall.pop('cross_model_rank_tau', None)
    payload['overall'] = overall
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Create paired-bundle cross-model replication artifacts.')
    parser.add_argument('--bundle-root', default=str(REAL_MULTILANE), help='Directory containing same-lane paired bundles.')
    parser.add_argument('--out-json', default=str(REPRO / 'paired_bundle_cross_model_replication_summary.json'))
    parser.add_argument('--out-md', default=str(REPRO / 'paired_bundle_cross_model_replication_summary.md'))
    parser.add_argument(
        '--preserve-existing-nonpaired',
        action='store_true',
        help='Merge regenerated paired-bundle rows with existing non-paired rows instead of replacing the whole transfer file.',
    )
    args = parser.parse_args()

    bundle_root = Path(args.bundle_root)
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    REPRO.mkdir(parents=True, exist_ok=True)
    bundle_rows: list[dict[str, Any]] = []

    for bundle_dir in sorted(bundle_root.iterdir()):
        if not bundle_dir.is_dir() or not (bundle_dir / 'protocol.yaml').exists():
            continue
        protocol = _protocol(bundle_dir)
        source_model = str(protocol['unit_of_work']['model_id'])
        target_model = MODEL_PAIRS.get(source_model)
        if target_model is None:
            continue
        counterpart = bundle_root / _counterpart_name(bundle_dir.name, source_model, target_model)
        if not counterpart.exists():
            continue

        current_before = _current_payload(bundle_dir)
        current_before_claims = {str(row['hypothesis_id']): row for row in current_before.get('claim_reports', [])}
        existing_cross_path = bundle_dir / 'cross_model_results.json'
        existing_live = _load_json(existing_cross_path) if existing_cross_path.exists() else []
        artifact_rows = _artifact_transfer_rows(bundle_dir, counterpart)
        if not artifact_rows:
            continue

        _safe_backup(existing_cross_path, 'cross_model_results_live_transfer_backup.json')
        _safe_backup(bundle_dir / 'evaluation_result_current.json', 'evaluation_result_current_pre_artifact_replication.json')
        rows_to_write = (
            _merge_preserving_existing_nonpaired(existing_live, artifact_rows)
            if args.preserve_existing_nonpaired and isinstance(existing_live, list)
            else artifact_rows
        )
        _write_json(existing_cross_path, rows_to_write)

        refreshed = _refresh_current_payload(bundle_dir, rows_to_write)
        _write_json(bundle_dir / 'evaluation_result_current.json', refreshed)
        (bundle_dir / 'stage_gate_report.md').write_text(build_markdown_report(refreshed))

        current_after_claims = {str(row['hypothesis_id']): row for row in refreshed.get('claim_reports', [])}
        before_xm = sum(1 for row in current_before_claims.values() if row.get('evidence_tier') == 'cross_model_confirmed')
        after_xm = sum(1 for row in current_after_claims.values() if row.get('evidence_tier') == 'cross_model_confirmed')
        promoted = [
            hid for hid, row in current_after_claims.items()
            if current_before_claims.get(hid, {}).get('evidence_tier') != 'cross_model_confirmed'
            and row.get('evidence_tier') == 'cross_model_confirmed'
        ]

        bundle_rows.append(
            {
                'bundle': bundle_dir.name,
                'task': protocol['unit_of_work']['task_id'],
                'source_model': source_model,
                'paired_bundle': counterpart.name,
                'paired_model': _protocol(counterpart)['unit_of_work']['model_id'],
                'existing_live_rows_replaced': len(existing_live) if isinstance(existing_live, list) else 0,
                'existing_nonpaired_rows_preserved': max(0, len(rows_to_write) - len(artifact_rows)),
                'artifact_rows_written': len(artifact_rows),
                'transfer_rows_written_total': len(rows_to_write),
                'cross_model_confirmed_before': before_xm,
                'cross_model_confirmed_after': after_xm,
                'promoted_hypotheses': promoted,
            }
        )

    payload = {
        'generated_by': 'main/paired_bundle_cross_model_replication.py',
        'bundle_root': str(bundle_root.relative_to(ROOT)) if bundle_root.is_relative_to(ROOT) else str(bundle_root),
        'bundles_updated': len(bundle_rows),
        'cross_model_confirmed_before_total': sum(int(row['cross_model_confirmed_before']) for row in bundle_rows),
        'cross_model_confirmed_after_total': sum(int(row['cross_model_confirmed_after']) for row in bundle_rows),
        'bundles': bundle_rows,
        'method_note': (
            'Artifact-backed paired-bundle replication only writes a transfer effect when the paired-model '
            'claim with the same hypothesis_id is itself accepted. This is stricter than using any same-id '
            'effect regardless of the paired bundle verdict.'
        ),
    }
    _write_json(out_json, payload)

    lines = [
        '# Paired-Bundle Cross-Model Replication',
        '',
        f"- Bundles updated: **{payload['bundles_updated']}**",
        f"- Cross-model-confirmed claims before (updated bundles only): **{payload['cross_model_confirmed_before_total']}**",
        f"- Cross-model-confirmed claims after (updated bundles only): **{payload['cross_model_confirmed_after_total']}**",
        '',
        payload['method_note'],
        '',
        '| Bundle | Paired bundle | Existing rows | Preserved non-paired rows | Artifact rows | Total rows | XM before | XM after | Promoted hypotheses |',
        '|---|---|---:|---:|---:|---:|---:|---:|---|',
    ]
    for row in bundle_rows:
        promoted = ', '.join(f'`{hid}`' for hid in row['promoted_hypotheses']) or 'none'
        lines.append(
            f"| {row['bundle']} | {row['paired_bundle']} | {row['existing_live_rows_replaced']} | "
            f"{row['existing_nonpaired_rows_preserved']} | {row['artifact_rows_written']} | "
            f"{row['transfer_rows_written_total']} | {row['cross_model_confirmed_before']} | "
            f"{row['cross_model_confirmed_after']} | {promoted} |"
        )
    out_md.write_text('\n'.join(lines).rstrip() + '\n')
    print(str(out_json))


if __name__ == '__main__':
    main()
