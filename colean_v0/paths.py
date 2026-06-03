from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "colean_mathlib").exists() or (parent / "work" / "colean_mathlib").exists():
            return parent
    return here.parents[1]


ROOT = repo_root()
_mathlib_project_override = os.environ.get("COLEAN_MATHLIB_PROJECT")
MATHLIB_PROJECT = (
    Path(_mathlib_project_override)
    if _mathlib_project_override
    else ROOT / "colean_mathlib"
    if (ROOT / "colean_mathlib").exists()
    else ROOT / "work" / "colean_mathlib"
)
OUT = ROOT / "outputs"
