from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "colean_mathlib").exists() or (parent / "work" / "colean_mathlib").exists():
            return parent
    return here.parents[1]


ROOT = repo_root()
MATHLIB_PROJECT = (
    ROOT / "colean_mathlib"
    if (ROOT / "colean_mathlib").exists()
    else ROOT / "work" / "colean_mathlib"
)
OUT = ROOT / "outputs"
