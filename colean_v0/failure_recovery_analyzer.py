from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from correspondence import Correspondence, Event, top_events
from paths import OUT


@dataclass(frozen=True)
class FailureClass:
    name: str
    repair: str
    confidence: float


def classify_tactics(tactics: list[str]) -> list[FailureClass]:
    text = "\n".join(tactics).lower()
    classes: list[FailureClass] = []
    if "first tactic" in text or "second tactic" in text:
        classes.append(
            FailureClass(
                "placeholder_output",
                "force candidate IDs only; reject placeholder tactic text",
                0.95,
            )
        )
    if any(token in text for token in ["rewrite", "finset.", "sum_pos_iff", "exists_le_sum"]):
        classes.append(
            FailureClass(
                "near_mathlib_declaration",
                "map informal tactic phrase to exact Mathlib declaration candidate",
                0.82,
            )
        )
    if "omega" in text or "hside" in text:
        classes.append(
            FailureClass(
                "missing_intermediate_state",
                "insert intermediate proof-state event before branch/destruct",
                0.78,
            )
        )
    if "exists" in text or "witness" in text or "bucket" in text:
        classes.append(
            FailureClass(
                "witness_shape_incomplete",
                "rank proof-chain candidates that explicitly build the witness tuple",
                0.74,
            )
        )
    if not classes:
        classes.append(
            FailureClass(
                "unclassified_failure",
                "preserve full candidate fiber and defer to Lean-verified top-k search",
                0.55,
            )
        )
    return classes


def load_result(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_failure_to_repair_correspondence(rows: list[dict[str, Any]]) -> Correspondence[str, str]:
    events: list[Event[str, str]] = []
    for row in rows:
        if row["accepted_by_mathlib_lean"]:
            continue
        source = f"{row['lemma']}::free_generation_failure"
        for cls in classify_tactics([str(tactic) for tactic in row["tactics"]]):
            events.append(
                Event(
                    source,
                    cls.repair,
                    cls.confidence,
                    cls.name,
                )
            )
    return Correspondence("failed LLM output", "repair action", events)


def build_repair_to_recovery_correspondence(rows: list[dict[str, Any]]) -> Correspondence[str, str]:
    events: list[Event[str, str]] = []
    for row in rows:
        accepted = bool(row["accepted_by_mathlib_lean"])
        rank = row["first_accepted_rank"]
        ranked = ", ".join(str(item) for item in row["ranked_option_ids"])
        appended = ", ".join(str(item) for item in row["missing_option_ids_appended_by_colean"])
        recovery = "Lean-accepted top-k proof" if accepted else "no accepted proof in checked fiber"
        base_weight = 1.0 if accepted else 0.2
        if rank is not None:
            base_weight = max(0.25, 1.05 - 0.12 * int(rank))
        label = f"ranked=[{ranked}]"
        if appended:
            label += f"; CoLean appended missing=[{appended}]"
        events.append(
            Event(
                f"{row['lemma']}::structured_candidate_fiber",
                recovery,
                round(base_weight, 4),
                label,
            )
        )
    return Correspondence("repair action", "verified recovery", events)


def analyze_model(path: Path) -> dict[str, Any]:
    data = load_result(path)
    constrained = data["constrained_experiment"]
    free_rows = data["results"]
    constrained_rows = constrained["results"]
    failure_to_repair = build_failure_to_repair_correspondence(free_rows)
    repair_to_recovery = build_repair_to_recovery_correspondence(constrained_rows)
    failure_classes = Counter(event.label for event in failure_to_repair.events)
    missing_appends = {
        row["lemma"]: row["missing_option_ids_appended_by_colean"]
        for row in constrained_rows
        if row["missing_option_ids_appended_by_colean"]
    }
    return {
        "model": data["model"],
        "free_generation": {
            "checked": data["candidates_checked"],
            "accepted": data["accepted"],
            "rejected": data["rejected"],
        },
        "constrained_ranking": {
            "checked": constrained["candidates_checked"],
            "accepted": constrained["accepted"],
            "rejected": constrained["rejected"],
            "topk_summary": constrained["topk_summary"],
        },
        "failure_class_counts": dict(sorted(failure_classes.items())),
        "missing_options_appended_by_colean": missing_appends,
        "failure_to_repair_edges": [asdict(event) for event in top_events(failure_to_repair, 12)],
        "repair_to_recovery_edges": [asdict(event) for event in top_events(repair_to_recovery, 12)],
    }


def main() -> None:
    OUT.mkdir(exist_ok=True)
    paths = [
        OUT / "colean_local_llm_results_qwen25coder15b.json",
        OUT / "colean_local_llm_results_qwen25coder7b.json",
        OUT / "colean_local_llm_results.json",
    ]
    existing = []
    seen_models = set()
    for path in paths:
        if not path.exists():
            continue
        model = load_result(path).get("model")
        if model in seen_models:
            continue
        seen_models.add(model)
        existing.append(path)
    analyses = [analyze_model(path) for path in existing]
    summary = {
        "experiment": "CoLean failure recovery event analysis",
        "claim": "LLM failures become structured correspondence events instead of discarded attempts.",
        "models": analyses,
    }
    json_path = OUT / "colean_failure_recovery_results.json"
    md_path = OUT / "colean_failure_recovery_report.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json_path)
    print(md_path)


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# CoLean Failure Recovery Report",
        "",
        str(summary["claim"]),
        "",
        "| model | free accepted | CoLean accepted | top-1 | top-3 | appended missing options |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for model in summary["models"]:
        free = model["free_generation"]
        constrained = model["constrained_ranking"]
        topk = constrained["topk_summary"]
        appended = "; ".join(
            f"{lemma}: {','.join(options)}"
            for lemma, options in model["missing_options_appended_by_colean"].items()
        )
        lines.append(
            f"| {model['model']} | {free['accepted']}/{free['checked']} | "
            f"{constrained['accepted']}/{constrained['checked']} | "
            f"{topk['top_1']['hits']}/{topk['top_1']['total']} | "
            f"{topk['top_3']['hits']}/{topk['top_3']['total']} | "
            f"{appended or '-'} |"
        )
    for model in summary["models"]:
        lines.extend(
            [
                "",
                f"## {model['model']}",
                "",
                "Failure classes:",
                "",
                "```json",
                json.dumps(model["failure_class_counts"], ensure_ascii=False, indent=2),
                "```",
                "",
                "Top failure -> repair edges:",
                "",
                "| failed output | repair action | weight | class |",
                "|---|---|---:|---|",
            ]
        )
        for edge in model["failure_to_repair_edges"][:8]:
            lines.append(
                f"| `{edge['source']}` | {edge['target']} | {edge['weight']} | {edge['label']} |"
            )
        lines.extend(
            [
                "",
                "Repair -> recovery edges:",
                "",
                "| candidate fiber | recovery | weight | evidence |",
                "|---|---|---:|---|",
            ]
        )
        for edge in model["repair_to_recovery_edges"][:8]:
            safe_label = str(edge["label"]).replace("|", "\\|")
            lines.append(
                f"| `{edge['source']}` | {edge['target']} | {edge['weight']} | {safe_label} |"
            )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
