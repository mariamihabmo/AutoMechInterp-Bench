#!/usr/bin/env python3
"""Run a broad per-file test sweep and record results.

This avoids rare end-of-session hangs observed when invoking the entire test
suite in a single pytest process in this environment. Each test file is run in
its own subprocess with a timeout, yielding a more reliable repo-health signal.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "main" / "output" / "repro"
OUT_JSON = REPRO / "wide_test_sweep.json"
OUT_MD = REPRO / "wide_test_sweep.md"
TIMEOUT_SECONDS = 180

TEST_FILES = sorted(
    [str(path.relative_to(ROOT)) for path in (ROOT / "packages").rglob("test_*.py")]
)


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [
            str(ROOT),
            str(ROOT / "packages" / "evaluator" / "src"),
            str(ROOT / "packages" / "runner" / "src"),
            env.get("PYTHONPATH", ""),
        ]
    ).rstrip(os.pathsep)
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    return env


def _run(test_file: str) -> dict[str, Any]:
    cmd = [sys.executable, "-m", "pytest", test_file, "-q"]
    started = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            env=_env(),
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        duration = time.time() - started
        return {
            "test_file": test_file,
            "returncode": result.returncode,
            "duration_seconds": round(duration, 3),
            "stdout_tail": result.stdout[-1200:],
            "stderr_tail": result.stderr[-1200:],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        duration = time.time() - started
        return {
            "test_file": test_file,
            "returncode": 124,
            "duration_seconds": round(duration, 3),
            "stdout_tail": (exc.stdout or "")[-1200:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-1200:] if isinstance(exc.stderr, str) else "",
            "timed_out": True,
        }


def main() -> None:
    REPRO.mkdir(parents=True, exist_ok=True)
    rows = [_run(test_file) for test_file in TEST_FILES]
    passed = sum(1 for row in rows if row["returncode"] == 0)
    failed = [row for row in rows if row["returncode"] != 0]
    payload = {
        "generated_by": "main/wide_test_sweep.py",
        "timeout_seconds_per_file": TIMEOUT_SECONDS,
        "n_test_files": len(rows),
        "n_passed": passed,
        "n_failed": len(failed),
        "all_passed": not failed,
        "results": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Wide Test Sweep",
        "",
        f"- Test files run: **{len(rows)}**",
        f"- Passed: **{passed}**",
        f"- Failed: **{len(failed)}**",
        f"- Timeout per file: **{TIMEOUT_SECONDS}s**",
        "",
        "| Test file | Return code | Duration (s) | Timed out |",
        "|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['test_file']}` | {row['returncode']} | {row['duration_seconds']:.3f} | {row['timed_out']} |"
        )
    if failed:
        lines.extend(["", "## Failures", ""])
        for row in failed:
            lines.append(f"### `{row['test_file']}`")
            lines.append("")
            lines.append(f"- Return code: `{row['returncode']}`")
            lines.append(f"- Timed out: `{row['timed_out']}`")
            stdout = row["stdout_tail"].strip()
            stderr = row["stderr_tail"].strip()
            if stdout:
                lines.extend(["", "```text", stdout, "```"])
            if stderr:
                lines.extend(["", "```text", stderr, "```"])
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(str(OUT_JSON))
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
