from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from local_llm_generator import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    default_tasks,
    extract_json_object,
    normalize_ranked_options,
    ollama_available,
    ollama_request,
    prompt_for_constrained_task,
    start_ollama_server,
)
from paths import OUT


def rank_task(task: Any, *, model: str) -> dict[str, Any]:
    started = time.perf_counter()
    valid_ids = {option_id for option_id, _ in task.options}
    raw_response = ollama_request(prompt_for_constrained_task(task), model=model)
    elapsed = round(time.perf_counter() - started, 3)
    try:
        model_ranked_ids = normalize_ranked_options(extract_json_object(raw_response), valid_ids)
        ranked_ids = model_ranked_ids + tuple(
            option_id for option_id, _ in task.options if option_id not in model_ranked_ids
        )
        parse_error = ""
    except Exception as exc:
        model_ranked_ids = ()
        ranked_ids = tuple(option_id for option_id, _ in task.options)
        parse_error = str(exc)

    return {
        "lemma": task.lemma,
        "model_ranked_option_ids": list(model_ranked_ids),
        "missing_option_ids_appended_by_colean": [
            option_id for option_id in ranked_ids if option_id not in model_ranked_ids
        ],
        "ranked_option_ids": list(ranked_ids),
        "elapsed_seconds": elapsed,
        "parse_error": parse_error,
        "raw_response": raw_response,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# CoLean Ollama Ranking Export",
        "",
        f"Host: `{summary['host']}`",
        f"Model: `{summary['model']}`",
        f"Tasks: `{summary['task_count']}`",
        "",
        "| lemma | ranking | appended | parse error |",
        "|---|---|---|---|",
    ]
    for row in summary["rankings"]:
        ranking = ", ".join(row["ranked_option_ids"])
        appended = ", ".join(row["missing_option_ids_appended_by_colean"]) or "-"
        parse_error = str(row["parse_error"]).replace("|", "\\|") or "-"
        lines.append(f"| {row['lemma']} | `{ranking}` | {appended} | {parse_error} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export local Ollama rankings for CoLean proof-chain options.")
    parser.add_argument("--model", default=OLLAMA_MODEL)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()

    OUT.mkdir(exist_ok=True)
    server_proc = start_ollama_server()
    server_started = server_proc is not None
    if not ollama_available():
        raise SystemExit(f"Ollama server is not reachable at {OLLAMA_HOST}")

    rankings = [rank_task(task, model=args.model) for task in default_tasks()]
    summary = {
        "experiment": "Local Ollama proof-chain ranking export",
        "host": OLLAMA_HOST,
        "model": args.model,
        "server_started_by_script": server_started,
        "task_count": len(rankings),
        "rankings": rankings,
    }

    json_path = args.output_json or OUT / f"colean_ollama_rankings_{args.model.replace(':', '').replace('.', '')}.json"
    md_path = args.output_md or json_path.with_suffix(".md")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
