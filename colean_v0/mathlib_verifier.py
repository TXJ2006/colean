from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from paths import MATHLIB_PROJECT, OUT
from typing import Iterable


PROJECT = MATHLIB_PROJECT


@dataclass(frozen=True)
class MathlibCandidate:
    lemma: str
    theorem_header: str
    tactic: str
    weight: float


def check_candidate(candidate: MathlibCandidate) -> dict[str, object]:
    source = "\n".join(
        [
            "import Mathlib.Algebra.BigOperators.Group.Finset.Basic",
            "import Mathlib.Algebra.Order.BigOperators.Group.Finset",
            "",
            "set_option linter.style.header false",
            "open scoped BigOperators",
            "namespace ColeanMathlibCandidate",
            "",
            candidate.theorem_header,
            f"  {candidate.tactic}",
            "",
            "end ColeanMathlibCandidate",
            "",
        ]
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "Candidate.lean"
        path.write_text(source, encoding="utf-8")
        proc = subprocess.run(
            ["lake", "env", "lean", str(path)],
            cwd=PROJECT,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    accepted = proc.returncode == 0
    return {
        "lemma": candidate.lemma,
        "tactic": candidate.tactic,
        "old_weight": candidate.weight,
        "accepted_by_mathlib_lean": accepted,
        "new_weight": round(candidate.weight + (0.10 if accepted else -0.06), 4),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def default_candidates() -> list[MathlibCandidate]:
    theorem = (
        "theorem finite_sum_filter_split {α : Type} (s : Finset α) (p : α → Prop)\n"
        "    [DecidablePred p] (f : α → Nat) :\n"
        "    (∑ x ∈ s.filter p, f x) + (∑ x ∈ s.filter (fun x => ¬ p x), f x) = ∑ x ∈ s, f x := by"
    )
    incidence = (
        "theorem incidence_identity_toy {Point Tube : Type} (tubes : Finset Tube)\n"
        "    (pointsIn : Tube → Finset Point) :\n"
        "    (∑ t ∈ tubes, (pointsIn t).card) = ∑ t ∈ tubes, (pointsIn t).card := by"
    )
    return [
        MathlibCandidate(
            "finite sum filter split",
            theorem,
            "exact Finset.sum_filter_add_sum_filter_not s p f",
            0.93,
        ),
        MathlibCandidate(
            "finite sum filter split",
            theorem,
            "rfl",
            0.25,
        ),
        MathlibCandidate(
            "positive mass bucket",
            (
                "theorem positive_mass_bucket {α : Type} (s : Finset α) (f : α → Nat)\n"
                "    (h : 0 < ∑ x ∈ s, f x) : ∃ x ∈ s, 0 < f x := by"
            ),
            "exact (Finset.sum_pos_iff).mp h",
            0.90,
        ),
        MathlibCandidate(
            "positive mass bucket",
            (
                "theorem positive_mass_bucket {α : Type} (s : Finset α) (f : α → Nat)\n"
                "    (h : 0 < ∑ x ∈ s, f x) : ∃ x ∈ s, 0 < f x := by"
            ),
            "exact h",
            0.22,
        ),
        MathlibCandidate(
            "incidence identity toy",
            incidence,
            "rfl",
            0.88,
        ),
        MathlibCandidate(
            "incidence identity toy",
            incidence,
            "exact Finset.sum_filter_add_sum_filter_not tubes (fun _ => True) (fun t => (pointsIn t).card)",
            0.24,
        ),
    ]


def candidates() -> list[MathlibCandidate]:
    try:
        from candidate_generator import make_generator

        return make_generator().mathlib_candidates()
    except Exception:
        return default_candidates()


def summarize_results(results: Iterable[dict[str, object]]) -> dict[str, object]:
    rows = list(results)
    return {
        "candidates_checked": len(rows),
        "accepted": sum(1 for row in rows if row["accepted_by_mathlib_lean"]),
        "rejected": sum(1 for row in rows if not row["accepted_by_mathlib_lean"]),
        "top1_by_lemma": top1_by_lemma(rows),
    }


def top1_by_lemma(rows: list[dict[str, object]]) -> dict[str, object]:
    by_lemma: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_lemma.setdefault(str(row["lemma"]), []).append(row)
    top1 = {}
    for lemma, lemma_rows in by_lemma.items():
        ranked = sorted(lemma_rows, key=lambda row: float(row["old_weight"]), reverse=True)
        top = ranked[0]
        top1[lemma] = {
            "tactic": top["tactic"],
            "accepted": top["accepted_by_mathlib_lean"],
            "weight": top["old_weight"],
        }
    return top1


def main() -> None:
    OUT.mkdir(exist_ok=True)
    results = [check_candidate(candidate) for candidate in candidates()]
    result_summary = summarize_results(results)
    summary = {
        "experiment": "Mathlib-backed Lean candidate verification",
        "project": str(PROJECT),
        "lean_version": subprocess.run(
            ["lake", "env", "lean", "--version"],
            cwd=PROJECT,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        ).stdout.strip(),
        **result_summary,
        "results": results,
    }
    json_path = OUT / "colean_mathlib_verifier_results.json"
    md_path = OUT / "colean_mathlib_verifier_report.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json_path)
    print(md_path)


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# CoLean Mathlib-Backed Verifier Report",
        "",
        f"Lean: `{summary['lean_version']}`",
        "",
        f"Candidates checked: `{summary['candidates_checked']}`",
        f"Accepted: `{summary['accepted']}`",
        f"Rejected: `{summary['rejected']}`",
        "",
        "| lemma | tactic | accepted | weight update |",
        "|---|---:|---:|---:|",
    ]
    for row in summary["results"]:
        lines.append(
            f"| {row['lemma']} | `{row['tactic']}` | {row['accepted_by_mathlib_lean']} | "
            f"{row['old_weight']} -> {row['new_weight']} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
