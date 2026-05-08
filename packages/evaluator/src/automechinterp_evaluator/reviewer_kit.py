"""Reviewer kit builder for publication.

This module assembles a portable, bundle-centered review package with the
artifacts needed to inspect a claim bundle and rerun the deterministic
Stage-1 evaluator. The kit is not fully standalone: reviewers still need
either the installed evaluator package or a checkout of the repository.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .evaluator import evaluate_bundle
from .ledger import write_claim_ledger
from .protocol_critic import critique_protocol, format_critic_report
from .reporting import build_markdown_report


def _repo_relative(path: Path) -> str:
    resolved = path.resolve()
    for parent in resolved.parents:
        if (parent / "packages").exists() and (parent / "main").exists():
            try:
                return str(resolved.relative_to(parent))
            except Exception:
                break
    # never leak host-local
    # absolute paths into reviewer-kit metadata. Reviewer kits are
    # public-facing; falling back to ``str(resolved)`` would expose the
    # author's home directory layout. Emit a placeholder that records the
    # filename only, so downstream consumers can still distinguish files.
    return f"<outside_repo>/{resolved.name}"


def build_reviewer_kit(
    bundle_dir: Path,
    output_dir: Path,
    *,
    include_env: bool = True,
) -> Path:
    """Assemble a reviewer-ready audit package.

    Contents:
        reviewer_kit/
        ├── protocol.yaml
        ├── hypothesis.jsonl
        ├── evaluation_result.json
        ├── manifest.json
        ├── cross_model_results.json (if available)
        ├── claim_ledger.json
        ├── stage_gate_report.md
        ├── protocol_critic_report.md
        ├── kit_manifest.json
        ├── README_reviewer.md
        ├── reproduce.sh
        ├── environment_lockfile.txt (if available)
        └── environment_info.json (if available)

    Reproduction requirement:
        the kit can be re-evaluated with either an installed
        ``automechinterp_evaluator`` package or a repository checkout made
        available via ``AUTOMECHINTERP_REPO_ROOT``.
    """
    bundle_dir = bundle_dir.resolve()
    output_dir = output_dir.resolve()
    kit_dir = output_dir / "reviewer_kit"
    kit_dir.mkdir(parents=True, exist_ok=True)

    copied_files: list[str] = []

    # Copy core artifacts.
    for name in (
        "protocol.yaml",
        "hypothesis.jsonl",
        "evaluation_result.json",
        "manifest.json",
        "cross_model_results.json",
        "submission_review.json",
        "submission_review.md",
    ):
        src = bundle_dir / name
        if src.exists():
            shutil.copy2(src, kit_dir / name)
            copied_files.append(name)

    # Copy environment files if present.
    if include_env:
        for name in ("environment_lockfile.txt", "environment_info.json"):
            src = bundle_dir / name
            if src.exists():
                shutil.copy2(src, kit_dir / name)
                copied_files.append(name)

    # Run evaluation and generate artifacts.
    result = evaluate_bundle(bundle_dir)

    # Write claim ledger.
    write_claim_ledger(result, kit_dir / "claim_ledger.json")

    # Write markdown report.
    report_md = build_markdown_report(result)
    (kit_dir / "stage_gate_report.md").write_text(report_md)

    # Write protocol critic report.
    protocol_path = bundle_dir / "protocol.yaml"
    critique = None
    if protocol_path.exists():
        import yaml
        try:
            with open(protocol_path) as f:
                protocol = yaml.safe_load(f) or {}
            critique = critique_protocol(protocol)
            critic_md = format_critic_report(critique)
            (kit_dir / "protocol_critic_report.md").write_text(critic_md)
        except Exception:
            critique = None  # non-critical — don't block kit generation

    # Write kit manifest.
    kit_manifest = {
        "bundle_source": _repo_relative(bundle_dir),
        "copied_files": sorted(copied_files),
        "generated_files": [
            "claim_ledger.json",
            "stage_gate_report.md",
            "protocol_critic_report.md" if critique is not None else None,
            "README_reviewer.md",
            "reproduce.sh",
        ],
        "reproduction_requirements": {
            "supports_installed_package": True,
            "supports_repo_checkout": True,
            "env_var_for_repo_checkout": "AUTOMECHINTERP_REPO_ROOT",
        },
    }
    (kit_dir / "kit_manifest.json").write_text(json.dumps(kit_manifest, sort_keys=True, indent=2) + "\n")

    # Write reproduction script and reviewer README.
    _write_reproduce_script(kit_dir)
    _write_reviewer_readme(kit_dir, result, bundle_dir)

    return kit_dir


def _write_reproduce_script(kit_dir: Path) -> None:
    script = """#!/usr/bin/env bash
# Reproduction script for reviewer audit
# Run: bash reproduce.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== AutoMechInterp reviewer-kit reproduction ==="
echo ""

resolve_cli() {
    if python3 -c "import automechinterp_evaluator" >/dev/null 2>&1; then
        export PYTHONPATH="${PYTHONPATH:-}"
        echo "python3 -m automechinterp_evaluator.cli"
        return 0
    fi

    if [ -n "${AUTOMECHINTERP_REPO_ROOT:-}" ] && [ -d "${AUTOMECHINTERP_REPO_ROOT}/packages/evaluator/src/automechinterp_evaluator" ]; then
        export PYTHONPATH="${AUTOMECHINTERP_REPO_ROOT}:${AUTOMECHINTERP_REPO_ROOT}/packages/evaluator/src:${AUTOMECHINTERP_REPO_ROOT}/packages/runner/src:${PYTHONPATH:-}"
        echo "python3 -m automechinterp_evaluator.cli"
        return 0
    fi

    if [ -d "${SCRIPT_DIR}/../packages/evaluator/src/automechinterp_evaluator" ]; then
        REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
        export PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/packages/evaluator/src:${REPO_ROOT}/packages/runner/src:${PYTHONPATH:-}"
        echo "python3 -m automechinterp_evaluator.cli"
        return 0
    fi

    echo "ERROR: reviewer_kit requires either" >&2
    echo "  1) an installed automechinterp_evaluator package, or" >&2
    echo "  2) a repo checkout exposed via AUTOMECHINTERP_REPO_ROOT." >&2
    return 1
}

CLI="$(resolve_cli)"
echo "Using CLI: ${CLI}"

echo ""
echo "Step 1: Evaluate bundle"
eval "${CLI} evaluate --bundle \"${SCRIPT_DIR}\" --output \"${SCRIPT_DIR}/reproduced_result.json\""

echo ""
echo "Step 2: Generate report"
eval "${CLI} report --bundle \"${SCRIPT_DIR}\" --output \"${SCRIPT_DIR}/reproduced_report.md\""

echo ""
echo "Step 3: Compare reports"
if diff -q "${SCRIPT_DIR}/stage_gate_report.md" "${SCRIPT_DIR}/reproduced_report.md" > /dev/null 2>&1; then
    echo "PASS: Reproduced report matches original."
else
    echo "WARN: Reproduced report differs from original."
    echo "      This may indicate non-determinism, artifact drift, or evaluator changes."
    diff "${SCRIPT_DIR}/stage_gate_report.md" "${SCRIPT_DIR}/reproduced_report.md" || true
fi

echo ""
echo "=== Reproduction complete ==="
"""
    path = kit_dir / "reproduce.sh"
    path.write_text(script)
    path.chmod(0o755)


def _write_reviewer_readme(kit_dir: Path, result: dict[str, Any], bundle_dir: Path) -> None:
    overall = result["overall"]
    readme = f"""# Reviewer Audit Kit

## What this is

This kit packages the core bundle artifacts, claim ledger, stage-gate report,
and protocol critic output for a single evaluated bundle.

It is **portable but not fully standalone**. To rerun the evaluator you need
either:

1. an installed `automechinterp_evaluator` package, or
2. a checkout of this repository exposed via `AUTOMECHINTERP_REPO_ROOT`.

## Quick Start
```bash
bash reproduce.sh
```

## Bundle source
- Source bundle: `{_repo_relative(bundle_dir)}`

## Contents
- `protocol.yaml` — frozen protocol defining all execution parameters
- `hypothesis.jsonl` — pre-registered hypotheses with predicted effects
- `evaluation_result.json` — raw intervention results with provenance
- `manifest.json` — SHA-256 hashes of core artifacts
- `cross_model_results.json` — released transfer diagnostics when present
- `claim_ledger.json` — machine-readable verdict for every claim
- `stage_gate_report.md` — human-readable stage-gate report
- `protocol_critic_report.md` — protocol-level readiness critique when available
- `kit_manifest.json` — reviewer-kit inventory and reproduction requirements
- `reproduce.sh` — one-command reproduction helper

## Summary
- **Protocol**: `{result['protocol_id']}`
- **Protocol Hash**: `{result['protocol_hash']}`
- **Total Hypotheses**: {overall['hypothesis_count']}
- **Accepted**: {overall['accepted_count']}
- **Unstable**: {overall['unstable_count']}
- **Rejected**: {overall['rejected_count']}
- **All Pass**: {overall['all_pass']}

## Verification Steps
1. Run `bash reproduce.sh` to re-evaluate from the copied artifacts.
2. Check that `manifest.json` hashes match file contents.
3. Review `claim_ledger.json` for per-claim verdicts.
4. Compare `stage_gate_report.md` with the reproduced output.
5. Inspect `protocol_critic_report.md` for missing controls or reporting gaps.

## Important caveats
- This kit does **not** prove mechanistic truth. It packages evidence for
  deterministic evaluation under the current contract.
- If `cross_model_results.json` is absent, the bundle should not be described as
  cross-model confirmed.
- The environment lockfile is a provenance artifact, not a guarantee that every
  dependency line is directly re-installable on every machine.
"""
    (kit_dir / "README_reviewer.md").write_text(readme)
