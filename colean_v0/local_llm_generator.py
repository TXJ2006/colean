from __future__ import annotations

import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from paths import OUT
from proof_chain_verifier import (
    ProofScriptCandidate,
    binary_level_theorem_header,
    check_candidate,
    finite_level_theorem_header,
    finite_level_threshold_theorem_header,
    split_positive_theorem_header,
)


OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
if not OLLAMA_HOST.startswith(("http://", "https://")):
    OLLAMA_HOST = f"http://{OLLAMA_HOST}"
if re.match(r"^https?://[^/:]+$", OLLAMA_HOST):
    OLLAMA_HOST = f"{OLLAMA_HOST}:11434"
OLLAMA_MODEL = os.environ.get("COLEAN_LOCAL_MODEL", "qwen2.5-coder:1.5b")


@dataclass(frozen=True)
class LocalLLMTask:
    lemma: str
    theorem_header: str
    informal_goal: str
    hints: tuple[str, ...]
    options: tuple[tuple[str, tuple[str, ...]], ...]


def default_tasks() -> list[LocalLLMTask]:
    return [
        LocalLLMTask(
            lemma="split positive mass bucket",
            theorem_header=split_positive_theorem_header(),
            informal_goal=(
                "A positive sum over a predicate split implies some element in the original "
                "finite set has positive mass."
            ),
            hints=(
                "Useful declaration: Finset.sum_filter_add_sum_filter_not",
                "Useful declaration: Finset.sum_pos_iff",
                "A good proof first rewrites h by the filter split identity.",
            ),
            options=(
                (
                    "A",
                    (
                        "rw [Finset.sum_filter_add_sum_filter_not] at h",
                        "exact (Finset.sum_pos_iff).mp h",
                    ),
                ),
                ("B", ("exact (Finset.sum_pos_iff).mp h",)),
                (
                    "C",
                    (
                        "exact (Finset.sum_pos_iff).mp h",
                        "rw [Finset.sum_filter_add_sum_filter_not] at h",
                    ),
                ),
            ),
        ),
        LocalLLMTask(
            lemma="binary level positive bucket",
            theorem_header=binary_level_theorem_header(),
            informal_goal=(
                "A positive sum split into two predicate buckets implies either the predicate "
                "bucket or the complement bucket contains a positive-mass point."
            ),
            hints=(
                "Use omega to turn positivity of a Nat sum into a positive side.",
                "Then branch with rcases hside with hp | hnp.",
                "Use Finset.sum_pos_iff on the positive side.",
            ),
            options=(
                (
                    "A",
                    (
                        "have hside : 0 < (∑ x ∈ s.filter p, f x) ∨ 0 < (∑ x ∈ s.filter (fun x => ¬ p x), f x) := by",
                        "  omega",
                        "rcases hside with hp | hnp",
                        "· left",
                        "  exact (Finset.sum_pos_iff).mp hp",
                        "· right",
                        "  exact (Finset.sum_pos_iff).mp hnp",
                    ),
                ),
                (
                    "B",
                    (
                        "left",
                        "exact (Finset.sum_pos_iff).mp h",
                    ),
                ),
                (
                    "C",
                    (
                        "have hside : 0 < (∑ x ∈ s.filter p, f x) ∨ 0 < (∑ x ∈ s.filter (fun x => ¬ p x), f x) := by",
                        "  omega",
                        "exact hside",
                    ),
                ),
            ),
        ),
        LocalLLMTask(
            lemma="finite level positive bucket",
            theorem_header=finite_level_theorem_header(),
            informal_goal=(
                "If total mass on a finite source set is positive and every source point maps "
                "to one of finitely many levels, then some level bucket has positive total mass."
            ),
            hints=(
                "First extract a positive-mass point using Finset.sum_pos_iff.",
                "Use level x as the witness bucket.",
                "Use hcover x hxs to prove the witness level is in levels.",
                "Use Finset.sum_pos_iff.mpr to prove the bucket sum is positive.",
            ),
            options=(
                (
                    "A",
                    (
                        "rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩",
                        "refine ⟨level x, hcover x hxs, ?_⟩",
                        "exact (Finset.sum_pos_iff).mpr ⟨x, by simp [hxs], hfx⟩",
                    ),
                ),
                (
                    "B",
                    (
                        "rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩",
                        "exact ⟨level x, hcover x hxs, hfx⟩",
                    ),
                ),
                (
                    "C",
                    (
                        "rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩",
                        "refine ⟨level x, ?_, ?_⟩",
                        "exact hxs",
                        "exact (Finset.sum_pos_iff).mpr ⟨x, by simp [hxs], hfx⟩",
                    ),
                ),
            ),
        ),
        LocalLLMTask(
            lemma="finite level threshold bucket",
            theorem_header=finite_level_threshold_theorem_header(),
            informal_goal=(
                "A finite weighted pigeonhole theorem: if total mass is at least "
                "levels.card * threshold, then one level has mass at least threshold."
            ),
            hints=(
                "Useful declaration: Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum",
                "Arguments available in context: hcover hnonempty hbig",
            ),
            options=(
                (
                    "A",
                    (
                        "exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty hbig",
                    ),
                ),
                (
                    "B",
                    (
                        "exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty",
                    ),
                ),
                (
                    "C",
                    (
                        "apply Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum",
                        "case h => exact hcover",
                    ),
                ),
            ),
        ),
    ]


def ollama_request(prompt: str, model: str = OLLAMA_MODEL, timeout: int = 180) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 450,
        },
    }
    request = urllib.request.Request(
        f"{OLLAMA_HOST}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data.get("response", ""))


def extract_json_object(text: str) -> dict[str, Any]:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end >= start:
            text = text[start : end + 1]
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("model response JSON must be an object")
    return data


def normalize_tactics(data: dict[str, Any]) -> tuple[str, ...]:
    tactics = data.get("tactics", [])
    if isinstance(tactics, str):
        tactics = [line.strip() for line in tactics.splitlines() if line.strip()]
    if not isinstance(tactics, list):
        raise ValueError("tactics must be a list")
    normalized = tuple(str(tactic).rstrip() for tactic in tactics if str(tactic).strip())
    if not normalized:
        raise ValueError("empty tactic list")
    return normalized


def prompt_for_task(task: LocalLLMTask) -> str:
    hints = "\n".join(f"- {hint}" for hint in task.hints)
    return f"""You generate Lean 4 / Mathlib proof tactics only.

Return exactly one JSON object:
{{"tactics": ["first tactic", "second tactic"]}}

Do not include the theorem header, imports, explanations, markdown, or comments.

Informal goal:
{task.informal_goal}

Lean theorem header:
{task.theorem_header}

Hints:
{hints}
"""


def prompt_for_constrained_task(task: LocalLLMTask) -> str:
    hints = "\n".join(f"- {hint}" for hint in task.hints)
    options = []
    for option_id, tactics in task.options:
        script = "\n".join(f"    {tactic}" for tactic in tactics)
        options.append(f"{option_id}:\n{script}")
    option_text = "\n\n".join(options)
    return f"""You rank Lean 4 / Mathlib proof-script candidates.

Return exactly one JSON object:
{{"ranked_option_ids": ["best id", "second id", "third id"]}}

Do not write tactics. Only rank the option IDs.
Include every option ID exactly once.

Informal goal:
{task.informal_goal}

Lean theorem header:
{task.theorem_header}

Hints:
{hints}

Candidate proof scripts:
{option_text}
"""


def generate_candidate(task: LocalLLMTask) -> dict[str, Any]:
    started = time.perf_counter()
    prompt = prompt_for_task(task)
    raw_response = ollama_request(prompt)
    elapsed = round(time.perf_counter() - started, 3)
    try:
        tactics = normalize_tactics(extract_json_object(raw_response))
        parse_error = ""
    except Exception as exc:
        tactics = ("fail",)
        parse_error = str(exc)

    candidate = ProofScriptCandidate(
        lemma=task.lemma,
        theorem_header=task.theorem_header,
        tactics=tactics,
        weight=0.50,
        source_path=f"local llm {OLLAMA_MODEL}",
    )
    verification = check_candidate(candidate)
    return {
        "lemma": task.lemma,
        "model": OLLAMA_MODEL,
        "elapsed_seconds": elapsed,
        "raw_response": raw_response,
        "parse_error": parse_error,
        "tactics": list(tactics),
        "accepted_by_mathlib_lean": verification["accepted_by_mathlib_lean"],
        "lean_stderr": verification["stderr"],
        "lean_stdout": verification["stdout"],
    }


def normalize_ranked_options(data: dict[str, Any], valid_ids: set[str]) -> tuple[str, ...]:
    ranked = data.get("ranked_option_ids", data.get("options", data.get("ids", [])))
    if isinstance(ranked, str):
        ranked = re.findall(r"[A-Z]", ranked)
    if not isinstance(ranked, list):
        raise ValueError("ranked_option_ids must be a list")
    output = []
    for item in ranked:
        option_id = str(item).strip().upper()
        if option_id in valid_ids and option_id not in output:
            output.append(option_id)
    if not output:
        raise ValueError("no valid option IDs in model response")
    return tuple(output)


def rank_and_verify_options(task: LocalLLMTask) -> dict[str, Any]:
    started = time.perf_counter()
    raw_response = ollama_request(prompt_for_constrained_task(task))
    elapsed = round(time.perf_counter() - started, 3)
    option_map = dict(task.options)
    try:
        model_ranked_ids = normalize_ranked_options(extract_json_object(raw_response), set(option_map))
        ranked_ids = model_ranked_ids + tuple(
            option_id for option_id, _ in task.options if option_id not in model_ranked_ids
        )
        parse_error = ""
    except Exception as exc:
        model_ranked_ids = ()
        ranked_ids = tuple(option_id for option_id, _ in task.options)
        parse_error = str(exc)

    checked = []
    for rank, option_id in enumerate(ranked_ids, start=1):
        tactics = option_map[option_id]
        candidate = ProofScriptCandidate(
            lemma=task.lemma,
            theorem_header=task.theorem_header,
            tactics=tactics,
            weight=max(0.10, 1.0 - rank * 0.1),
            source_path=f"local llm {OLLAMA_MODEL} ranked option {option_id}",
        )
        verification = check_candidate(candidate)
        checked.append(
            {
                "rank": rank,
                "option_id": option_id,
                "tactics": list(tactics),
                "accepted_by_mathlib_lean": verification["accepted_by_mathlib_lean"],
                "lean_stderr": verification["stderr"],
                "lean_stdout": verification["stdout"],
            }
        )
    first_accept = next((row for row in checked if row["accepted_by_mathlib_lean"]), None)
    return {
        "lemma": task.lemma,
        "model": OLLAMA_MODEL,
        "elapsed_seconds": elapsed,
        "raw_response": raw_response,
        "parse_error": parse_error,
        "model_ranked_option_ids": list(model_ranked_ids),
        "missing_option_ids_appended_by_colean": [
            option_id for option_id in ranked_ids if option_id not in model_ranked_ids
        ],
        "ranked_option_ids": list(ranked_ids),
        "accepted_by_mathlib_lean": first_accept is not None,
        "first_accepted_rank": None if first_accept is None else first_accept["rank"],
        "checked_options": checked,
    }


def topk_summary(rows: list[dict[str, Any]], ks: tuple[int, ...] = (1, 2, 3)) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    total = len(rows)
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


def ollama_available() -> bool:
    try:
        with urllib.request.urlopen(f"{OLLAMA_HOST}/api/tags", timeout=5) as response:
            response.read()
        return True
    except (urllib.error.URLError, TimeoutError):
        return False


def start_ollama_server() -> subprocess.Popen[str] | None:
    if ollama_available():
        return None
    exe = os.environ.get(
        "OLLAMA_EXE",
        str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"),
    )
    if not Path(exe).exists():
        return None
    proc = subprocess.Popen(
        [exe, "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    for _ in range(20):
        if ollama_available():
            return proc
        time.sleep(1)
    return proc


def main() -> None:
    OUT.mkdir(exist_ok=True)
    server_proc = start_ollama_server()
    server_started = server_proc is not None
    results: list[dict[str, Any]] = []
    error = ""
    if not ollama_available():
        error = f"Ollama server is not reachable at {OLLAMA_HOST}."
    else:
        for task in default_tasks():
            results.append(generate_candidate(task))
    constrained_results: list[dict[str, Any]] = []
    if not error:
        for task in default_tasks():
            constrained_results.append(rank_and_verify_options(task))

    summary = {
        "experiment": "Local Ollama LLM proof-candidate generation",
        "host": OLLAMA_HOST,
        "model": OLLAMA_MODEL,
        "server_started_by_script": server_started,
        "error": error,
        "candidates_checked": len(results),
        "accepted": sum(1 for row in results if row["accepted_by_mathlib_lean"]),
        "rejected": sum(1 for row in results if not row["accepted_by_mathlib_lean"]),
        "results": results,
        "constrained_experiment": {
            "mode": "local LLM ranks CoLean candidate proof chains; Lean verifies ranked options",
            "candidates_checked": len(constrained_results),
            "accepted": sum(1 for row in constrained_results if row["accepted_by_mathlib_lean"]),
            "rejected": sum(1 for row in constrained_results if not row["accepted_by_mathlib_lean"]),
            "topk_summary": topk_summary(constrained_results),
            "results": constrained_results,
        },
    }
    json_path = OUT / "colean_local_llm_results.json"
    md_path = OUT / "colean_local_llm_report.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json_path)
    print(md_path)


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# CoLean Local LLM Report",
        "",
        f"Host: `{summary['host']}`",
        f"Model: `{summary['model']}`",
        f"Candidates checked: `{summary['candidates_checked']}`",
        f"Accepted: `{summary['accepted']}`",
        f"Rejected: `{summary['rejected']}`",
    ]
    if summary["error"]:
        lines.extend(["", f"Error: `{summary['error']}`"])
    lines.extend(
        [
            "",
            "| lemma | accepted | elapsed seconds | tactics | parse error |",
            "|---|---:|---:|---|---|",
        ]
    )
    for row in summary["results"]:
        tactics = "<br>".join(f"`{tactic}`" for tactic in row["tactics"])
        parse_error = str(row["parse_error"]).replace("|", "\\|")
        lines.append(
            f"| {row['lemma']} | {row['accepted_by_mathlib_lean']} | "
            f"{row['elapsed_seconds']} | {tactics} | {parse_error} |"
        )
    constrained = summary["constrained_experiment"]
    lines.extend(
        [
            "",
            "## Constrained CoLean Ranking",
            "",
            f"Candidates checked: `{constrained['candidates_checked']}`",
            f"Accepted: `{constrained['accepted']}`",
            f"Rejected: `{constrained['rejected']}`",
            "",
            "Top-k summary:",
            "",
            "```json",
            json.dumps(constrained["topk_summary"], ensure_ascii=False, indent=2),
            "```",
            "",
            "| lemma | accepted | first accepted rank | model ranking |",
            "|---|---:|---:|---|",
        ]
    )
    for row in constrained["results"]:
        ranking = ", ".join(row["ranked_option_ids"])
        lines.append(
            f"| {row['lemma']} | {row['accepted_by_mathlib_lean']} | "
            f"{row['first_accepted_rank']} | `{ranking}` |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
