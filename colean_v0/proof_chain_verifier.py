from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from paths import MATHLIB_PROJECT, OUT


PROJECT = MATHLIB_PROJECT


@dataclass(frozen=True)
class ProofScriptCandidate:
    lemma: str
    theorem_header: str
    tactics: tuple[str, ...]
    weight: float
    source_path: str

    @property
    def script(self) -> str:
        return "\n".join(f"  {tactic}" for tactic in self.tactics)


def split_positive_theorem_header() -> str:
    return (
        "theorem split_positive_mass_bucket {α : Type} (s : Finset α) (p : α → Prop)\n"
        "    [DecidablePred p] (f : α → Nat)\n"
        "    (h : 0 < (∑ x ∈ s.filter p, f x) + (∑ x ∈ s.filter (fun x => ¬ p x), f x)) :\n"
        "    ∃ x ∈ s, 0 < f x := by"
    )


def binary_level_theorem_header() -> str:
    return (
        "theorem binary_level_positive_bucket {α : Type} (s : Finset α) (p : α → Prop)\n"
        "    [DecidablePred p] (f : α → Nat)\n"
        "    (h : 0 < (∑ x ∈ s.filter p, f x) + (∑ x ∈ s.filter (fun x => ¬ p x), f x)) :\n"
        "    (∃ x ∈ s.filter p, 0 < f x) ∨ (∃ x ∈ s.filter (fun x => ¬ p x), 0 < f x) := by"
    )


def finite_level_theorem_header() -> str:
    return (
        "theorem finite_level_positive_bucket {α β : Type} [DecidableEq β]\n"
        "    (s : Finset α) (levels : Finset β) (level : α → β) (f : α → Nat)\n"
        "    (hcover : ∀ x ∈ s, level x ∈ levels)\n"
        "    (h : 0 < ∑ x ∈ s, f x) :\n"
        "    ∃ b ∈ levels, 0 < ∑ x ∈ s.filter (fun x => level x = b), f x := by"
    )


def finite_level_threshold_theorem_header() -> str:
    return (
        "theorem finite_level_threshold_bucket {α β : Type} [DecidableEq β]\n"
        "    (s : Finset α) (levels : Finset β) (level : α → β) (f : α → Nat)\n"
        "    (threshold : Nat)\n"
        "    (hcover : ∀ x ∈ s, level x ∈ levels)\n"
        "    (hnonempty : levels.Nonempty)\n"
        "    (hbig : levels.card • threshold ≤ ∑ x ∈ s, f x) :\n"
        "    ∃ b ∈ levels, threshold ≤ ∑ x ∈ s.filter (fun x => level x = b), f x := by"
    )


def candidates() -> list[ProofScriptCandidate]:
    header = split_positive_theorem_header()
    binary_header = binary_level_theorem_header()
    finite_header = finite_level_theorem_header()
    threshold_header = finite_level_threshold_theorem_header()
    return [
        ProofScriptCandidate(
            "split positive mass bucket",
            header,
            (
                "rw [Finset.sum_filter_add_sum_filter_not] at h",
                "exact (Finset.sum_pos_iff).mp h",
            ),
            0.91,
            "filter split declaration -> rewrite hypothesis -> positive mass declaration",
        ),
        ProofScriptCandidate(
            "split positive mass bucket",
            header,
            ("exact (Finset.sum_pos_iff).mp h",),
            0.46,
            "positive mass declaration without rewrite",
        ),
        ProofScriptCandidate(
            "split positive mass bucket",
            header,
            (
                "exact (Finset.sum_pos_iff).mp h",
                "rw [Finset.sum_filter_add_sum_filter_not] at h",
            ),
            0.31,
            "wrong tactic order",
        ),
        ProofScriptCandidate(
            "split positive mass bucket",
            header,
            ("rfl",),
            0.12,
            "definitionally-equal guess",
        ),
        ProofScriptCandidate(
            "binary level positive bucket",
            binary_header,
            (
                "have hside : 0 < (∑ x ∈ s.filter p, f x) ∨ 0 < (∑ x ∈ s.filter (fun x => ¬ p x), f x) := by",
                "  omega",
                "rcases hside with hp | hnp",
                "· left",
                "  exact (Finset.sum_pos_iff).mp hp",
                "· right",
                "  exact (Finset.sum_pos_iff).mp hnp",
            ),
            0.88,
            "positive add split -> branch on positive side -> sum_pos_iff",
        ),
        ProofScriptCandidate(
            "binary level positive bucket",
            binary_header,
            (
                "left",
                "exact (Finset.sum_pos_iff).mp h",
            ),
            0.34,
            "incorrectly assumes left side positive",
        ),
        ProofScriptCandidate(
            "binary level positive bucket",
            binary_header,
            (
                "have hside : 0 < (∑ x ∈ s.filter p, f x) ∨ 0 < (∑ x ∈ s.filter (fun x => ¬ p x), f x) := by",
                "  omega",
                "exact hside",
            ),
            0.28,
            "forgets to convert positive side sum to witness",
        ),
        ProofScriptCandidate(
            "finite level positive bucket",
            finite_header,
            (
                "rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩",
                "refine ⟨level x, hcover x hxs, ?_⟩",
                "exact (Finset.sum_pos_iff).mpr ⟨x, by simp [hxs], hfx⟩",
            ),
            0.86,
            "positive point -> level bucket -> positive bucket sum",
        ),
        ProofScriptCandidate(
            "finite level positive bucket",
            finite_header,
            (
                "rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩",
                "exact ⟨level x, hcover x hxs, hfx⟩",
            ),
            0.33,
            "forgets to prove bucket sum positive",
        ),
        ProofScriptCandidate(
            "finite level positive bucket",
            finite_header,
            (
                "rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩",
                "refine ⟨level x, ?_, ?_⟩",
                "exact hxs",
                "exact (Finset.sum_pos_iff).mpr ⟨x, by simp [hxs], hfx⟩",
            ),
            0.25,
            "uses source membership instead of level cover",
        ),
        ProofScriptCandidate(
            "finite level threshold bucket",
            threshold_header,
            (
                "exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty hbig",
            ),
            0.90,
            "Mathlib weighted pigeonhole declaration",
        ),
        ProofScriptCandidate(
            "finite level threshold bucket",
            threshold_header,
            (
                "exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty",
            ),
            0.32,
            "forgets threshold inequality argument",
        ),
        ProofScriptCandidate(
            "finite level threshold bucket",
            threshold_header,
            (
                "rcases (Finset.sum_pos_iff).mp (Nat.lt_of_lt_of_le (Nat.succ_pos 0) hbig) with ⟨x, hxs, hfx⟩",
                "refine ⟨level x, hcover x hxs, ?_⟩",
                "exact Nat.le_of_lt hfx",
            ),
            0.20,
            "wrongly tries positive-mass proof for threshold bound",
        ),
    ]


def check_candidate(candidate: ProofScriptCandidate) -> dict[str, object]:
    source = "\n".join(
        [
            "import Mathlib.Algebra.BigOperators.Group.Finset.Basic",
            "import Mathlib.Algebra.Order.BigOperators.Group.Finset",
            "import Mathlib.Combinatorics.Pigeonhole",
            "import Mathlib.Tactic",
            "",
            "set_option linter.style.header false",
            "open scoped BigOperators",
            "namespace ColeanProofChainCandidate",
            "",
            candidate.theorem_header,
            candidate.script,
            "",
            "end ColeanProofChainCandidate",
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
        "tactics": list(candidate.tactics),
        "source_path": candidate.source_path,
        "old_weight": candidate.weight,
        "accepted_by_mathlib_lean": accepted,
        "new_weight": round(candidate.weight + (0.12 if accepted else -0.07), 4),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def main() -> None:
    OUT.mkdir(exist_ok=True)
    results = [check_candidate(candidate) for candidate in candidates()]
    summary = {
        "experiment": "Mathlib-backed multi-step proof-chain verification",
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
        "scripts_checked": len(results),
        "accepted": sum(1 for row in results if row["accepted_by_mathlib_lean"]),
        "rejected": sum(1 for row in results if not row["accepted_by_mathlib_lean"]),
        "results": results,
    }
    json_path = OUT / "colean_proof_chain_verifier_results.json"
    md_path = OUT / "colean_proof_chain_verifier_report.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json_path)
    print(md_path)


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# CoLean Multi-Step Proof-Chain Verifier Report",
        "",
        f"Lean: `{summary['lean_version']}`",
        "",
        f"Scripts checked: `{summary['scripts_checked']}`",
        f"Accepted: `{summary['accepted']}`",
        f"Rejected: `{summary['rejected']}`",
        "",
        "| lemma | script | accepted | weight update |",
        "|---|---|---:|---:|",
    ]
    for row in summary["results"]:
        script = "<br>".join(f"`{t}`" for t in row["tactics"])
        lines.append(
            f"| {row['lemma']} | {script} | {row['accepted_by_mathlib_lean']} | "
            f"{row['old_weight']} -> {row['new_weight']} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
