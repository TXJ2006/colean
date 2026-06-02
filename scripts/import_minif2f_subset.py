from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "downloads" / "miniF2F-lean4"
DEFAULT_OUTPUT = ROOT / "docs" / "benchmarks" / "miniF2F_sample_v0.json"


def extract_theorem_header(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(theorem\s+.*?)(:=\s*by\s+sorry)", text, re.DOTALL)
    if not match:
        return None
    header = match.group(1).rstrip()
    return f"{header} := by"


def task_from_file(path: Path, source_root: Path) -> dict[str, object] | None:
    theorem_header = extract_theorem_header(path)
    if theorem_header is None:
        return None
    task_id = path.stem
    relative_path = path.relative_to(source_root).as_posix()
    return {
        "task_id": f"minif2f_test_{task_id}",
        "source": "miniF2F-lean4/test",
        "source_path": relative_path,
        "project_path": "downloads/miniF2F-lean4",
        "imports": ["Mathlib"],
        "lemma": task_id,
        "theorem_header": theorem_header,
        "informal_goal": "",
        "candidates": [
            {"option_id": "rfl", "weight": 0.50, "tactics": ["rfl"]},
            {"option_id": "norm_num", "weight": 0.45, "tactics": ["norm_num"]},
            {"option_id": "ring_nf", "weight": 0.40, "tactics": ["ring_nf"]},
            {"option_id": "omega", "weight": 0.35, "tactics": ["omega"]},
            {"option_id": "linarith", "weight": 0.30, "tactics": ["linarith"]},
            {"option_id": "nlinarith", "weight": 0.25, "tactics": ["nlinarith"]},
        ],
    }


def build_subset(source_root: Path, split: str, limit: int) -> list[dict[str, object]]:
    split_dir = source_root / "MiniF2F" / split
    if not split_dir.exists():
        raise FileNotFoundError(f"miniF2F split directory not found: {split_dir}")
    tasks: list[dict[str, object]] = []
    for path in sorted(split_dir.glob("*.lean")):
        task = task_from_file(path, source_root)
        if task is None:
            continue
        tasks.append(task)
        if len(tasks) >= limit:
            break
    return tasks


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a CoLean harness JSON subset from miniF2F-lean4.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--split", default="Test")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    tasks = build_subset(args.source, args.split, args.limit)
    payload = {
        "benchmark": "miniF2F-lean4",
        "split": args.split,
        "source_repository": "https://github.com/yangky11/miniF2F-lean4",
        "source_revision": git_revision(args.source),
        "tasks": tasks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)


def git_revision(path: Path) -> str:
    head = path / ".git" / "HEAD"
    if not head.exists():
        return "unknown"
    value = head.read_text(encoding="utf-8").strip()
    if value.startswith("ref: "):
        ref = path / ".git" / value[5:]
        if ref.exists():
            return ref.read_text(encoding="utf-8").strip()
    return value


if __name__ == "__main__":
    main()
