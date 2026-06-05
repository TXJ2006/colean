from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from local_llm_generator import default_tasks, topk_summary
from paths import OUT
from proof_chain_verifier import ProofScriptCandidate, check_candidate


def verify_ranking_file(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = {task.lemma: task for task in default_tasks()}
    results: list[dict[str, Any]] = []

    for row in data["rankings"]:
        lemma = str(row["lemma"])
        task = tasks[lemma]
        option_map = dict(task.options)
        ranked_ids = [str(option_id) for option_id in row["ranked_option_ids"]]
        checked = []
        first_accept_rank: int | None = None
        for rank, option_id in enumerate(ranked_ids, start=1):
            candidate = ProofScriptCandidate(
                lemma=lemma,
                theorem_header=task.theorem_header,
                tactics=tuple(option_map[option_id]),
                weight=max(0.10, 1.0 - rank * 0.1),
                source_path=f"{data['model']} ranked option {option_id}",
            )
            verification = check_candidate(candidate)
            accepted = bool(verification["accepted_by_mathlib_lean"])
            if accepted and first_accept_rank is None:
                first_accept_rank = rank
            checked.append(
                {
                    "rank": rank,
                    "option_id": option_id,
                    "accepted_by_mathlib_lean": accepted,
                    "returncode": verification["returncode"],
                    "stderr": verification["stderr"],
                }
            )
        results.append(
            {
                "lemma": lemma,
                "accepted_by_mathlib_lean": first_accept_rank is not None,
                "first_accepted_rank": first_accept_rank,
                "ranked_option_ids": ranked_ids,
                "checked_options": checked,
            }
        )

    return {
        "experiment": "Verify exported Ollama rankings with Lean/Mathlib",
        "ranking_file": str(path),
        "model": data["model"],
        "task_count": len(results),
        "accepted": sum(1 for row in results if row["accepted_by_mathlib_lean"]),
        "rejected": sum(1 for row in results if not row["accepted_by_mathlib_lean"]),
        "topk_summary": topk_summary(results),
        "results": results,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# CoLean Ollama Ranking Verification",
        "",
        f"Model: `{summary['model']}`",
        f"Tasks: `{summary['task_count']}`",
        f"Accepted: `{summary['accepted']}`",
        f"Rejected: `{summary['rejected']}`",
        "",
        "```json",
        json.dumps(summary["topk_summary"], ensure_ascii=False, indent=2),
        "```",
        "",
        "| lemma | accepted | first accepted rank | ranking |",
        "|---|---:|---:|---|",
    ]
    for row in summary["results"]:
        ranking = ", ".join(row["ranked_option_ids"])
        lines.append(
            f"| {row['lemma']} | {row['accepted_by_mathlib_lean']} | "
            f"{row['first_accepted_rank']} | `{ranking}` |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify exported Ollama ranking files with Lean/Mathlib.")
    parser.add_argument("ranking_json", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()

    OUT.mkdir(exist_ok=True)
    summary = verify_ranking_file(args.ranking_json)
    json_path = args.output_json or OUT / "colean_ollama_ranking_verification.json"
    md_path = args.output_md or json_path.with_suffix(".md")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json_path)
    print(md_path)
    if summary["accepted"] != summary["task_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
