from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "tools" / "check_release_overclaims.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_release_overclaims", CHECKER_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_overclaim_checker_allows_negated_spotlight_quality_language() -> None:
    checker = _load_checker()

    text = "The current evidence is not high-confidence release quality until external evidence lands."

    assert checker.find_overclaims(text) == []


def test_overclaim_checker_rejects_positive_spotlight_ready_language() -> None:
    checker = _load_checker()

    text = "The paper is spotlight-ready after this pass."

    findings = checker.find_overclaims(text)

    assert findings
    assert "spotlight-ready" in findings[0]


def test_overclaim_checker_rejects_positive_genuine_quality_language(tmp_path: Path) -> None:
    checker = _load_checker()
    paper = tmp_path / "paper.md"
    paper.write_text("This is now high-confidence release quality.\n")

    failures = checker.check_files([paper], release_quality_certified=False)

    assert failures
    assert failures[0]["path"].endswith("paper.md") or failures[0]["path"]


def test_overclaim_checker_skips_when_certified(tmp_path: Path) -> None:
    checker = _load_checker()
    paper = tmp_path / "paper.md"
    paper.write_text("This is now high-confidence release quality.\n")

    assert checker.check_files([paper], release_quality_certified=True) == []
