#!/usr/bin/env bash
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
eval "${CLI} evaluate --bundle "${SCRIPT_DIR}" --output "${SCRIPT_DIR}/reproduced_result.json""

echo ""
echo "Step 2: Generate report"
eval "${CLI} report --bundle "${SCRIPT_DIR}" --output "${SCRIPT_DIR}/reproduced_report.md""

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
