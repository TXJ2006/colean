from __future__ import annotations

import json
from dataclasses import dataclass

from incremental_proof_chain_verifier import candidates, check_candidate
from paths import OUT


@dataclass(frozen=True)
class EdgeUpdate:
    edge: str
    reason: str
    delta: float


def step_edge(lemma: str, step: int, line: str) -> str:
    return f"{lemma}::step{step}::{line}"


def collect_updates(result: dict[str, object]) -> list[EdgeUpdate]:
    lemma = str(result["lemma"])
    accepted = bool(result["accepted_by_mathlib_lean"])
    updates: list[EdgeUpdate] = []
    for step_result in result["step_results"]:
        step = int(step_result["step"])
        status = str(step_result["status"])
        lines = [str(line) for line in step_result["lines"]]
        for line in lines:
            edge = step_edge(lemma, step, line)
            if accepted and status in {"valid_incomplete", "complete"}:
                updates.append(EdgeUpdate(edge, "accepted proof path", +0.12))
            elif not accepted and status == "failed":
                updates.append(EdgeUpdate(edge, "first failing proof step", -0.10))
            elif not accepted and status == "valid_incomplete":
                updates.append(EdgeUpdate(edge, "valid prefix before later failure", +0.03))
    return updates


def run_learning_round() -> dict[str, object]:
    checked = [check_candidate(candidate) for candidate in candidates()]
    before = {
        str(result["source_path"]): float(result["old_weight"])
        for result in checked
    }
    all_updates: list[EdgeUpdate] = []
    after = dict(before)
    for result in checked:
        source_path = str(result["source_path"])
        accepted = bool(result["accepted_by_mathlib_lean"])
        first_failure = result["first_failure_step"]
        path_delta = 0.0
        if accepted:
            path_delta += 0.15
        else:
            path_delta -= 0.08
            if first_failure is not None and int(first_failure) > 1:
                path_delta += 0.03
        after[source_path] = round(max(0.0, before[source_path] + path_delta), 4)
        all_updates.extend(collect_updates(result))

    return {
        "experiment": "incremental verifier feedback learning round",
        "scripts_checked": len(checked),
        "accepted": sum(1 for row in checked if row["accepted_by_mathlib_lean"]),
        "rejected": sum(1 for row in checked if not row["accepted_by_mathlib_lean"]),
        "ranking_before": sorted(before.items(), key=lambda item: item[1], reverse=True),
        "ranking_after": sorted(after.items(), key=lambda item: item[1], reverse=True),
        "edge_updates": [
            {"edge": update.edge, "reason": update.reason, "delta": update.delta}
            for update in all_updates
        ],
    }


def main() -> None:
    OUT.mkdir(exist_ok=True)
    summary = run_learning_round()
    json_path = OUT / "colean_feedback_learning_results.json"
    md_path = OUT / "colean_feedback_learning_report.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json_path)
    print(md_path)


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# CoLean Feedback Learning Report",
        "",
        f"Scripts checked: `{summary['scripts_checked']}`",
        f"Accepted: `{summary['accepted']}`",
        f"Rejected: `{summary['rejected']}`",
        "",
        "## Ranking Before",
        "",
        "| path | weight |",
        "|---|---:|",
    ]
    for path, weight in summary["ranking_before"]:
        lines.append(f"| {path} | {weight} |")
    lines.extend(["", "## Ranking After", "", "| path | weight |", "|---|---:|"])
    for path, weight in summary["ranking_after"]:
        lines.append(f"| {path} | {weight} |")
    lines.extend(["", "## Edge Updates", "", "| edge | reason | delta |", "|---|---|---:|"])
    for row in summary["edge_updates"]:
        lines.append(f"| `{row['edge']}` | {row['reason']} | {row['delta']} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
