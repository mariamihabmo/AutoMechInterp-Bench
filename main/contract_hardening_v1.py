#!/usr/bin/env python3
"""Evaluate a conservative contract-hardening candidate against current bundles.

This does NOT overwrite the released protocol. Instead it asks a concrete
question: is there a single, substantively-defensible tightening of the public
contract that sharply reduces agnostic false accepts while preserving most real
accepted claims?

Candidate V1:
- ``min_causal_effect`` >= 0.15
- ``statistical_policy.min_effect_floor`` >= 0.15
- ``min_specificity_ratio`` >= 5.0

The script re-evaluates the current canonical released bundle surface in
scratch copies with only those protocol fields hardened. That surface uses the
same zero-task real-repair supersession semantics as the publication summaries:
same-named legacy zero-task bundles are replaced by their real repair reruns
instead of double-counted. The script also runs the fresh agnostic stress under
the hardened protocol on multiple rotated namespaces using the evaluator's
default release-grade statistical budget. This is still a migration candidate,
not a silent change to the released contract.
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'main'))
sys.path.insert(0, str(ROOT / 'packages' / 'evaluator' / 'src'))

from _bundle_analysis import REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR, find_bundle_dirs, wilson_interval  # noqa: E402
from _stress_utils import build_synthetic_bundle  # noqa: E402
from stress_test_agnostic import _latent_hypotheses, _row_builder_factory  # noqa: E402
import automechinterp_evaluator.evaluator as evaluator_module  # noqa: E402
from automechinterp_evaluator.evaluator import evaluate_bundle  # noqa: E402
from automechinterp_evaluator.io_utils import read_jsonl, read_yaml  # noqa: E402

REPRO = ROOT / 'main' / 'output' / 'repro'
OUT_JSON = REPRO / 'contract_hardening_v1_summary.json'
OUT_MD = REPRO / 'contract_hardening_v1_summary.md'
STRESS_JSON = REPRO / 'stress_test_agnostic_hardened_v1.json'
STRESS_MD = REPRO / 'stress_test_agnostic_hardened_v1.md'
STRESS_REPLICATES_JSON = REPRO / 'stress_test_agnostic_hardened_v1_replicates.json'
STRESS_REPLICATES_MD = REPRO / 'stress_test_agnostic_hardened_v1_replicates.md'

HARDENING = {
    'min_causal_effect': 0.15,
    'min_effect_floor': 0.15,
    'min_specificity_ratio': 5.0,
}

STRESS_NAMESPACES = [
    'rotated_2026q2',
    'rotated_2026q3',
]

BOOTSTRAP_RESAMPLES: int | None = None
PERMUTATION_ITERATIONS: int | None = None

@contextmanager
def _stat_budget(
    bootstrap_resamples: int | None = BOOTSTRAP_RESAMPLES,
    permutation_iterations: int | None = PERMUTATION_ITERATIONS,
):
    if bootstrap_resamples is None and permutation_iterations is None:
        yield
        return

    original_bootstrap = evaluator_module._bootstrap_ci
    original_perm = evaluator_module._permutation_p_value

    def bootstrap_wrapper(values, confidence=0.95, n_resamples=None, seed='bootstrap'):
        target = bootstrap_resamples if bootstrap_resamples is not None else n_resamples
        return original_bootstrap(values, confidence=confidence, n_resamples=target, seed=seed)

    def perm_wrapper(values, n_permutations=None, seed='permtest'):
        target = permutation_iterations if permutation_iterations is not None else n_permutations
        return original_perm(values, n_permutations=target, seed=seed)

    evaluator_module._bootstrap_ci = bootstrap_wrapper
    evaluator_module._permutation_p_value = perm_wrapper
    try:
        yield
    finally:
        evaluator_module._bootstrap_ci = original_bootstrap
        evaluator_module._permutation_p_value = original_perm

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _bundle_dirs() -> list[Path]:
    return find_bundle_dirs(REAL_MULTI_TASK_DIR, REAL_MULTILANE_DIR)

def _harden_protocol(protocol: dict[str, Any]) -> dict[str, Any]:
    hardened = copy.deepcopy(protocol)
    hardened['protocol_id'] = f"{protocol['protocol_id']}_contract_hardening_v1"
    hardened['protocol_version'] = f"{protocol.get('protocol_version', '1.0')}-contract_hardening_v1"
    hardened.setdefault('stage_gates', {})
    hardened.setdefault('statistical_policy', {})
    hardened['stage_gates']['min_causal_effect'] = max(
        float(hardened['stage_gates'].get('min_causal_effect', 0.0)), HARDENING['min_causal_effect']
    )
    hardened['statistical_policy']['min_effect_floor'] = max(
        float(hardened['statistical_policy'].get('min_effect_floor', 0.0)), HARDENING['min_effect_floor']
    )
    hardened['stage_gates']['min_specificity_ratio'] = max(
        float(hardened['stage_gates'].get('min_specificity_ratio', 0.0)), HARDENING['min_specificity_ratio']
    )
    return hardened

def _rewrite_hypotheses(bundle_dir: Path, protocol_id: str) -> str:
    lines = []
    for line in (bundle_dir / 'hypothesis.jsonl').read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        row['protocol_id'] = protocol_id
        lines.append(json.dumps(row, sort_keys=False))
    return '\n'.join(lines) + ('\n' if lines else '')

def _evaluate_hardened_bundle(bundle_dir: Path) -> dict[str, Any]:
    protocol = yaml.safe_load((bundle_dir / 'protocol.yaml').read_text())
    hardened_protocol = _harden_protocol(protocol)
    with tempfile.TemporaryDirectory(prefix='contract_hardening_v1_') as tmpdir:
        tmp = Path(tmpdir)
        protocol_text = yaml.safe_dump(hardened_protocol, sort_keys=False)
        (tmp / 'protocol.yaml').write_text(protocol_text)
        (tmp / 'hypothesis.jsonl').write_text(_rewrite_hypotheses(bundle_dir, hardened_protocol['protocol_id']))

        evaluation_payload = json.loads((bundle_dir / 'evaluation_result.json').read_text())
        evaluation_payload['protocol_id'] = hardened_protocol['protocol_id']
        evaluation_payload['protocol_sha256'] = hashlib.sha256(protocol_text.encode()).hexdigest()
        (tmp / 'evaluation_result.json').write_text(json.dumps(evaluation_payload, indent=2, sort_keys=True) + '\n')

        cross_path = bundle_dir / 'cross_model_results.json'
        if cross_path.exists():
            shutil.copy2(cross_path, tmp / 'cross_model_results.json')

        manifest = {
            'protocol.yaml': _sha256(tmp / 'protocol.yaml'),
            'hypothesis.jsonl': _sha256(tmp / 'hypothesis.jsonl'),
            'evaluation_result.json': _sha256(tmp / 'evaluation_result.json'),
        }
        # the loader's transfer-hash
        # enforcementrequires
        # cross_model_results.json to appear in the manifest hash chain
        # whenever the file is present in the bundle. The hardened-bundle
        # rebuild copies the file but previously omitted its hash from the
        # rebuilt manifest, which now raises BundleError. Mirror the loader
        # contract by hashing the copy alongside the other canonical inputs.
        if (tmp / 'cross_model_results.json').exists():
            manifest['cross_model_results.json'] = _sha256(tmp / 'cross_model_results.json')
        (tmp / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
        with _stat_budget():
            return evaluate_bundle(tmp)

def _run_hardened_stress(seed_namespace: str) -> dict[str, Any]:
    base_bundle = ROOT / 'main' / 'output' / 'real_multi_task' / 'ioi_v0_gpt2-small'
    protocol = _harden_protocol(read_yaml(base_bundle / 'protocol.yaml'))
    protocol['protocol_id'] = f'stress_hardened_v1_{seed_namespace}_ioi_v0_gpt2-small'
    protocol['claim_budget']['max_total_claims'] = 200
    protocol['claim_budget']['max_claims_per_task'] = 200
    template = read_jsonl(base_bundle / 'hypothesis.jsonl')[0]
    hypotheses = _latent_hypotheses(
        template,
        protocol,
        200,
        seed_namespace=seed_namespace,
        generator_regime='fresh_v2',
    )
    for row in hypotheses:
        row['protocol_id'] = protocol['protocol_id']
    row_builder = _row_builder_factory(seed_namespace, 'fresh_v2')

    with tempfile.TemporaryDirectory(prefix='stress_hardened_v1_') as tmpdir:
        tmp = Path(tmpdir)
        build_synthetic_bundle(tmp, protocol, hypotheses, row_builder)
        with _stat_budget():
            result = evaluate_bundle(tmp)

    leaked_rows = [row for row in result.get('claim_reports', []) if row.get('passed')]
    leaked = len(leaked_rows)
    total = int(result.get('overall', {}).get('hypothesis_count', len(hypotheses)))
    ci = wilson_interval(leaked, total)
    payload = {
        'generated_by': 'main/contract_hardening_v1.py',
        'contract_hardening_v1': HARDENING,
        'generator_regime': 'fresh_v2',
        'seed_namespace': seed_namespace,
        # match the
        # provenance label emitted by main/stress_test_agnostic.py so external
        # readers cannot mistake the maintainer-authored generator for an
        # author-independent attack. See the longer note in
        # main/stress_test_agnostic.py.
        'stress_source': 'internal_maintainer',
        'stress_source_note': (
            "'agnostic' = evaluator-internals-blind (no suite labels / no "
            "threshold lookups), NOT author-independent. The generator is "
            "maintainer-authored; see "
            "methodology/independent_agnostic_stress_protocol.md for the "
            "future external-author protocol."
        ),
        'negatives': total,
        'leaked': leaked,
        'false_accept_rate': leaked / total if total else 0.0,
        'false_accept_rate_ci95': ci,
        'statistical_budget': {
            'bootstrap_resamples': BOOTSTRAP_RESAMPLES,
            'permutation_iterations': PERMUTATION_ITERATIONS,
        },
    }
    return payload

def _write_stress_reports(stress_rows: list[dict[str, Any]]) -> None:
    primary = stress_rows[0]
    STRESS_JSON.write_text(json.dumps(primary, indent=2, sort_keys=True) + '\n')
    primary_lines = [
        '# Evaluator-Agnostic Stress Under Contract Hardening V1',
        '',
        f"- Overrides: **min_causal_effect={HARDENING['min_causal_effect']}, min_effect_floor={HARDENING['min_effect_floor']}, min_specificity_ratio={HARDENING['min_specificity_ratio']}**",
        f"- Generator regime: **fresh_v2**",
        f"- Seed namespace: **{primary['seed_namespace']}**",
        f"- Negatives: **{primary['negatives']}**",
        f"- Leaked: **{primary['leaked']}/{primary['negatives']}**",
        f"- FAR: **{primary['false_accept_rate'] * 100:.1f}%**",
        f"- 95% CI: **{primary['false_accept_rate_ci95']['label']}**",
        '',
        'This compatibility artifact records the primary rotated namespace. The multi-namespace replicate report is `stress_test_agnostic_hardened_v1_replicates.md`.',
    ]
    STRESS_MD.write_text('\n'.join(primary_lines).rstrip() + '\n')

    worst_ci_high = max(float(row['false_accept_rate_ci95']['high']) for row in stress_rows)
    replicates = {
        'generated_by': 'main/contract_hardening_v1.py',
        'contract_hardening_v1': HARDENING,
        'generator_regime': 'fresh_v2',
        'namespace_count': len(stress_rows),
        'negatives_per_namespace': int(stress_rows[0]['negatives']) if stress_rows else 0,
        'statistical_budget': {
            'bootstrap_resamples': BOOTSTRAP_RESAMPLES,
            'permutation_iterations': PERMUTATION_ITERATIONS,
        },
        'worst_ci95_high': worst_ci_high,
        'all_ci95_upper_bounds_below_5pct': worst_ci_high < 0.05,
        'replicates': stress_rows,
    }
    STRESS_REPLICATES_JSON.write_text(json.dumps(replicates, indent=2, sort_keys=True) + '\n')
    lines = [
        '# Evaluator-Agnostic Stress Replicates Under Contract Hardening V1',
        '',
        f"- Overrides: **min_causal_effect={HARDENING['min_causal_effect']}, min_effect_floor={HARDENING['min_effect_floor']}, min_specificity_ratio={HARDENING['min_specificity_ratio']}**",
        f"- Generator regime: **fresh_v2**",
        f"- Statistical budget: **{'default release-grade' if BOOTSTRAP_RESAMPLES is None and PERMUTATION_ITERATIONS is None else f'bootstrap={BOOTSTRAP_RESAMPLES}, permutation={PERMUTATION_ITERATIONS}'}**",
        f"- Namespaces: **{len(stress_rows)}**",
        f"- Worst 95% upper bound: **{worst_ci_high * 100:.1f}%**",
        f"- All upper bounds below 5%: **{'yes' if worst_ci_high < 0.05 else 'no'}**",
        '',
        '| Seed namespace | Leaked | FAR | 95% CI |',
        '|---|---:|---:|---|',
    ]
    for row in stress_rows:
        lines.append(
            f"| `{row['seed_namespace']}` | {row['leaked']}/{row['negatives']} | {row['false_accept_rate'] * 100:.1f}% | {row['false_accept_rate_ci95']['label']} |"
        )
    lines.extend(
        [
            '',
            'These are diagnostic stress replicates for a versioned contract-migration candidate. They do not change the released contract unless adopted through protocol governance.',
        ]
    )
    STRESS_REPLICATES_MD.write_text('\n'.join(lines).rstrip() + '\n')

def main() -> None:
    REPRO.mkdir(parents=True, exist_ok=True)
    bundle_rows: list[dict[str, Any]] = []
    tasks_with_accept_after: set[str] = set()

    for bundle_dir in _bundle_dirs():
        protocol = yaml.safe_load((bundle_dir / 'protocol.yaml').read_text())
        current = json.loads((bundle_dir / 'evaluation_result_current.json').read_text())
        hardened = _evaluate_hardened_bundle(bundle_dir)
        task = str(protocol['unit_of_work']['task_id'])

        before_claims = {str(row['hypothesis_id']): row for row in current.get('claim_reports', [])}
        after_claims = {str(row['hypothesis_id']): row for row in hardened.get('claim_reports', [])}
        if int(hardened.get('overall', {}).get('accepted_count', 0)) > 0:
            tasks_with_accept_after.add(task)

        demoted = [
            hid for hid, row in before_claims.items()
            if bool(row.get('passed')) and not bool(after_claims.get(hid, {}).get('passed'))
        ]
        promoted = [
            hid for hid, row in after_claims.items()
            if bool(row.get('passed')) and not bool(before_claims.get(hid, {}).get('passed'))
        ]
        bundle_rows.append(
            {
                'bundle': bundle_dir.name,
                'task': task,
                'model': protocol['unit_of_work']['model_id'],
                'accepted_before': int(current.get('overall', {}).get('accepted_count', 0)),
                'accepted_after': int(hardened.get('overall', {}).get('accepted_count', 0)),
                'cross_model_confirmed_after': sum(
                    1 for row in hardened.get('claim_reports', [])
                    if row.get('evidence_tier') == 'cross_model_confirmed'
                ),
                'demoted_hypotheses': demoted,
                'newly_promoted_hypotheses': promoted,
            }
        )

    stress_rows = [_run_hardened_stress(namespace) for namespace in STRESS_NAMESPACES]
    _write_stress_reports(stress_rows)
    primary_stress = stress_rows[0]
    worst_stress_ci_high = max(float(row['false_accept_rate_ci95']['high']) for row in stress_rows)
    total_before = sum(int(row['accepted_before']) for row in bundle_rows)
    total_after = sum(int(row['accepted_after']) for row in bundle_rows)
    cross_model_after = sum(int(row['cross_model_confirmed_after']) for row in bundle_rows)
    criteria = {
        'second_cross_model_confirmed_claim': cross_model_after >= 2,
        'agnostic_far_upper_bound_below_5pct': worst_stress_ci_high < 0.05,
    }

    payload = {
        'generated_by': 'main/contract_hardening_v1.py',
        'contract_hardening_v1': HARDENING,
        'accepted_claims_before_total': total_before,
        'accepted_claims_after_total': total_after,
        'accepted_claim_retention_rate': total_after / total_before if total_before else 0.0,
        'tasks_with_accepted_after': sorted(tasks_with_accept_after),
        'tasks_with_accepted_after_count': len(tasks_with_accept_after),
        'cross_model_confirmed_after_total': cross_model_after,
        'bundles_changed': [row for row in bundle_rows if row['accepted_before'] != row['accepted_after'] or row['demoted_hypotheses'] or row['newly_promoted_hypotheses']],
        'bundles': bundle_rows,
        'fresh_agnostic_hardened_v1': primary_stress,
        'fresh_agnostic_hardened_v1_replicates': {
            'namespace_count': len(stress_rows),
            'worst_ci95_high': worst_stress_ci_high,
            'all_ci95_upper_bounds_below_5pct': worst_stress_ci_high < 0.05,
            'replicates': stress_rows,
        },
        'criteria_closed_under_v1': criteria,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')

    lines = [
        '# Contract Hardening V1 Summary',
        '',
        f"- Overrides: **min_causal_effect={HARDENING['min_causal_effect']}, min_effect_floor={HARDENING['min_effect_floor']}, min_specificity_ratio={HARDENING['min_specificity_ratio']}**",
        f"- Accepted claims before: **{total_before}**",
        f"- Accepted claims after: **{total_after}**",
        f"- Accepted-claim retention: **{(total_after / total_before * 100) if total_before else 0:.1f}%**",
        f"- Tasks with accepted claims after: **{len(tasks_with_accept_after)}** ({', '.join(sorted(tasks_with_accept_after))})",
        f"- Cross-model-confirmed claims after: **{cross_model_after}**",
        f"- Primary fresh agnostic hardened FAR: **{primary_stress['false_accept_rate'] * 100:.1f}%** with 95% CI **{primary_stress['false_accept_rate_ci95']['label']}**",
        f"- Worst agnostic replicate 95% upper bound: **{worst_stress_ci_high * 100:.1f}%**",
        '',
        '## Which release-quality blockers this closes under V1',
        '',
        f"- `second_cross_model_confirmed_claim`: **{'yes' if criteria['second_cross_model_confirmed_claim'] else 'no'}**",
        f"- `agnostic_far_upper_bound_below_5pct`: **{'yes' if criteria['agnostic_far_upper_bound_below_5pct'] else 'no'}**",
        '',
        '## Agnostic stress replicates',
        '',
        '| Seed namespace | Leaked | FAR | 95% CI |',
        '|---|---:|---:|---|',
    ]
    for row in stress_rows:
        lines.append(
            f"| `{row['seed_namespace']}` | {row['leaked']}/{row['negatives']} | {row['false_accept_rate'] * 100:.1f}% | {row['false_accept_rate_ci95']['label']} |"
        )
    lines.extend(
        [
            '',
            'This is a versioned protocol-migration candidate, not the current released contract. The retention and stress results should be read as a tradeoff analysis.',
            '',
            '## Bundles with changed accepted counts',
            '',
            '| Bundle | Accepted before | Accepted after | Cross-model confirmed after | Demoted hypotheses |',
            '|---|---:|---:|---:|---|',
        ]
    )
    changed_rows = [row for row in bundle_rows if row['accepted_before'] != row['accepted_after']]
    if changed_rows:
        for row in changed_rows:
            demoted = ', '.join(f'`{hid}`' for hid in row['demoted_hypotheses']) or 'none'
            lines.append(
                f"| {row['bundle']} | {row['accepted_before']} | {row['accepted_after']} | {row['cross_model_confirmed_after']} | {demoted} |"
            )
    else:
        lines.append('| _none_ |  |  |  |  |')
    OUT_MD.write_text('\n'.join(lines).rstrip() + '\n')
    print(str(OUT_JSON))

if __name__ == '__main__':
    main()
