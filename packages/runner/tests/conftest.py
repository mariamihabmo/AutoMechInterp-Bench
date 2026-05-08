from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
STAGE1_SRC = ROOT.parent / "evaluator" / "src"

for path in (SRC, STAGE1_SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
