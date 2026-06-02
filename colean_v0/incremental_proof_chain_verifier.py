from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from paths import MATHLIB_PROJECT, OUT


PROJECT = MATHLIB_PROJECT


@dataclass(frozen=True)
class IncrementalCandidate:
    lemma: str
    theorem_header: str
    steps: tuple[tuple[str, ...], ...]
    weight: float
    source_path: str


def imports() -> list[str]:
    return [
        "import Mathlib.Algebra.BigOperators.Group.Finset.Basic",
        "import Mathlib.Algebra.Order.BigOperators.Group.Finset",
        "import Mathlib.Combinatorics.Pigeonhole",
        "import Mathlib.Tactic",
        "",
        "set_option linter.style.header false",
        "open scoped BigOperators",
        "namespace ColeanIncrementalCandidate",
        "",
    ]


def render_source(header: str, lines: list[str], *, append_sorry: bool) -> str:
    proof_lines = [f"  {line}" for line in lines]
    if append_sorry:
        proof_lines.append("  sorry")
    return "\n".join(
        [
            *imports(),
            header,
            *proof_lines,
            "",
            "end ColeanIncrementalCandidate",
            "",
        ]
    )


def run_lean(source: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "Candidate.lean"
        path.write_text(source, encoding="utf-8")
        return subprocess.run(
            ["lake", "env", "lean", str(path)],
            cwd=PROJECT,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )


def check_prefix(header: str, lines: list[str], *, final: bool) -> dict[str, object]:
    exact_proc = run_lean(render_source(header, lines, append_sorry=False))
    if exact_proc.returncode == 0:
        return {
            "status": "complete",
            "returncode": 0,
            "stdout": exact_proc.stdout.strip(),
            "stderr": exact_proc.stderr.strip(),
        }
    if final:
        return {
            "status": "failed",
            "returncode": exact_proc.returncode,
            "stdout": exact_proc.stdout.strip(),
            "stderr": exact_proc.stderr.strip(),
        }

    sorry_proc = run_lean(render_source(header, lines, append_sorry=True))
    if sorry_proc.returncode == 0:
        return {
            "status": "valid_incomplete",
            "returncode": 0,
            "stdout": sorry_proc.stdout.strip(),
            "stderr": sorry_proc.stderr.strip(),
        }
    return {
        "status": "failed",
        "returncode": sorry_proc.returncode,
        "stdout": sorry_proc.stdout.strip(),
        "stderr": sorry_proc.stderr.strip(),
    }


def split_positive_header() -> str:
    return (
        "theorem split_positive_mass_bucket {α : Type} (s : Finset α) (p : α → Prop)\n"
        "    [DecidablePred p] (f : α → Nat)\n"
        "    (h : 0 < (∑ x ∈ s.filter p, f x) + (∑ x ∈ s.filter (fun x => ¬ p x), f x)) :\n"
        "    ∃ x ∈ s, 0 < f x := by"
    )


def finite_level_header() -> str:
    return (
        "theorem finite_level_positive_bucket {α β : Type} [DecidableEq β]\n"
        "    (s : Finset α) (levels : Finset β) (level : α → β) (f : α → Nat)\n"
        "    (hcover : ∀ x ∈ s, level x ∈ levels)\n"
        "    (h : 0 < ∑ x ∈ s, f x) :\n"
        "    ∃ b ∈ levels, 0 < ∑ x ∈ s.filter (fun x => level x = b), f x := by"
    )


def threshold_header() -> str:
    return (
        "theorem finite_level_threshold_bucket {α β : Type} [DecidableEq β]\n"
        "    (s : Finset α) (levels : Finset β) (level : α → β) (f : α → Nat)\n"
        "    (threshold : Nat)\n"
        "    (hcover : ∀ x ∈ s, level x ∈ levels)\n"
        "    (hnonempty : levels.Nonempty)\n"
        "    (hbig : levels.card • threshold ≤ ∑ x ∈ s, f x) :\n"
        "    ∃ b ∈ levels, threshold ≤ ∑ x ∈ s.filter (fun x => level x = b), f x := by"
    )


def candidates() -> list[IncrementalCandidate]:
    return [
        IncrementalCandidate(
            "split positive mass bucket",
            split_positive_header(),
            (
                ("rw [Finset.sum_filter_add_sum_filter_not] at h",),
                ("exact (Finset.sum_pos_iff).mp h",),
            ),
            0.91,
            "rewrite hypothesis -> positive mass declaration",
        ),
        IncrementalCandidate(
            "split positive mass bucket",
            split_positive_header(),
            (("exact (Finset.sum_pos_iff).mp h",),),
            0.46,
            "missing rewrite",
        ),
        IncrementalCandidate(
            "finite level positive bucket",
            finite_level_header(),
            (
                ("rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩",),
                ("refine ⟨level x, hcover x hxs, ?_⟩",),
                ("exact (Finset.sum_pos_iff).mpr ⟨x, by simp [hxs], hfx⟩",),
            ),
            0.86,
            "positive point -> level witness -> positive bucket sum",
        ),
        IncrementalCandidate(
            "finite level positive bucket",
            finite_level_header(),
            (
                ("rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩",),
                ("exact ⟨level x, hcover x hxs, hfx⟩",),
            ),
            0.33,
            "forgets bucket sum proof",
        ),
        IncrementalCandidate(
            "finite level threshold bucket",
            threshold_header(),
            (("exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty hbig",),),
            0.90,
            "direct weighted pigeonhole declaration",
        ),
        IncrementalCandidate(
            "finite level threshold bucket",
            threshold_header(),
            (("exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty",),),
            0.32,
            "missing threshold inequality",
        ),
    ]


def check_candidate(candidate: IncrementalCandidate) -> dict[str, object]:
    prefix: list[str] = []
    step_results: list[dict[str, object]] = []
    for idx, step in enumerate(candidate.steps, start=1):
        prefix.extend(step)
        result = check_prefix(candidate.theorem_header, prefix, final=idx == len(candidate.steps))
        step_results.append(
            {
                "step": idx,
                "lines": list(step),
                **result,
            }
        )
        if result["status"] == "failed":
            break
        if result["status"] == "complete":
            break
    accepted = bool(step_results and step_results[-1]["status"] == "complete")
    return {
        "lemma": candidate.lemma,
        "source_path": candidate.source_path,
        "old_weight": candidate.weight,
        "accepted_by_mathlib_lean": accepted,
        "new_weight": round(candidate.weight + (0.12 if accepted else -0.07), 4),
        "first_failure_step": next((row["step"] for row in step_results if row["status"] == "failed"), None),
        "step_results": step_results,
    }


def main() -> None:
    OUT.mkdir(exist_ok=True)
    results = [check_candidate(candidate) for candidate in candidates()]
    summary = {
        "experiment": "Mathlib-backed incremental proof-chain verification",
        "project": str(PROJECT),
        "scripts_checked": len(results),
        "accepted": sum(1 for row in results if row["accepted_by_mathlib_lean"]),
        "rejected": sum(1 for row in results if not row["accepted_by_mathlib_lean"]),
        "results": results,
    }
    json_path = OUT / "colean_incremental_verifier_results.json"
    md_path = OUT / "colean_incremental_verifier_report.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json_path)
    print(md_path)


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# CoLean Incremental Proof-Chain Verifier Report",
        "",
        f"Scripts checked: `{summary['scripts_checked']}`",
        f"Accepted: `{summary['accepted']}`",
        f"Rejected: `{summary['rejected']}`",
        "",
        "| lemma | source path | accepted | first failure step |",
        "|---|---|---:|---:|",
    ]
    for row in summary["results"]:
        lines.append(
            f"| {row['lemma']} | {row['source_path']} | {row['accepted_by_mathlib_lean']} | "
            f"{row['first_failure_step']} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
