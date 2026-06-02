from __future__ import annotations

import argparse
import json
import subprocess
import time
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from local_llm_generator import default_tasks
from paths import MATHLIB_PROJECT, OUT, ROOT


@dataclass(frozen=True)
class BenchmarkCandidate:
    option_id: str
    tactics: tuple[str, ...]
    weight: float


@dataclass(frozen=True)
class BenchmarkTask:
    task_id: str
    source: str
    lemma: str
    theorem_header: str
    informal_goal: str
    imports: tuple[str, ...]
    project_path: Path
    candidates: tuple[BenchmarkCandidate, ...]


def colean_smoke_tasks() -> list[BenchmarkTask]:
    tasks: list[BenchmarkTask] = []
    for index, task in enumerate(default_tasks(), start=1):
        candidates = tuple(
            BenchmarkCandidate(option_id, tuple(tactics), max(0.1, 1.0 - rank * 0.1))
            for rank, (option_id, tactics) in enumerate(task.options, start=1)
        )
        tasks.append(
            BenchmarkTask(
                task_id=f"colean_smoke_{index:03d}",
                source="colean_smoke_v0",
                lemma=task.lemma,
                theorem_header=task.theorem_header,
                informal_goal=task.informal_goal,
                imports=(
                    "Mathlib.Algebra.BigOperators.Group.Finset.Basic",
                    "Mathlib.Algebra.Order.BigOperators.Group.Finset",
                    "Mathlib.Combinatorics.Pigeonhole",
                    "Mathlib.Tactic",
                ),
                project_path=MATHLIB_PROJECT,
                candidates=candidates,
            )
        )
    return tasks


def load_json_tasks(path: Path) -> list[BenchmarkTask]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("tasks", data)
    if not isinstance(rows, list):
        raise ValueError("benchmark JSON must be a list or an object with a 'tasks' list")

    tasks: list[BenchmarkTask] = []
    for row in rows:
        project_path = Path(str(row.get("project_path", MATHLIB_PROJECT)))
        if not project_path.is_absolute():
            project_path = ROOT / project_path
        candidates = tuple(
            BenchmarkCandidate(
                option_id=str(candidate.get("option_id", candidate.get("id", index))),
                tactics=tuple(str(tactic) for tactic in candidate["tactics"]),
                weight=float(candidate.get("weight", max(0.1, 1.0 - index * 0.1))),
            )
            for index, candidate in enumerate(row["candidates"], start=1)
        )
        tasks.append(
            BenchmarkTask(
                task_id=str(row["task_id"]),
                source=str(row.get("source", path.name)),
                lemma=str(row["lemma"]),
                theorem_header=str(row["theorem_header"]),
                informal_goal=str(row.get("informal_goal", "")),
                imports=tuple(str(item) for item in row.get("imports", ["Mathlib"])),
                project_path=project_path,
                candidates=candidates,
            )
        )
    return tasks


def lean_version() -> str:
    proc = subprocess.run(
        ["lake", "env", "lean", "--version"],
        cwd=MATHLIB_PROJECT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    return proc.stdout.strip()


def imports_available(project_path: Path, imports: tuple[str, ...]) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ImportMathlib.lean"
        path.write_text(
            "\n".join([*(f"import {name}" for name in imports), "#check Nat", ""]),
            encoding="utf-8",
        )
        proc = subprocess.run(
            ["lake", "env", "lean", str(path)],
            cwd=project_path,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    return proc.returncode == 0


def prepare_project_cache(project_path: Path, imports: tuple[str, ...]) -> dict[str, Any]:
    if imports_available(project_path, imports):
        return {
            "project": str(project_path),
            "needed": False,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
        }

    started = time.perf_counter()
    proc = subprocess.run(
        ["lake", "exe", "cache", "get"],
        cwd=project_path,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=900,
    )
    return {
        "project": str(project_path),
        "needed": True,
        "returncode": proc.returncode,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "imports_available_after": imports_available(project_path, imports),
    }


def candidate_uses_forbidden_placeholder(candidate: BenchmarkCandidate) -> bool:
    forbidden = ("sorry", "admit")
    return any(any(word in tactic for word in forbidden) for tactic in candidate.tactics)


def check_benchmark_candidate(task: BenchmarkTask, candidate: BenchmarkCandidate) -> dict[str, Any]:
    if candidate_uses_forbidden_placeholder(candidate):
        return {
            "accepted_by_lean": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "candidate contains forbidden placeholder tactic: sorry/admit",
        }

    source = "\n".join(
        [
            *(f"import {name}" for name in task.imports),
            "",
            "set_option maxHeartbeats 0",
            "set_option linter.style.header false",
            "open scoped BigOperators",
            "open BigOperators Real Nat Topology Rat",
            "",
            task.theorem_header,
            *[f"  {tactic}" for tactic in candidate.tactics],
            "",
        ]
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "Candidate.lean"
        path.write_text(source, encoding="utf-8")
        proc = subprocess.run(
            ["lake", "env", "lean", str(path)],
            cwd=task.project_path,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
    output = f"{proc.stdout}\n{proc.stderr}"
    accepted = proc.returncode == 0 and "declaration uses 'sorry'" not in output
    return {
        "accepted_by_lean": accepted,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def verify_task(task: BenchmarkTask) -> dict[str, Any]:
    ranked = sorted(task.candidates, key=lambda candidate: candidate.weight, reverse=True)
    checked = []
    first_accept_rank: int | None = None
    started = time.perf_counter()

    for rank, candidate in enumerate(ranked, start=1):
        candidate_start = time.perf_counter()
        result = check_benchmark_candidate(task, candidate)
        elapsed = round(time.perf_counter() - candidate_start, 4)
        accepted = bool(result["accepted_by_lean"])
        if accepted and first_accept_rank is None:
            first_accept_rank = rank
        checked.append(
            {
                "rank": rank,
                "option_id": candidate.option_id,
                "weight": candidate.weight,
                "accepted": accepted,
                "elapsed_seconds": elapsed,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            }
        )

    return {
        "task_id": task.task_id,
        "source": task.source,
        "lemma": task.lemma,
        "candidate_count": len(ranked),
        "accepted": first_accept_rank is not None,
        "first_accepted_rank": first_accept_rank,
        "time_to_first_verified_seconds": time_to_first_verified(checked),
        "elapsed_seconds": round(time.perf_counter() - started, 4),
        "checked": checked,
    }


def time_to_first_verified(checked: list[dict[str, Any]]) -> float | None:
    total = 0.0
    for row in checked:
        total += float(row["elapsed_seconds"])
        if row["accepted"]:
            return round(total, 4)
    return None


def topk(rows: list[dict[str, Any]], ks: tuple[int, ...] = (1, 2, 3, 5)) -> dict[str, Any]:
    total = len(rows)
    summary: dict[str, Any] = {}
    for k in ks:
        hits = sum(
            1
            for row in rows
            if row["first_accepted_rank"] is not None and int(row["first_accepted_rank"]) <= k
        )
        summary[f"top_{k}"] = {
            "hits": hits,
            "total": total,
            "rate": round(hits / total, 4) if total else 0.0,
        }
    return summary


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# CoLean Benchmark Harness Report",
        "",
        f"Suite: `{summary['suite']}`",
        f"Lean: `{summary['lean_version']}`",
        f"Tasks: `{summary['task_count']}`",
        f"Accepted: `{summary['accepted']}`",
        f"Rejected: `{summary['rejected']}`",
        "",
        "Top-k:",
        "",
        "```json",
        json.dumps(summary["topk"], ensure_ascii=False, indent=2),
        "```",
        "",
        "| task | lemma | accepted | first accepted rank | time to first verified |",
        "|---|---|---:|---:|---:|",
    ]
    for row in summary["results"]:
        lines.append(
            f"| {row['task_id']} | {row['lemma']} | {row['accepted']} | "
            f"{row['first_accepted_rank']} | {row['time_to_first_verified_seconds']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CoLean benchmark-style verification metrics.")
    parser.add_argument("--suite", default="colean_smoke_v0", help="Suite name for output files.")
    parser.add_argument("--tasks-json", type=Path, help="Optional external benchmark task JSON.")
    args = parser.parse_args()

    tasks = load_json_tasks(args.tasks_json) if args.tasks_json else colean_smoke_tasks()
    cache = [
        prepare_project_cache(project, imports)
        for project, imports in sorted(
            {(task.project_path, task.imports) for task in tasks},
            key=lambda item: str(item[0]),
        )
    ]
    results = [verify_task(task) for task in tasks]
    summary = {
        "experiment": "CoLean benchmark harness",
        "suite": args.suite,
        "project": str(MATHLIB_PROJECT),
        "lean_version": lean_version(),
        "mathlib_cache": cache,
        "task_count": len(results),
        "accepted": sum(1 for row in results if row["accepted"]),
        "rejected": sum(1 for row in results if not row["accepted"]),
        "topk": topk(results),
        "results": results,
    }

    out_dir = OUT / "benchmarks"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{args.suite}.json"
    md_path = out_dir / f"{args.suite}.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
